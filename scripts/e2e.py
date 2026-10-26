"""End-to-end test against the running stack (make up; make e2e).

Talks to the gateway exactly like the web app: opens the SSE stream, sends
chat actions, and waits for the orchestrator's replies.
"""

import asyncio
import json
import sys
import time

import httpx

GW = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8000"
CV = """Aziz Karimov
Tashkent University of Information Technologies, Bachelor of Computer Science
3 years experience as backend developer: Python, FastAPI, PostgreSQL, Docker, Git
Languages: Uzbek, Russian, English (IELTS 6.5), Korean TOPIK 3
"""


class Client:
    def __init__(self) -> None:
        self.http = httpx.AsyncClient(base_url=GW, timeout=60)
        self.replies: asyncio.Queue = asyncio.Queue()
        self.events: list[dict] = []

    async def start(self) -> None:
        self.sid = (await self.http.post("/api/session")).json()["session_id"]
        self.task = asyncio.create_task(self._listen())
        await asyncio.sleep(1.5)

    async def _listen(self) -> None:
        async with httpx.AsyncClient(base_url=GW, timeout=None) as c, c.stream("GET", f"/api/stream/{self.sid}") as r:
            async for line in r.aiter_lines():
                if line.startswith("data: "):
                    d = json.loads(line[6:])
                    (self.replies.put_nowait(d) if d["type"] == "reply" else self.events.append(d))

    async def send(self, text: str | None = None, action: dict | None = None) -> None:
        await self.http.post("/api/chat", json={"session_id": self.sid, "text": text, "action": action})

    async def expect(self, kind: str, timeout: float = 60) -> dict:
        end = time.time() + timeout
        while time.time() < end:
            try:
                r = await asyncio.wait_for(self.replies.get(), timeout=end - time.time())
            except TimeoutError:
                break
            print(f"   ← {r['kind']:<12} {str(r.get('text') or '')[:70]}")
            if r["kind"] == kind:
                return r
            if r["kind"] == "error":
                raise AssertionError(f"error reply: {r}")
        raise AssertionError(f"timed out waiting for {kind}")


def ok(msg: str) -> None:
    print(f"✓ {msg}")


async def main() -> None:
    c = Client()
    await c.start()

    print("\n[1] CV upload → profile agent (A2A)")
    r = await c.http.post("/api/cv", data={"session_id": c.sid}, files={"file": ("cv.txt", CV.encode())})
    prof = r.json()["profile"]
    assert {"Python", "FastAPI", "Docker"} <= set(prof["skills"]), prof
    ok(f"CV parsed: {prof['name']}, {len(prof['skills'])} skills, {prof['korean_level']}")

    print("\n[2] Language → mode → country → role → salary → visa → matches")
    await c.send(action={"type": "start"})
    q = await c.expect("question")
    assert q["slot"] == "lang"
    await c.send(action={"type": "lang", "value": "uz"})
    q = await c.expect("question")
    assert q["slot"] == "mode" and q["lang"] == "uz", q
    await c.send(action={"type": "mode", "value": "jobs"})
    assert (await c.expect("question"))["slot"] == "scope"
    await c.send(action={"type": "choose", "slot": "scope", "value": "multi"})
    nxt = await c.expect("question")
    if nxt["slot"] == "role":  # skipped when the CV already told us the role
        await c.send(action={"type": "choose", "slot": "role", "value": "dev"})
        nxt = await c.expect("question")
    assert nxt["slot"] == "salary"
    await c.send(action={"type": "choose", "slot": "salary", "value": "10M so‘m"})
    assert (await c.expect("question"))["slot"] == "visa"
    await c.send(action={"type": "choose", "slot": "visa", "value": "E-7"})
    jobs = (await c.expect("jobs"))["data"]["jobs"]
    assert jobs and all(j["country"] in ("UZ", "KR") for j in jobs)
    assert jobs[0]["risk_level"] != "high"
    ok(f"{len(jobs)} jobs, top: {jobs[0]['title']} @ {jobs[0]['company']} ({jobs[0]['match']}%), have={jobs[0]['have']}")

    print("\n[3] Practice interview from the job card (real company research)")
    await c.send(action={"type": "practice", "company": "Kakao", "role": "dev"})
    assert (await c.expect("question"))["slot"] == "type"
    await c.send(action={"type": "choose", "slot": "type", "value": "stress"})
    first = await c.expect("interview_q", timeout=90)
    ok(f"Q1 ({first['data']['category']}): {first['text'][:80]}")
    await c.send("Men tayyorman.")
    sc = await c.expect("score")
    fu = await c.expect("interview_q")
    assert fu["data"]["follow_up"], fu
    ok(f"short answer scored {sc['data']['total']}/100 → follow-up asked")
    await c.send("Oldingi ishimda to'lov tizimini Python va Kafka bilan qayta qurdim, natijada xatolar 40% kamaydi.")
    await c.expect("score")
    await c.send(action={"type": "end_interview"})
    rep = await c.expect("report")
    ok(f"report: readiness {rep['data']['readiness']}, axes {rep['data']['axes']}")

    print("\n[4] Roadmap from weak spots")
    await c.send(action={"type": "roadmap_from_weak"})
    assert (await c.expect("question"))["slot"] == "days"
    await c.send(action={"type": "choose", "slot": "days", "value": "60"})
    await c.expect("question")
    await c.send(action={"type": "choose", "slot": "hours", "value": "10"})
    plan = (await c.expect("roadmap"))["data"]
    assert plan["total_hours"] <= plan["budget_hours"] * 1.1
    ok(f"{plan['weeks']} weeks, {plan['total_hours']}h / {plan['budget_hours']}h budget, gaps: {plan['gap'][:4]}")

    agents = sorted({e.get("agent") for e in c.events if e.get("agent")})
    verdicts = [e["text"] for e in c.events if e.get("status") == "verdict"]
    ok(f"live events from agents: {agents}")
    ok(f"judge verdicts seen: {verdicts}")
    c.task.cancel()
    print("\nALL E2E CHECKS PASSED")


if __name__ == "__main__":
    asyncio.run(main())
