"""Creates the Data Contract model."""

from typing import Optional

from sqlalchemy import ForeignKeyConstraint
from sqlmodel import Column, Field, Relationship

from bifrost.model.data_contracts.contract_fundamentals import ContractFundamentalsModel
from bifrost.model.data_contracts.contract_schema import ContractSchemaModel
from bifrost.model.data_contracts.contract_schema_property import (
    ContractSchemaPropertyModel,
)
from bifrost.model.data_contracts.contract_servers import ContractServerModel


class ContractSchemaProperty(ContractSchemaPropertyModel, table=True):
    """Data Contract Schema Property Model."""

    __tablename__ = "contract_schema_property"
    __table_args__ = (
        ForeignKeyConstraint(
            ["contract_schema_id", "contract_id", "contract_version"],
            [
                "data_contracts.contract_schema.id",
                "data_contracts.contract_schema.contract_id",
                "data_contracts.contract_schema.contract_version",
            ],
        ),
        {
            "schema": "data_contracts",
            "extend_existing": True,
        },
    )

    contract_schema_id: str | None = Field(default=None, sa_column=Column(primary_key=True))
    contract_id: str | None = Field(default=None, sa_column=Column(primary_key=True))
    contract_version: str | None = Field(default=None, sa_column=Column(primary_key=True))

    contract_schema: Optional["ContractSchema"] = Relationship(
        back_populates="properties",
        sa_relationship_kwargs={"lazy": "selectin"},
    )


class ContractSchema(ContractSchemaModel, table=True):
    """Data Contract Schema Model."""

    __tablename__ = "contract_schema"
    __table_args__ = (
        ForeignKeyConstraint(
            ["contract_id", "contract_version"],
            ["data_contracts.contract.id", "data_contracts.contract.version"],
        ),
        {
            "schema": "data_contracts",
            "extend_existing": True,
        },
    )

    contract_id: str | None = Field(default=None, sa_column=Column(primary_key=True))
    contract_version: str | None = Field(default=None, sa_column=Column(primary_key=True))

    properties: list["ContractSchemaProperty"] | None = Relationship(
        back_populates="contract_schema",
        sa_relationship_kwargs={"lazy": "selectin"},
    )

    contract: Optional["Contract"] = Relationship(
        back_populates="schema",
        sa_relationship_kwargs={"lazy": "selectin"},
    )


class ContractServer(ContractServerModel, table=True):
    """Data Contract Server Model."""

    __tablename__ = "contract_server"
    __table_args__ = (
        ForeignKeyConstraint(
            ["contract_id", "contract_version"],
            ["data_contracts.contract.id", "data_contracts.contract.version"],
        ),
        {
            "schema": "data_contracts",
            "extend_existing": True,
        },
    )

    contract_id: str | None = Field(default=None, sa_column=Column(primary_key=True))
    contract_version: str | None = Field(default=None, sa_column=Column(primary_key=True))

    contract: Optional["Contract"] = Relationship(
        back_populates="servers",
        sa_relationship_kwargs={"lazy": "selectin"},
    )


class Contract(ContractFundamentalsModel, table=True):
    """Data Contract Model."""

    __tablename__ = "contract"
    __table_args__ = {"schema": "data_contracts", "extend_existing": True}

    __ignore_on_hash__ = ["version", "status"]

    schema: list[ContractSchema] | None = Relationship(
        back_populates="contract",
        sa_relationship_kwargs={"lazy": "selectin"},
    )

    servers: list[ContractServer] | None = Relationship(
        back_populates="contract",
        sa_relationship_kwargs={"lazy": "selectin"},
    )

    class Config:
        arbitrary_types_allowed = True
