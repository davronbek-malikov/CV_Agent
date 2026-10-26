"""Minimal A2A (Agent2Agent) support.

Each agent publishes an Agent Card at /.well-known/agent.json and accepts
JSON-RPC 2.0 calls at POST /a2a. Method "tasks/send" runs a named skill
synchronously and returns its output.
"""

from typing import Any

import httpx

from .envelope import new_id
from .settings import get_settings


def agent_card(name: str, description: str, skills: list[dict[str, Any]], url: str) -> dict[str, Any]:
    return {
        "name": name,
        "description": description,
        "url": url,
        "version": "0.1.0",
        "protocol": "a2a/jsonrpc-2.0",
        "capabilities": {"streaming": False, "kafka": True},
        "defaultInputModes": ["application/json"],
        "defaultOutputModes": ["application/json"],
        "skills": skills,
    }


def agent_url(name: str) -> str:
    # Hostnames cannot contain "_", so company_research is served at company-research.
    return get_settings().a2a_host_pattern.format(name=name.replace("_", "-"))


class A2AError(RuntimeError):
    pass


async def call(agent: str, skill: str, input: dict[str, Any], trace_id: str | None = None, timeout: float = 30) -> Any:
    body = {
        "jsonrpc": "2.0",
        "id": new_id(),
        "method": "tasks/send",
        "params": {"skill": skill, "input": input, "trace_id": trace_id},
    }
    async with httpx.AsyncClient(timeout=timeout) as client:
        r = await client.post(f"{agent_url(agent)}/a2a", json=body)
        r.raise_for_status()
        data = r.json()
    if "error" in data:
        raise A2AError(f"{agent}.{skill}: {data['error'].get('message')}")
    return data["result"]


async def fetch_card(agent: str) -> dict[str, Any] | None:
    try:
        async with httpx.AsyncClient(timeout=3) as client:
            r = await client.get(f"{agent_url(agent)}/.well-known/agent.json")
            r.raise_for_status()
            return r.json()
    except Exception:
        return None
