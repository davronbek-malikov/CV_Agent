"""Explainable job scoring: every number in the match % has a reason."""

from typing import Any

from portiq_common.jobs import ROLE_SKILLS, guess_role, parse_salary

# Rough FX to compare salary wishes across currencies (monthly USD).
TO_USD = {"USD": 1, "EUR": 1.08, "UZS": 1 / 12_700, "KRW": 1 / 1_380, "RUB": 1 / 95}


def monthly_usd(amount: float | None, currency: str | None) -> float | None:
    if not amount or currency not in TO_USD:
        return None
    if currency == "KRW" and amount > 10_000_000 * 4:  # yearly 연봉 -> monthly
        amount /= 12
    return amount * TO_USD[currency]


def score_job(job: dict[str, Any], user_skills: list[str], role: str | None, salary_wish: str | None,
              visa: str | None, similarity: float) -> dict[str, Any]:
    job_skills = list(job.get("skills") or [])
    have = [s for s in job_skills if s in user_skills]
    missing = [s for s in job_skills if s not in user_skills]
    if not user_skills and role:
        # No CV yet: compare with the role's core skills instead.
        missing = [s for s in job_skills if s not in ROLE_SKILLS.get(role, [])]

    reasons: list[str] = []
    score = 40.0 + max(similarity, 0) * 20
    if job_skills and user_skills:
        score += 30 * len(have) / len(job_skills)
    job_role = guess_role(f"{job['title']} {' '.join(job_skills)}")
    if role and (job_role == role or (role == "dev" and job_role in ("dev", "frontend"))):
        score += 12
        reasons.append("role_fit")

    wish = parse_salary(salary_wish or "")
    want = monthly_usd(wish["min"], wish["currency"])
    offer = monthly_usd(job.get("salary_max") and float(job["salary_max"]), job.get("currency"))
    if want and offer:
        if offer >= want:
            score += 8
            reasons.append("salary_ok")
        else:
            score -= 8
            reasons.append("salary_low")

    if visa and job.get("visa") and visa.upper() in job["visa"].upper():
        score += 6
        reasons.append("visa_ok")

    score -= (job.get("risk_score") or 0) / 2
    return {
        "match": int(max(5, min(score, 98))),
        "have": have[:4],
        "missing": missing[:3],
        "reasons": reasons,
    }
