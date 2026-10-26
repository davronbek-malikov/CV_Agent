"""Source agent: pulls jobs from every enabled connector on a schedule and
publishes them to `jobs.raw`."""

import asyncio
import json
from typing import Any

import redis.asyncio as aioredis

from portiq_common.agent import Agent
from portiq_common.envelope import Envelope, Topics
from portiq_common.settings import get_settings

from . import connectors


class SourcesAgent(Agent):
    name = "sources"
    description = "Collects job posts from Uzbekistan, Korea, global boards and Telegram channels."
    skills = [
        {"id": "refresh", "name": "Refresh sources", "description": "Fetch all enabled sources now."},
        {"id": "status", "name": "Source status", "description": "Which sources are enabled and last counts."},
    ]

    async def on_start(self) -> None:
        self.redis = aioredis.from_url(get_settings().redis_url, decode_responses=True)
        self.counts: dict[str, Any] = {}
        self._bg.append(asyncio.create_task(self._loop()))

    async def _loop(self) -> None:
        await asyncio.sleep(3)
        while True:
            try:
                await self.refresh()
            except Exception:
                self.log.exception("refresh failed")
            await asyncio.sleep(get_settings().source_interval_min * 60)

    async def refresh(self) -> dict[str, Any]:
        on = connectors.enabled()
        env = Envelope(type="event", source_agent=self.name, session_id="pipeline")
        for name, active in on.items():
            if not active:
                self.counts[name] = "off (no key)"
                continue
            try:
                if name == "sample":
                    jobs = connectors.seed()
                elif name == "remotive":
                    jobs = await connectors.remotive()
                elif name == "saramin":
                    jobs = await connectors.saramin()
                elif name == "hh.uz":
                    jobs = await connectors.hh_uz()
                else:
                    last = json.loads(await self.redis.get("tg:last_ids") or "{}")
                    jobs, last = await connectors.telegram(last)
                    await self.redis.set("tg:last_ids", json.dumps(last))
            except Exception as e:
                self.log.warning("source %s failed: %s", name, e)
                self.counts[name] = f"error: {e}"
                continue
            for job in jobs:
                await self.bus.publish(Topics.JOBS_RAW, env.child(type="job", source_agent=self.name, payload=job),
                                       key=job.get("url") or job.get("title"))
            self.counts[name] = len(jobs)
            await self.emit(env, f"{name}: {len(jobs)} posts fetched", "done")
        return self.counts

    async def skill(self, skill_id: str, input: dict[str, Any], trace_id: str | None) -> Any:
        if skill_id == "refresh":
            return await self.refresh()
        if skill_id == "status":
            return {"enabled": connectors.enabled(), "last": self.counts}
        return await super().skill(skill_id, input, trace_id)


if __name__ == "__main__":
    SourcesAgent().run()
