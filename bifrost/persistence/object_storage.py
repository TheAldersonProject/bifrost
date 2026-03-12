"""Boto3 S3 Helper"""

import os
from collections import namedtuple
from typing import NamedTuple

import boto3
from botocore.config import Config
from dotenv import load_dotenv
from midgard.logs import Logger
from pydantic import Field, AnyHttpUrl, BaseModel


class S3Config(BaseModel):
    """S3 Config"""

    host: str | AnyHttpUrl = Field(..., description="S3 endpoint url")
    key: str = Field(..., description="AWS access key id")
    secret: str = Field(..., description="AWS secret access key")
    region: str = Field(..., description="AWS region name")
    ssl: str | bool | None = Field(default=True, description="Indicates whether to use SSL.")
    bucket: str | None = Field(default=None, description="AWS region name")


class S3Connector:
    """S3 Connector"""

    def __init__(self, s3_config: S3Config):
        """Initialize the S3 Helper."""

        self.logs = Logger.get_logger(logger_name="S3Connector")
        if not s3_config:
            self.logs.error("S3 Client Config cannot be empty.")
            raise ValueError("S3 Client Config cannot be empty.")

        self._s3_config = self._load_param_values(s3_config)
        self._s3 = boto3.client(
            "s3",
            endpoint_url=self._s3_config.host,
            aws_access_key_id=self._s3_config.key,
            aws_secret_access_key=self._s3_config.secret,
            config=Config(signature_version="s3v4"),
            region_name=self._s3_config.region,
        )

    def _load_param_values(self, config: S3Config) -> NamedTuple:
        """Loads the ORM config from system variables."""

        self.logs.debug("Loading ORM config from system variables.")
        load_dotenv()

        Config = namedtuple("Config", ["host", "key", "secret", "region", "ssl", "bucket"])
        config = Config(
            os.environ.get(config.host),
            os.environ.get(config.key),
            os.environ.get(config.secret),
            os.environ.get(config.region),
            os.environ.get(config.ssl),
            os.environ.get(config.bucket),
        )

        return config

    @property
    def bucket(self) -> str:
        """Retrieve the bucket name from the config."""
        return self._s3_config.bucket

    def create_bucket(self, bucket_name: str | None = None) -> None:
        """Create a bucket."""

        if not bucket_name:
            bucket_name = self.bucket

        if not bucket_name:
            self.logs.error("Bucket name cannot be empty.")
            raise ValueError("Bucket name cannot be empty.")

        self.logs.debug("Trying to create a new bucket.", bucket_name=bucket_name)
        try:
            self._s3.create_bucket(Bucket=bucket_name)
            self.logs.debug("Bucket created.", bucket_name=bucket_name)

        except self._s3.exceptions.BucketAlreadyOwnedByYou:
            self.logs.debug("Bucket already exists.", bucket_name=bucket_name)

        except Exception as e:
            self.logs.error("Error creating bucket.", error=str(e))
            raise e

    def write_to_s3(self, bucket_name: str, content: str, file_name: str) -> None:
        """Write a file to S3."""

        try:
            self._s3.put_object(Bucket=bucket_name, Key=file_name, Body=content)

        except Exception as e:
            self.logs.error("Error writing to S3.", error=str(e))
            raise e
