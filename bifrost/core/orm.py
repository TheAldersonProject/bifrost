"""Object Relational Mapping."""

import enum
import os
from collections import namedtuple
from urllib.parse import quote

from dotenv import load_dotenv
from midgard.logs import Logger
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import Engine, create_engine


class OrmRelationalDatabaseConfig(BaseModel):
    """ORM Config."""

    host: str = Field(..., description="Database host")
    name: str | int = Field(..., description="Database name")
    port: str | int = Field(..., description="Database port")
    user: str = Field(..., description="Database user")
    password: str = Field(..., description="Database user")
    auto_commit: bool | None = Field(default=True, description="Auto commit")

    # engine: Engine | None = Field(default=None, description="Database engine")


class OrmDuckLakeDatabaseConfig(OrmRelationalDatabaseConfig):
    """ORM Config."""

    additional_modules: list[str] | None = Field(default_factory=list, description="DuckDB Modules")


class OrmType(enum.Enum):
    """ORM Type."""

    PG_BIFROST_SETUP = "pg_bifrost_setup"
    PG_BIFROST = "pg_bifrost"
    PG_DUCKLAKE = "pg_ducklake"


class OrmConfig(BaseModel):
    """ORM Config."""

    model_config = ConfigDict(use_enum_values=True)

    parameters: OrmRelationalDatabaseConfig | OrmDuckLakeDatabaseConfig
    type: OrmType = Field(default=OrmType.PG_BIFROST)


class Orm:
    """Performs ORM operations.

    Provides methods for interacting with the database using ORM techniques.
    """

    POSTGRES_URL = "postgresql+psycopg2://{user}:{password}@{host}:{port}/{database}"
    DUCKDB_URL = "duckdb:////{user}:{password}@{host}:{port}/{database}"

    def __init__(self, config: OrmConfig | list[OrmConfig]):
        """Initialize ORM."""

        self.logs = Logger.get_logger(logger_name=self.__class__.__name__)
        self.logs.debug("Initializing ORM.")

        if not isinstance(config, list):
            config = [config]

        self._config_list: list[OrmConfig] = config
        self._engines_map: dict[str, Engine] = self._create_database_engines()

    @property
    def engine(self) -> Engine:
        """Get the database engine."""

        return self._engines_map.get("default")

    def get_engine(self, engine_name: str) -> Engine:
        """Get the database engine."""
        return self._engines_map.get(engine_name)

    def _load_param_values(self, config: OrmConfig) -> namedtuple:
        """Loads the ORM config from system variables."""

        self.logs.debug("Loading ORM config from system variables.")
        load_dotenv()

        Config = namedtuple("Config", ["host", "port", "name", "user", "password"])
        config = Config(
            os.environ.get(config.parameters.host),
            os.environ.get(config.parameters.port),
            os.environ.get(config.parameters.name),
            os.environ.get(config.parameters.user),
            os.environ.get(config.parameters.password),
        )

        return config

    def _create_database_engines(self) -> dict:
        """Returns the database engine."""
        self.logs.debug("Creating database engines.")

        database_engines = {}
        for conf in self._config_list:
            params = self._load_param_values(conf)
            database_url = self.POSTGRES_URL.format(
                host=params.host,
                port=params.port,
                database=params.name,
                user=params.user,
                password=quote(params.password),
            )

            engine = create_engine(url=database_url, echo=False, isolation_level="AUTOCOMMIT")
            self.logs.debug("Database engine created.")
            if len(self._config_list) == 1 or conf.type == OrmType.PG_BIFROST:
                database_engines["default"] = engine

            database_engines[conf.type] = engine

        return database_engines
