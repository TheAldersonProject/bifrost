"""Polyglot main functionalities"""

from bifrost.core.service import Service
from bifrost.model.data_contracts.contract import Contract


class Bifrost:
    """Bifrost main class"""

    def __init__(self, contract: Contract | None = None) -> None:
        """Initialize Bifrost Service"""

        if contract and isinstance(contract, Contract):
            contract = self._load_from_id(contract.id)

        self._contract = contract

    @property
    def contract(self) -> Contract:
        """Get the Bifrost Contract"""

        if not self._contract:
            raise ValueError("Contract not loaded")

        return self._contract

    @staticmethod
    def _load_from_id(contract_id: str) -> Contract:
        """Load the contract from the id, if return_last is True, return the last version of the contract"""

        contract_from_id = Service().load_from_id(contract_id)
        if not contract_from_id:
            raise ValueError("Contract with id %s not found", contract_id)

        contract_from_id = contract_from_id[0]
        return contract_from_id

    @staticmethod
    def list_all() -> list[Contract]:
        """List all versions of the contract from the id"""

        return Service().list_all_contracts()

    @staticmethod
    def setup(checkfirst: bool = True) -> None:
        Service().setup(checkfirst=checkfirst)


if __name__ == "__main__":
    Bifrost.setup()
    # Contract.create_table(checkfirst=True, create_schema=True)
    # contract_file = "/Users/thiagodias/Tad/projects/tyr/ygg-data-contracts/local-dev/contract.yaml"
    # contract_content = JsonFileTools.yaml_to_json(contract_file)
    # contract = Contract.inflate(contract_content)
    # contract.add()
    # all_contracts = Bifrost(contract=contract)

    # print(all_contracts.contract.tenant)
    # all_contracts.contract.tenant = "Dexter"
    # all_contracts.contract.update()
    # print(all_contracts.contract.tenant)
    # id = all_contracts[0].id
    # print(id)
    #
    # lid = Bifrost.load_from_id(id)
    # print(lid.id, lid.status)
    #
    # lids = Bifrost.load_from_id_and_status(lid.id, lid.status)
    # print(lids[0].servers)
    #
    # load = Bifrost.load_from_id(id)
