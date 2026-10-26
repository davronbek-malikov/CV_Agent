"""Quality checks the Judge runs on every agent output.

Each check returns (hard_issues, soft_issues). Hard issues trigger a RETRY
(then FAIL); soft issues are passed through as warnings.
"""

from typing import Any

from darvoza_common.text import mentions

Issues = tuple[list[str], list[str]]


def check_match(out: dict[str, Any], inp: dict[str, Any]) -> Issues:
    hard, soft = [], []
    jobs = out.get("jobs", [])
    if not jobs:
        soft.append("no_jobs_in_scope")
    for j in jobs:
        if not 0 <= j.get("match", -1) <= 100:
            hard.append(f"bad_match_value:{j.get('title')}")
        invented = [s for s in j.get("have", []) if s not in (j.get("skills") or [])]
        if invented:
            hard.append(f"reason_not_in_job_text:{','.join(invented)}")
    if jobs and jobs[0].get("risk_level") == "high":
        hard.append("high_risk_job_ranked_first")
    mode = (inp.get("scope") or {}).get("mode")
    countries = (inp.get("scope") or {}).get("countries") or []
    if mode in ("single", "multi") and countries:
        outside = [j["title"] for j in jobs if j.get("country") not in countries]
        if outside:
            hard.append("job_outside_scope")
    return hard, soft


def check_brief(out: dict[str, Any], inp: dict[str, Any]) -> Issues:
    if not out.get("found"):
        return [], ["no_public_sources"]
    hard, soft = [], []
    rows = out.get("rows", [])
    unsourced = [r.get("text", "")[:30] for r in rows if not (r.get("source") or {}).get("url")]
    if unsourced:
        hard.append(f"claims_without_source:{len(unsourced)}")
    company = inp.get("company") or out.get("company") or ""
    off_topic = [r for r in rows
                 if not mentions(company, f"{r.get('text', '')} {(r.get('source') or {}).get('title', '')}")]
    if company and off_topic:
        hard.append(f"rows_not_about_company:{len(off_topic)}")
    if len(rows) < 2:
        soft.append("thin_brief")
    return hard, soft


def check_interview(out: dict[str, Any], inp: dict[str, Any]) -> Issues:
    hard = []
    qs = out.get("questions", [])
    if len(qs) < 3:
        hard.append("too_few_questions")
    if any(not q.get("text") or "{" in q["text"] for q in qs):
        hard.append("empty_or_unfilled_question")
    return hard, []


def check_roadmap(out: dict[str, Any], inp: dict[str, Any]) -> Issues:
    hard, soft = [], []
    if out.get("total_hours", 0) > out.get("budget_hours", 0) * 1.1:
        hard.append("plan_exceeds_weekly_hours")
    if len(out.get("blocks", [])) < 3:
        soft.append("missing_blocks")
    if not any(b.get("tasks") for b in out.get("blocks", [])):
        hard.append("empty_plan")
    return hard, soft


CHECKS = {
    "match_jobs": check_match,
    "company_brief": check_brief,
    "plan_interview": check_interview,
    "build_roadmap": check_roadmap,
}


def judge_output(task: str, out: dict[str, Any], inp: dict[str, Any]) -> tuple[str, list[str], list[str]]:
    if "error" in out:
        return "RETRY", [f"agent_error:{out['error'][:80]}"], []
    check = CHECKS.get(task)
    if not check:
        return "PASS", [], ["no_check_for_task"]
    hard, soft = check(out, inp)
    return ("RETRY" if hard else "PASS"), hard, soft
