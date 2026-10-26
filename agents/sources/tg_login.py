"""One-time Telegram login. Run inside the sources container:

    docker compose -f infra/docker-compose.yml run --rm sources python -m agents.sources.tg_login

It asks for your phone number and the code Telegram sends you, then saves a
session file in the `tgsession` volume. After that the sources agent reads
public channels without asking again.
"""

import asyncio

from telethon import TelegramClient

from portiq_common.settings import get_settings


async def main() -> None:
    s = get_settings()
    async with TelegramClient(f"/app/data/{s.tg_session}", int(s.tg_api_id), s.tg_api_hash) as client:
        me = await client.get_me()
        print(f"Logged in as {me.username or me.first_name}. Session saved.")


if __name__ == "__main__":
    asyncio.run(main())
