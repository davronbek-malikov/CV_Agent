"""Company Research agent: a short Past / Now / Next brief where every line has a source."""

import re
from typing import Any

from portiq_common import db, llm
from portiq_common.agent import Agent
from portiq_common.envelope import Envelope

from . import sources

FUTURE = re.compile(r"plan|will|launch|expand|invest|target|aim|next year|2027|계획|출시|진출|투자|예정|планир|запуст|расшир|инвест", re.I)

BRIEF_PROMPT = (
    "You write a short company brief for a job candidate from the given sources only. "
    'Return {"rows": [{"key": "past"|"now"|"next", "text": str, "source": int}]} with 3-5 rows, '
    "where source is the index of the source you used. Never add facts that are not in the sources. "
    "Write the text in language: {lang}."
)


def _sentences(text: str, n: int) -> str:
    parts = re.split(r"(?<=[.!?])\s+", text.strip())
    return " ".join(parts[:n])


def heuristic_brief(wiki: dict | None, items: list[dict]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    if wiki and wiki.get("extract"):
        rows.append({"key": "past", "text": _sentences(wiki["extract"], 2),
                     "source": {"title": f"Wikipedia: {wiki['title']}", "url": wiki["url"]}})
    future = [i for i in items if FUTURE.search(i["title"])]
    now = [i for i in items if i not in future]
    for i in now[:2]:
        rows.append({"key": "now", "text": i["title"], "source": {"title": i.get("source") or "news", "url": i["url"]}})
    for i in future[:2]:
        rows.append({"key": "next", "text": i["title"], "source": {"title": i.get("source") or "news", "url": i["url"]}})
    return rows


class CompanyResearchAgent(Agent):
    name = "company_research"
    description = "Researches a company from public sources (Wikipedia, news) into a sourced brief."
    skills = [{"id": "company_brief", "name": "Company brief", "description": "Past / Now / Next with a source per line."}]
    tasks = {"company_brief"}

    async def brief(self, company: str, lang: str, env: Envelope | None = None) -> dict[str, Any]:
        pool = await db.pool()
        cached = await pool.fetchrow(
            "SELECT brief FROM companies WHERE name=$1 AND updated_at > now() - interval '14 days'", company.lower())
        if cached and cached["brief"].get("lang") == lang:
            return {**cached["brief"], "cached": True}

        wiki, items = None, []
        try:
            wiki = await sources.wikipedia(company)
        except Exception as e:
            self.log.warning("wikipedia failed: %s", e)
        if env:
            await self.emit(env, "Wikipedia checked" + (f": {wiki['title']}" if wiki else " (no page)"))
        try:
            items = await sources.news(company, lang)
        except Exception as e:
            self.log.warning("news failed: %s", e)
        if env:
            await self.emit(env, f"{len(items)} news articles read")

        srcs = ([{"title": f"Wikipedia: {wiki['title']}", "url": wiki["url"], "text": wiki["extract"]}] if wiki else []) + [
            {"title": i.get("source") or "news", "url": i["url"], "text": i["title"]} for i in items]

        def fallback() -> dict:
            return {"rows": heuristic_brief(wiki, items)}

        rows: list[dict[str, Any]]
        if srcs:
            data, model = await llm.complete_json(
                BRIEF_PROMPT.replace("{lang}", lang),
                "\n".join(f"[{n}] {s['title']}: {s['text']}" for n, s in enumerate(srcs)),
                fallback)
            rows = []
            for r in data.get("rows", []):
                src = r.get("source")
                if isinstance(src, int) and 0 <= src < len(srcs):
                    r["source"] = {"title": srcs[src]["title"], "url": srcs[src]["url"]}
                rows.append(r)
        else:
            rows, model = [], "none"

        out = {"company": company, "lang": lang, "found": bool(srcs), "rows": rows, "news": items[:5], "model": model}
        await pool.execute(
            "INSERT INTO companies (name, brief) VALUES ($1, $2) ON CONFLICT (name) DO UPDATE SET brief=$2, updated_at=now()",
            company.lower(), out)
        return out

    async def handle_task(self, env: Envelope) -> dict[str, Any]:
        company = env.payload.get("company", "").strip()
        await self.emit(env, f"researching {company}…")
        return await self.brief(company, env.lang, env)

    async def skill(self, skill_id: str, input: dict[str, Any], trace_id: str | None) -> Any:
        if skill_id == "company_brief":
            return await self.brief(input["company"], input.get("lang", "en"))
        return await super().skill(skill_id, input, trace_id)


if __name__ == "__main__":
    CompanyResearchAgent().run()

