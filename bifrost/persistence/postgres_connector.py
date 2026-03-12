"""Set of tools for PostgresSql."""

from midgard.logs import Logger
from sqlalchemy import Engine, text


class PgDuckDbConnector:
    """Postgres DuckDb Connector"""

    def __init__(self, database_name: str, engine: Engine):
        """Postgres Connector"""

        self.logs = Logger.get_logger(logger_name=self.__class__.__name__)
        self._db_name = database_name
        self._engine: Engine = engine

        self.logs.debug(
            "Postgres Connector Initialized.",
            db=self._db_name,
        )

    def create_database(self) -> None:
        """Creates a Postgres Database."""

        # with Session(self._engine) as session:
        #     session.exec()

        stmt: str = f"CREATE DATABASE {self._db_name}"
        with self._engine.connect() as conn:
            result = conn.execute(text(f"SELECT 1 FROM pg_database WHERE datname = '{self._db_name}'"))
            if not result.fetchone():
                conn.execute(text(stmt))
            conn.commit()

        self.logs.debug("New database created.", db_name=self._db_name)
