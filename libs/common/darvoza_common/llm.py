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
}


def provider() -> str:
    s = get_settings()
    if s.llm_provider != "auto":
        return s.llm_provider
    if s.anthropic_api_key:
        return "anthropic"
    if s.gemini_api_key:
        return "gemini"
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


async def _call(system: str, user: str, model: str) -> str:
    s = get_settings()
    p = provider()
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
