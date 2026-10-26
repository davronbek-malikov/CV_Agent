import asyncio
import json
import logging

import asyncpg

from .settings import get_settings

log = logging.getLogger("db")
_pool: asyncpg.Pool | None = None


async def _init(conn: asyncpg.Connection) -> None:
    await conn.set_type_codec("jsonb", encoder=json.dumps, decoder=json.loads, schema="pg_catalog")


async def pool() -> asyncpg.Pool:
    global _pool
    if _pool is None:
        for attempt in range(30):
            try:
                _pool = await asyncpg.create_pool(get_settings().database_url, min_size=1, max_size=5, init=_init)
                break
            except (OSError, asyncpg.PostgresError) as e:
                log.warning("postgres not ready (%s), attempt %s", e, attempt + 1)
                await asyncio.sleep(2)
        else:
            raise RuntimeError("could not connect to Postgres")
    return _pool
