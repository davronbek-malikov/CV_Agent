"""Normalizer agent: jobs.raw -> jobs.clean (one schema, deduplicated)."""

from typing import Any

import redis.asyncio as aioredis

from portiq_common import llm
from portiq_common.agent import Agent
from portiq_common.envelope import Envelope, Topics
from portiq_common.settings import get_settings

from .normalize import heuristic_extract, normalize

EXTRACT_PROMPT = (
    "You extract job posts from Telegram messages (Uzbek, Russian, Korean or English). "
    'Return {"title": str, "company": str|null, "salary_text": str}. Title in the post language, short.'
)


class NormalizerAgent(Agent):
    name = "normalizer"
    description = "Normalizes raw job posts into one schema, removes duplicates."
    skills = [{"id": "normalize", "name": "Normalize one post", "description": "Raw post -> clean job."}]

    async def on_start(self) -> None:
        self.redis = aioredis.from_url(get_settings().redis_url, decode_responses=True)

    def consumers(self):
        return [([Topics.JOBS_RAW], "normalizer", self.on_raw)]

    async def clean(self, raw: dict[str, Any]) -> dict[str, Any]:
        extracted = None
        if raw.get("raw_text"):
            extracted, _ = await llm.complete_json(
                EXTRACT_PROMPT, raw["raw_text"][:3000], lambda: heuristic_extract(raw["raw_text"]), max_tokens=192)
        return normalize(raw, extracted)

    async def on_raw(self, env: Envelope) -> None:
        job = await self.clean(env.payload)
        # Same job seen in the last 7 days (any source) -> drop it.
        if not await self.redis.set(f"job:seen:{job['hash']}", "1", nx=True, ex=7 * 86400):
            return
        await self.bus.publish(Topics.JOBS_CLEAN, env.child(type="job", source_agent=self.name, payload=job), key=job["hash"])

    async def skill(self, skill_id: str, input: dict[str, Any], trace_id: str | None) -> Any:
        if skill_id == "normalize":
            return await self.clean(input)
        return await super().skill(skill_id, input, trace_id)


if __name__ == "__main__":
    NormalizerAgent().run()
