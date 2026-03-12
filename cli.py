"""Polyglot main functionalities"""

from midgard.logs import Logger

from bifrost.core.service import Service
from bifrost.model.data_contracts.contract import Contract


class Bifrost:
    """Bifrost main class"""

    def __init__(self, contract: Contract | None = None) -> None:
        """Initialize Bifrost Service"""

        self.logs = Logger.get_logger(logger_name=self.__class__.__name__)
        if contract and isinstance(contract, Contract):
            contract: Contract = self._load_from_id_and_version(contract=contract)

        self.logs.info("Bifrost initialized.", contract=contract.id, version=contract.version)
        self._contract: Contract = contract

    @property
    def contract(self) -> Contract:
        """Get the Bifrost Contract"""

        if not self._contract:
            self.logs.error("Contract not loaded")
            return None

        return self._contract

    @staticmethod
    def _load_from_id_and_version(contract: Contract) -> Contract:
        """Load the contract from the id, if return_last is True, return the last version of the contract"""

        contract_from_id = Service().load_from_id_and_version(contract=contract)
        if not contract_from_id:
            return None

        contract_from_id = contract_from_id[0]
        return contract_from_id

    @staticmethod
    def setup(checkfirst: bool = True, drop_before_create: bool = False) -> None:
        Service().setup(checkfirst=checkfirst, drop_before_create=drop_before_create)

    @staticmethod
    def create_or_load_from_dict(contract_content: dict) -> "Bifrost":
        """Create or load a Bifrost contract from a dict"""
        contract = Contract.inflate(contract_content)
        bf = Bifrost(contract=contract)
        if not bf.contract:
            contract.add()
            bf = Bifrost(contract=contract)

        return bf
