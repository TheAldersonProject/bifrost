"""Bifrost Service"""

from midgard.logs import Logger
from sqlalchemy import Engine
from sqlalchemy.orm import selectinload
from sqlmodel import Session, select

from bifrost.core.driver import DatabaseDriver
from bifrost.core.release import ObjectStorageRelease
from bifrost.model.data_contracts.contract import Contract, ContractSchema


class Service:
    """Bifrost Service"""

    def __init__(self):
        """Initialize Service"""

        self.logs = Logger.get_logger(logger_name=self.__class__.__name__)
        self._bifrost_orm: Engine = DatabaseDriver().orm.get_engine("pg_bifrost")

    def setup(self, checkfirst: bool = True, drop_before_create: bool = False) -> None:
        """Sets up the Bifrost Service"""

        self.logs.debug("Starting Bifrost setup.")
        from bifrost.core.release import DatabaseRelease

        DatabaseRelease().setup(checkfirst=checkfirst, drop_before_create=drop_before_create)
        ObjectStorageRelease().setup()

        self.logs.debug("Bifrost Service setup complete.")

    def list_all_contracts(self, contract_id: str | None = None, contract_version: str | None = None) -> list[Contract]:
        """List all contracts"""

        with Session(self._bifrost_orm) as session:
            stmt = select(Contract).options(
                selectinload(Contract.schema).selectinload(ContractSchema.properties),
                selectinload(Contract.servers),
            )

            if contract_id:
                stmt = stmt.where(Contract.id == contract_id)
            if contract_version:
                stmt = stmt.where(Contract.version == contract_version)

            res = session.exec(stmt).all()

        return res

    def load_from_id(self, contract_id: str) -> list[Contract]:
        """List all contracts"""

        return self.list_all_contracts(contract_id=contract_id)

    def load_from_id_and_version(self, contract: Contract) -> list[Contract]:
        """List all contracts"""

        contract_id: str = contract.id
        contract_version: str = contract.version
        return self.list_all_contracts(contract_id=contract_id, contract_version=contract_version)
