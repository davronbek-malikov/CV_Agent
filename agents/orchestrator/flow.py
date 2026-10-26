"""Conversation logic for one user turn, as a LangGraph state graph.

    apply_input -> ensure_lang -> interview_turn -> ensure_mode -> fill_slots -> dispatch

Each node may add replies and stop the turn (e.g. to ask the next question).
Agent calls go through `Services`, so the graph is testable without Kafka.
"""

import re
from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from typing import Any, TypedDict

from langgraph.graph import END, StateGraph

from portiq_common.jobs import guess_role
from portiq_common.lang import detect_lang

from .messages import LANG_CHIPS, SALARY_CHIPS, VISA_CHIPS, chips, msg

SCOPES = {
    "uz": {"mode": "single", "countries": ["UZ"]},
    "kr": {"mode": "single", "countries": ["KR"]},
    "multi": {"mode": "multi", "countries": ["UZ", "KR"]},
    "all": {"mode": "all", "countries": []},
    "remote": {"mode": "remote", "countries": []},
}

MODE_WORDS = {
    "interview": r"interview|suhbat|интервью|собеседован|면접",
    "roadmap": r"roadmap|plan|reja|yo[‘'ʻ`’]?l xarita|план|로드맵|계획|learn|o[‘'ʻ`’]rgan|учить|공부",
    "jobs": r"job|work|vacanc|ish\b|ish qidir|ishga|работ|ваканс|일자리|채용|취업|구직",
}


@dataclass
class Services:
    get_profile: Callable[[str], Awaitable[dict[str, Any] | None]]
    score: Callable[[dict[str, Any]], Awaitable[dict[str, Any]]]
    follow_up: Callable[[str, str], Awaitable[str | None]]


class Turn(TypedDict, total=False):
    session_id: str
    session: dict[str, Any]
    input: dict[str, Any]
    replies: list[dict[str, Any]]
    tasks: list[dict[str, Any]]
    stop: bool


def new_session() -> dict[str, Any]:
    return {"lang": None, "mode": None, "slots": {}, "asking": None, "stage": "intake",
            "pending": {}, "interview": None, "last_jobs": [], "last_role": None}


# --- parsing free text into slot values ---------------------------------------

def parse_scope(text: str) -> str:
    low = text.lower()
    uz = re.search(r"uzbek|o[‘'ʻ`’]?zbek|узбек|우즈벡|우즈베키|tashkent|toshkent", low)
    kr = re.search(r"korea|koreya|коре|한국|seoul|서울", low)
    if re.search(r"remote|masofa|удал|원격", low):
        return "remote"
    if uz and kr:
        return "multi"
    if uz:
        return "uz"
    if kr:
        return "kr"
    return "all"


def parse_type(text: str) -> str:
    low = text.lower()
    if re.search(r"stress|стресс|압박", low):
        return "stress"
    if re.search(r"tech|техн|기술|texnik", low):
        return "tech"
    if re.search(r"salary|зарплат|연봉|maosh", low):
        return "salary"
    return "full"


def parse_slot(slot: str, text: str) -> str:
    text = text.strip()
    if slot == "scope":
        return parse_scope(text)
    if slot in ("role", "target"):
        return guess_role(text) or (text if slot == "target" else "")
    if slot == "visa":
        m = re.search(r"\b([EDF])\s*-?\s*(\d{1,2})\b", text, re.I)
        return f"{m.group(1).upper()}-{m.group(2)}" if m else ""
    if slot == "type":
        return parse_type(text)
    if slot == "days":
        m = re.search(r"\d+", text)
        return str(min((30, 60, 90), key=lambda d: abs(d - int(m.group(0))))) if m else "60"
    if slot == "hours":
        m = re.search(r"\d+", text)
        return m.group(0) if m else "10"
    return text


def detect_mode(text: str) -> str | None:
    low = text.lower()
    for mode, pat in MODE_WORDS.items():
        if re.search(pat, low):
            return mode
    return None


def required_slots(mode: str, slots: dict[str, Any]) -> list[str]:
    if mode == "jobs":
        need = ["scope", "role", "salary"]
        if slots.get("scope") in ("kr", "multi"):
            need.append("visa")
        return need
    if mode == "interview":
        return ["company", "role", "type"]
    if mode == "roadmap":
        return ["target", "days", "hours"]
    return []


