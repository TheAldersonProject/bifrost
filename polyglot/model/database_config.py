"""Database configuration."""

from pathlib import Path

from pydantic import Field

from polyglot.model.polyglot_entity import PolyglotBaseModel


class DatabaseConfig(PolyglotBaseModel):
    """Polyglot Database Config"""

    host: str | None = Field(default=None, description="Database host")
    db_name: str | None = Field(default=None, description="Database name")
    port: str | int | None = Field(default=None, description="Database port")
    user: str | None = Field(default=None, description="Database user")
    password: str | None = Field(default=None, description="Database password")
    path: str | Path | None = Field(default=None, description="Database path")
    auto_commit: bool | None = Field(default=True, description="Auto commit")
