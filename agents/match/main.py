"""Smart Match agent: rank jobs for a user and explain each match."""

from typing import Any

from darvoza_common import a2a, db
from darvoza_common.agent import Agent
from darvoza_common.embed import embed, to_pgvector
from darvoza_common.envelope import Envelope
from darvoza_common.jobs import ROLE_SKILLS, ROLE_WORDS

from .scoring import score_job

SEARCH = """
SELECT id, source, url, title, company, city, country, remote, salary_min, salary_max, currency, salary_text,
       skills, visa, risk_score, risk_level, risk_reasons, sample,
       1 - (embedding <=> $1::vector) AS similarity
FROM jobs
WHERE ($2::text[] IS NULL OR country = ANY($2::text[]))
  AND ($3::boolean IS NOT TRUE OR remote)
ORDER BY embedding <=> $1::vector
LIMIT 60
"""


def scope_filter(scope: dict[str, Any] | None) -> tuple[list[str] | None, bool]:
    mode = (scope or {}).get("mode", "all")
    if mode == "remote":
        return None, True
    if mode in ("single", "multi"):
        return scope.get("countries") or None, False
    return None, False


class MatchAgent(Agent):
    name = "match"
    description = "Ranks jobs for a user's profile and wishes; explains reasons and missing skills."
    skills = [{"id": "match_jobs", "name": "Match jobs", "description": "Top jobs with match %, reasons, gaps."}]
    tasks = {"match_jobs"}

    async def match(self, inp: dict[str, Any], trace_id: str | None) -> dict[str, Any]:
        profile = None
        try:
            profile = await a2a.call("profile", "get_profile", {"session_id": inp.get("session_id")}, trace_id)
        except Exception as e:
            self.log.warning("profile lookup failed: %s", e)
        user_skills = (profile or {}).get("skills", [])
        role = inp.get("role") or None
        role_words = [w for w in ROLE_WORDS.get(role, []) if "\\" not in w][:3]
        query = " ".join([*role_words, *ROLE_SKILLS.get(role, [])[:4], *user_skills, inp.get("query", "")])
        countries, remote_only = scope_filter(inp.get("scope"))
        rows = await (await db.pool()).fetch(SEARCH, to_pgvector(embed(query or "job")), countries, remote_only)

        ranked = []
        for r in rows:
            job = dict(r)
            s = score_job(job, user_skills, role, inp.get("salary"), inp.get("visa"), float(job.pop("similarity") or 0))
            for k in ("salary_min", "salary_max"):
                job[k] = float(job[k]) if job[k] is not None else None
            ranked.append({**job, **s})
        ranked.sort(key=lambda j: (j["risk_level"] == "high", -j["match"]))
        return {"jobs": ranked[: int(inp.get("limit", 5))], "searched": len(rows), "used_profile": bool(user_skills)}

    async def handle_task(self, env: Envelope) -> dict[str, Any]:
        await self.emit(env, "searching jobs in scope…")
        out = await self.match({**env.payload, "session_id": env.session_id}, env.trace_id)
        await self.emit(env, f"{out['searched']} jobs compared, top {len(out['jobs'])} ranked")
        return out

    async def skill(self, skill_id: str, input: dict[str, Any], trace_id: str | None) -> Any:
        if skill_id == "match_jobs":
            return await self.match(input, trace_id)
        return await super().skill(skill_id, input, trace_id)


if __name__ == "__main__":
    MatchAgent().run()
