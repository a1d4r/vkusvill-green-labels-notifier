import contextlib

from collections.abc import AsyncIterator

import psycopg
import pytest

from pytest_alembic import MigrationContext
from pytest_postgresql.janitor import DatabaseJanitor
from redis.asyncio import Redis
from sqlalchemy import NullPool
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine
from testcontainers.postgres import PostgresContainer
from testcontainers.redis import RedisContainer


@pytest.fixture
def _init_postgres(postgres_container: PostgresContainer) -> None:
    janitor = DatabaseJanitor(
        user=postgres_container.username,
        host=postgres_container.get_container_host_ip(),
        port=postgres_container.get_exposed_port(postgres_container.port),
        dbname=postgres_container.dbname,
        version="16.0",
        password=postgres_container.password,
        connection_timeout=1,
    )
    with contextlib.suppress(psycopg.errors.DatabaseError):
        janitor.drop()
    janitor.init()


@pytest.fixture
def async_engine(_init_postgres, postgres_container: PostgresContainer) -> AsyncEngine:
    return create_async_engine(
        postgres_container.get_connection_url(),
        poolclass=NullPool,  # https://stackoverflow.com/a/75444607/12530392
    )


@pytest.fixture
def alembic_engine(_init_postgres, postgres_container: PostgresContainer) -> AsyncEngine:
    return create_async_engine(
        postgres_container.get_connection_url(),
        poolclass=NullPool,  # https://stackoverflow.com/a/75444607/12530392
    )


@pytest.fixture
def _run_migrations(alembic_runner: MigrationContext):
    alembic_runner.migrate_up_to("heads", return_current=False)


@pytest.fixture
async def redis_client(redis_container: RedisContainer) -> AsyncIterator[Redis]:
    redis = Redis(
        host=redis_container.get_container_host_ip(),
        port=int(redis_container.get_exposed_port(redis_container.port)),
    )
    await redis.flushdb()
    yield redis
    await redis.close()


@pytest.fixture
async def session(async_engine, _run_migrations) -> AsyncIterator[AsyncSession]:
    async with AsyncSession(
        async_engine, expire_on_commit=False, autoflush=False, autocommit=False
    ) as session:
        yield session


@pytest.fixture
async def test_session(async_engine, _run_migrations) -> AsyncIterator[AsyncSession]:  # noqa: PT019
    async with AsyncSession(
        async_engine, expire_on_commit=False, autoflush=False, autocommit=False
    ) as session:
        yield session
