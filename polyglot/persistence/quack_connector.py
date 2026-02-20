"""Quack is a DuckDB and DuckLake connector."""

from typing import Any, Self

import duckdb
from midgard.logs import Logger

from polyglot.model.custom import get_data_type
from polyglot.model.enums import QuackType
from polyglot.model.polyglot_config import PolyglotConfig
from polyglot.model.polyglot_entity import ColumnDataType, EntityColumn, PolyglotBaseModel
from polyglot.persistence.postgres_connector import PostgresConnector
from polyglot.polyglot import PolyglotBaseConfig


class _QuackResource(PolyglotBaseModel):
    """Quack Resource."""

    schema_ddl: str
    entity_ddl: str


class _QuackDuckLakeResource(_QuackResource):
    """Quack Resource."""

    install_modules: str
    load_modules: str
    s3_secret: str
    catalog_secret: str
    duck_lake_secret: str
    attach_duck_lake: str


class QuackConnector:
    """Quack Connector."""

    def __init__(self):
        """Initialize Quack Connector."""

        self.logs = Logger.get_logger(logger_name=self.__class__.__name__)
        self.config: PolyglotConfig = PolyglotBaseConfig.config()

        self._duck_lake_connector: _QuackDuckLakeResource | None = self._ducklake_setup()
        self._duck_db_connector: _QuackResource | None = self._duckdb_setup()

    @staticmethod
    def _dialect(value: ColumnDataType) -> Any | None:
        """Build the dialect."""

        if value.specific_physical:
            return value.specific_physical

        value = get_data_type(value.name, "physical").get("type")

        return value

    def _schema_ddl(self, quack_type: QuackType) -> str:
        """Get the DuckDb schema ddl."""

        ducklake_catalog = ""
        if quack_type == QuackType.DUCKLAKE:
            ducklake_catalog: str = f"{self.config.polyglot_entity.catalog}."

        entity_schema_spec = f"CREATE SCHEMA IF NOT EXISTS {ducklake_catalog}{self.config.polyglot_entity.schema_};"
        self.logs.debug("Entity schema spec created")

        return entity_schema_spec

    def _get_entity_spec(self, entity_type: QuackType) -> str:
        """Create or replace or if not exists entities in DuckLake"""

        header = self._get_create_entity_header(entity_type=entity_type)
        columns = self._get_entity_columns_definition(entity_type)

        stmt: str = f"{header} (\n{columns}\n);"
        return stmt

    def _get_create_entity_header(self, entity_type: QuackType) -> str:
        """Return the creation statement of the entity header."""

        create_or_replace: str = "CREATE OR REPLACE TABLE"
        create_if_not_exists: str = "CREATE TABLE IF NOT EXISTS"

        ducklake_catalog = ""
        if entity_type == QuackType.DUCKLAKE:
            ducklake_catalog: str = f"{self.config.polyglot_entity.catalog}."

        create_table_header: str = (
            create_if_not_exists if not self.config.recreate_existing_entity else create_or_replace
        )
        entity_header = f"{create_table_header} {ducklake_catalog}{self.config.polyglot_entity.schema_.lower()}.{self.config.polyglot_entity.name.lower()}"

        return entity_header

    @staticmethod
    def _get_db_column_ddl_definition(column: EntityColumn, entity_type: QuackType) -> str:
        """Return the column ddl definition."""

        duck_lake_column_spec: str = "{name} {type}"
        duck_db_column_spec: str = duck_lake_column_spec + "{default_value}{nullable}{check_constraint}"
        column_ddl_definition: str = ""

        reserved_names_translation = {"date": "date_", "timestamp": "timestamp_"}
        column_name = reserved_names_translation.get(column.name, column.name)

        if entity_type == QuackType.DUCKLAKE:
            column_ddl_definition = duck_lake_column_spec.format(
                name=column_name.lower(),
                type=QuackConnector._dialect(column.data_type),
            )

        elif entity_type == QuackType.DUCKDB:
            default_value: str = ""
            nullable: str = "" if column.nullable else " NOT NULL"

            if column.enum:
                data_type: str = f""" ENUM({", ".join(["'" + enum_ + "'" for enum_ in column.enum])}) """
                check_constraint: str | None = None

            else:
                data_type: str = QuackConnector._dialect(column.data_type)
                check_constraint: str | None = None

                if column.data_type.regex_pattern:
                    column_check_constraint = (
                        f"regexp_matches({column_name.lower()}, '{column.data_type.regex_pattern}')"
                    )
                    check_constraint = f" CHECK ({column_check_constraint})"

            if default_value not in ("None", ...) and (column.default_value or column.default_value_function):
                if data_type.upper() in ("TIMESTAMP", "TIMESTAMPTZ", "TIMESTAMP_LTZ", "BIGINT", "INTEGER"):
                    if column.default_value_function:
                        default_value = f" DEFAULT {column.default_value_function}"
                    else:
                        default_value = f" DEFAULT {column.default_value}"

                elif data_type.upper() not in ("BOOL", "BOOLEAN"):
                    default_value = f" DEFAULT '{column.default_value}'"

                elif data_type.upper() in ("BOOL", "BOOLEAN"):
                    default_value = f" DEFAULT {1 if column.default_value else 0}"

                elif default_value == ...:
                    default_value = ""

                else:
                    default_value = f" DEFAULT {column.default_value}"

            if default_value in ("None", ..., None):
                default_value = ""

            column_ddl_definition = duck_db_column_spec.format(
                default_value=default_value or "",
                name=column_name.lower(),
                type=data_type,
                nullable=nullable or "",
                check_constraint=check_constraint or "",
            )

        return column_ddl_definition

    def _get_entity_columns_definition(self, entity_type: QuackType) -> str:
        """Return the entity definition."""

        columns: list[str] = []
        primary_key_columns: list[str] = []
        for column in self.config.polyglot_entity.columns:
            column_ddl_definition = self._get_db_column_ddl_definition(column, entity_type)
            columns.append(column_ddl_definition)

            if column.primary_key:
                primary_key_columns.append(column.name)

        if entity_type == QuackType.DUCKDB:
            primary_key_ddl_definition = f"PRIMARY KEY ({', '.join(primary_key_columns)})"
            columns.append(primary_key_ddl_definition)

        columns_definition = "  ,\n".join(columns)
        return columns_definition

    def _duckdb_setup(self) -> _QuackResource:
        """Configure DuckDB."""

        return _QuackResource(
            schema_ddl=self._schema_ddl(QuackType.DUCKDB),
            entity_ddl=self._get_entity_spec(QuackType.DUCKDB),
        )

    def _ducklake_setup(self) -> _QuackDuckLakeResource:
        """Configure DuckLake."""

        install_modules = "".join([f"install {m}; " for m in self.config.duckdb_modules])
        load_modules = "".join([f"load {m}; " for m in self.config.duckdb_modules])

        return _QuackDuckLakeResource(
            install_modules=install_modules,
            load_modules=load_modules,
            schema_ddl=self._schema_ddl(QuackType.DUCKLAKE),
            s3_secret=self.config.s3_config,
            catalog_secret=self.config.catalog_database_secret,
            duck_lake_secret=self.config.ducklake_secret,
            attach_duck_lake=self.config.attach_ducklake_catalog,
            entity_ddl=self._get_entity_spec(QuackType.DUCKLAKE),
        )

    def _execute_instructions(self, instructions: list[str] | str, duckdb_file: str | None = ":memory:") -> None:
        """Execute a list of SQL statements against the database."""

        if not instructions:
            raise ValueError("Instructions cannot be empty.")

        if isinstance(instructions, str):
            instructions = [instructions]

        with duckdb.connect(duckdb_file, read_only=False) as con:
            try:
                for statement in instructions:
                    self.logs.debug("Executing SQL statement.")
                    if isinstance(statement, dict):
                        con.execute(statement["statement"], statement["values"])
                        short_statement = (
                            str(statement["statement"]).replace("\n", " ").replace("\t", " ").strip().lower()[:30]
                        )
                        self.logs.debug("SQL statement executed successfully.", statement=short_statement)
                        continue
                    elif isinstance(statement, list):
                        statement = " ".join(statement)

                    con.execute(statement)
                    short_statement = str(statement).replace("\n", " ").replace("\t", " ").strip().lower()[:30]
                    self.logs.debug("SQL statement executed successfully.", statement=short_statement)

            except Exception as e:
                self.logs.error("Error executing SQL statement.", error=str(e), statement=str(statement))
                raise e

    def write(self, duckdb_instructions: list[str], ducklake_instructions: list[str]) -> Self:
        """Configure Quack Driver."""

        self.logs.info("Setting up Quack Resources!")

        ducklake_map = self._ducklake_setup()

        ddb = self._duckdb_setup()
        instructions = [
            ddb.schema_ddl,
            ddb.entity_ddl,
            ducklake_map.install_modules,
            ducklake_map.load_modules,
            ducklake_map.s3_secret,
            ducklake_map.catalog_secret,
            ducklake_map.duck_lake_secret,
            ducklake_map.attach_duck_lake,
        ]

        base_instructions = "\n".join(instructions) + "\n"
        instructions = [base_instructions] + duckdb_instructions + ducklake_instructions

        self._execute_instructions(instructions)
        return self

    def setup(self) -> Self:
        """Set up the Quack Resources."""

        self.logs.info("Setting up Quack Resources.")

        duckdb_map = self._duckdb_setup()
        ducklake_map = self._ducklake_setup()

        instructions = [
            duckdb_map.schema_ddl,
            duckdb_map.entity_ddl,
            ducklake_map.install_modules,
            ducklake_map.load_modules,
            ducklake_map.s3_secret,
            ducklake_map.catalog_secret,
            ducklake_map.duck_lake_secret,
            ducklake_map.attach_duck_lake,
            ducklake_map.schema_ddl,
            ducklake_map.entity_ddl,
        ]

        PostgresConnector().create_database()

        self._execute_instructions(instructions)
        return self
