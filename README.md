# Portiq — multi-agent job hub

> **Your door to the right job.** Jobs from Uzbekistan, Korea and worldwide (incl. Telegram channels),
> skill-gap roadmaps, and company-specific mock interviews — in Uzbek, Russian, Korean and English.

**Live design preview:** https://portiq-gamma.vercel.app · **Full plan:** [PLAN.md](PLAN.md) · **Architecture:** [docs/architecture.md](docs/architecture.md)

Built as a real multi-agent system: an **orchestrator** (LangGraph) plans the work, **Kafka** carries
tasks and the job pipeline, agents call each other over **A2A** (Agent Cards + JSON-RPC), and a **Judge
agent** checks every output — sending weak work back for a retry — before the user sees it.

```
 Web app / curl ──► Gateway (FastAPI, SSE) ──► user.requests ──► Orchestrator (LangGraph)
                                                                     │  agent.tasks
                      ┌──────────────┬──────────────┬───────────────┼──────────────┐
                    match     company_research   interviewer      roadmap      (A2A: profile, judge)
                      └──────────────┴──────── agent.results ───────┘
                                              ▼
                                       Judge ── RETRY ──► agent.tasks
                                              │ PASS / FAIL
                                       judge.verdicts ──► Orchestrator ──► session.replies ──► SSE

 sources (seed, Remotive, Saramin*, hh.uz*, Telegram*) ─► jobs.raw ─► normalizer ─► jobs.clean
                                                         ─► scam ─► jobs.ready ─► indexer ─► Postgres + pgvector
                                                                                         (* = needs a key)
```

## Run it locally

Needs Docker Desktop, Python 3.12, Node 20+ and pnpm.

```bash
make up                      # Kafka, Postgres+pgvector, Redis, Jaeger, Redpanda Console, gateway + 11 agents
python -m venv .venv && .venv/Scripts/pip install -r requirements-dev.txt
make e2e                     # end-to-end conversation through every agent
cd apps/web && pnpm install && pnpm dev   # http://localhost:3000/app
```

| URL | What |
|---|---|
| http://localhost:3000/app | Chat app with live agent activity |
| http://localhost:8000/docs | Gateway API |
| http://localhost:8080 | Redpanda Console — watch Kafka topics |
| http://localhost:16686 | Jaeger — traces across agents |

No keys needed: without an LLM key the agents use deterministic fallbacks (rules, question bank,
rubric) and jobs come from sample data + Remotive. Copy `.env.example` to `.env` to add keys —
`ANTHROPIC_API_KEY` or `GEMINI_API_KEY` (or `OLLAMA_URL`) switches every agent to a real model;
`SARAMIN_API_KEY`, `HH_ACCESS_TOKEN`, `TG_API_ID/TG_API_HASH/TG_CHANNELS` switch on more job sources.

## Agents

| Agent | Talks via | Does |
|---|---|---|
| orchestrator | Kafka + A2A | language → mode → country → only-missing questions → plan → route; LangGraph state graph |
| profile | A2A | CV (PDF/DOCX/TXT) → skills, education, languages, TOPIK level |
| match | Kafka | pgvector search in the chosen countries + explainable match % (have / missing / salary / visa) |
| company_research | Kafka | Wikipedia + Google News RSS → Past / Now / Next brief, every line sourced |
| interviewer | Kafka + A2A | 11 rounds (intro … stress … salary … reverse) in 4 languages, follow-ups |
| roadmap | Kafka | gaps → 30/60/90-day plan that fits weekly hours, free official resources |
| judge | Kafka + A2A | quality checks with RETRY loop; answer rubric (knowledge, STAR structure, clarity, fit) |
| sources | Kafka | connectors on a schedule |
| normalizer | Kafka | one schema, salary parsing (so‘m / ₩ / $), language, dedup, Telegram post parsing |
| scam | Kafka | multilingual risk rules: upfront fees, visa guarantees, passport requests, crypto |
| indexer | Kafka | upsert into Postgres with embeddings |

## Quality

```bash
make test     # 20 unit tests (orchestrator conversations, judge, scam, parsing, roadmap…)
make e2e      # live: CV → jobs (uz) → Kakao interview → report → roadmap
make evals    # scam precision/recall, rubric pairwise accuracy, live Judge pass rate
```

The eval datasets in `evals/datasets` are small and hand-written; replace them with real labeled
posts and human-scored answers before trusting the numbers.
