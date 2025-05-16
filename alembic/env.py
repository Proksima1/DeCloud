import logging
import sys
from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool

from alembic import context
from backend_context.persistent.pg import api  # noqa # noqa: PGH004
from base.persistent.pg.base import Base
from base.settings import settings

logger = logging.getLogger(__name__)
config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)


settings.pg_rw.protocol = "postgresql"
config.set_main_option("sqlalchemy.url", str(settings.pg_rw.dsn()))

target_schema = Base.metadata.schema
target_metadata = Base.metadata


def include_name(name: str | None, type_: str, parent_names) -> bool:  # noqa: ARG001, ANN001
    if type_ == "schema":
        return name == target_schema

    return True


def check_if_downgrade() -> None:
    cmd_opts = config.cmd_opts
    if cmd_opts is None:
        return

    RED = "\033[91m"  # noqa: N806
    ENDC = "\033[0m"  # noqa: N806

    if cmd_opts.cmd[0].__name__ != "downgrade":
        return

    print(f"{RED} DOWNGRADE DETECTED on database: {settings.pg_rw.dsn_safe()}{ENDC}")  # noqa: T201
    if settings.pg_rw.host not in ("localhost", "postgres"):
        print("Downgrade only allowed for localhost database")  # noqa: T201
        sys.exit(1)


def run_migrations_online() -> None:
    check_if_downgrade()

    connectable = engine_from_config(
        config.get_section(config.config_ini_section),  # type: ignore
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            include_schemas=True,
            include_name=include_name,
            transactional_ddl=False,
        )

        with context.begin_transaction():
            context.run_migrations()


logging.info("migrations.running dns=%s", settings.pg_rw.dsn_safe())
run_migrations_online()
