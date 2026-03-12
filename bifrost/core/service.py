"""Bifrost Service"""

import os

from midgard.logs import Logger
from sqlalchemy.orm import selectinload
from sqlmodel import Session, select

from bifrost.core.orm import Orm, OrmConfig, OrmRelationalDatabaseConfig, OrmType
from bifrost.model.data_contracts.contract import Contract, ContractSchema
from bifrost.persistence.postgres_connector import PgDuckDbConnector


class Service:
    """Bifrost Service"""

    def __init__(self):
        """Initialize Service"""

        self.logs = Logger.get_logger(logger_name=self.__class__.__name__)

    def setup(self, checkfirst: bool = True) -> None:
        """Sets up the Bifrost Service"""

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

        bifrost_setup = OrmConfig(
            type=OrmType.PG_BIFROST_SETUP,
            parameters=OrmRelationalDatabaseConfig(**bifrost_setup_database_params),
        )

        bifrost = OrmConfig(
            type=OrmType.PG_BIFROST,
            parameters=OrmRelationalDatabaseConfig(**bifrost_database_params),
        )

        orm = Orm(config=[bifrost_setup, bifrost])
        setup_engine = orm.get_engine("pg_bifrost_setup")
        bifrost_database_name = os.getenv(bifrost.parameters.name, "bifrost")
        pg_conn = PgDuckDbConnector(
            database_name=bifrost_database_name, schema_name="data_contracts", engine=setup_engine
        )
        pg_conn.create_database()

        bifrost_engine = orm.get_engine("pg_bifrost")
        Contract.create_table(engine=bifrost_engine, checkfirst=checkfirst, create_schema=True)
        self.logs.debug("Bifrost Service setup complete.")

    def list_all_contracts(self, contract_id: str | None = None, status: str | None = None) -> list[Contract]:
        """List all contracts"""
        with Session(self._orm) as session:
            stmt = select(Contract).options(
                selectinload(Contract.schema).selectinload(ContractSchema.properties),
                selectinload(Contract.servers),
            )

            if contract_id:
                stmt = stmt.where(Contract.id == contract_id)
            if status:
                stmt = stmt.where(Contract.status == status)

            res = session.exec(stmt).all()

        return res

    def load_from_id(self, contract_id: str) -> list[Contract]:
        """List all contracts"""

        return self.list_all_contracts(contract_id=contract_id)
