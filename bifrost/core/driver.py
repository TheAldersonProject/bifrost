"""Bifrost Driver"""

from midgard.custom_decorators import singleton
from midgard.logs import Logger

from bifrost.core.orm import Orm, OrmConfig, OrmRelationalDatabaseConfig, OrmType
from bifrost.persistence.object_storage import S3Config, S3Connector


@singleton
class DatabaseDriver:
    """Bifrost Database Driver"""

    def __init__(self):
        """Bifrost Driver"""

        self.logs = Logger.get_logger(logger_name=self.__class__.__name__)
        self.logs.debug("Initializing Bifrost Driver.")

        bifrost_setup_database_params = dict(
            host="BIFROST_SETUP_DATABASE_HOST",
            name="BIFROST_SETUP_DATABASE_NAME",
            user="BIFROST_SETUP_DATABASE_USER",
            password="BIFROST_SETUP_DATABASE_PASSWORD",
            port="BIFROST_SETUP_DATABASE_PORT",
        )

        bifrost_database_params = dict(
            host="BIFROST_DB_HOST",
            name="BIFROST_DB_NAME",
            user="BIFROST_DB_USER",
            password="BIFROST_DB_PASSWORD",
            port="BIFROST_DB_PORT",
        )

        bifrost_ducklake_params = dict(
            host="BIFROST_DL_HOST",
            name="BIFROST_DL_NAME",
            user="BIFROST_DL_USER",
            password="BIFROST_DL_PASSWORD",
            port="BIFROST_DL_PORT",
        )

        self._bifrost_setup = OrmConfig(
            type=OrmType.PG_BIFROST_SETUP,
            parameters=OrmRelationalDatabaseConfig(**bifrost_setup_database_params),
        )

        self._bifrost_db = OrmConfig(
            type=OrmType.PG_BIFROST,
            parameters=OrmRelationalDatabaseConfig(**bifrost_database_params),
        )

        self._bifrost_ducklake = OrmConfig(
            type=OrmType.PG_DUCKLAKE,
            parameters=OrmRelationalDatabaseConfig(**bifrost_ducklake_params),
        )

        self._orm = self._load_engines()

    def _load_engines(self) -> Orm:
        """Loads the database engines."""

        self.logs.debug("Loading database engines.")
        return Orm(config=[self._bifrost_setup, self._bifrost_db])

    @property
    def orm(self) -> Orm:
        """Get the database engine."""

        return self._orm

    @property
    def bifrost_database_name(self) -> str:
        """Get the database name."""
        return self._bifrost_db.parameters.name


@singleton
class ObjectStorageDriver:
    """Bifrost Object Storage Driver"""

    def __init__(self):
        """Bifrost Object Storage Driver"""

        self.logs = Logger.get_logger(logger_name=self.__class__.__name__)
        self.logs.debug("Initializing ObjectStorageRelease.")

        bifrost_artifacts_s3_params = dict(
            host="BIFROST_S3_HOST",
            key="BIFROST_S3_KEY",
            secret="BIFROST_S3_SECRET",
            region="BIFROST_S3_REGION",
            ssl="BIFROST_S3_SSL",
            bucket="BIFROST_S3_BUCKET",
        )

        bifrost_read_s3_params = dict(
            host="BIFROST_READ_S3_HOST",
            key="BIFROST_READ_S3_KEY",
            secret="BIFROST_READ_S3_SECRET",
            region="BIFROST_READ_S3_REGION",
            ssl="BIFROST_READ_S3_SSL",
            bucket="BIFROST_READ_S3_BUCKET",
        )

        bifrost_write_s3_params = dict(
            host="BIFROST_WRITE_S3_HOST",
            key="BIFROST_WRITE_S3_KEY",
            secret="BIFROST_WRITE_S3_SECRET",
            region="BIFROST_WRITE_S3_REGION",
            ssl="BIFROST_WRITE_S3_SSL",
            bucket="BIFROST_WRITE_S3_BUCKET",
        )

        self._artifacts_s3 = S3Connector(S3Config(**bifrost_artifacts_s3_params))
        self._read_s3 = S3Connector(S3Config(**bifrost_read_s3_params))
        self._write_s3 = S3Connector(S3Config(**bifrost_write_s3_params))

    @property
    def artifacts_s3(self) -> S3Connector:
        """Get the artifacts S3 connector."""

        return self._artifacts_s3

    @property
    def read_s3(self) -> S3Connector:
        """Get the read S3 connector."""

        return self._read_s3

    @property
    def write_s3(self) -> S3Connector:
        """Get the write S3 connector."""

        return self._write_s3
