"""Profile agent: parses CVs and keeps what we know about the user."""

from typing import Any

from darvoza_common import db, llm
from darvoza_common.agent import Agent
from darvoza_common.jobs import SKILLS

from .parse import parse_cv

CV_PROMPT = (
    "Extract a CV into JSON: {name, skills: [str], education: [str], experience_years: int|null, "
    "languages: [str], korean_level: str|null, role_guess: one of dev|frontend|data|ai|design|marketing|null}. "
    f"Use these canonical skill names when they apply: {', '.join(SKILLS)}."
)


class ProfileAgent(Agent):
    name = "profile"
    description = "Parses CVs (uz/ru/ko/en) and stores the user's skills, education, languages and wishes."
    skills = [
        {"id": "parse_cv", "name": "Parse CV", "description": "CV text -> structured profile, saved."},
        {"id": "get_profile", "name": "Get profile", "description": "Everything known about a session's user."},
        {"id": "update_profile", "name": "Update profile", "description": "Merge fields (skills, wishes...)."},
        {"id": "delete_profile", "name": "Delete profile", "description": "Remove all stored data."},
    ]

    async def get(self, session_id: str) -> dict[str, Any] | None:
        row = await (await db.pool()).fetchrow("SELECT * FROM profiles WHERE session_id=$1", session_id)
        if not row:
            return None
        d = dict(row)
        d.pop("cv_text", None)
        d["updated_at"] = d["updated_at"].isoformat()
        return d

    async def save(self, session_id: str, p: dict[str, Any], cv_text: str | None = None) -> None:
        await (await db.pool()).execute(
            """INSERT INTO profiles (session_id, name, skills, education, experience, languages, wishes, cv_text)
               VALUES ($1,$2,$3,$4,$5,$6,$7,$8)
               ON CONFLICT (session_id) DO UPDATE SET name=COALESCE(EXCLUDED.name, profiles.name),
                 skills=EXCLUDED.skills, education=EXCLUDED.education, experience=EXCLUDED.experience,
                 languages=EXCLUDED.languages, wishes=profiles.wishes || EXCLUDED.wishes,
                 cv_text=COALESCE(EXCLUDED.cv_text, profiles.cv_text), updated_at=now()""",
            session_id, p.get("name"), p.get("skills", []), p.get("education", []),
            [{"years": p.get("experience_years")}] if p.get("experience_years") else [],
            p.get("languages", []), p.get("wishes", {}), cv_text,
        )

    async def skill(self, skill_id: str, input: dict[str, Any], trace_id: str | None) -> Any:
        sid = input.get("session_id", "")
        if skill_id == "parse_cv":
            text = input.get("text", "")[:15000]
            parsed, model = await llm.complete_json(CV_PROMPT, text, lambda: parse_cv(text))
            wishes = {k: parsed[k] for k in ("korean_level", "role_guess") if parsed.get(k)}
            await self.save(sid, {**parsed, "wishes": wishes}, cv_text=text)
            return {"profile": parsed, "model": model}
        if skill_id == "get_profile":
            return await self.get(sid)
        if skill_id == "update_profile":
            current = await self.get(sid) or {}
            fields = input.get("fields", {})
            merged = {
                "name": fields.get("name", current.get("name")),
                "skills": sorted(set(current.get("skills", [])) | set(fields.get("skills", []))),
                "education": current.get("education", []),
                "experience_years": (current.get("experience") or [{}])[0].get("years"),
                "languages": sorted(set(current.get("languages", [])) | set(fields.get("languages", []))),
                "wishes": fields.get("wishes", {}),
            }
            await self.save(sid, merged)
            return await self.get(sid)
        if skill_id == "delete_profile":
            await (await db.pool()).execute("DELETE FROM profiles WHERE session_id=$1", sid)
            return {"deleted": True}
        return await super().skill(skill_id, input, trace_id)


if __name__ == "__main__":
    ProfileAgent().run()

