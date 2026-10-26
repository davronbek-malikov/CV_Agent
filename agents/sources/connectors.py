"""Job source connectors. Each returns raw job dicts for `jobs.raw`.

A connector is enabled only when its key or setting is present, so the
pipeline runs today with seed + Remotive and grows as keys arrive.
"""

import json
import logging
import re
from html import unescape
from pathlib import Path
from typing import Any

import httpx

from darvoza_common.settings import get_settings

log = logging.getLogger("sources")
UA = "DarvozaJobHub/0.1 (+https://github.com/davronbek-malikov/CV_Agent)"


def _strip_html(html: str) -> str:
    return re.sub(r"\s+", " ", unescape(re.sub(r"<[^>]+>", " ", html or ""))).strip()


def seed() -> list[dict[str, Any]]:
    """Sample Uzbekistan and Korea jobs (fictional companies) so the demo works offline."""
    data = json.loads((Path(__file__).parent / "seed_jobs.json").read_text(encoding="utf-8"))
    for j in data:
        j.update(source="sample", sample=True)
    return data


async def remotive(limit: int = 60) -> list[dict[str, Any]]:
    async with httpx.AsyncClient(timeout=30, headers={"User-Agent": UA}) as c:
        r = await c.get("https://remotive.com/api/remote-jobs", params={"limit": limit})
        r.raise_for_status()
    out = []
    for j in r.json().get("jobs", []):
        out.append({
            "source": "remotive",
            "url": j.get("url"),
            "title": j.get("title"),
            "company": j.get("company_name"),
            "city": "Remote",
            "country": "GL",
            "remote": True,
            "salary_text": j.get("salary") or "",
            "description": _strip_html(j.get("description", ""))[:4000],
            "tags": j.get("tags", []),
            "location_note": j.get("candidate_required_location"),
            "posted_at": j.get("publication_date"),
        })
    return out


async def saramin(count: int = 50) -> list[dict[str, Any]]:
    key = get_settings().saramin_api_key
    async with httpx.AsyncClient(timeout=30, headers={"Accept": "application/json", "User-Agent": UA}) as c:
        r = await c.get("https://oapi.saramin.co.kr/job-search", params={"access-key": key, "count": count})
        r.raise_for_status()
    out = []
    for j in r.json().get("jobs", {}).get("job", []):
        pos = j.get("position", {})
        out.append({
            "source": "saramin",
            "url": j.get("url"),
            "title": pos.get("title"),
            "company": j.get("company", {}).get("detail", {}).get("name"),
            "city": (pos.get("location", {}).get("name") or "").split(",")[0],
            "country": "KR",
            "salary_text": j.get("salary", {}).get("name", ""),
            "description": " ".join(filter(None, [pos.get("job-code", {}).get("name"), j.get("keyword")])),
            "posted_at": j.get("posting-date"),
        })
    return out


async def hh_uz(per_page: int = 50) -> list[dict[str, Any]]:
    """hh.uz uses the hh.ru API. Area 97 = Uzbekistan. Needs an app token."""
    token = get_settings().hh_access_token
    async with httpx.AsyncClient(timeout=30, headers={"User-Agent": UA, "Authorization": f"Bearer {token}"}) as c:
        r = await c.get("https://api.hh.ru/vacancies", params={"area": 97, "per_page": per_page})
        r.raise_for_status()
    out = []
    for j in r.json().get("items", []):
        sal = j.get("salary") or {}
        salary_text = " ".join(str(x) for x in (sal.get("from"), "-", sal.get("to"), sal.get("currency")) if x)
        snip = j.get("snippet") or {}
        out.append({
            "source": "hh.uz",
            "url": j.get("alternate_url"),
            "title": j.get("name"),
            "company": (j.get("employer") or {}).get("name"),
            "city": (j.get("area") or {}).get("name"),
            "country": "UZ",
            "salary_text": salary_text,
            "description": _strip_html(f"{snip.get('requirement', '')} {snip.get('responsibility', '')}"),
            "posted_at": j.get("published_at"),
        })
    return out


async def telegram(last_ids: dict[str, int]) -> tuple[list[dict[str, Any]], dict[str, int]]:
    """Read new posts from public job channels. Needs a one-time login (see README)."""
    from telethon import TelegramClient

    s = get_settings()
    channels = [c.strip().lstrip("@") for c in s.tg_channels.split(",") if c.strip()]
    out: list[dict[str, Any]] = []
    async with TelegramClient(f"/app/data/{s.tg_session}", int(s.tg_api_id), s.tg_api_hash) as client:
        for ch in channels:
            newest = last_ids.get(ch, 0)
            async for msg in client.iter_messages(ch, limit=50, min_id=newest):
                if not msg.message or len(msg.message) < 40:
                    continue
                newest = max(newest, msg.id)
                out.append({
                    "source": "telegram",
                    "channel": ch,
                    "url": f"https://t.me/{ch}/{msg.id}",
                    "raw_text": msg.message[:4000],
                    "country": "UZ",
                    "posted_at": msg.date.isoformat() if msg.date else None,
                })
            last_ids[ch] = newest
    return out, last_ids


def enabled() -> dict[str, bool]:
    s = get_settings()
    return {
        "sample": s.seed_enabled,
        "remotive": s.remotive_enabled,
        "saramin": bool(s.saramin_api_key),
        "hh.uz": bool(s.hh_access_token),
        "telegram": bool(s.tg_api_id and s.tg_api_hash and s.tg_channels),
    }
