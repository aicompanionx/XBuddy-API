import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

import redis.asyncio as redis
from sqlalchemy.ext.asyncio import AsyncConnection, create_async_engine

from app.config import get_config

# Set up logger
logger = logging.getLogger(__name__)

# Create database engine and session
cfg = get_config()
DATABASE_URL = f"postgresql+asyncpg://{cfg['postgres']['user']}:{cfg['postgres']['password']}@{cfg['postgres']['host']}:{cfg['postgres']['port']}/{cfg['postgres']['db']}"

engine = create_async_engine(DATABASE_URL)


@asynccontextmanager
async def get_db() -> AsyncGenerator[AsyncConnection, None]:
    """
    Get a database connection from the connection pool.
    """
    conn = await engine.connect()
    try:
        yield conn
    finally:
        await conn.close()


@asynccontextmanager
async def get_redis() -> AsyncGenerator[redis.Redis, None]:
    """
    Get a Redis connection from the connection pool.
    """
    _cfg = get_config()
    redis_uri = (
        f"redis://{_cfg['redis']['host']}:{_cfg['redis']['port']}/{_cfg['redis']['db']}"
    )
    r = redis.from_url(redis_uri, decode_responses=True)
    try:
        yield r
    finally:
        await r.close()
