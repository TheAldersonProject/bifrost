"""Polyglot Driver"""

import re
from datetime import datetime
from typing import Annotated, Any, Literal, Optional, Type, Union

from midgard.logs import Logger
from pydantic import AliasChoices, ConfigDict, Field, create_model

from polyglot.core.shared_model import PolyglotModelMixin
from polyglot.model.polyglot_config import PolyglotConfig
from polyglot.model.polyglot_entity import PolyglotBaseModel
from polyglot.polyglot import PolyglotBaseConfig


class Driver:
    """Polyglot Driver"""

    def __init__(self):
        """Polyglot Driver"""

        self.logs = Logger.get_logger(logger_name=self.__class__.__name__)
        self.config: PolyglotConfig = PolyglotBaseConfig.config()

        self._driver: Type[Union[PolyglotBaseModel, PolyglotModelMixin]] | None = None
        self._build_polyglot_driver()

    @property
    def instance(self) -> Type[Union[PolyglotBaseModel, PolyglotModelMixin]]:
        """Get the driver"""

        return self._driver

    @staticmethod
    def _dialect(value: Any) -> str | None:
        """Build the dialect."""

        logical_type = {"string": str, "int": int, "integer": int, "timestamp": datetime}
        return value.specific_physical or logical_type.get(value.logical.lower().strip(), None)

    def _build_polyglot_driver(self) -> None:
        """Build the dynamic model instances."""

        logical_entity_name = re.sub(r"(?:^|_)(.)", lambda m: m.group(1).upper(), self.config.polyglot_entity.name)

        fields_map: dict[str, Any] = {}
        for col in self.config.polyglot_entity.columns:
            field = Field(
                default=col.default_value,
                validation_alias=AliasChoices(col.name, col.alias or col.name),
                description=col.comment,
                examples=col.examples,
                pattern=col.data_type.regex_pattern,
            )

            logical_type = self._dialect(col.data_type)
            if col.enum and isinstance(col.enum, list):
                logical_type = Literal[tuple(col.enum)]  # type: ignore

            annotated_field = Annotated[logical_type if not col.nullable else Optional[logical_type], field]
            fields_map[col.name] = annotated_field

        instance = create_model(
            logical_entity_name,
            __config__=ConfigDict(title=self.config.polyglot_entity.comment),
            __base__=(PolyglotBaseModel, PolyglotModelMixin),
            **fields_map,
        )

        self._driver = instance
        self.logs.debug("Dynamic Model Instance Created.", instance=instance.__name__)
