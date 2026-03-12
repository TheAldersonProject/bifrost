"""Base Data Model for the Ygg project, to be reutilized by other models."""

import datetime
import enum
import time
from typing import Self

from midgard.file_utils import JsonFileTools
from sqlalchemy import Engine
from sqlalchemy.dialects.postgresql import (
    ARRAY,
    BIGINT,
    BOOLEAN,
    DATE,
    INTEGER,
    JSONB,
    TEXT,
    TIMESTAMP,
    VARCHAR,
)
from sqlalchemy.sql.ddl import CreateSchema
from sqlmodel import Session, SQLModel, inspect

from bifrost.core.orm import Orm

SEMANTICAL_VERSION_PATTERN: str = r"^(?P<major>0|[1-9]\d*)\.(?P<minor>0|[1-9]\d*)\.(?P<patch>0|[1-9]\d*)(?:-(?P<prerelease>(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*)(?:\.(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*))*))?(?:\+(?P<buildmetadata>[0-9a-zA-Z-]+(?:\.[0-9a-zA-Z-]+)*))?$"


class YggPostgresDialect(enum.Enum):
    """Ygg Base Dialect Enum."""

    ARRAY_TYPE = ARRAY
    BIGINT_TYPE = BIGINT
    BOOLEAN_TYPE = BOOLEAN
    DATE_TYPE = DATE
    INTEGER_TYPE = INTEGER
    JSONB_TYPE = JSONB
    LIST_OF_STRINGS = ARRAY(VARCHAR)
    TEXT_TYPE = TEXT
    TIMESTAMP_TYPE = TIMESTAMP
    VARCHAR_TYPE = VARCHAR


YGG_LOGICAL_TYPES_MAP = {
    "boolean": bool,
    "string": str,
    "text": str,
    "bigint": int,
    "integer": int,
    "float": float,
    "json": dict,
    "jsonb": dict,
    "variant": dict,
    "list_of_strings": list[str],
    "date": datetime.datetime,
    "timestamp": datetime.datetime,
}


class CommonModel(SQLModel):
    """Base Models to be inherited by other data models."""

    def add(self) -> None:
        """Write the model to the database."""

        with Session(Orm().engine) as session:
            session.add(self)
            session.commit()
            session.refresh(self)

    def update(self) -> None:
        """Update the model to the database."""

        with Session(Orm().engine) as session:
            session.add(self)
            session.commit()
            session.refresh(self)

    @staticmethod
    def get_logical_data_type(data_type: str) -> type:
        """Get the logical data type from the mapped data types."""

        return YGG_LOGICAL_TYPES_MAP.get(data_type, str)

    @staticmethod
    def ets() -> int:
        """Get the epoch timestamp."""
        return int(time.time_ns())

    @classmethod
    def _get_relationship_fields(cls) -> dict[str, type]:
        """Auto-detect relationship fields and their target models."""

        from sqlalchemy import inspect as sa_inspect

        relationships = {}
        mapper = sa_inspect(cls, raiseerr=False)
        if not mapper:
            return relationships

        for rel in mapper.relationships:
            relationships[rel.key] = rel.mapper.class_

        return relationships

    @classmethod
    def inflate(cls, data: dict) -> Self:
        """Recursively inflate nested dicts into model instances."""
        if not data:
            return None

        data = data.copy()
        relationships = cls._get_relationship_fields()

        for field_name, model_cls in relationships.items():
            if field_name in data:
                value = data[field_name]
                if isinstance(value, list):
                    data[field_name] = [model_cls.inflate(item) if isinstance(item, dict) else item for item in value]
                elif isinstance(value, dict):
                    data[field_name] = model_cls.inflate(value)

        instance = cls(**data)
        instance._compute_id_value()
        instance._compute_record_hash()
        return instance

    def _compute_id_value(self) -> None:
        """Compute and set the id value."""
        if not self.__class__.__composed_id_prefix__ or not self.__class__.__composed_id_columns__:
            return

        prefix = self.__class__.__composed_id_prefix__
        columns = self.__class__.__composed_id_columns__

        data = self.model_dump()
        composed_key = [data[c] for c in columns if c in data]
        composed_values = "-".join(composed_key).lower()

        self.id = f"{prefix}-{composed_values}"

    def _compute_record_hash(self) -> None:
        """Compute and set the record hash."""
        pk_columns = self.get_primary_keys()
        ignore_columns = ["creation_ets", "status_ets"]
        ignore_on_hash = getattr(self.__class__, "__ignore_on_hash__", [])
        relationship_fields = list(self._get_relationship_fields().keys())

        vals = {
            k: v
            for k, v in self.model_dump().items()
            if k not in ignore_on_hash
            and k not in ignore_columns
            and k not in pk_columns
            and k not in relationship_fields
            and not k.endswith("record_hash")
        }
        self.record_hash = JsonFileTools.json_to_sha256(vals)

    @classmethod
    def get_primary_keys(cls):
        return [col.name for col in inspect(cls).primary_key]

    @classmethod
    def _create_schema(cls, engine: Engine) -> None:
        """Create the schema."""

        schema_name = cls.__table_args__.get("schema", None)
        with Session(engine) as conn:
            try:
                conn.exec(CreateSchema(schema_name, if_not_exists=True))
                conn.commit()

            except Exception as e:
                raise e

    @classmethod
    def create_table(cls, engine: Engine, checkfirst: bool = True, create_schema: bool = True) -> None:
        """Create the table."""

        if create_schema:
            cls._create_schema(engine=engine)

        cls.metadata.create_all(bind=engine, checkfirst=checkfirst)
