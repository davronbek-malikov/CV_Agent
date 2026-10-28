"""TeachHelp provider, with the HTTP layer mocked."""

import json

import httpx
import pytest

from portiq_common import llm
from portiq_common.settings import get_settings

BASE = "https://demo.trycloudflare.com/v1"


@pytest.fixture
def teachhelp(monkeypatch):
    for k in ("ANTHROPIC_API_KEY", "GEMINI_API_KEY", "OLLAMA_URL", "LLM_MODEL", "LLM_JUDGE_MODEL"):
        monkeypatch.setenv(k, "")
    monkeypatch.setenv("LLM_PROVIDER", "auto")
    monkeypatch.setenv("TEACHHELP_API_KEY", "sk-th-test")
    monkeypatch.setenv("TEACHHELP_BASE_URL", BASE + "/")
    get_settings.cache_clear()
    seen: list[httpx.Request] = []
    state = {"status": 200, "content": '{"name": "Aziz", "skills": ["Python"]}', "finish": "stop", "pad": ""}

    def handler(request: httpx.Request) -> httpx.Response:
        seen.append(request)
        if state["status"] != 200:
            return httpx.Response(state["status"], json={"error": "x"})
        body = json.dumps({"choices": [{"message": {"content": state["content"]}, "finish_reason": state["finish"]}]})
        # TeachHelp keeps the tunnel alive by sending whitespace before the JSON body.
        return httpx.Response(200, content=(state["pad"] + body).encode(), headers={"content-type": "application/json"})

    real = httpx.AsyncClient
    monkeypatch.setattr(llm.httpx, "AsyncClient", lambda **kw: real(transport=httpx.MockTransport(handler), **kw))
    yield seen, state
    get_settings.cache_clear()


async def test_auto_picks_teachhelp_and_sends_openai_request(teachhelp):
    seen, _ = teachhelp
    assert llm.provider() == "teachhelp"
    data, model = await llm.complete_json("Extract a CV.", "Aziz, Python", lambda: {"fallback": True})
    assert data == {"name": "Aziz", "skills": ["Python"]} and model == "qwen3.5-4b"

    req = seen[0]
    assert str(req.url) == f"{BASE}/chat/completions"
    assert req.headers["authorization"] == "Bearer sk-th-test"
    body = json.loads(req.content)
    assert body["model"] == "qwen3.5-4b"
    assert body["messages"][0]["role"] == "system" and body["messages"][1] == {"role": "user", "content": "Aziz, Python"}
    assert body["max_tokens"] == 1024 and body["temperature"] == 0
    assert body["response_format"] == {"type": "json_object"}


async def test_judge_model_override(teachhelp, monkeypatch):
    seen, _ = teachhelp
    monkeypatch.setenv("LLM_JUDGE_MODEL", "sft-lora-dpo-v2")
    get_settings.cache_clear()
    _, model = await llm.complete_json("Score.", "answer", lambda: {}, judge=True)
    assert model == "sft-lora-dpo-v2" and json.loads(seen[0].content)["model"] == "sft-lora-dpo-v2"


async def test_long_input_is_trimmed_to_fit_context(teachhelp):
    seen, _ = teachhelp
    cv = "Python developer with FastAPI and Docker experience. " * 2000  # ~100k chars
    await llm.complete_json("Extract a CV.", cv, lambda: {})
    body = json.loads(seen[0].content)
    prompt_tokens = sum(llm.estimate_tokens(m["content"]) for m in body["messages"])
    assert prompt_tokens + body["max_tokens"] <= llm.TEACHHELP_CONTEXT
    assert len(body["messages"][1]["content"]) < len(cv)


def test_token_estimate_counts_non_latin_text_as_denser():
    assert llm.estimate_tokens("한국어 이력서" * 100) > llm.estimate_tokens("resume text" * 100)
    assert llm.estimate_tokens(llm.fit_tokens("абв " * 5000, 500)) <= 500


@pytest.mark.parametrize("status", [401, 403, 429, 503])
async def test_errors_fall_back(teachhelp, status):
    _, state = teachhelp
    state["status"] = status
    data, model = await llm.complete_json("x", "y", lambda: {"fallback": True})
    assert data == {"fallback": True} and model == "fallback"


async def test_per_call_budget_and_cap(teachhelp):
    seen, _ = teachhelp
    await llm.complete_json("x", "y", lambda: {}, max_tokens=256)
    await llm.complete_json("x", "y", lambda: {}, max_tokens=4000)
    assert [json.loads(r.content)["max_tokens"] for r in seen] == [256, llm.TEACHHELP_MAX_ANSWER]


async def test_leading_whitespace_body_parses(teachhelp):
    _, state = teachhelp
    state["pad"] = " \n" * 500
    data, model = await llm.complete_json("x", "y", lambda: {"fallback": True})
    assert data == {"name": "Aziz", "skills": ["Python"]} and model == "qwen3.5-4b"


async def test_cut_off_answer_is_logged_and_falls_back(teachhelp, caplog):
    _, state = teachhelp
    state.update(finish="length", content='{"name": "Az')
    data, model = await llm.complete_json("x", "y", lambda: {"fallback": True}, max_tokens=64)
    assert data == {"fallback": True} and model == "fallback"
    assert "hit max_tokens (64)" in caplog.text
