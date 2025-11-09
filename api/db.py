from __future__ import annotations

import os
from contextlib import asynccontextmanager
from typing import AsyncIterator, Optional

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine


DATABASE_URL = os.getenv("DATABASE_URL")

if DATABASE_URL:
    engine = create_async_engine(DATABASE_URL, echo=False, future=True)
    SessionLocal = async_sessionmaker(engine, expire_on_commit=False)
else:
    engine = None
    SessionLocal = None


@asynccontextmanager
async def get_session() -> AsyncIterator[Optional[AsyncSession]]:
    if SessionLocal is None:
        yield None
        return

    session = SessionLocal()
    try:
        yield session
        await session.commit()
    except Exception:  # noqa: BLE001
        await session.rollback()
        raise
    finally:
        await session.close()

