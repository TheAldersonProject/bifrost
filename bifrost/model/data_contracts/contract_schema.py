"""Physical data model representation of the Ygg Contract Table."""

from pydantic import AliasChoices
from sqlmodel import Column, Field

import bifrost.model.data_contracts.contract_schema_property as sp
from bifrost.model.data_contracts.data_contract_commons import CommonModel
from bifrost.model.data_contracts.data_contract_commons import YggPostgresDialect as p


class ContractSchemaModel(CommonModel):
    """This entity describes the schema of the data contract."""

    __relationship_map__ = {"properties": sp.ContractSchemaPropertyModel}
    __composed_id_prefix__ = "dc-schema"
    __composed_id_columns__ = ["physical_type", "physical_name"]

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
            comment="Name of the element.",
        ),
        validation_alias=AliasChoices("name", "NAME"),
    )

    physical_type: str = Field(
        sa_column=Column(
            name="physical_type",
            type_=p.VARCHAR_TYPE.value,
            primary_key=False,
            index=False,
            autoincrement=False,
            nullable=False,
            comment="The physical element data type in the data source.",
        ),
        alias="physicalType",
        validation_alias=AliasChoices("physical_type", "physicalType", "PHYSICAL_TYPE"),
    )

    description: str = Field(
        sa_column=Column(
            name="description",
            type_=p.VARCHAR_TYPE.value,
            primary_key=False,
            index=False,
            autoincrement=False,
            nullable=False,
            comment="Description of the element.",
        ),
        validation_alias=AliasChoices("description", "DESCRIPTION"),
    )

    business_name: str = Field(
        sa_column=Column(
            name="business_name",
            type_=p.VARCHAR_TYPE.value,
            primary_key=False,
            index=False,
            autoincrement=False,
            nullable=False,
            comment="Description of the element.",
        ),
        alias="businessName",
        validation_alias=AliasChoices("business_name", "businessName", "BUSINESS_NAME"),
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

    tags: list[str] | None = Field(
        default=None,
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

    custom_properties: dict | list[dict] | None = Field(
        default=None,
        sa_column=Column(
            name="custom_properties",
            type_=p.JSONB_TYPE.value,
            primary_key=False,
            index=False,
            autoincrement=False,
            nullable=True,
            comment="Additional properties.",
        ),
        alias="customProperties",
        validation_alias=AliasChoices(
            "custom_properties",
            "customProperties",
            "CUSTOM_PROPERTIES",
        ),
    )

    physical_name: str = Field(
        sa_column=Column(
            name="physical_name",
            type_=p.VARCHAR_TYPE.value,
            primary_key=False,
            index=False,
            autoincrement=False,
            nullable=False,
            comment="The physical element data type in the data source.",
        ),
        alias="physicalName",
        validation_alias=AliasChoices("physical_name", "physicalName", "PHYSICAL_NAME"),
    )

    data_granularity_description: str | None = Field(
        default=None,
        sa_column=Column(
            name="data_granularity_description",
            type_=p.VARCHAR_TYPE.value,
            primary_key=False,
            index=False,
            autoincrement=False,
            nullable=True,
            comment="The physical element data type in the data source.",
        ),
        alias="dataGranularityDescription",
        validation_alias=AliasChoices(
            "data_granularity_description",
            "physicalName",
            "DATA_GRANULARITY_DESCRIPTION",
        ),
    )

    record_hash: str | None = Field(
        default=None,
        sa_column=Column(
            name="record_hash",
            type_=p.VARCHAR_TYPE.value,
            primary_key=True,
            index=True,
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
