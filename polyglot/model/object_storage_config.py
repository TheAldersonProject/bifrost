"""Object storage config."""

from pydantic import Field

from polyglot.model.polyglot_entity import PolyglotBaseModel


class S3Config(PolyglotBaseModel):
    """S3 Config"""

    endpoint_url: str = Field(..., description="S3 endpoint url")
    aws_access_key_id: str = Field(..., description="AWS access key id")
    aws_secret_access_key: str = Field(..., description="AWS secret access key")
    region_name: str = Field(..., description="AWS region name")
    use_ssl: bool | None = Field(default=True, description="Indicates whether to use SSL.")
