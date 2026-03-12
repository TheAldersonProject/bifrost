"""Physical data model representation of the Ygg Contract Table."""

import enum
from typing import Literal

from pydantic import AliasChoices
from sqlmodel import Column, Field

import bifrost.model.data_contracts.contract_schema as sc
import bifrost.model.data_contracts.contract_servers as ss
from bifrost.model.data_contracts.data_contract_commons import (
    SEMANTICAL_VERSION_PATTERN,
    CommonModel,
)
from bifrost.model.data_contracts.data_contract_commons import YggPostgresDialect as p


class KindEnum(str, enum.Enum):
    """Ygg Contract Enum."""

    DATA_CONTRACT = "DataContract"


class StatusEnum(str, enum.Enum):
    """Ygg Contract Enum."""

    DRAFT = "draft"
    ACTIVE = "active"
    RELEASE_CANDIDATE = "release_candidate"
    INACTIVE = "inactive"
    DEPRECATED = "deprecated"


class ContractFundamentalsModel(CommonModel):
    """This section contains general information about the contract. Fundamentals were also called demographics in early versions of ODCS."""

    __relationship_map__ = {
        "schema": sc.ContractSchemaModel,
        "servers": ss.ContractServerModel,
    }
    __composed_id_prefix__ = "dc"
    __composed_id_columns__ = ["name", "tenant", "domain", "physical_name"]
    __ignore_on_hash__ = [
        "record_hash",
    ]

    api_version: Literal["v3.1.0"] | None = Field(
        default="v3.1.0",
        sa_column=Column(
            name="api_version",
            type_=p.VARCHAR_TYPE.value,
            primary_key=False,
            index=False,
            autoincrement=False,
            nullable=False,
            default="v3.1.0",
            comment="Version of the standard used to build data contract. Default value is v3.1.0.",
        ),
        alias="apiVersion",
        validation_alias=AliasChoices("api_version", "API_VERSION", "apiVersion", "APIVERSION"),
    )

    kind: Literal["DataContract"] | None = Field(
        default="DataContract",
        sa_column=Column(
            name="kind",
            type_=p.VARCHAR_TYPE.value,
            primary_key=False,
            index=False,
            autoincrement=False,
            nullable=False,
            default="DataContract",
            comment="Version of the standard used to build data contract. Default value is v3.1.0.",
        ),
        validation_alias=AliasChoices("kind", "KIND"),
    )

    id: str | None = Field(
        default=None,
        regex=r"^[A-Za-z0-9_-]+$",
        sa_column=Column(
            name="id",
            type_=p.VARCHAR_TYPE.value,
            primary_key=True,
            index=True,
            autoincrement=False,
            nullable=False,
            comment="""Stable technical identifier for references. 
            Must be unique within its containing array.
            Cannot contain special characters ('-', '_' allowed).""",
        ),
        validation_alias=AliasChoices("id", "ID"),
    )

    name: str = Field(
        regex=r"^[A-Za-z0-9_-]+$",
        sa_column=Column(
            name="name",
            type_=p.VARCHAR_TYPE.value,
            primary_key=False,
            index=False,
            autoincrement=False,
            nullable=False,
            comment="Name of the data contract.",
        ),
        validation_alias=AliasChoices("name", "NAME"),
    )

    version: str | None = Field(
        default="0.0.1",
        regex=SEMANTICAL_VERSION_PATTERN,
        sa_column=Column(
            name="version",
            type_=p.VARCHAR_TYPE.value,
            default="0.0.1",
            primary_key=True,
            index=True,
            autoincrement=False,
            nullable=False,
            comment="Current version of the data contract.",
        ),
        validation_alias=AliasChoices("version", "VERSION"),
    )

    status: Literal["draft", "active", "deprecated", "latest"] | None = Field(
        default="draft",
        sa_column=Column(
            name="status",
            type_=p.VARCHAR_TYPE.value,
            default="draft",
            primary_key=False,
            index=False,
            autoincrement=False,
            nullable=False,
            comment="Current status of the dataset.",
        ),
        validation_alias=AliasChoices("status", "STATUS"),
    )

    tenant: str = Field(
        regex=r"^[A-Za-z0-9_-]+$",
        sa_column=Column(
            name="tenant",
            type_=p.VARCHAR_TYPE.value,
            primary_key=False,
            index=False,
            autoincrement=False,
            nullable=False,
            comment="Indicates the property the data is primarily associated with. Value is case insensitive.",
        ),
        validation_alias=AliasChoices("tenant", "TENANT"),
    )

    domain: str = Field(
        regex=r"^[A-Za-z0-9_-]+$",
        sa_column=Column(
            name="domain",
            type_=p.VARCHAR_TYPE.value,
            primary_key=False,
            index=False,
            autoincrement=False,
            nullable=False,
            comment="Name of the logical data domain.",
        ),
        validation_alias=AliasChoices("domain", "DOMAIN"),
    )

    data_product: str = Field(
        regex=r"^[A-Za-z0-9_-]+$",
        alias="dataProduct",
        sa_column=Column(
            name="data_product",
            type_=p.VARCHAR_TYPE.value,
            primary_key=False,
            index=False,
            autoincrement=False,
            nullable=False,
            comment="The name of the data product.",
        ),
        validation_alias=AliasChoices("data_product", "dataProduct", "DATA_PRODUCT"),
    )

    tags: list[str] | None = Field(
        sa_column=Column(
            name="tags",
            type_=p.LIST_OF_STRINGS.value,
            primary_key=False,
            index=False,
            autoincrement=False,
            nullable=True,
            comment="""A list of tags that may be assigned to the elements (object or property);
            the tags keyword may appear at any level. Tags may be used to better categorize an element.
            For example, `finance`, `sensitive`, `employee_record`.""",
        ),
        validation_alias=AliasChoices("tags", "TAGS"),
    )

    authoritative_definitions: list[dict] | None = Field(
        sa_column=Column(
            name="authoritative_definitions",
            type_=p.JSONB_TYPE.value,
            primary_key=False,
            index=False,
            autoincrement=False,
            nullable=True,
            comment="""List of links to sources that provide more details on the dataset;
            examples would be a link to an external definition, a training video, a git repo,
            data catalog, or another tool. Authoritative definitions follow the same structure in the standard.""",
        ),
        alias="authoritativeDefinitions",
        validation_alias=AliasChoices(
            "authoritative_definitions",
            "authoritativeDefinitions",
            "AUTHORITATIVE_DEFINITIONS",
        ),
    )

    description: dict = Field(
        sa_column=Column(
            name="description",
            type_=p.JSONB_TYPE.value,
            primary_key=False,
            index=False,
            autoincrement=False,
            nullable=True,
            comment="High level description of the dataset.",
        ),
        validation_alias=AliasChoices("description", "DESCRIPTION"),
    )

    record_hash: str | None = Field(
        default=None,
        sa_column=Column(
            name="record_hash",
            type_=p.VARCHAR_TYPE.value,
            primary_key=False,
            index=False,
            autoincrement=False,
            nullable=True,
            comment="The hash of the record.",
        ),
        validation_alias=AliasChoices("record_hash", "RECORD_HASH"),
    )

    creation_ets: int | None = Field(
        default=CommonModel.ets(),
        sa_column=Column(
            name="creation_ets",
            type_=p.BIGINT_TYPE.value,
            primary_key=False,
            index=False,
            autoincrement=False,
            nullable=True,
            comment="The creation epoch timestamp of the record.",
        ),
        validation_alias=AliasChoices("creation_ets", "CREATION_ETS"),
    )

    status_ets: int | None = Field(
        default=CommonModel.ets(),
        sa_column=Column(
            name="status_ets",
            type_=p.BIGINT_TYPE.value,
            primary_key=False,
            index=False,
            autoincrement=False,
            nullable=True,
            comment="The status epoch timestamp of the record.",
        ),
        validation_alias=AliasChoices("status_ets", "STATUS_ETS"),
    )
