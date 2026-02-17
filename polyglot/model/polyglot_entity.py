"""Polyglot Entity"""

from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class PolyglotBaseModel(BaseModel):
    """Dynamic Models Factory Base Model."""

    model_config = ConfigDict(use_enum_values=True)


class ColumnDataType(PolyglotBaseModel):
    """Polyglot Db Entity Column Data Type"""

    name: str = Field(..., description="Column data type")
    logical: str = Field(default=None, description="Column data type value", examples=["string, int, float"])
    specific_physical: str | None = Field(default=None, description="Specific data type physical value")
    regex_pattern: str | None = Field(default=None, description="Regex pattern")


class EntityColumn(PolyglotBaseModel):
    """Polyglot Db Entity Column"""

    name: str = Field(..., description="Column name")
    alias: str | None = Field(default=None, description="Column name alias")
    data_type: ColumnDataType = Field(..., description="Column data type")
    enum: list | None = Field(default=None)
    comment: str | None = Field(default=None, description="Column comment")
    nullable: bool | None = Field(default=False, description="Whether the column can be null")
    primary_key: bool | None = Field(default=False, description="Whether the column is a primary key")
    unique_key: bool | None = Field(default=False, description="Whether the column is a unique key")
    check_constraint: str | None = Field(default=None, description="Check constraint")
    skip_from_update: bool | None = Field(default=False, description="Whether to skip the column from update")
    default_value: str | Any | None = Field(default=None, description="Default value")
    default_value_function: str | None = Field(default=None, description="Database function for default value")
    examples: list[Any] | None = Field(default=None)

    skip_from_signature: bool | None = Field(default=False, description="Whether to skip the column from signature")
    skip_from_physical_model: bool | None = Field(
        default=False, description="Whether to skip the column from physical model"
    )


class Entity(PolyglotBaseModel):
    """Polyglot Db Entity"""

    name: str = Field(..., description="Entity name")
    catalog: str = Field(..., description="Entity catalog name")
    schema_: str = Field(..., description="Entity schema name")
    comment: str | None = Field(default=None, description="Entity comment")
    update_allowed: bool | None = Field(default=True, description="Whether the entity can be updated")
    delete_allowed: bool | None = Field(default=True, description="Whether the entity can be deleted")
    columns: list[EntityColumn] | None = Field(default=None, description="Entity list of columns")
