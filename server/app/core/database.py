from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.pool import NullPool, StaticPool

from app.core.config import get_settings

settings = get_settings()

_db_url = settings.DATABASE_URL
if _db_url.startswith("sqlite"):
    _pool = StaticPool if ":memory:" in _db_url else NullPool
    engine = create_async_engine(
        _db_url,
        echo=False,
        connect_args={"check_same_thread": False},
        poolclass=_pool,
    )
else:
    engine = create_async_engine(_db_url, echo=False, pool_size=20, max_overflow=10)

async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


async def get_db() -> AsyncSession:
    async with async_session() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
