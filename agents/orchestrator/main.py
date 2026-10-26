"""Orchestrator agent.

Consumes `user.requests` (chat turns) and `judge.verdicts` (checked agent
results), keeps session state in Redis, runs the LangGraph turn graph, sends
tasks on `agent.tasks`, and replies on `session.replies`.
"""

import asyncio
import json
from collections import defaultdict
from typing import Any

import redis.asyncio as aioredis

from darvoza_common import a2a
from darvoza_common.agent import Agent
from darvoza_common.envelope import Envelope, Topics, new_id
from darvoza_common.settings import get_settings
from darvoza_common.tracing import span

from .flow import Services, build_graph, new_session, on_verdict


class OrchestratorAgent(Agent):
    name = "orchestrator"
    description = "Understands the user, asks only missing questions, plans work and routes it to agents."
    skills = [{"id": "session", "name": "Session state", "description": "Current state of a chat session."}]

    async def on_start(self) -> None:
        self.redis = aioredis.from_url(get_settings().redis_url, decode_responses=True)
        self.locks: dict[str, asyncio.Lock] = defaultdict(asyncio.Lock)
        self.graph = build_graph(Services(get_profile=self._profile, score=self._score, follow_up=self._follow_up))

    def consumers(self):
        return [
            ([Topics.USER_REQUESTS], "orchestrator-requests", self.on_request),
            ([Topics.JUDGE_VERDICTS], "orchestrator-verdicts", self.on_verdict),
        ]

    # --- A2A calls used by the graph ---------------------------------------
    async def _profile(self, session_id: str) -> dict[str, Any] | None:
        try:
            return await a2a.call("profile", "get_profile", {"session_id": session_id})
        except Exception as e:
            self.log.warning("profile A2A failed: %s", e)
            return None

    async def _score(self, inp: dict[str, Any]) -> dict[str, Any]:
        return await a2a.call("judge", "score_answer", inp, timeout=60)

    async def _follow_up(self, answer: str, lang: str) -> str | None:
        try:
            return (await a2a.call("interviewer", "follow_up", {"answer": answer, "lang": lang}))["follow_up"]
        except Exception:
            return None

    # --- state --------------------------------------------------------------
    async def load(self, sid: str) -> dict[str, Any]:
        raw = await self.redis.get(f"session:{sid}")
        return json.loads(raw) if raw else new_session()

    async def save(self, sid: str, s: dict[str, Any]) -> None:
        await self.redis.set(f"session:{sid}", json.dumps(s), ex=7 * 86400)

    # --- outputs ------------------------------------------------------------
    async def send(self, env: Envelope, s: dict[str, Any], replies: list[dict], tasks: list[dict]) -> None:
        for r in replies:
            await self.bus.publish(Topics.SESSION_REPLIES, env.child(
                type="reply", source_agent=self.name, lang=s["lang"] or "en", payload={**r, "lang": s["lang"]}))
        for t in tasks:
            task_id = new_id()
            s["pending"][task_id] = t["task"]
            await self.emit(env, f"→ {t['target_agent']}: {t['task']}", "progress")
            await self.bus.publish(Topics.AGENT_TASKS, env.child(
                type="task", source_agent=self.name, target_agent=t["target_agent"], task=t["task"],
                task_id=task_id, attempt=1, lang=s["lang"] or "en", payload=t["payload"]))

    async def on_request(self, env: Envelope) -> None:
        sid = env.session_id
        async with self.locks[sid]:
            s = await self.load(sid)
            with span("orchestrator.turn", env.trace_id):
                result = await self.graph.ainvoke({"session_id": sid, "session": s, "input": env.payload,
                                                   "replies": [], "tasks": []})
            s = result["session"]
            if result.get("tasks"):
                await self.emit(env, f"plan: {', '.join(t['task'] for t in result['tasks'])}", "progress")
            await self.send(env, s, result.get("replies", []), result.get("tasks", []))
            await self.save(sid, s)

    async def on_verdict(self, env: Envelope) -> None:
        sid = env.session_id
        async with self.locks[sid]:
            s = await self.load(sid)
            if s["pending"].pop(env.task_id or "", None) is None:
                return  # stale (user restarted) or unknown
            replies, tasks = on_verdict(s, env.task or "", env.payload)
            await self.send(env, s, replies, tasks)
            await self.save(sid, s)

    async def skill(self, skill_id: str, input: dict[str, Any], trace_id: str | None) -> Any:
        if skill_id == "session":
            return await self.load(input["session_id"])
        return await super().skill(skill_id, input, trace_id)


if __name__ == "__main__":
    OrchestratorAgent().run()
