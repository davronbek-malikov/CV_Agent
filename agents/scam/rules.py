"""Scam rules for job posts. Multilingual (uz/ru/ko/en). Each rule adds risk points."""

import re
from typing import Any

RULES: list[tuple[str, int, list[str]]] = [
    ("upfront_fee", 45, [
        r"upfront", r"\bfee\b", r"deposit", r"pay (us|first|before)",
        r"oldindan to[‘'ʻ`’]?lov", r"to[‘'ʻ`’]?lov qiling", r"\bto[‘'ʻ`’]?lov\b.*\$",
        r"предоплат", r"взнос", r"оплатить", r"선입금", r"수수료", r"보증금",
    ]),
    ("visa_guarantee", 35, [
        r"visa guarantee", r"guaranteed visa", r"100\s*% ?(visa|viza|виза)",
        r"viza kafolat", r"kafolatlangan viza", r"гарантия визы", r"виза гарантир", r"비자 보장",
    ]),
    ("passport_request", 25, [
        r"send (your )?passport", r"passport (copy|scan)", r"pasport nusxa", r"pasportingizni",
        r"паспорт.{0,20}(отправ|скин|фото)", r"여권.{0,10}(보내|사본)",
    ]),
    ("urgent_abroad", 20, [
        r"urgent.{0,30}abroad", r"chet el.{0,30}tezda", r"koreyaga tezda", r"tezda.{0,20}koreya",
        r"срочно.{0,30}(за границ|в корею|корея)", r"급구.{0,20}해외",
    ]),
    ("crypto_payment", 30, [r"\busdt\b", r"crypto", r"крипт", r"bitcoin", r"코인"]),
    ("contact_only_messenger", 15, [r"faqat telegram", r"only (telegram|whatsapp)", r"только (в )?(телеграм|whatsapp|ватсап)"]),
]

_COMPILED = [(name, pts, [re.compile(p, re.I) for p in pats]) for name, pts, pats in RULES]

# Monthly salary far above market for the region is a classic lure.
TOO_GOOD = {"UZS": 60_000_000, "USD": 15_000, "KRW": 30_000_000}


def assess(job: dict[str, Any]) -> dict[str, Any]:
    text = f"{job.get('title', '')} {job.get('description', '')} {job.get('salary_text') or ''}"
    reasons: list[str] = []
    score = 0
    for name, pts, pats in _COMPILED:
        if any(p.search(text) for p in pats):
            score += pts
            reasons.append(name)
    cur, top = job.get("currency"), job.get("salary_max")
    if cur in TOO_GOOD and top:
        monthly = top / 12 if cur == "KRW" and top > 10_000_000 * 4 else top  # Korean salaries are often yearly
        if monthly > TOO_GOOD[cur]:
            score += 20
            reasons.append("salary_too_good")
    if not job.get("company"):
        score += 10
        reasons.append("no_company_name")
    score = min(score, 100)
    level = "safe" if score < 30 else "check" if score < 60 else "high"
    return {"risk_score": score, "risk_level": level, "risk_reasons": reasons}
