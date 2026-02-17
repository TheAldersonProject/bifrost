"""Set of tools for PostgresSql."""

import psycopg
from midgard.logs import Logger
from psycopg import sql

from polyglot.polyglot import PolyglotBaseConfig

logs = Logger.get_logger(logger_name="PostgresConnector")


class PostgresConnector:
    """Postgres Connector"""

    def __init__(self):
        """Postgres Connector"""

        self.config = PolyglotBaseConfig.config()
        self._db_config = PolyglotBaseConfig.config().catalog_database_config
        logs.debug("Postgres Connector Initialized.", db_name=self._db_config.db_name)

    def _get_connection(self, db_name=None):
        """Creates a connection to the specified database."""

        target = db_name if db_name else self._db_config.db_name
        conn = psycopg.connect(
            host=self._db_config.host,
            user=self._db_config.user,
            password=self._db_config.password,
            port=self._db_config.port,
            dbname=target,
        )
        logs.debug("Postgres Connection Established.", db_name=target)
        return conn

    def _check_if_database_exists(self) -> bool:
        """Checks pg_catalog to see if the database exists."""

        logs.debug("Checking if database exists.", db_name=self._db_config.db_name)
        conn = self._get_connection(self._db_config.db_name)
        conn.autocommit = True
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT 1 FROM pg_catalog.pg_database WHERE datname = %s", (self.config.polyglot_entity.catalog,)
                )
                exists = cur.fetchone() is not None
                logs.debug("Database Exists Check Completed.", exists=exists)

        finally:
            conn.close()

        return exists

    def create_database(self) -> None:
        """Creates a database."""

        target_db_name = self.config.polyglot_entity.catalog
        logs.debug("Trying to create a new database.", db_name=target_db_name)
        if self._check_if_database_exists():
            logs.info("Database already exists.", db_name=target_db_name)

        else:
            conn = self._get_connection(self._db_config.db_name)
            conn.autocommit = True

            try:
                with conn.cursor() as cur:
                    logs.debug("Creating database.", db_name=target_db_name)
                    cur.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(target_db_name)))

            except psycopg.errors.DuplicateDatabase:
                logs.warning("Database already exists (race condition caught).", db_name=target_db_name)

            except Exception as e:
                logs.error("Error creating database.", db_name=target_db_name, error=str(e))
                raise

            else:
                logs.debug("Database Created.", db_name=target_db_name)

            finally:
                conn.close()
