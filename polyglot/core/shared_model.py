"""Shared Model Mixin."""

from typing import Any, Self

from midgard.file_utils import JsonFileTools as cm
from midgard.logs import Logger
from midgard.shared_model_mixin import SharedModelMixin

from polyglot.model.polyglot_entity import Entity, PolyglotBaseModel
from polyglot.persistence.quack_connector import QuackConnector
from polyglot.polyglot import PolyglotBaseConfig

logs = Logger.get_logger(logger_name="PolyglotModelMixin")


class PolyglotModelMixin(SharedModelMixin):
    """Shared Model Mixin."""

    def _model_hydrate(self, hydrate_data: dict) -> None:
        """Hydrate the model."""

        if not hydrate_data:
            return

        me = self
        dct = {k: v for k, v in hydrate_data.items() if k in me.model_fields}  #  type: ignore
        for k, v in dct.items():
            setattr(self, k, v)

    def _statement_map(self) -> dict[str, Any]:
        """Get the insert statement."""

        entity: Entity = None
        me: PolyglotBaseModel = self

        if isinstance(me, PolyglotBaseModel):
            entity = PolyglotBaseConfig.config().polyglot_entity

        values_map = me.model_dump()
        entity_catalog: str = entity.catalog
        entity_schema: str = entity.schema_
        entity_name: str = entity.name

        signature_skip_columns = [c.name for c in entity.columns if c.skip_from_signature]
        signature_dictionary = {k: v for k, v in values_map.items() if v and k not in signature_skip_columns}
        record_signature = cm.json_to_sha256(signature_dictionary)

        values_map["record_hash"] = record_signature
        logs.debug("Record signature", signature=record_signature)

        empty_columns = [k for k, v in values_map.items() if v in (None, "None", "")]
        non_model_columns = [m for m in list(values_map.keys()) if m not in [e.name for e in entity.columns]]
        drop_columns: list = [
            c.name
            for c in entity.columns
            if c.skip_from_physical_model or c.name in empty_columns or c.name in non_model_columns
        ] + non_model_columns or []

        if drop_columns:
            logs.debug("Dropping columns from the model.", columns=drop_columns)

        for drop in drop_columns or []:
            if drop in values_map:
                del values_map[drop]

        primary_key_columns: list[str] = [c.name for c in entity.columns if c.primary_key]
        hydrate_return: dict = {}
        for pk in primary_key_columns:
            hydrate_return[f"{entity_name}_{pk}"] = values_map.get(pk)

        first_layer_db_header: list[str] = [
            f
            for f in me.model_fields.keys()
            if f in list(values_map.keys()) and f in [c.name for c in entity.columns] and f not in drop_columns
        ]
        params: list[str] = ", ".join(["?" for f in first_layer_db_header])
        first_layer_db_header_string: str = ", ".join(first_layer_db_header)

        second_layer_db_header: list[str] = [c.name for c in entity.columns]
        second_layer_db_header_string: str = ", ".join(second_layer_db_header)

        values_list = list(values_map.values())
        values_list = [None if v in ("None", ...) else v for v in values_list]

        on_conflict_ignore = not entity.update_allowed
        first_layer_db_insert_statement: str = f"""
            INSERT INTO {entity_schema}.{entity_name} ({first_layer_db_header_string}) VALUES ({params}) 
            {" ON CONFLICT DO NOTHING" if on_conflict_ignore else ""}
        """

        logs.debug("First Layer Database Insert Statement Created.")

        second_layer_db_insert_statement: str = f"""
            INSERT INTO {entity_catalog}.{entity_schema}.{entity_name} ({second_layer_db_header_string})
            SELECT {second_layer_db_header_string} 
            FROM {entity_schema}.{entity_name}
        """
        second_layer_merge_constraints = "".join([f" and t.{pk} = s.{pk}" for pk in primary_key_columns])
        second_layer_db_merge_statement: str = f"""
            MERGE INTO {entity_catalog}.{entity_schema}.{entity_name} t
            USING (SELECT {second_layer_db_header_string} FROM {entity_schema}.{entity_name}) s
            ON (1=1 {second_layer_merge_constraints}) 
            {"WHEN MATCHED THEN UPDATE" if entity.update_allowed else ""}
            WHEN NOT MATCHED THEN INSERT
        """

        logs.debug("Second Layer Database Insert Statement Created.")
        statement_map = {
            "hydrate_return": hydrate_return,
            "first_layer_db_write_statement": first_layer_db_insert_statement,
            "first_layer_db_write_values": values_list,
            "second_layer_db_insert_statement": second_layer_db_insert_statement,
            "second_layer_db_merge_statement": second_layer_db_merge_statement,
        }
        logs.info("Insert Statement Created.")

        return statement_map

    def write(self) -> dict[str, Any]:
        """Write the model to the database."""

        instructions_map = self._statement_map()

        first_layer = {
            "statement": instructions_map.get("first_layer_db_write_statement", None),
            "values": instructions_map.get("first_layer_db_write_values", []),
        }

        QuackConnector().write(
            duckdb_instructions=[first_layer],
            ducklake_instructions=[instructions_map.get("second_layer_db_merge_statement", [])],
        )

        return instructions_map.get("hydrate_return", {})

    @classmethod
    def create_entity(cls) -> None:
        """Create an entity."""

        QuackConnector().setup()

    @classmethod
    def inflate(cls, data: dict, polyglot_entity: Entity | None = None, model_hydrate: dict | None = None) -> Self:
        """Inflate the model."""

        logs.debug("Inflating Model.", name=cls.__name__)

        me: Entity = cls
        data.update({"polyglot_entity": polyglot_entity})
        model = me(**data)
        if model_hydrate:
            model._model_hydrate(model_hydrate)

        return model
