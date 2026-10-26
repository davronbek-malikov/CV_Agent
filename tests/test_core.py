from agents.interviewer.main import build_plan, follow_up
from agents.judge.checks import judge_output
from agents.judge.rubric import score_answer
from agents.match.scoring import score_job
from agents.normalizer.normalize import normalize
from agents.profile.parse import parse_cv
from agents.roadmap.plan import build_plan as build_roadmap
from agents.scam.rules import assess
from portiq_common.embed import cosine, embed
from portiq_common.envelope import Envelope
from portiq_common.jobs import extract_skills, guess_role, parse_salary
from portiq_common.lang import detect_lang


def test_detect_lang():
    assert detect_lang("Men Toshkentda dasturchi bo‘lib ishlamoqchiman") == "uz"
    assert detect_lang("Ищу работу разработчиком в Ташкенте") == "ru"
    assert detect_lang("서울에서 백엔드 개발자 일자리를 찾고 있어요") == "ko"
    assert detect_lang("I want a backend job in Seoul") == "en"
    assert detect_lang("Мен иш қидиряпман") == "uz"


def test_salary_parsing():
    assert parse_salary("12-18 mln so'm") == {"min": 12e6, "max": 18e6, "currency": "UZS"}
    assert parse_salary("4,200만원 - 5,000만원") == {"min": 42e6, "max": 50e6, "currency": "KRW"}
    assert parse_salary("$2,500–3,500")["currency"] == "USD"
    assert parse_salary("negotiable")["min"] is None


def test_skills_and_roles():
    s = extract_skills("Python, FastAPI, PostgreSQL, Docker. 카프카 경험 우대")
    assert {"Python", "FastAPI", "SQL", "Docker", "Kafka"} <= set(s)
    assert guess_role("Data Analyst") == "data"
    assert guess_role("백엔드 개발자") == "dev"
    assert guess_role("Frontend Engineer (React)") == "frontend"


def test_envelope_roundtrip_and_child():
    e = Envelope(type="task", source_agent="orchestrator", session_id="s1", task="match_jobs", task_id="t1")
    back = Envelope.from_bytes(e.to_bytes())
    assert back.task_id == "t1"
    c = e.child(type="result", source_agent="match")
    assert (c.trace_id, c.session_id, c.task_id) == (e.trace_id, "s1", "t1")


def test_embedding_similarity():
    a, b, c = embed("python backend developer"), embed("backend python engineer"), embed("graphic designer figma")
    assert cosine(a, b) > cosine(a, c)


def test_scam_rules():
    scam = assess({"title": "Koreyaga tezda", "company": "",
                   "description": "Viza kafolat 100%. Oldindan to'lov 500$. Pasport nusxasini yuboring."})
    assert scam["risk_level"] == "high"
    assert {"upfront_fee", "visa_guarantee", "passport_request"} <= set(scam["risk_reasons"])
    ok = assess({"title": "Backend Developer", "company": "PayLink", "description": "Python, Docker",
                 "currency": "UZS", "salary_max": 18e6})
    assert ok["risk_level"] == "safe"


def test_normalize_telegram_post():
    raw = {"source": "telegram", "url": "https://t.me/x/1", "country": "UZ",
           "raw_text": "📌 Python dasturchi kerak\nKompaniya: SoftBridge\nMaosh: 10-14 mln so'm\nToshkent, Django, SQL"}
    j = normalize(raw)
    assert j["title"] == "Python dasturchi kerak"
    assert j["company"] == "SoftBridge"
    assert j["city"] == "Tashkent" and j["currency"] == "UZS"
    assert "Python" in j["skills"] and "Django" in j["skills"]


def test_match_scoring_explains():
    job = {"title": "Backend Developer", "skills": ["Python", "Docker", "Kafka"], "salary_max": 18e6,
           "currency": "UZS", "risk_score": 0, "visa": None}
    s = score_job(job, ["Python", "Docker"], "dev", "10M so‘m", None, 0.5)
    assert s["have"] == ["Python", "Docker"] and s["missing"] == ["Kafka"]
    assert "role_fit" in s["reasons"] and "salary_ok" in s["reasons"]
    risky = score_job({**job, "risk_score": 80}, ["Python", "Docker"], "dev", None, None, 0.5)
    assert risky["match"] < s["match"]


