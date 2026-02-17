"""Polyglot Config"""

from pathlib import Path
from textwrap import dedent

from pydantic import Field

from polyglot.model.database_config import DatabaseConfig
from polyglot.model.object_storage_config import S3Config
from polyglot.model.polyglot_entity import Entity, PolyglotBaseModel


class PolyglotConfig(PolyglotBaseModel):
    """Polyglot Config"""

    polyglot_entity: Entity = Field(..., description="Polyglot Entity")
    catalog_database_config: DatabaseConfig = Field(..., description="Catalog Database Configuration Parameters")
    object_storage_config: S3Config = Field(..., description="Object Storage Configuration Parameters")
    recreate_existing_entity: bool = Field(default=False, description="Recreate existing objects")
    duckdb_modules: list[str] = Field(default_factory=list, description="DuckDB Modules")
    cache_folder: str | Path | None = Field(default=None, description="Cache Folder")
    data: dict | None = Field(default=None, description="Polyglot Data")
    parquet_from_s3: str | None = Field(default=None, description="Polyglot Data from s3")

    @property
    def attach_ducklake_catalog(self) -> str:
        """Attach the DuckLake catalog instruction."""

        catalog = self.polyglot_entity.catalog.lower()
        return f"ATTACH 'ducklake:{catalog}_secret' as {catalog};"

    @property
    def ducklake_secret(self) -> str:
        """Get the object storage secret."""

        catalog = self.polyglot_entity.catalog.lower()
        ducklake_secret = f"""
            CREATE OR REPLACE PERSISTENT SECRET {catalog}_secret (
            TYPE ducklake,
            METADATA_PATH 'dbname={catalog}',
            DATA_PATH 's3://repository/{catalog}/',
        """
        ducklake_secret += "\nMETADATA_PARAMETERS MAP {'TYPE': 'postgres', 'SECRET': 'CATALOG_POSTGRES'});"
        ducklake_secret = dedent(ducklake_secret)

        return ducklake_secret

    @property
    def catalog_database_secret(self) -> str:
        """Get the object storage secret."""

        catalog_secret = f"""
            CREATE OR REPLACE PERSISTENT SECRET CATALOG_POSTGRES (
            TYPE postgres,
            HOST '{self.catalog_database_config.host}',
            PORT {self.catalog_database_config.port},
            DATABASE {self.catalog_database_config.db_name},
            USER '{self.catalog_database_config.user}',
            PASSWORD '{self.catalog_database_config.password}'
            );
        """
        catalog_secret = dedent(catalog_secret)

        return catalog_secret

    @property
    def s3_config(self) -> str:
        """Get the object storage secret."""
        object_storage_secret = f"""
            CREATE OR REPLACE PERSISTENT SECRET OBJECT_STORAGE_SECRET (
            TYPE S3,
            KEY_ID '{self.object_storage_config.aws_access_key_id}',
            SECRET '{self.object_storage_config.aws_secret_access_key}',
            ENDPOINT '{self.object_storage_config.endpoint_url}',
            URL_STYLE 'path',
            USE_SSL false
            );
        """
        object_storage_secret = dedent(object_storage_secret)
        return object_storage_secret
