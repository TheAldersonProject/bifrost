"""Polyglot Driver"""

from midgard.logs import Logger

from bifrost.model.data_contracts.contract import Contract


class Driver:
    """Polyglot Driver"""

    def __init__(self, contract: Contract):
        """Polyglot Driver"""

        self.logs = Logger.get_logger(logger_name=self.__class__.__name__)
        self._contract = contract

        self.logs.debug("Initializing Polyglot Driver.", contract=contract.id)