def slot_question(slot: str, s: dict[str, Any]) -> dict[str, Any]:
    lang = s["lang"]
    skip = {"value": "", "label": msg("skip", lang)}
    if slot == "scope":
        return {"text": msg("ask_scope", lang), "chips": chips("scope", lang)}
    if slot in ("role", "target"):
        c = chips("role", lang)
        return {"text": msg("ask_role" if slot == "role" else "ask_target", lang), "chips": c + ([skip] if slot == "role" else [])}
    if slot == "salary":
        scope = s["slots"].get("scope")
        cur = {"uz": ["UZS"], "kr": ["KRW"], "multi": ["UZS", "KRW"]}.get(scope, ["USD"])
        values = [v for c in cur for v in SALARY_CHIPS[c][: 4 // len(cur)]]
        return {"text": msg("ask_salary", lang),
                "chips": [{"value": v, "label": v} for v in values] + [{"value": "", "label": msg("not_sure", lang)}]}
    if slot == "visa":
        return {"text": msg("ask_visa", lang),
                "chips": [{"value": v, "label": v} for v in VISA_CHIPS] + [{"value": "", "label": msg("not_sure", lang)}]}
    if slot == "company":
        recent = [{"value": j["company"], "label": j["company"]} for j in s.get("last_jobs", []) if j.get("company")][:3]
        return {"text": msg("ask_company", lang), "chips": recent}
    if slot == "type":
        return {"text": msg("ask_type", lang), "chips": chips("type", lang)}
    if slot == "days":
        return {"text": msg("ask_days", lang), "chips": chips("days", lang)}
    if slot == "hours":
        return {"text": msg("ask_hours", lang), "chips": chips("hours", lang)}
    return {"text": slot, "chips": []}


def question_reply(s: dict[str, Any]) -> dict[str, Any]:
    iv = s["interview"]
    q = iv["questions"][iv["idx"]]
    lang = s["lang"]
    return {
        "kind": "interview_q",
        "text": iv.get("follow_up_text") or q["text"],
        "data": {"index": iv["idx"], "total": len(iv["questions"]), "category": q.get("category"),
                 "follow_up": bool(iv.get("follow_up_text")), "follow_up_label": msg("follow_up", lang),
                 "source": q.get("source"), "company": iv.get("company")},
        "chips": [{"value": "skip_question", "label": msg("skip", lang), "action": "skip_question"},
                  {"value": "end_interview", "label": msg("end", lang), "action": "end_interview"}],
    }


def report_reply(s: dict[str, Any]) -> dict[str, Any]:
    iv = s["interview"]
    lang = s["lang"]
    turns = iv.get("turns", [])
    axes = ["knowledge", "structure", "clarity", "fit"]
    avg = {a: round(sum(t["scores"][a] for t in turns) / len(turns), 1) if turns else 0 for a in axes}
    readiness = round(sum(t["total"] for t in turns) / len(turns)) if turns else 0
    s["stage"] = "done"
    s["weak_axes"] = [a for a in axes if avg[a] and avg[a] < 3]
    return {
        "kind": "report",
        "text": msg("report", lang),
        "data": {"readiness": readiness, "axes": avg, "answered": len(turns), "company": iv.get("company"),
                 "weakest": min(avg, key=avg.get) if turns else None},
        "chips": [{"value": "roadmap_from_weak", "label": msg("to_roadmap", lang), "action": "roadmap_from_weak"},
                  {"value": "restart", "label": msg("again", lang), "action": "restart"}],
    }


# --- graph ---------------------------------------------------------------

def build_graph(services: Services):
    def reply(state: Turn, r: dict[str, Any], stop: bool = True) -> Turn:
        return {"replies": state.get("replies", []) + [r], "stop": stop}

    async def apply_input(state: Turn) -> Turn:
        s, inp = state["session"], state["input"]
        action, text = inp.get("action") or {}, (inp.get("text") or "").strip()
        kind = action.get("type")
        if kind == "restart":
            lang = s["lang"]
            s.clear()
            s.update(new_session(), lang=lang)
        elif kind == "lang":
            s["lang"] = action["value"]
            s["asking"] = None
        elif kind == "mode":
            s.update(mode=action["value"], stage="intake", asking=None, interview=None)
            s["slots"] = {k: v for k, v in s["slots"].items() if k in ("scope", "role")}
        elif kind == "choose":
            s["slots"][action["slot"]] = action.get("value", "")
            s["asking"] = None
        elif kind == "practice":
            s.update(mode="interview", stage="intake", asking=None, interview=None)
            s["slots"] = {**s["slots"], "company": action.get("company", ""), "role": action.get("role") or s["slots"].get("role", "")}
        elif kind == "roadmap_from_weak":
            missing = sorted({m for j in s.get("last_jobs", [])[:3] for m in j.get("missing", [])})
            s.update(mode="roadmap", stage="intake", asking=None)
            s["slots"] = {"target": s["slots"].get("role") or s.get("last_role") or "dev", "missing": missing}
        elif text:
            if not s["lang"]:
                s["lang"] = detect_lang(text)
            if s["stage"] == "interview":
                return {"input": {**inp, "answer": text}}
            if s.get("asking"):
                s["slots"][s["asking"]] = parse_slot(s["asking"], text)
                s["asking"] = None
            elif not s["mode"] or s["stage"] in ("done", "working"):
                mode = detect_mode(text)
                if mode:
                    s.update(mode=mode, stage="intake", interview=None)
                    role = guess_role(text)
                    if role:
                        s["slots"]["role"] = role
                    if mode == "jobs" and re.search(r"korea|koreya|коре|한국|uzbek|o[‘'ʻ`’]?zbek|узбек|remote|원격", text, re.I):
                        s["slots"]["scope"] = parse_scope(text)
        return {}

    def ensure_lang(state: Turn) -> Turn:
        s = state["session"]
        if not s["lang"]:
            s["asking"] = "lang"
            return reply(state, {"kind": "question", "text": msg("ask_lang", "en"), "slot": "lang",
                                 "chips": [{**c, "action": "lang"} for c in LANG_CHIPS]})
        return {}

    async def interview_turn(state: Turn) -> Turn:
        s, inp = state["session"], state["input"]
        action = (inp.get("action") or {}).get("type")
        iv = s.get("interview")
        if s["stage"] != "interview" or not iv:
            return {}
        if action == "end_interview":
            return reply(state, report_reply(s))
        out: list[dict[str, Any]] = []
        if inp.get("answer"):
            q = iv["questions"][iv["idx"]]
            question = iv.get("follow_up_text") or q["text"]
            result = await services.score({
                "session_id": state["session_id"], "question": question, "answer": inp["answer"],
                "category": q.get("category"), "lang": s["lang"], "company": iv.get("company", ""),
                "brief_terms": iv.get("brief_terms", [])})
            iv.setdefault("turns", []).append({"category": q.get("category"), "scores": result["scores"], "total": result["total"]})
            out.append({"kind": "score", "data": {**result, "category": q.get("category")}})
            if not iv.get("follow_up_text"):
                fu = await services.follow_up(inp["answer"], s["lang"])
                if fu:
                    iv["follow_up_text"] = fu
                    out.append(question_reply(s))
                    return {"replies": state.get("replies", []) + out, "stop": True}
        elif action != "skip_question":
            return {}
        iv["follow_up_text"] = None
        iv["idx"] += 1
        out.append(question_reply(s) if iv["idx"] < len(iv["questions"]) else report_reply(s))
        return {"replies": state.get("replies", []) + out, "stop": True}

    def ensure_mode(state: Turn) -> Turn:
        s = state["session"]
        # A finished flow plus a message that names no new mode -> ask what's next.
        if not s["mode"] or s["stage"] == "done":
            s["mode"] = None
            return reply(state, {"kind": "question", "text": msg("ask_mode", s["lang"]), "slot": "mode",
                                 "chips": [{**c, "action": "mode"} for c in chips("mode", s["lang"])]})
        return {}

    async def fill_slots(state: Turn) -> Turn:
        s = state["session"]
        if s["stage"] != "intake":
            return {"stop": True}
        if "role" not in s["slots"] and s["mode"] in ("jobs", "interview"):
            prof = await services.get_profile(state["session_id"])
            role = ((prof or {}).get("wishes") or {}).get("role_guess")
            if role:
                s["slots"]["role"] = role
        for slot in required_slots(s["mode"], s["slots"]):
            if slot not in s["slots"]:
                s["asking"] = slot
                q = slot_question(slot, s)
                return reply(state, {"kind": "question", "slot": slot, "text": q["text"],
                                     "chips": [{**c, "action": "choose", "slot": slot} for c in q["chips"]]})
        return {}

    def dispatch(state: Turn) -> Turn:
        s = state["session"]
        sl, lang = s["slots"], s["lang"]
        s["stage"] = "working"
        if s["mode"] == "jobs":
            s["last_role"] = sl.get("role") or s.get("last_role")
            task = {"target_agent": "match", "task": "match_jobs",
                    "payload": {"scope": SCOPES.get(sl.get("scope"), SCOPES["all"]), "role": sl.get("role") or None,
                                "salary": sl.get("salary"), "visa": sl.get("visa"), "limit": 5}}
            text = msg("working_jobs", lang)
        elif s["mode"] == "interview":
            task = {"target_agent": "company_research", "task": "company_brief",
                    "payload": {"company": sl.get("company", ""), "role": sl.get("role")}}
            text = msg("working_research", lang, company=sl.get("company", ""))
        else:
            task = {"target_agent": "roadmap", "task": "build_roadmap",
                    "payload": {"target": sl.get("target"), "days": sl.get("days"), "hours": sl.get("hours"),
                                "missing": sl.get("missing", [])}}
            text = msg("working_roadmap", lang)
        return {"replies": state.get("replies", []) + [{"kind": "status", "text": text}],
                "tasks": state.get("tasks", []) + [task], "stop": True}

    def route(next_node: str):
        return lambda st: END if st.get("stop") else next_node

    g = StateGraph(Turn)
    for name, fn in [("apply_input", apply_input), ("ensure_lang", ensure_lang), ("interview_turn", interview_turn),
                     ("ensure_mode", ensure_mode), ("fill_slots", fill_slots), ("dispatch", dispatch)]:
        g.add_node(name, fn)
    g.set_entry_point("apply_input")
    g.add_conditional_edges("apply_input", route("ensure_lang"))
    g.add_conditional_edges("ensure_lang", route("interview_turn"))
    g.add_conditional_edges("interview_turn", route("ensure_mode"))
    g.add_conditional_edges("ensure_mode", route("fill_slots"))
    g.add_conditional_edges("fill_slots", route("dispatch"))
    g.add_edge("dispatch", END)
    return g.compile()


# --- verdicts from the Judge -------------------------------------------------

def on_verdict(s: dict[str, Any], task: str, payload: dict[str, Any]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Turn a judge verdict into replies to the user and follow-up tasks."""
    lang = s["lang"] or "en"
    verdict, out = payload["verdict"], payload.get("output", {})
    if verdict == "FAIL" and task != "company_brief":
        s["stage"] = "done"
        return [{"kind": "error", "text": msg("failed", lang)}], []

    if task == "match_jobs":
        s["stage"] = "done"
        jobs = out.get("jobs", [])
        s["last_jobs"] = [{"company": j.get("company"), "title": j.get("title"), "missing": j.get("missing", [])} for j in jobs]
        if not jobs:
            return [{"kind": "text", "text": msg("no_jobs", lang)}], []
        return [{"kind": "jobs", "text": msg("jobs_title", lang),
                 "data": {"jobs": jobs, "used_profile": out.get("used_profile"), "warnings": payload.get("warnings", [])}}], []

    if task == "company_brief":
        replies = []
        if verdict == "FAIL":
            out = {}  # the Judge rejected the brief: interview with general questions instead
        if out.get("rows"):
            replies.append({"kind": "brief", "data": out})
        else:
            replies.append({"kind": "text", "text": msg("no_sources", lang)})
        terms = re.findall(r"\w{5,}", " ".join(r.get("text", "") for r in out.get("rows", [])))[:30]
        s["interview"] = {"company": s["slots"].get("company"), "brief_terms": terms, "questions": [], "idx": 0}
        follow = {"target_agent": "interviewer", "task": "plan_interview",
                  "payload": {"company": s["slots"].get("company"), "role": s["slots"].get("role") or None,
                              "type": s["slots"].get("type") or "full",
                              "brief": out if out.get("rows") else None}}
        return replies, [follow]

    if task == "plan_interview":
        iv = s.get("interview") or {"company": s["slots"].get("company"), "brief_terms": []}
        iv.update(questions=out.get("questions", []), idx=0, turns=[], follow_up_text=None)
        s["interview"] = iv
        if not iv["questions"]:
            s["stage"] = "done"
            return [{"kind": "error", "text": msg("failed", lang)}], []
        s["stage"] = "interview"
        return [question_reply(s)], []

    if task == "build_roadmap":
        s["stage"] = "done"
        return [{"kind": "roadmap", "data": out}], []

    return [], []
