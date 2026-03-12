"""Physical data model representation of the Ygg Contract Servers Table."""

from typing import Literal

from pydantic import AliasChoices
from sqlmodel import Column, Field

from bifrost.model.data_contracts.data_contract_commons import CommonModel
from bifrost.model.data_contracts.data_contract_commons import YggPostgresDialect as p


class ContractServerModel(CommonModel):
    """This entity describes a server of the data contract."""

    __relationship_map__ = {"none": ""}
    __composed_id_prefix__ = "dc-srv"
    __composed_id_columns__ = [
        "environment",
        "server",
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

    server: str | None = Field(
        default=None,
        regex=r"^[A-Za-z0-9_-]+$",
        sa_column=Column(
            name="server",
            type_=p.VARCHAR_TYPE.value,
            primary_key=True,
            index=True,
            autoincrement=False,
            nullable=False,
            comment="Name of the server",
        ),
        validation_alias=AliasChoices("server", "SERVER"),
    )

    type: Literal[
        "duckdb",
        "ducklake",
        "file",
        "pg_bifrost",
        "pg_duckdb",
        "pg_ducklake",
        "postgresql",
        "s3_bifrost",
        "s3_read",
        "s3_write",
        "snowflake",
    ] = Field(
        sa_column=Column(
            name="type",
            type_=p.VARCHAR_TYPE.value,
            primary_key=False,
            index=False,
            autoincrement=False,
            nullable=False,
            comment="Type of the server.",
        ),
        validation_alias=AliasChoices("type", "TYPE"),
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

    environment: Literal["production", "staging", "development", "testing", "qa", "local", "general"] = Field(
        sa_column=Column(
            name="environment",
            type_=p.VARCHAR_TYPE.value,
            primary_key=False,
            index=False,
            autoincrement=False,
            nullable=False,
            comment="environment of the server.",
        ),
        validation_alias=AliasChoices("environment", "ENVIRONMENT"),
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
