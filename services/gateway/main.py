"""Gateway: the only public entry point.

- POST /api/session            new chat session
- POST /api/chat               user message or button action -> user.requests
- GET  /api/stream/{session}   Server-Sent Events: agent events + replies
- POST /api/cv                 upload a CV -> profile agent (A2A)
- GET  /api/jobs               browse indexed jobs
- GET  /api/agents             every agent's A2A card
- GET  /api/stats              pipeline and Judge numbers
"""

import asyncio
import json
from collections import defaultdict
from contextlib import asynccontextmanager
from typing import Any
from uuid import uuid4

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from portiq_common import a2a, db, llm
from portiq_common.bus import Bus
from portiq_common.envelope import Envelope, Topics
from portiq_common.settings import get_settings
from portiq_common.tracing import setup_logging, setup_tracing, span

from .cv_text import MAX_BYTES, extract_text

AGENTS = ["orchestrator", "profile", "match", "company_research", "interviewer", "roadmap", "judge",
          "sources", "normalizer", "scam", "indexer"]

setup_logging("gateway")
setup_tracing("gateway")
bus = Bus("gateway")
listeners: dict[str, set[asyncio.Queue]] = defaultdict(set)


async def fan_out(env: Envelope) -> None:
    for q in list(listeners.get(env.session_id, ())):
        q.put_nowait(env)


@asynccontextmanager
async def lifespan(_: FastAPI):
    await bus.start()
    task = asyncio.create_task(bus.consume(
        [Topics.AGENT_EVENTS, Topics.SESSION_REPLIES], f"gateway-{uuid4().hex[:8]}", fan_out, from_latest=True))
    yield
    task.cancel()
    await bus.stop()


app = FastAPI(title="Portiq Gateway", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in get_settings().cors_origins.split(",")],
    allow_origin_regex=r"http://(localhost|127\.0\.0\.1):\d+",
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatIn(BaseModel):
    session_id: str
    text: str | None = None
    action: dict[str, Any] | None = None


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "llm": llm.provider()}


@app.post("/api/session")
async def new_session() -> dict[str, str]:
    return {"session_id": uuid4().hex}


@app.post("/api/chat")
async def chat(body: ChatIn) -> dict[str, str]:
    if not body.text and not body.action:
        raise HTTPException(400, "text or action required")
    env = Envelope(type="request", session_id=body.session_id, source_agent="gateway",
                   payload={"text": (body.text or "")[:2000], "action": body.action})
    with span("gateway.chat", env.trace_id):
        await bus.publish(Topics.USER_REQUESTS, env)
    return {"trace_id": env.trace_id}


@app.get("/api/stream/{session_id}")
async def stream(session_id: str) -> StreamingResponse:
    q: asyncio.Queue = asyncio.Queue()
    listeners[session_id].add(q)

    async def gen():
        try:
            yield "retry: 2000\n\n"
            while True:
                try:
                    env: Envelope = await asyncio.wait_for(q.get(), timeout=15)
                except TimeoutError:
                    yield ": ping\n\n"
                    continue
                # "type" says reply vs event; a reply's own "kind" (question, jobs...) is kept.
                data = {**env.payload, "type": "reply" if env.type == "reply" else "event",
                        "trace_id": env.trace_id, "agent": env.source_agent, "at": env.created_at.isoformat()}
                yield f"data: {json.dumps(data, ensure_ascii=False, default=str)}\n\n"
        finally:
            listeners[session_id].discard(q)

    return StreamingResponse(gen(), media_type="text/event-stream",
                             headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})


@app.post("/api/cv")
async def upload_cv(session_id: str = Form(...), file: UploadFile = File(...)) -> dict[str, Any]:
    data = await file.read()
    if len(data) > MAX_BYTES:
        raise HTTPException(413, "CV must be under 5 MB")
    try:
        text = extract_text(file.filename or "", data)
    except ValueError as e:
        raise HTTPException(415, str(e)) from e
    if len(text.strip()) < 30:
        raise HTTPException(422, "Could not read text from this file (scanned image?)")
    env = Envelope(type="event", session_id=session_id, source_agent="gateway")
    await bus.publish(Topics.AGENT_EVENTS, env.child(type="event", source_agent="gateway",
                      payload={"agent": "profile", "status": "started", "text": "reading CV…"}))
    result = await a2a.call("profile", "parse_cv", {"session_id": session_id, "text": text}, env.trace_id,
                          timeout=get_settings().a2a_llm_timeout)
    await bus.publish(Topics.AGENT_EVENTS, env.child(type="event", source_agent="profile",
                      payload={"agent": "profile", "status": "done",
                               "text": f"{len(result['profile'].get('skills', []))} skills found"}))
    return result


@app.delete("/api/profile/{session_id}")
async def delete_profile(session_id: str) -> dict[str, Any]:
    return await a2a.call("profile", "delete_profile", {"session_id": session_id})


@app.get("/api/jobs")
async def jobs(country: str | None = None, q: str | None = None, limit: int = 30) -> dict[str, Any]:
    rows = await (await db.pool()).fetch(
        """SELECT id, source, url, title, company, city, country, remote, salary_text, skills, risk_level,
                  risk_reasons, sample, created_at
           FROM jobs WHERE ($1::text IS NULL OR country=$1) AND ($2::text IS NULL OR title ILIKE '%'||$2||'%')
           ORDER BY created_at DESC LIMIT $3""", country, q, min(limit, 100))
    return {"jobs": [dict(r) for r in rows]}


@app.get("/api/agents")
async def agents() -> dict[str, Any]:
    cards = await asyncio.gather(*(a2a.fetch_card(a) for a in AGENTS))
    return {"agents": [c or {"name": a, "status": "down"} for a, c in zip(AGENTS, cards, strict=False)]}


@app.get("/api/stats")
async def stats() -> dict[str, Any]:
    pool = await db.pool()
    by_source = await pool.fetch("SELECT source, country, count(*) AS n FROM jobs GROUP BY 1,2 ORDER BY 3 DESC")
    by_risk = await pool.fetch("SELECT risk_level, count(*) AS n FROM jobs GROUP BY 1")
    verdicts = await pool.fetch("SELECT agent, verdict, count(*) AS n FROM verdicts GROUP BY 1,2 ORDER BY 1")
    return {"llm": llm.provider(), "jobs_by_source": [dict(r) for r in by_source],
            "jobs_by_risk": [dict(r) for r in by_risk], "verdicts": [dict(r) for r in verdicts]}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=get_settings().agent_port, log_level="warning")
