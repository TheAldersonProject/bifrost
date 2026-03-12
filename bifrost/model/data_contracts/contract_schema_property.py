"""Creates the Data Contract Schema Property Model."""

from typing import Literal

from pydantic import AliasChoices
from sqlmodel import Column, Field

from bifrost.model.data_contracts.data_contract_commons import CommonModel
from bifrost.model.data_contracts.data_contract_commons import YggPostgresDialect as p


class ContractSchemaPropertyModel(CommonModel):
    """This entity describes the schema of the data contract."""

    __relationship_map__ = {"none": ""}
    __composed_id_prefix__ = "dc-schema-property"
    __composed_id_columns__ = ["physical_name", "logical_type"]
    __ignore_on_hash__ = [
        "record_hash",
    ]

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
            comment="Additional properties required for rule execution.",
        ),
        alias="authoritativeDefinitions",
        validation_alias=AliasChoices(
            "custom_properties",
            "customProperties",
            "CUSTOM_PROPERTIES",
        ),
    )

    primary_key: bool | None = Field(
        default=False,
        sa_column=Column(
            name="primary_key",
            type_=p.BOOLEAN_TYPE.value,
            primary_key=False,
            index=False,
            autoincrement=False,
            nullable=False,
            comment="Boolean value specifying whether the element is primary or not. Default is false.",
        ),
        alias="primaryKey",
        validation_alias=AliasChoices(
            "primary_key",
            "primaryKey",
            "PRIMARY_KEY",
        ),
    )

    primary_key_position: int | None = Field(
        default=-1,
        sa_column=Column(
            name="primary_key_position",
            type_=p.INTEGER_TYPE.value,
            primary_key=False,
            index=False,
            autoincrement=False,
            nullable=False,
            comment="""If element is a primary key, the position of the primary key element.
            Starts from 1. Example of `account_id, name` being primary key columns, `account_id`
            has primaryKeyPosition 1 and `name` primaryKeyPosition 2. Default to -1.""",
        ),
        alias="primaryKeyPosition",
        validation_alias=AliasChoices(
            "primary_key_position",
            "primaryKeyPosition",
            "PRIMARY_KEY_POSITION",
        ),
    )

    logical_type: Literal[
        "string",
        "date",
        "timestamp",
        "time",
        "number",
        "integer",
        "object",
        "array",
        "boolean",
        "float",
    ] = Field(
        sa_column=Column(
            name="logical_type",
            type_=p.VARCHAR_TYPE.value,
            primary_key=False,
            index=False,
            autoincrement=False,
            nullable=False,
            comment="The logical element data type.",
        ),
        alias="logicalType",
        validation_alias=AliasChoices("logical_type", "logicalType", "LOGICAL_TYPE"),
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

    physical_name: str = Field(
        sa_column=Column(
            name="physical_name",
            type_=p.VARCHAR_TYPE.value,
            primary_key=False,
            index=False,
            autoincrement=False,
            nullable=False,
            comment="The physical name of the element.",
        ),
        alias="physicalName",
        validation_alias=AliasChoices("physical_name", "physicalName", "PHYSICAL_NAME"),
    )

    required: bool | None = Field(
        default=False,
        sa_column=Column(
            name="required",
            type_=p.BOOLEAN_TYPE.value,
            primary_key=False,
            index=False,
            autoincrement=False,
            nullable=False,
            comment="""Indicates if the element may contain Null values;
            possible values are true and false. Default is false.""",
        ),
        alias="required",
        validation_alias=AliasChoices(
            "required",
            "REQUIRED",
        ),
    )

    unique: bool | None = Field(
        default=False,
        sa_column=Column(
            name="is_unique",
            type_=p.BOOLEAN_TYPE.value,
            primary_key=False,
            index=False,
            autoincrement=False,
            nullable=False,
            comment="""Indicates if the element contains unique values; possible values are true and false.
            Default is false.""",
        ),
        alias="unique",
        validation_alias=AliasChoices(
            "unique",
            "UNIQUE",
        ),
    )

    partitioned: bool | None = Field(
        default=False,
        sa_column=Column(
            name="partitioned",
            type_=p.BOOLEAN_TYPE.value,
            primary_key=False,
            index=False,
            autoincrement=False,
            nullable=False,
            comment="Indicates if the element is partitioned; possible values are true and false.",
        ),
        alias="partitioned",
        validation_alias=AliasChoices(
            "partitioned",
            "PARTITIONED",
        ),
    )

    partition_key_position: int | None = Field(
        default=-1,
        sa_column=Column(
            name="partition_key_position",
            type_=p.INTEGER_TYPE.value,
            primary_key=False,
            index=False,
            autoincrement=False,
            nullable=False,
            comment="""If element is used for partitioning, the position of the partition element.
            Starts from 1. Example of `country, year` being partition columns, `country` has
            partitionKeyPosition 1 and `year` partitionKeyPosition 2. Default to -1.""",
        ),
        alias="partitionKeyPosition",
        validation_alias=AliasChoices(
            "partition_key_position",
            "partitionKeyPosition",
            "PARTITION_KEY_POSITION",
        ),
    )

    classification: str | None = Field(
        default=None,
        sa_column=Column(
            name="classification",
            type_=p.VARCHAR_TYPE.value,
            primary_key=False,
            index=False,
            autoincrement=False,
            nullable=True,
            comment="""Can be anything, like confidential, restricted, and public to more advanced categorization.
            Some companies like PayPal, use data classification indicating the class of data in the element;
            expected values are 1, 2, 3, 4, or 5.""",
        ),
        alias="classification",
        validation_alias=AliasChoices("classification", "CLASSIFICATION"),
    )

    encrypted_name: str | None = Field(
        default=None,
        sa_column=Column(
            name="encrypted_name",
            type_=p.VARCHAR_TYPE.value,
            primary_key=False,
            index=False,
            autoincrement=False,
            nullable=True,
            comment="""The element name within the dataset that contains the encrypted element value.
            For example, unencrypted element `email_address` might have an encryptedName of `email_address_encrypt`.""",
        ),
        alias="encryptedName",
        validation_alias=AliasChoices("encrypted_name", "encryptedName", "CLASSIFICATION"),
    )

    examples: list[str] | None = Field(
        default=None,
        sa_column=Column(
            name="examples",
            type_=p.LIST_OF_STRINGS.value,
            primary_key=False,
            index=False,
            autoincrement=False,
            nullable=True,
            comment="List of sample element values.",
        ),
        validation_alias=AliasChoices("examples", "EXAMPLES"),
    )

    critical_data_element: bool | None = Field(
        default=False,
        sa_column=Column(
            name="critical_data_element",
            type_=p.BOOLEAN_TYPE.value,
            primary_key=False,
            index=False,
            autoincrement=False,
            nullable=True,
            comment="""True or false indicator;
            If element is considered a critical data element (CDE) then true else false.""",
        ),
        alias="criticalDataElement",
        validation_alias=AliasChoices("critical_data_element", "criticalDataElement", "CRITICAL_DATA_ELEMENT"),
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
