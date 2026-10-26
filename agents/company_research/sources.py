"""Free public sources: Wikipedia and Google News RSS. No API keys."""

import re
from typing import Any
from urllib.parse import quote

import feedparser
import httpx

from portiq_common.text import mentions

UA = "PortiqJobHub/0.1 (+https://github.com/davronbek-malikov/CV_Agent)"

NEWS_LOCALE = {
    "ko": ("ko", "KR", "KR:ko"),
    "ru": ("ru", "RU", "RU:ru"),
    "uz": ("ru", "RU", "RU:ru"),  # Google News has few Uzbek-language sources
    "en": ("en-US", "US", "US:en"),
}


async def wikipedia(company: str) -> dict[str, Any] | None:
    wikis = ["ko", "en"] if re.search(r"[가-힣]", company) else ["en", "ru"]
    async with httpx.AsyncClient(timeout=15, headers={"User-Agent": UA}) as c:
        for wiki in wikis:
            r = await c.get(f"https://{wiki}.wikipedia.org/w/api.php",
                            params={"action": "query", "list": "search", "srsearch": f"{company} company",
                                    "format": "json", "srlimit": 3})
            hits = r.json().get("query", {}).get("search", [])
            # The page title must name this company, not a look-alike ("Bazaar Online" != "Cafe Bazaar").
            hit = next((h for h in hits if mentions(company, h["title"])), None)
            if not hit:
                continue
            s = await c.get(f"https://{wiki}.wikipedia.org/api/rest_v1/page/summary/{quote(hit['title'])}")
            if s.status_code != 200:
                continue
            d = s.json()
            if d.get("type") == "disambiguation":
                continue
            return {"title": d.get("title"), "extract": d.get("extract", ""),
                    "url": d.get("content_urls", {}).get("desktop", {}).get("page")}
    return None


async def news(company: str, lang: str, limit: int = 6) -> list[dict[str, Any]]:
    hl, gl, ceid = NEWS_LOCALE.get(lang, NEWS_LOCALE["en"])
    url = f"https://news.google.com/rss/search?q={quote(chr(34) + company + chr(34))}&hl={hl}&gl={gl}&ceid={ceid}"
    async with httpx.AsyncClient(timeout=15, headers={"User-Agent": UA}, follow_redirects=True) as c:
        r = await c.get(url)
    feed = feedparser.parse(r.text)
    items = []
    for e in feed.entries:
        if len(items) >= limit:
            break
        title = re.sub(r"\s+-\s+[^-]+$", "", e.get("title", ""))
        if not mentions(company, title):
            continue  # the quoted query also matches outlet names, e.g. "The American Bazaar"
        items.append({
            "title": title,
            "url": e.get("link"),
            "source": (e.get("source") or {}).get("title"),
            "published": e.get("published"),
        })
    return items
