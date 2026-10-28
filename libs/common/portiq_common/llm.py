"""Provider-agnostic LLM client.

Every call passes a `fallback` that returns a usable answer without any model.
With no key configured the provider is "mock" and the fallback is used, so the
whole system runs offline. Add a key to .env and the same calls use a real model.
"""

import json
import logging
import re
from collections.abc import Callable
from typing import Any

import httpx

from .settings import get_settings

log = logging.getLogger("llm")

DEFAULT_MODELS = {
    "anthropic": ("claude-sonnet-5-5", "claude-haiku-5-5"),
    "gemini": ("gemini-2.5-flash", "gemini-2.5-flash-lite"),
    "ollama": ("qwen2.5:3b", "qwen2.5:3b"),
    # Our own model served by the TeachHelp API (OpenAI-compatible, runs on a CPU).
    "teachhelp": ("qwen3.5-4b", "qwen3.5-4b"),
}

# TeachHelp: 4096-token context shared by prompt and answer; ~8-10 tokens/s on CPU.
TEACHHELP_CONTEXT = 4096
TEACHHELP_MAX_ANSWER = 1536
TEACHHELP_TIMEOUT = 300
TEACHHELP_ERRORS = {
    401: "key revoked or expired",
    403: "key is limited to another model",
    429: "rate limit (20/min, 500/day per user)",
    503: "TeachHelp server is off",
}


def provider() -> str:
    s = get_settings()
    if s.llm_provider != "auto":
        return s.llm_provider
    if s.anthropic_api_key:
        return "anthropic"
    if s.gemini_api_key:
        return "gemini"
    if s.teachhelp_api_key and s.teachhelp_base_url:
        return "teachhelp"
    if s.ollama_url:
        return "ollama"
    return "mock"


def _model(judge: bool) -> str:
    s = get_settings()
    p = provider()
    if p == "mock":
        return "mock"
    main, judge_default = DEFAULT_MODELS[p]
    if judge:
        return s.llm_judge_model or judge_default
    return s.llm_model or main


def _extract_json(text: str) -> Any:
    m = re.search(r"\{.*\}|\[.*\]", text, re.S)
    if not m:
        raise ValueError("no JSON in model output")
    return json.loads(m.group(0))


def estimate_tokens(text: str) -> int:
    """Rough count: ~4 chars per token for Latin text, ~2 for Cyrillic/Hangul."""
    non_ascii = sum(1 for ch in text if ord(ch) > 127)
    return (len(text) - non_ascii) // 4 + non_ascii // 2 + 1


def fit_tokens(text: str, max_tokens: int) -> str:
    """Cut text so its estimated size stays within max_tokens."""
    if estimate_tokens(text) <= max_tokens:
        return text
    lo, hi = 0, len(text)
    while lo < hi:
        mid = (lo + hi + 1) // 2
        if estimate_tokens(text[:mid]) <= max_tokens:
            lo = mid
        else:
            hi = mid - 1
    return text[:lo]


async def _teachhelp(system: str, user: str, model: str) -> str:
    s = get_settings()
    # Prompt + answer must fit the context: trim the user text (e.g. a long CV), never the instructions.
    budget = TEACHHELP_CONTEXT - TEACHHELP_MAX_ANSWER - estimate_tokens(system) - 64
    user = fit_tokens(user, max(budget, 256))
    async with httpx.AsyncClient(timeout=TEACHHELP_TIMEOUT) as client:
        r = await client.post(
            f"{s.teachhelp_base_url.rstrip('/')}/chat/completions",
            headers={"Authorization": f"Bearer {s.teachhelp_api_key}"},
            json={"model": model,
                  "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}],
                  "max_tokens": TEACHHELP_MAX_ANSWER, "temperature": 0,
                  "response_format": {"type": "json_object"}},
        )
    if r.status_code in TEACHHELP_ERRORS:
        raise RuntimeError(f"teachhelp {r.status_code}: {TEACHHELP_ERRORS[r.status_code]}")
    r.raise_for_status()
    return r.json()["choices"][0]["message"]["content"]


async def _call(system: str, user: str, model: str) -> str:
    s = get_settings()
    p = provider()
    if p == "teachhelp":
        return await _teachhelp(system, user, model)
    async with httpx.AsyncClient(timeout=60) as client:
        if p == "anthropic":
            r = await client.post(
                "https://api.anthropic.com/v1/messages",
                headers={"x-api-key": s.anthropic_api_key, "anthropic-version": "2023-06-01"},
                json={"model": model, "max_tokens": 2000, "system": system,
                      "messages": [{"role": "user", "content": user}]},
            )
            r.raise_for_status()
            return "".join(b.get("text", "") for b in r.json()["content"])
        if p == "gemini":
            r = await client.post(
                f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent",
                params={"key": s.gemini_api_key},
                json={"systemInstruction": {"parts": [{"text": system}]},
                      "contents": [{"role": "user", "parts": [{"text": user}]}],
                      "generationConfig": {"responseMimeType": "application/json"}},
            )
            r.raise_for_status()
            return r.json()["candidates"][0]["content"]["parts"][0]["text"]
        if p == "ollama":
            r = await client.post(
                f"{s.ollama_url.rstrip('/')}/api/chat",
                json={"model": model, "stream": False, "format": "json",
                      "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}]},
            )
            r.raise_for_status()
            return r.json()["message"]["content"]
    raise RuntimeError(f"unknown provider {p}")


async def complete_json(system: str, user: str, fallback: Callable[[], Any], judge: bool = False) -> tuple[Any, str]:
    """Return (data, model_used). Falls back on mock mode or any provider error."""
    model = _model(judge)
    if model == "mock":
        return fallback(), "mock"
    try:
        text = await _call(system + "\nReply with JSON only.", user, model)
        return _extract_json(text), model
    except Exception as e:
        log.warning("llm call failed (%s), using fallback", e)
        return fallback(), "fallback"
