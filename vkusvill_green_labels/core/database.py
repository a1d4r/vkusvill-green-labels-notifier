from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from vkusvill_green_labels.core.settings import settings

engine = create_async_engine(
    url=settings.database.url,
    pool_pre_ping=True,
    pool_recycle=settings.database.pool_recycle_seconds,
)

async_session_factory = async_sessionmaker(
    bind=engine, expire_on_commit=False, autoflush=False, autocommit=False
)
