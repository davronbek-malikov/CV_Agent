# Architecture

## Why both Kafka and A2A

| Need | Transport | Example |
|---|---|---|
| Slow work, fan-out, retries, replay, audit trail | **Kafka** | job pipeline, company research, Judge retry loop |
| Quick request-reply between agents | **A2A** (JSON-RPC 2.0 + Agent Card) | orchestrator → judge `score_answer`, match → profile `get_profile` |

Every agent serves `/.well-known/agent.json` and `POST /a2a`. `GET /api/agents` on the gateway lists all cards.

## Message envelope

Every Kafka message is an `Envelope` (`libs/common/portiq_common/envelope.py`):
`message_id, trace_id, session_id, type, source_agent, target_agent, task, task_id, attempt, lang, payload`.
`trace_id` follows one user request across every agent; `task_id` ties a Judge verdict back to the
orchestrator's pending task; `attempt` counts Judge retries.

## Topics

| Topic | Producer → consumer |
|---|---|
| `user.requests` | gateway → orchestrator |
| `agent.tasks` | orchestrator / judge (retry) → worker agents (filtered by `target_agent`) |
| `agent.results` | workers → judge |
| `judge.verdicts` | judge → orchestrator |
| `session.replies` | orchestrator → gateway → browser (SSE) |
| `agent.events` | everyone → gateway → Activity panel |
| `jobs.raw` → `jobs.clean` → `jobs.ready` | sources → normalizer → scam → indexer |
| `agent.dlq` | any consumer after 3 failed handler attempts |

Keys are `session_id` (chat) or the job hash (pipeline), so ordering holds per session and per job.

## The Judge loop

```
worker ─► agent.results ─► judge.check(task, output, input)
                              ├─ hard issues & attempt ≤ MAX_RETRIES ─► agent.tasks (attempt+1, judge_feedback)
                              ├─ hard issues & no retries left       ─► FAIL  ─► judge.verdicts
                              └─ no hard issues                      ─► PASS (+ warnings) ─► judge.verdicts
```

Checks (`agents/judge/checks.py`): match reasons must exist in the job text, jobs must be inside the
chosen countries, a high-risk job may not rank first; every brief line needs a source URL and must be
about the named company; interview plans need real, filled questions; roadmaps must fit the weekly hours.
Every verdict is stored in `verdicts` for evals.

## Orchestrator graph (LangGraph)

```
apply_input ─► ensure_lang ─► interview_turn ─► ensure_mode ─► fill_slots ─► dispatch
```

Any node can stop the turn with a reply (e.g. the next question). Session state lives in Redis.
Slots are asked one at a time with chips; the language is asked first, then mode, then the country
scope (one country / several / all / remote). Slots already known (e.g. role from the CV) are skipped.

## LLM use

`portiq_common/llm.py` picks Anthropic, Gemini, TeachHelp (our own model, OpenAI-compatible) or Ollama from the keys in `.env`, else `mock`. Every
call passes a deterministic fallback, so the system works offline and degrades gracefully when a
provider fails. The Judge uses a separate model (`LLM_JUDGE_MODEL`) to avoid grading its own work.

## Known limits (Phase 1 backend)

- Hashing embeddings are not cross-lingual; a multilingual embedding model is the next step.
- Name matching keeps company research on-topic, but cannot tell a person named "Uzum" from the company;
  an LLM relevance check fixes that once a key is set.
- Sessions are anonymous (no login yet); CVs are stored in Postgres unencrypted.
