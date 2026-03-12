"""Database configuration."""

from pathlib import Path

from pydantic import AnyHttpUrl, BaseModel, ConfigDict, Field, model_validator


class PolyglotBaseModel(BaseModel):
    """Dynamic Models Factory Base Model."""

    model_config = ConfigDict(use_enum_values=True)


class S3Config(PolyglotBaseModel):
    """S3 Config"""

    endpoint_url: AnyHttpUrl = Field(..., description="S3 endpoint url")
    aws_access_key_id: str = Field(..., description="AWS access key id")
    aws_secret_access_key: str = Field(..., description="AWS secret access key")
    region_name: str = Field(..., description="AWS region name")
    use_ssl: bool | None = Field(default=True, description="Indicates whether to use SSL.")

    @model_validator(mode="after")
    def validate_ssl_endpoint(self) -> "S3Config":
        if (
            self.use_ssl
            and not self.endpoint_url.scheme == "https"
            or (not self.use_ssl and self.endpoint_url.scheme == "https")
        ):
            raise ValueError("endpoint_url must use HTTPS when use_ssl is True or HTTP when use_ssl is False.")

        return self


class RelationalDatabaseConfig(PolyglotBaseModel):
    """Polyglot Database Config"""

    host: str | None = Field(default=None, description="Database host")
    name: str | None = Field(default=None, description="Database name")
    port: str | int | None = Field(default=None, description="Database port")
    user: str | None = Field(default=None, description="Database user")
    password: str | None = Field(default=None, description="Database password")
    auto_commit: bool | None = Field(default=True, description="Auto commit")


class DuckDbConfig(PolyglotBaseModel):
    """Polyglot Database Config"""

    path: str | Path | None = Field(default=":memory:", description="Database path, default is ':memory:'")
    duckdb_modules: list[str] | None = Field(default=None, description="DuckDB Modules")
    relational_db_config: RelationalDatabaseConfig | None = Field(default=None, description="Database host")


class PersistenceConfig(PolyglotBaseModel):
    """Polyglot Persistence Config"""

    db_config: RelationalDatabaseConfig | DuckDbConfig | None = Field(default=None, description="Database config.")
    cache_folder: str | Path | None = Field(default=None, description="Cache Folder")
    s3_config: S3Config | None = Field(default=None, description="Object Storage Configuration Parameters")
