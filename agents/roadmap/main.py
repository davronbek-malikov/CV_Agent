"""Roadmap agent: target job + gaps -> week-by-week plan."""

import re
from typing import Any

from portiq_common import a2a, db
from portiq_common.agent import Agent
from portiq_common.envelope import Envelope

from .plan import build_plan


def _int(v: Any, default: int) -> int:
    m = re.search(r"\d+", str(v or ""))
    return int(m.group(0)) if m else default


class RoadmapAgent(Agent):
    name = "roadmap"
    description = "Turns skill gaps into a 30/60/90-day plan that fits the user's weekly hours."
    skills = [{"id": "build_roadmap", "name": "Build roadmap", "description": "Target + gaps -> weekly plan."}]
    tasks = {"build_roadmap"}

    async def build(self, inp: dict[str, Any], lang: str, session_id: str, trace_id: str | None) -> dict[str, Any]:
        have: list[str] = []
        try:
            prof = await a2a.call("profile", "get_profile", {"session_id": session_id}, trace_id)
            have = (prof or {}).get("skills", [])
        except Exception as e:
            self.log.warning("profile lookup failed: %s", e)
        plan = build_plan(inp.get("target") or "dev", _int(inp.get("days"), 60), _int(inp.get("hours"), 10),
                          have, inp.get("missing") or [], lang)
        await (await db.pool()).execute(
            "INSERT INTO roadmaps (session_id, target, plan) VALUES ($1,$2,$3)", session_id, plan["target"], plan)
        return plan

    async def handle_task(self, env: Envelope) -> dict[str, Any]:
        out = await self.build(env.payload, env.lang, env.session_id, env.trace_id)
        await self.emit(env, f"{len(out['gap'])} gaps → {out['weeks']}-week plan")
        return out

    async def skill(self, skill_id: str, input: dict[str, Any], trace_id: str | None) -> Any:
        if skill_id == "build_roadmap":
            return await self.build(input, input.get("lang", "en"), input.get("session_id", ""), trace_id)
        return await super().skill(skill_id, input, trace_id)


if __name__ == "__main__":
    RoadmapAgent().run()