def test_profile_parse():
    cv = """Aziz Karimov
    Tashkent University of Information Technologies, Bachelor
    3 years experience: Python, FastAPI, PostgreSQL, Docker
    Languages: Uzbek, Russian, English (IELTS 6.5), Korean TOPIK 3"""
    p = parse_cv(cv)
    assert p["name"] == "Aziz Karimov"
    assert p["experience_years"] == 3 and p["korean_level"] == "TOPIK 3"
    assert {"English", "Korean", "Russian", "Uzbek"} <= set(p["languages"])
    assert p["role_guess"] == "dev"


def test_interview_plan_all_languages():
    for lang in ("en", "uz", "ru", "ko"):
        qs = build_plan("Kakao", "dev", "full", lang, ["Python"], "Kakao launches new AI service")
        assert len(qs) == 11
        assert all("{" not in q["text"] for q in qs)
        assert qs[2]["category"] == "company" and "Kakao launches" in qs[2]["text"]
    assert follow_up("I did it.", "en")
    assert follow_up("I led a team of three to rebuild the payment queue and cut failures by 40% in two months. " * 2, "en") is None


def test_rubric_rewards_star_and_numbers():
    q = "Tell me about a project where you used Python."
    weak = score_answer(q, "I know Python well.", "en")
    strong = score_answer(q, "When our payment API failed under load, my task was to fix it. I rebuilt the queue in "
                             "Python with Kafka and added retries. As a result failures dropped by 40% in two weeks.", "en",
                          company="PayLink", brief_terms=["payments"])
    assert strong["total"] > weak["total"]
    assert weak["weakest"] in ("structure", "knowledge")


def test_judge_checks():
    good = {"jobs": [{"title": "A", "match": 80, "have": ["Python"], "skills": ["Python"], "country": "UZ", "risk_level": "safe"}]}
    assert judge_output("match_jobs", good, {"scope": {"mode": "single", "countries": ["UZ"]}})[0] == "PASS"
    invented = {"jobs": [{"title": "A", "match": 80, "have": ["Rust"], "skills": ["Python"], "country": "UZ", "risk_level": "safe"}]}
    assert judge_output("match_jobs", invented, {})[0] == "RETRY"
    wrong_scope = {"jobs": [{**good["jobs"][0], "country": "KR"}]}
    assert judge_output("match_jobs", wrong_scope, {"scope": {"mode": "single", "countries": ["UZ"]}})[0] == "RETRY"
    unsourced = {"found": True, "rows": [{"key": "now", "text": "x", "source": None}]}
    assert judge_output("company_brief", unsourced, {})[0] == "RETRY"
    assert judge_output("company_brief", {"found": False, "rows": []}, {})[0] == "PASS"
    assert judge_output("anything", {"error": "boom"}, {})[0] == "RETRY"


def test_roadmap_fits_hours():
    for days, hours in ((30, 5), (60, 10), (90, 20), (14, 3)):
        plan = build_roadmap("dev", days, hours, ["Python"], ["Kafka"], "uz")
        assert plan["total_hours"] <= plan["budget_hours"] * 1.1
        assert plan["gap"][0] == "Kafka"
        assert len(plan["blocks"]) == 3
        assert all("–" not in b["weeks"] or int(b["weeks"].split("–")[0]) <= int(b["weeks"].split("–")[1]) for b in plan["blocks"])


def test_prompt_templates_format():
    from agents.interviewer.main import PLAN_PROMPT
    assert '{"questions"' in PLAN_PROMPT.format(company="K", role="dev", lang="en", cats="intro")


def test_company_relevance():
    from portiq_common.text import mentions
    assert mentions("Kakao", "Kakao Corporation")
    assert mentions("Kakao Corp.", "Kakao launches AI assistant")
    assert not mentions("Bazaar Online", "Cafe Bazaar")
    assert not mentions("Bazaar Online", "Audi to invest $4.2 billion in Georgia factory")
    off = {"found": True, "company": "Bazaar Online",
           "rows": [{"key": "now", "text": "Audi to invest in Georgia", "source": {"title": "The American Bazaar", "url": "u"}}]}
    assert judge_output("company_brief", off, {"company": "Bazaar Online"})[0] == "RETRY"
