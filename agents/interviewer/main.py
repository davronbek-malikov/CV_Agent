"""Interviewer agent: plans a company-specific interview and asks follow-ups."""

import re
from typing import Any

from darvoza_common import llm
from darvoza_common.agent import Agent
from darvoza_common.envelope import Envelope
from darvoza_common.jobs import ROLE_SKILLS

from .bank import BANK, FOLLOW_UP, PLANS, ROLE_NAME

PLAN_PROMPT = (
    "You are a strict but fair interviewer at {company}. Write interview questions for a {role} candidate "
    "in language {lang}. Use the company brief and CV skills given. Categories in order: {cats}. "
    'Return {{"questions": [{{"category": str, "text": str}}]}} with exactly one question per category.'
)


def build_plan(company: str, role: str | None, kind: str, lang: str, skills: list[str],
               headline: str | None) -> list[dict[str, Any]]:
    lang = lang if lang in ("en", "uz", "ru", "ko") else "en"
    role_key = role if role in ROLE_NAME else "dev"
    skill_pool = [s for s in skills if s in ROLE_SKILLS.get(role_key, [])] or ROLE_SKILLS[role_key]
    used: dict[str, int] = {}
    questions = []
    for i, cat in enumerate(PLANS.get(kind, PLANS["full"])):
        if cat == "company" and not headline:
            variants = BANK[cat][lang][1:]
        elif cat == "company":
            variants = BANK[cat][lang][:1]
        else:
            variants = BANK[cat][lang]
        n = used.get(cat, 0)
        used[cat] = n + 1
        text = variants[n % len(variants)].format(
            company=company or "us", role=ROLE_NAME[role_key][lang],
            skill=skill_pool[(i + n) % len(skill_pool)], headline=headline or "")
        questions.append({"id": i, "category": cat, "text": text})
    return questions


def follow_up(answer: str, lang: str) -> str | None:
    words = len(answer.split())
    if words < 12:
        return FOLLOW_UP["short"].get(lang, FOLLOW_UP["short"]["en"])
    if not re.search(r"\d", answer) and words < 80:
        return FOLLOW_UP["number"].get(lang, FOLLOW_UP["number"]["en"])
    return None


class InterviewerAgent(Agent):
    name = "interviewer"
    description = "Runs company-specific mock interviews (11 rounds incl. stress and salary) in uz/ru/ko/en."
    skills = [
        {"id": "plan_interview", "name": "Plan interview", "description": "Question plan from company brief + CV."},
        {"id": "follow_up", "name": "Follow-up", "description": "One follow-up question for a weak answer, or none."},
    ]
    tasks = {"plan_interview"}

    async def plan(self, inp: dict[str, Any], lang: str) -> dict[str, Any]:
        brief = inp.get("brief") or {}
        news = brief.get("news") or []
        headline = news[0]["title"] if news else None
        kind = inp.get("type") or "full"
        skills = inp.get("skills") or []
        fallback = build_plan(inp.get("company", ""), inp.get("role"), kind, lang, skills, headline)

        def fb() -> dict:
            return {"questions": fallback}

        cats = [q["category"] for q in fallback]
        data, model = await llm.complete_json(
            PLAN_PROMPT.format(company=inp.get("company"), role=inp.get("role") or "dev", lang=lang, cats=", ".join(cats)),
            f"Brief: {[r.get('text') for r in brief.get('rows', [])]}\nCV skills: {skills}", fb)
        qs = data.get("questions") or fallback
        for i, q in enumerate(qs):
            q["id"] = i
            if i < len(fallback) and fallback[i]["category"] == "company" and headline:
                q["source"] = news[0].get("url")
        return {"questions": qs, "type": kind, "company": inp.get("company"), "model": model}

    async def handle_task(self, env: Envelope) -> dict[str, Any]:
        out = await self.plan(env.payload, env.lang)
        await self.emit(env, f"{len(out['questions'])} questions planned")
        return out

    async def skill(self, skill_id: str, input: dict[str, Any], trace_id: str | None) -> Any:
        if skill_id == "plan_interview":
            return await self.plan(input, input.get("lang", "en"))
        if skill_id == "follow_up":
            return {"follow_up": follow_up(input.get("answer", ""), input.get("lang", "en"))}
        return await super().skill(skill_id, input, trace_id)


if __name__ == "__main__":
    InterviewerAgent().run()
