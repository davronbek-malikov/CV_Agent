"""Base class for every Portiq agent.

An agent gets, for free:
- an A2A Agent Card at /.well-known/agent.json and a JSON-RPC endpoint at /a2a
- a Kafka consumer on `agent.tasks` (only messages whose target_agent is this agent)
- results published to `agent.results` for the Judge
- live events on `agent.events` for the UI activity panel
- an OpenTelemetry span per task
"""

import asyncio
import logging
from contextlib import asynccontextmanager
from typing import Any

import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from .a2a import agent_card, agent_url
from .bus import Bus
from .envelope import Envelope, Topics
from .settings import get_settings
from .tracing import setup_logging, setup_tracing, span


class Agent:
    name: str = "agent"
    description: str = ""
    skills: list[dict[str, Any]] = []
    tasks: set[str] = set()

    def __init__(self) -> None:
        setup_logging(self.name)
        setup_tracing(self.name)
        self.log = logging.getLogger(self.name)
        self.bus = Bus(self.name)
        self._bg: list[asyncio.Task] = []

    # --- override these -------------------------------------------------
    async def handle_task(self, env: Envelope) -> dict[str, Any]:
        raise NotImplementedError

    async def skill(self, skill_id: str, input: dict[str, Any], trace_id: str | None) -> Any:
        raise NotImplementedError(f"unknown skill {skill_id}")

    def consumers(self) -> list[tuple[list[str], str, Any]]:
        """Extra (topics, group, handler) consumers, e.g. for the job pipeline."""
        return []

    async def on_start(self) -> None:
        pass

    # --- helpers --------------------------------------------------------
    async def emit(self, env: Envelope, text: str, status: str = "progress", **extra: Any) -> None:
        await self.bus.publish(
            Topics.AGENT_EVENTS,
            env.child(type="event", source_agent=self.name,
                      payload={"agent": self.name, "status": status, "text": text, **extra}),
        )

    async def _on_task(self, env: Envelope) -> None:
        if env.target_agent != self.name or env.task not in self.tasks:
            return
        await self.emit(env, f"{env.task} started", "started")
        with span(f"{self.name}.{env.task}", env.trace_id, attempt=env.attempt):
            try:
                output = await self.handle_task(env)
            except Exception as e:
                self.log.exception("task failed")
                await self.emit(env, f"{env.task} failed: {e}", "error")
                output = {"error": str(e)}
        await self.bus.publish(
            Topics.AGENT_RESULTS,
            env.child(type="result", source_agent=self.name, target_agent="judge",
                      payload={"agent": self.name, "output": output, "task_input": env.payload}),
        )
        await self.emit(env, f"{env.task} done", "done")

    # --- app --------------------------------------------------------------
    def build_app(self) -> FastAPI:
        @asynccontextmanager
        async def lifespan(_: FastAPI):
            await self.bus.start()
            await self.on_start()
            if self.tasks:
                self._bg.append(asyncio.create_task(
                    self.bus.consume([Topics.AGENT_TASKS], f"agent-{self.name}", self._on_task)))
            for topics, group, handler in self.consumers():
                self._bg.append(asyncio.create_task(self.bus.consume(topics, group, handler)))
            yield
            for t in self._bg:
                t.cancel()
            await self.bus.stop()

        app = FastAPI(title=f"portiq-{self.name}", lifespan=lifespan)

        @app.get("/health")
        async def health() -> dict[str, str]:
            return {"status": "ok", "agent": self.name}

        @app.get("/.well-known/agent.json")
        async def card() -> dict[str, Any]:
            return agent_card(self.name, self.description, self.skills, agent_url(self.name))

        @app.post("/a2a")
        async def a2a(request: Request) -> JSONResponse:
            body = await request.json()
            rid = body.get("id")
            if body.get("method") != "tasks/send":
                return JSONResponse({"jsonrpc": "2.0", "id": rid, "error": {"code": -32601, "message": "method not found"}})
            params = body.get("params", {})
            try:
                with span(f"{self.name}.a2a.{params.get('skill')}", params.get("trace_id") or ""):
                    result = await self.skill(params.get("skill", ""), params.get("input", {}), params.get("trace_id"))
                return JSONResponse({"jsonrpc": "2.0", "id": rid, "result": result})
            except NotImplementedError as e:
                return JSONResponse({"jsonrpc": "2.0", "id": rid, "error": {"code": -32602, "message": str(e)}})
            except Exception as e:
                self.log.exception("a2a skill failed")
                return JSONResponse({"jsonrpc": "2.0", "id": rid, "error": {"code": -32000, "message": str(e)}})

        return app

    def run(self) -> None:
        uvicorn.run(self.build_app(), host="0.0.0.0", port=get_settings().agent_port, log_level="warning")
