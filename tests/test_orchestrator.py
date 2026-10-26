"""Drive the orchestrator graph through full conversations with fake agents."""

from agents.orchestrator.flow import Services, build_graph, new_session, on_verdict


async def fake_profile(_sid):
    return None


async def fake_score(inp):
    return {"scores": {"knowledge": 3, "structure": 2, "clarity": 4, "fit": 3}, "total": 60, "feedback": "ok"}


async def fake_follow_up(answer, lang):
    return "Give me a number." if len(answer.split()) < 5 else None


GRAPH = build_graph(Services(fake_profile, fake_score, fake_follow_up))


async def turn(s, text=None, action=None):
    out = await GRAPH.ainvoke({"session_id": "s1", "session": s, "input": {"text": text, "action": action},
                               "replies": [], "tasks": []})
    return out["session"], out.get("replies", []), out.get("tasks", [])


async def test_language_first_then_mode_then_country():
    s = new_session()
    s, r, _ = await turn(s, action={"type": "start"})
    assert r[0]["slot"] == "lang"
    s, r, _ = await turn(s, action={"type": "lang", "value": "uz"})
    assert r[0]["slot"] == "mode" and r[0]["text"] == "Bugun sizga nima kerak?"
    s, r, _ = await turn(s, action={"type": "mode", "value": "jobs"})
    assert r[0]["slot"] == "scope"
    assert [c["value"] for c in r[0]["chips"]] == ["uz", "kr", "multi", "all", "remote"]


async def test_jobs_flow_asks_visa_only_for_korea():
    s = new_session()
    s["lang"] = "en"
    s, _, _ = await turn(s, action={"type": "mode", "value": "jobs"})
    s, r, _ = await turn(s, action={"type": "choose", "slot": "scope", "value": "uz"})
    assert r[0]["slot"] == "role"
    s, r, _ = await turn(s, action={"type": "choose", "slot": "role", "value": "dev"})
    assert r[0]["slot"] == "salary" and "so‘m" in r[0]["chips"][0]["label"]
    s, r, tasks = await turn(s, action={"type": "choose", "slot": "salary", "value": "10M so‘m"})
    assert tasks[0]["task"] == "match_jobs"
    assert tasks[0]["payload"]["scope"] == {"mode": "single", "countries": ["UZ"]}

    s2 = new_session()
    s2["lang"] = "ko"
    s2, _, _ = await turn(s2, action={"type": "mode", "value": "jobs"})
    s2, _, _ = await turn(s2, action={"type": "choose", "slot": "scope", "value": "kr"})
    s2, _, _ = await turn(s2, action={"type": "choose", "slot": "role", "value": "data"})
    s2, r, _ = await turn(s2, action={"type": "choose", "slot": "salary", "value": ""})
    assert r[0]["slot"] == "visa"


async def test_free_text_detects_language_mode_and_scope():
    s = new_session()
    s, r, _ = await turn(s, text="Koreyada data tahlilchi sifatida ish qidiryapman")
    assert s["lang"] == "uz" and s["mode"] == "jobs"
    assert s["slots"]["scope"] == "kr" and s["slots"]["role"] == "data"
    assert r[0]["slot"] == "salary"


async def test_interview_flow_with_follow_up_and_report():
    s = new_session()
    s["lang"] = "en"
    s, _, _ = await turn(s, action={"type": "mode", "value": "interview"})
    s, r, _ = await turn(s, text="Kakao")
    assert s["slots"]["company"] == "Kakao"
    s, _, _ = await turn(s, action={"type": "choose", "slot": "role", "value": "dev"})
    s, r, tasks = await turn(s, action={"type": "choose", "slot": "type", "value": "salary"})
    assert tasks[0]["task"] == "company_brief"

    replies, follow = on_verdict(s, "company_brief", {"verdict": "PASS", "output": {"found": False, "rows": []}})
    assert follow[0]["task"] == "plan_interview"
    qs = [{"category": "intro", "text": "Q1"}, {"category": "salary", "text": "Q2"}]
    replies, _ = on_verdict(s, "plan_interview", {"verdict": "PASS", "output": {"questions": qs}})
    assert replies[0]["kind"] == "interview_q" and s["stage"] == "interview"

    s, r, _ = await turn(s, text="short one")  # -> score + follow-up
    assert [x["kind"] for x in r] == ["score", "interview_q"] and r[1]["data"]["follow_up"]
    s, r, _ = await turn(s, text="Now a longer answer with 40 percent improvement")
    assert [x["kind"] for x in r] == ["score", "interview_q"] and r[1]["text"] == "Q2"
    s, r, _ = await turn(s, action={"type": "end_interview"})
    assert r[0]["kind"] == "report" and r[0]["data"]["answered"] == 2


async def test_practice_from_job_card_skips_known_slots():
    s = new_session()
    s["lang"] = "ru"
    s, r, _ = await turn(s, action={"type": "practice", "company": "PayLink", "role": "dev"})
    assert r[0]["slot"] == "type"
