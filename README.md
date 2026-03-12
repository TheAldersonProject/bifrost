# Bifrost

A small toolkit to build dynamic, typed data models from a Polyglot Data Model and write data into DuckDB/DuckLake (with a PostgreSQL-backed catalog) and S3-compatible object storage.

Bifrost turns an entity specification into a runtime Pydantic model and provides simple helpers to create the physical entity and write records safely.

## Features
- Dynamic Pydantic model generation from an entity spec
- Two-layer write flow: stage in DuckDB, then merge into DuckLake catalog
- Simple API to create entities and write data
- S3 object storage integration via DuckDB/HTTPFS
- Minimal dependencies; logs and utilities via Midgard

## Requirements
- Python 3.13+
- DuckDB 1.4+
- Access to a PostgreSQL instance (for the DuckLake catalog metadata)
- S3-compatible storage (e.g., AWS S3, MinIO) for repository data

## Installation
Bifrost is a regular Python project. You can install it in editable mode while developing locally:

```bash
# with pip
pip install -e .

# or with uv (recommended for speed)
uv pip install -e .
```

## Quickstart
Below is a minimal end-to-end example showing how to:
- Define an entity (name, catalog, schema, and columns)
- Configure the catalog database and S3
- Create the physical entity
- Write a record

```python
from bifrost.model.database_config import DatabaseConfig
from bifrost.model.object_storage_config import S3Config
from bifrost.model.polyglot_config import PolyglotConfig
from bifrost.model.polyglot_entity import (
    ColumnDataType, Entity, EntityColumn,
)
from bifrost.main import SugarPolyglot

# 1) Describe your entity
entity = Entity(
    name="release",
    catalog="bifrost",
    schema_="public",
    comment="Release entity",
    columns=[
        EntityColumn(
            name="version",
            data_type=ColumnDataType(name="text", logical="string"),
            primary_key=True,
            comment="Semantic version",
            examples=["v1.0.0"],
        ),
        EntityColumn(
            name="status",
            data_type=ColumnDataType(name="text", logical="string"),
            nullable=False,
            examples=["rc", "ga"],
        ),
    ],
)

# 2) Configure the catalog database (PostgreSQL) and S3
catalog_db = DatabaseConfig(
    host="localhost",
    port=5432,
    db_name="bifrost",
    user="postgres",
    password="postgres",
)

s3 = S3Config(
    endpoint_url="http://localhost:9000",
    aws_access_key_id="minio",
    aws_secret_access_key="minio123",
    region_name="us-east-1",
    use_ssl=False,
)

# 3) Build the Polyglot configuration
config = PolyglotConfig(
    polyglot_entity=entity,
    catalog_database_config=catalog_db,
    object_storage_config=s3,
    recreate_existing_entity=True,
    duckdb_modules=["httpfs", "postgres", "ducklake"],
    cache_folder=".cache/bifrost",
    data={
        "version": "v1.0.0",
        "status": "rc",
    },
)

# 4) Create the entity (DDL) and write data
result = SugarPolyglot.write(config=config, create=True)
print(result)  # contains key fields such as generated primary key aliases and/or hashes
```

Notes:
- If you prefer more control, you can use the lower-level `Polyglot` class:

```python
from bifrost.main import Bifrost

poly = Bifrost(config)
poly.create()  # create DDL
poly.write()  # write using config.data
```

## How it works (short)
- `Driver` dynamically creates a Pydantic model from your `Entity` definition (fields, types, constraints).
- `write()` computes a content-based `record_hash`, inserts staged data into DuckDB, and then merges it into the DuckLake catalog (backed by Postgres), honoring update/insert rules from your entity spec.
- `QuackConnector` prepares DuckDB/DuckLake (secrets, modules) and executes all SQL instructions.

## Configuration Hints
- Ensure DuckDB can load modules `httpfs`, `postgres`, and `ducklake` (see `duckdb_modules` in the example).
- The catalog database credentials must be valid and reachable from where you run Bifrost.
- For local S3 (e.g., MinIO), set `endpoint_url` and `use_ssl=False` accordingly.
- You may load configuration and entity definitions from YAML/JSON; see `polyglot/dev/val.py` for a reference workflow.

## Development
- Linting: `ruff check .`
- Project metadata and dependencies are defined in `pyproject.toml`.
- Example invocation and local experiments live in `polyglot/dev/`.

## License
This project is licensed under the MIT License. See `LICENSE` for details.
