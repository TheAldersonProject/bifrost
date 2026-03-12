"""Module for managing Bifrost releases and versioning."""

import os

from midgard.logs import Logger

from bifrost.core.driver import DatabaseDriver, ObjectStorageDriver
from bifrost.core.orm import Orm
from bifrost.model.data_contracts.contract import Contract


class DatabaseRelease:
    """Database release"""

    def __init__(self):
        """Initialize DatabaseRelease"""

        self.logs = Logger.get_logger(logger_name=self.__class__.__name__)
        self.logs.debug("Initializing DatabaseRelease.")

        _database_driver = DatabaseDriver()
        self._orm = _database_driver.orm
        self._bifrost_database_name = _database_driver.bifrost_database_name

    @staticmethod
    def _create_database(database_name: str, engine: Orm) -> None:
        """Creates a database."""
        from bifrost.persistence.postgres_connector import PgDuckDbConnector

        pg_conn = PgDuckDbConnector(database_name=database_name, engine=engine)
        pg_conn.create_database()

    def _create_bifrost_database(self) -> None:
        """Creates the Bifrost database."""

        self.logs.debug("Creating Bifrost database.")

        setup_engine = self._orm.get_engine("pg_bifrost_setup")
        bifrost_database_name = os.getenv(self._bifrost_database_name, "bifrost")
        self._create_database(database_name=bifrost_database_name, engine=setup_engine)

    def _create_bifrost_tables(self, checkfirst: bool = True, drop_before_create: bool = False) -> None:
        """Creates the Bifrost tables."""

        self.logs.debug("Creating Bifrost tables.")
        bifrost_engine = self._orm.get_engine("pg_bifrost")
        Contract.create_table(
            engine=bifrost_engine,
            checkfirst=checkfirst,
            create_schema=True,
            drop_before_create=drop_before_create,
        )
        self.logs.debug(
            "Bifrost tables created.",
            engine=bifrost_engine,
        )

    def setup(self, checkfirst: bool = True, drop_before_create: bool = False) -> None:
        """Sets up the database."""

        self.logs.debug("Setting up Bifrost database.")
        self._create_bifrost_database()
        self._create_bifrost_tables(checkfirst=checkfirst, drop_before_create=drop_before_create)


class ObjectStorageRelease:
    """Database release"""

    def __init__(self):
        """Initialize DatabaseRelease"""

        self.logs = Logger.get_logger(logger_name=self.__class__.__name__)
        self.logs.debug("Initializing ObjectStorageRelease.")

        self._artifacts_s3 = ObjectStorageDriver().artifacts_s3
        self._read_s3 = ObjectStorageDriver().read_s3
        self._write_s3 = ObjectStorageDriver().write_s3

    def setup(self) -> None:
        """Sets up the database."""

        self._artifacts_s3.create_bucket()
        self._read_s3.create_bucket()
        self._write_s3.create_bucket()
