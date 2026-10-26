"""Scam agent: jobs.clean -> jobs.ready with a risk score and reasons."""

from typing import Any

from darvoza_common.agent import Agent
from darvoza_common.envelope import Envelope, Topics

from .rules import assess


class ScamAgent(Agent):
    name = "scam"
    description = "Scores every job post for scam risk (fees, fake visas, passport requests)."
    skills = [{"id": "assess", "name": "Assess a job", "description": "Return risk score, level and reasons."}]

    def consumers(self):
        return [([Topics.JOBS_CLEAN], "scam", self.on_clean)]

    async def on_clean(self, env: Envelope) -> None:
        job = {**env.payload, **assess(env.payload)}
        if job["risk_level"] != "safe":
            await self.emit(env, f"flagged '{job['title'][:40]}': {', '.join(job['risk_reasons'])}", "progress")
        await self.bus.publish(Topics.JOBS_READY, env.child(type="job", source_agent=self.name, payload=job), key=job["hash"])

    async def skill(self, skill_id: str, input: dict[str, Any], trace_id: str | None) -> Any:
        if skill_id == "assess":
            return assess(input)
        return await super().skill(skill_id, input, trace_id)


if __name__ == "__main__":
    ScamAgent().run()
