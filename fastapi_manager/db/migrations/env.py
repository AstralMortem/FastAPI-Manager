# use article https://medium.com/@karuhanga/of-modular-alembic-migrations-e94aee9113cd


import asyncio
from logging.config import fileConfig
from typing import List

from sqlalchemy import MetaData, pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

from alembic import context
from sqlalchemy.schema import CreateSchema
from fastapi_manager.conf import settings

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

config.set_main_option("sqlalchemy.url", settings.DATABASES)
# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
# target_metadata = None

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def _include_object(target_schema):
    if target_schema is None:
        return None

    def include_object(obj, name, object_type, reflected, compare_to):
        print(name, object_type)
        if object_type == "table" and reflected and name not in target_schema:
            return False
        return True

    return include_object


def run_migrations_offline(target_metadata, app_name, schema) -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        include_schemas=True,
        include_object=_include_object(schema),
        version_table=f"{app_name}_alembic_migration",
        version_table_schema="migrations",
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(
    connection: Connection, target_metadata, app_name, schema
) -> None:
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        include_schemas=True,
        include_object=_include_object(schema),
        version_table=f"{app_name}_alembic_migration",
        version_table_schema="migrations",
    )

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations(target_metadata, app_name, schema) -> None:
    """In this scenario we need to create an Engine
    and associate a connection with the context.

    """

    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.execute(CreateSchema("migrations", True))
        await connection.run_sync(do_run_migrations, target_metadata, app_name, schema)

    await connectable.dispose()


def run_migrations_online(target_metadata, app_name, schema) -> None:
    """Run migrations in 'online' mode."""

    asyncio.run(run_async_migrations(target_metadata, app_name, schema))


def run_migrations(metadata: MetaData, app_name, schema: List[str] | None = None):
    # if schema not defined, try get schema from metadata
    if schema is None:
        schema = [app_name]
    if metadata.schema is not None:
        schema = metadata.schema

    if context.is_offline_mode():
        run_migrations_offline(metadata, app_name, schema)
    else:
        run_migrations_online(metadata, app_name, schema)
