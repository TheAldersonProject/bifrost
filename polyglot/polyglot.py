"""Polyglot main functionalities"""

from typing import Self

from midgard.custom_decorators import singleton

from polyglot.model.polyglot_config import PolyglotConfig


@singleton
class PolyglotBaseConfig:
    """Polyglot main class"""

    def __init__(self, config: PolyglotConfig | None = None):
        """Initialize Polyglot Service"""

        self._config = config

    def set_config(self, config: PolyglotConfig):
        """Set the Polyglot Config"""

        self._config = config

    @property
    def get_config(self) -> PolyglotConfig:
        """Get the Polyglot Config"""

        return self._config

    @staticmethod
    def config() -> PolyglotConfig:
        return PolyglotBaseConfig().get_config


class Polyglot:
    """Polyglot main class"""

    def __init__(self, config: PolyglotConfig):
        """Initialize Polyglot Service"""

        from polyglot.core.driver import Driver

        PolyglotBaseConfig().set_config(config)
        self._driver = Driver()

    @property
    def driver(self):
        """Get the driver"""

        return self._driver.instance

    def create(self) -> Self:
        """Create the polyglot entity."""

        self.driver.create_entity()
        return self

    def write(self) -> dict:
        """Write data to the Polyglot Catalog"""

        data = PolyglotBaseConfig.config().data
        if not data:
            raise ValueError("Data must be provided.")

        return self.driver.inflate(data).write()


class SugarPolyglot:
    """Polyglot main class"""

    @staticmethod
    def write(config: PolyglotConfig, create: bool = False) -> dict:
        """Write data to the Polyglot Catalog & Create Polyglot Entity if True"""

        p = Polyglot(config)
        if create:
            p.create()

        return p.write()
