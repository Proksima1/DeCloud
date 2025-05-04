import logging
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from base.settings import Postgres, settings

logger = logging.getLogger(__name__)


def engine_from_settings_both() -> tuple[async_sessionmaker[AsyncSession], async_sessionmaker[AsyncSession]]:
    return engine_from_settings(rw=True), engine_from_settings(rw=False)


def engine_from_settings(rw: bool) -> async_sessionmaker[AsyncSession]:  # noqa: FBT001
    if rw:
        return get_engine(settings.pg_rw, rw=True)

    return get_engine(settings.pg_ro, rw=False)


def get_engine(pg: Postgres, rw: bool) -> async_sessionmaker[AsyncSession]:  # noqa: FBT001
    if rw:
        return _get_engine(pg, extra_connect_args={"target_session_attrs": "read-write"})

    return _get_engine(pg, extra_connect_args={"target_session_attrs": "any"})


def _get_engine_args(pg: Postgres, extra_connect_args: dict[str, Any] | None) -> tuple[str, dict[str, Any]]:
    connect_args = {}
    connect_args["server_settings"] = {"application_name": settings.service_name}
    connect_args["statement_cache_size"] = pg.statement_cache_size  # type: ignore
    connect_args["prepared_statement_cache_size"] = pg.prepared_statement_cache_size  # type: ignore

    if extra_connect_args is not None:
        connect_args.update(extra_connect_args)

    pool_settings = {}
    if pg.pool:
        pool_settings["pool_size"] = pg.max_pool_size
        pool_settings["max_overflow"] = pg.max_overflow
        pool_settings["pool_pre_ping"] = pg.pool_pre_ping
        pool_settings["pool_recycle"] = pg.pool_recycle.seconds
    else:
        # ! USE ONLY FOR PY-TESTS tests
        # https://github.com/MagicStack/asyncpg/issues/863
        pool_settings["poolclass"] = NullPool  # type: ignore

    kwargs = {"connect_args": connect_args, "echo": pg.echo, **pool_settings}

    logger.debug(
        "pg.engine.config.build",
        extra={"dsn": pg.dsn_safe(), "kwargs": kwargs},
    )

    return pg.dsn(), kwargs


def _get_engine(conf: Postgres, extra_connect_args: dict[str, Any] | None) -> async_sessionmaker[AsyncSession]:
    dsn, kwargs = _get_engine_args(conf, extra_connect_args)

    engine = create_async_engine(dsn, **kwargs)

    return async_sessionmaker(engine, expire_on_commit=conf.expire_on_commit)
