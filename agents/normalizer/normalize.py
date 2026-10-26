"""Turn any raw post (API job or free-text Telegram message) into one schema."""

import re
from typing import Any

from portiq_common.jobs import extract_skills, job_hash, parse_salary
from portiq_common.lang import detect_lang

CITIES = {
    "Tashkent": ["tashkent", "toshkent", "ташкент"],
    "Samarkand": ["samarkand", "samarqand", "самарканд"],
    "Bukhara": ["bukhara", "buxoro", "бухара"],
    "Namangan": ["namangan", "наманган"],
    "Andijan": ["andijan", "andijon", "андижан"],
    "Fergana": ["fergana", "farg'ona", "фергана"],
    "Seoul": ["seoul", "서울", "сеул", "seul"],
    "Busan": ["busan", "부산", "пусан"],
    "Pangyo": ["pangyo", "판교"],
    "Incheon": ["incheon", "인천"],
    "Remote": ["remote", "masofaviy", "удален", "удалён", "원격"],
}
KR_CITIES = {"Seoul", "Busan", "Pangyo", "Incheon"}


def find_city(text: str) -> str | None:
    low = text.lower()
    for city, names in CITIES.items():
        if any(n in low for n in names):
            return city
    return None


def heuristic_extract(raw_text: str) -> dict[str, Any]:
    """Fallback parser for Telegram posts when no LLM is configured."""
    lines = [l.strip(" *#•-—📌✅🔥") for l in raw_text.splitlines() if l.strip()]
    title = next((l for l in lines if 3 < len(l) < 90), lines[0][:90] if lines else "Job post")
    company = None
    m = re.search(r"(?:kompaniya|company|компания|회사)\s*[:\-–]\s*(.+)", raw_text, re.I)
    if m:
        company = m.group(1).strip()[:80]
    sal = re.search(r"(?:maosh|salary|зарплата|з/п|oylik|급여|연봉)\s*[:\-–]?\s*(.+)", raw_text, re.I)
    return {"title": title, "company": company, "salary_text": sal.group(1)[:80] if sal else ""}


def normalize(raw: dict[str, Any], extracted: dict[str, Any] | None = None) -> dict[str, Any]:
    if raw.get("raw_text"):
        fields = extracted or heuristic_extract(raw["raw_text"])
        text = raw["raw_text"]
        title, company, salary_text = fields.get("title"), fields.get("company"), fields.get("salary_text", "")
        description = text
    else:
        title, company = raw.get("title"), raw.get("company")
        salary_text = raw.get("salary_text", "")
        description = raw.get("description", "")
        text = f"{title} {description}"

    city = raw.get("city") or find_city(text)
    country = raw.get("country") or ("KR" if city in KR_CITIES else "GL")
    sal = parse_salary(salary_text or "")
    skills = sorted(set(extract_skills(f"{title} {description}")) | set(raw.get("tags_skills", [])))
    return {
        "hash": job_hash(title or "", company, city),
        "source": raw.get("source", "unknown"),
        "url": raw.get("url"),
        "title": (title or "Job post").strip()[:200],
        "company": (company or "").strip()[:200] or None,
        "city": city,
        "country": country,
        "remote": bool(raw.get("remote")) or city == "Remote",
        "salary_min": sal["min"],
        "salary_max": sal["max"],
        "currency": sal["currency"],
        "salary_text": salary_text or None,
        "lang": detect_lang(text),
        "skills": skills,
        "description": (description or "")[:4000],
        "visa": raw.get("visa"),
        "posted_at": raw.get("posted_at"),
        "sample": bool(raw.get("sample")),
    }
