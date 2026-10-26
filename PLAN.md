# CV_Agent — Full Project Plan (A to Z)

> **One hub to find your job, build your skills, and get ready for the interview.**
> Jobs from Uzbekistan, Korea and the world — in Uzbek, Russian, Korean and English.

**Product name:** Darvoza ("door/gate" in Uzbek). **Live preview:** https://darvoza-eight.vercel.app

## Progress (2026-10-26)

| Phase | Status | Notes |
|---|---|---|
| UI preview | ✅ | Landing, 4 languages, demo, comparison table — on Vercel |
| 0 Foundations | ✅ | docker-compose (Kafka KRaft, Postgres+pgvector, Redis, Jaeger, Redpanda Console), Makefile, CI |
| 1 Multi-agent core | ✅ | Gateway + SSE, LangGraph orchestrator, A2A cards/JSON-RPC, Judge RETRY loop, DLQ, events, tracing |
| 2 UI + real chat | ✅ | `/app`: language → mode → country flow, chips, rich blocks, live Agent Activity panel |
| 3 Profile | ✅ | CV upload (PDF/DOCX/TXT) → skills, languages, TOPIK; skips known questions |
| 4 Job Hub | 🟡 | Pipeline done; live sources: Remotive + sample. Saramin / hh.uz / Telegram coded, need keys |
| 5 Match + Scam | ✅ | Explainable match %, multilingual scam rules |
| 6 Interview Prep | ✅ | Wikipedia + news brief with sources, 11 rounds × 4 languages, follow-ups, rubric, report |
| 7 Roadmap | ✅ | Gaps → plan that fits weekly hours, free resources |
| 8 Korea Path | ❌ | Next |
| 9 Telegram bot | ❌ | Needs bot token |
| 10 Global | 🟡 | Remotive live; Adzuna/Jooble need keys |
| 11 Evals + hardening | 🟡 | 20 unit tests, e2e, evals; login/rate limits/encryption not yet |
| 12 Cloud backend | ❌ | Needs accounts |
| 13–14 Voice, Avatar | ❌ | Later |
| 15 Portfolio | 🟡 | README + architecture doc done; video later |

---

## Table of Contents

1. [Vision](#1-vision)
2. [Users](#2-users)
3. [Core Features](#3-core-features)
4. [Our Strengths vs Competitors](#4-our-strengths-vs-competitors)
5. [System Architecture](#5-system-architecture)
6. [UI Design System](#6-ui-design-system)
7. [Environments: Local → Vercel](#7-environments-local--vercel)
8. [Phase Overview](#8-phase-overview)
9. [Phase 0 — Foundations](#phase-0--foundations)
10. [Phase 1 — Multi-Agent Core](#phase-1--multi-agent-core)
11. [Phase 2 — UI Shell + Chat](#phase-2--ui-shell--chat)
12. [Phase 3 — Profile Agent](#phase-3--profile-agent)
13. [Phase 4 — Job Hub Ingestion](#phase-4--job-hub-ingestion)
14. [Phase 5 — Smart Match + Scam Check](#phase-5--smart-match--scam-check)
15. [Phase 6 — Interview Prep](#phase-6--interview-prep)
16. [Phase 7 — Career Roadmap](#phase-7--career-roadmap)
17. [Phase 8 — Korea Path](#phase-8--korea-path)
18. [Phase 9 — Telegram Bot](#phase-9--telegram-bot)
19. [Phase 10 — Global Sources](#phase-10--global-sources)
20. [Phase 11 — Evals, Observability, Hardening](#phase-11--evals-observability-hardening)
21. [Phase 12 — Cloud Deploy (Vercel)](#phase-12--cloud-deploy-vercel)
22. [Phase 13 — Voice Interview](#phase-13--voice-interview)
23. [Phase 14 — AI Avatar Interviewer](#phase-14--ai-avatar-interviewer)
24. [Phase 15 — Portfolio Packaging](#phase-15--portfolio-packaging)
25. [Legal, Privacy, Ethics](#25-legal-privacy-ethics)
26. [Risks and Mitigations](#26-risks-and-mitigations)
27. [Glossary](#27-glossary)

---

## 1. Vision

Job seekers in Uzbekistan and Korea search in many places: hh.uz, OLX, dozens of Telegram
channels, Saramin, Wanted, LinkedIn. The data is split, often in a language they do not read
well, and full of scams. Interview practice tools are generic and US-focused.

**CV_Agent** is a multi-agent AI hub that:

1. **Collects** jobs from Uzbekistan, Korea and global sources (including Telegram).
2. **Matches** them to the user's CV, skills and wishes — and explains why.
3. **Builds a roadmap** to close the skill gap for a target job.
4. **Researches the company** and runs a full, realistic mock interview.
5. **Checks every job and every AI answer** with a Judge agent before the user sees it.

**Product promise:** *Find → Learn → Practice → Get hired.*

**Portfolio promise:** a real, working showcase of **multi-agent orchestration, A2A protocol,
Kafka event streaming, LLM-as-Judge, tracing and evals**.

---

## 2. Users

| Persona | Who | Main need |
|---|---|---|
| **Aziz** | Uzbek CS student in Tashkent | IT job in Tashkent or remote; interview practice |
| **Malika** | Uzbek student at a Korean university (D-2 → D-10) | Korean company job, E-7 visa, Korean interview |
| **Jasur** | Worker preparing for EPS (E-9) to Korea | Legal path, EPS-TOPIK prep, scam safety |
| **Min-ji** | Korean graduate | Company-specific interview practice |
| **Global user** | Anyone | Remote jobs, English interview practice |

**First target (MVP):** Uzbek students and young tech workers in Uzbekistan and Korea.

---

## 3. Core Features

| # | Feature | What it does | Standalone? |
|---|---|---|---|
| 1 | **Job Hub** | One search over UZ + KR + global sites + Telegram channels | ✅ |
| 2 | **Smart Match** | CV + wishes → ranked jobs, match %, reasons, missing skills | ✅ |
| 3 | **Career Roadmap** | Missing skills → 30/60/90-day plan with progress tracking | ✅ |
| 4 | **Interview Prep** | Company research → full A-to-Z interview → Judge score | ✅ |
| 5 | **Korea Path** | E-9 / E-7 / D-10 guides, EPS-TOPIK prep, document checklist | ✅ |
| 6 | **Scam Check** | Risk score for every job (fees, fake companies, "fast abroad") | Built-in |
| 7 | **Telegram Bot** | Full app inside Telegram | ✅ |
| 8 | **Voice Interview** *(later)* | Speak your answers, get delivery feedback | ✅ |
| 9 | **AI Avatar** *(later)* | Live interviewer with face, voice, personality | ✅ |

**Every feature works alone.** A user who only wants interview practice never touches job search.

### 3.1 Interview coverage (A to Z)

1. Self-introduction (1-minute 자기소개 / o'zini tanishtirish)
2. Motivation — why this company, why this role
3. Company knowledge — products, strategy, news, values
4. Technical / academic knowledge — from the job description
5. Behavioral (STAR) questions
6. CV verification — gaps, claims, projects deep dive
7. Stress test (압박면접) — pressure, interruptions, hard follow-ups
8. Culture fit (인성)
9. Background check — visa, relocation, availability
10. Salary expectation and negotiation
11. Reverse questions — what the user should ask the company

### 3.2 Languages

| Language | UI | Chat | Interview | Job posts |
|---|---|---|---|---|
| Uzbek (Latin) | ✅ | ✅ | ✅ | translated |
| Russian | ✅ | ✅ | ✅ | many UZ posts are in Russian |
| Korean | ✅ | ✅ | ✅ (존댓말) | native |
| English | ✅ | ✅ | ✅ | global |

The user **chooses the language first** (see 3.3). After that, the whole app — UI, chat,
questions, job summaries, interview — uses that language. A switch is always in the header
to change it later.

### 3.3 First-run flow: Language → Country scope

Before anything else, the agent asks two things, in this order:

**Step 1 — Choose language** (first screen, before chat starts)

```
Choose your language
[🇺🇿 O'zbekcha]  [🇷🇺 Русский]  [🇰🇷 한국어]  [🇬🇧 English]
```

- Saved to the profile + cookie; never asked again.
- If the user types in another language later, the agent asks once: "Switch to Русский?" [Yes] [No].

**Step 2 — Choose where to search** (asked in the chosen language)

```
🤖 Where do you want to find a job?
[🇺🇿 Only Uzbekistan]  [🇰🇷 Only Korea]  [🌍 Other country…]
[✅ Pick several]      [🌐 All countries]  [💻 Remote only]
```

| Option | What happens |
|---|---|
| **Only one country** | Search, match, salary and scam rules use only that country |
| **Other country…** | Searchable country list (from Phase 10 global sources) |
| **Pick several** | Multi-select chips, e.g. Uzbekistan + Korea |
| **All countries** | No country filter; results grouped by country |
| **Remote only** | Only remote jobs, any country |

- Shown as `search_scope` in the session: `{ "mode": "single|multi|all|remote", "countries": ["UZ","KR"] }`.
- Next questions adapt to the scope:
  - Korea in scope → ask visa + Korean level.
  - Uzbekistan only → skip visa; salary chips in so'm.
  - All / multi → salary in the user's chosen currency.
- The scope is always visible as a chip above results (`🇺🇿 + 🇰🇷 ✎`) and can be changed in one tap.
- **Interview Prep and Roadmap skip Step 2** if the user came only for them — the country comes from the company or target job.

---

## 4. Our Strengths vs Competitors

| Competitor | What they do | Our edge |
|---|---|---|
| **hh.uz** | Biggest Uzbek job board | AI match, Telegram jobs, interview prep, Korea path |
| **OLX.uz / Ishkop / Myjob** | Boards for listings | Search across all + scam check |
| **Telegram job channels** | Fast, messy, scams | Sorted, searchable, verified, in one place |
| **IT Market (IT Park)** | IT jobs listing | AI coaching on top |
| **Saramin / JobKorea** | Korean jobs, AI interview (KR only) | UZ/RU support, company research, UZ → KR path |
| **Wanted** | KR startups, AI coaching | Multi-country, multi-language |
| **KLiK / Komate** | Foreigners in Korea | Full prep loop, not only listings |
| **Final Round AI / Huru / Yoodli** | Global interview practice | Local companies, local languages, real jobs |
| **LinkedIn** | Global network | Telegram-first, built for UZ market |

### Four unique strengths

1. **Telegram jobs become searchable** — no one does this with AI.
2. **Uzbekistan → Korea corridor** — ~50,000 Uzbeks have worked in Korea on E-9 since 2007; no prep tool exists.
3. **Four languages** — Uzbek, Russian, Korean, English.
4. **Judge-verified** — every job (scam check) and every AI output (quality check) is reviewed.

---

## 5. System Architecture

### 5.1 Big picture

```
                 ┌────────────────────┐      ┌──────────────────┐
                 │  Web App (Next.js) │      │  Telegram Bot    │
                 └─────────┬──────────┘      └────────┬─────────┘
                           │  HTTPS + WebSocket/SSE   │
                           ▼                          ▼
                    ┌──────────────────────────────────────┐
                    │       Gateway (FastAPI)               │
                    │  auth · sessions · stream to client   │
                    └──────────────────┬───────────────────┘
                                       │
                                       ▼
                    ┌──────────────────────────────────────┐
                    │        Orchestrator (LangGraph)       │
                    │  intent · language · slots · plan     │
                    └───────┬───────────────────┬──────────┘
                     A2A (sync)            Kafka (async)
                            │                   │
       ┌────────────────────┼───────────────────┼─────────────────────┐
       ▼                    ▼                   ▼                     ▼
  Profile Agent      Smart Match Agent   Company Research      Interviewer Agent
                     Roadmap Agent       Korea Path Agent
                                                │
                                                ▼
                                    ┌────────────────────┐
                                    │    Judge Agent     │
                                    │ quality + scoring  │
                                    └────────────────────┘

  ── Ingestion pipeline (always running) ─────────────────────────────────
  UZ Source ┐
  KR Source ├─► jobs.raw ─► Normalizer ─► jobs.clean ─► Scam Agent ─► jobs.ready ─► DB + vectors
  Global    │
  Telegram ─┘
```

### 5.2 Agents

| Agent | Role | Talks via | Tools |
|---|---|---|---|
| **Orchestrator** | Understand request, ask missing info, plan steps, route tasks, merge results | A2A + Kafka | LangGraph state, session memory |
| **Profile Agent** | Parse CV, store skills/goals/visa/salary, answer "what do we know?" | A2A | PDF/DOCX parser, LLM extraction |
| **UZ Source Agent** | Pull jobs from hh.uz API, IT Market, public sources | Kafka out | HTTP clients |
| **KR Source Agent** | Pull jobs from Saramin API, Work24 | Kafka out | HTTP clients |
| **Global Source Agent** | Adzuna, Jooble, Remotive | Kafka out | HTTP clients |
| **Telegram Source Agent** | Read public job channels | Kafka out | Telethon (MTProto) |
| **Normalizer Agent** | One schema, dedup, language detect, translate, embed | Kafka in/out | LLM, embeddings |
| **Scam Agent** | Risk score + reasons for each job | Kafka in/out | Rules + LLM |
| **Smart Match Agent** | Rank jobs for a profile, explain, list gaps | A2A + Kafka | pgvector, LLM |
| **Roadmap Agent** | Gap → weekly plan, track progress, re-plan | Kafka | LLM, course catalog |
| **Company Research Agent** | Company brief with sources | Kafka | Web search, DART, news, site fetch |
| **Interviewer Agent** | Run interview, follow-ups, personas | A2A (low latency) | LLM, question bank |
| **Korea Path Agent** | Visa guidance, EPS steps, checklists | Kafka | Curated knowledge base (RAG) |
| **Judge Agent** | (A) check agent outputs (B) score user answers | Kafka | Rubrics, separate LLM |

### 5.3 Why both A2A and Kafka

| Need | Use | Why |
|---|---|---|
| Fast, request-reply (interview turn, profile lookup) | **A2A** (JSON-RPC over HTTP, Agent Cards) | Low latency, standard discovery |
| Slow, fan-out, retry, replay (research, ingestion, judging) | **Kafka** | Durable, scalable, many producers/consumers, audit trail |

### 5.4 Kafka topics

| Topic | Key | Producer → Consumer | Notes |
|---|---|---|---|
| `user.requests` | session_id | Gateway → Orchestrator | chat messages, button clicks |
| `agent.tasks` | session_id | Orchestrator → workers | `target_agent` field routes |
| `agent.results` | session_id | Workers → Judge | raw outputs |
| `judge.verdicts` | session_id | Judge → Orchestrator | PASS / RETRY / FAIL |
| `agent.events` | session_id | All → Gateway | live Activity panel |
| `jobs.raw` | source_id | Source agents → Normalizer | as fetched |
| `jobs.clean` | job_hash | Normalizer → Scam Agent | unified schema |
| `jobs.ready` | job_hash | Scam Agent → DB writer | with risk score |
| `agent.dlq` | any | Any → ops | failed after max retries |

### 5.5 Message envelope (every message)

```json
{
  "message_id": "uuid",
  "trace_id": "uuid",
  "session_id": "uuid",
  "user_id": "uuid | null",
  "type": "task | result | verdict | event",
  "source_agent": "orchestrator",
  "target_agent": "company_research",
  "attempt": 1,
  "lang": "uz | ru | ko | en",
  "created_at": "ISO-8601",
  "payload": { }
}
```

Schemas live in `libs/common/schemas/` (Pydantic) and are versioned (`schema_version`).

### 5.6 Judge loop

```
Worker result ──► Judge
                   │
         ┌─────────┼──────────┐
       PASS      RETRY       FAIL
         │    (reason, ≤2x)   │
         ▼         │          ▼
   Orchestrator    └─► Worker  Orchestrator → polite fallback to user
   → user               fixes
```

- Judge uses a **different model or prompt** than the generator.
- Every verdict is stored → used later for evals and dashboards.

### 5.7 Data model (Postgres + pgvector)

| Table | Key columns |
|---|---|
| `users` | id, telegram_id, email, lang, created_at |
| `profiles` | user_id, cv_text, skills[], education, experience, wishes (json), visa, korean_level, salary_min |
| `jobs` | id, hash, source, url, title, company, location, country, salary_min/max, currency, lang, description, posted_at, risk_score, risk_reasons, embedding |
| `companies` | id, name, country, site, brief (json), sources[], updated_at |
| `matches` | user_id, job_id, score, reasons, gaps |
| `roadmaps` | id, user_id, target, weeks (json), progress |
| `interviews` | id, user_id, company_id, job_id, persona, lang, status |
| `interview_turns` | interview_id, q, a, scores (json), feedback, model_answer |
| `verdicts` | trace_id, agent, verdict, reason, attempt |
| `sessions` | id, user_id, lang, search_scope (json), slots (json), state |

### 5.8 Tech stack

| Layer | Choice |
|---|---|
| Frontend | Next.js (App Router), TypeScript, Tailwind CSS, shadcn/ui, Framer Motion, next-intl |
| Gateway | Python, FastAPI, WebSocket / SSE |
| Agents | Python, FastAPI per agent, LangGraph (orchestrator), Pydantic |
| Messaging | Apache Kafka (KRaft mode) locally; managed Kafka in cloud |
| A2A | A2A protocol (Agent Cards at `/.well-known/agent.json`, JSON-RPC) |
| Database | Postgres + pgvector (Supabase in cloud) |
| Cache | Redis (sessions, rate limits) |
| LLM | Provider with tool use; Judge on a different model |
| Embeddings | Multilingual embedding model (must handle uz/ru/ko/en) |
| Tracing | OpenTelemetry + Langfuse |
| Kafka UI | Redpanda Console (or Kafka UI) |
| Telegram | Telethon (read channels), aiogram (bot) |
| Infra | Docker, docker-compose; GitHub Actions CI |

### 5.9 Folder layout

```
CV_Agent/
├── apps/
│   └── web/                     # Next.js app
├── services/
│   ├── gateway/                 # FastAPI + WebSocket
│   └── telegram_bot/            # aiogram bot
├── agents/
│   ├── orchestrator/
│   ├── profile/
│   ├── sources/
│   │   ├── uz/
│   │   ├── kr/
│   │   ├── global/
│   │   └── telegram/
│   ├── normalizer/
│   ├── scam/
│   ├── match/
│   ├── roadmap/
│   ├── company_research/
│   ├── interviewer/
│   ├── korea_path/
│   └── judge/
├── libs/
│   └── common/                  # schemas, kafka client, a2a helpers, llm client, tracing
├── infra/
│   ├── docker-compose.yml
│   ├── kafka/topics.sh
│   └── db/migrations/
├── evals/
│   ├── datasets/
│   └── run_evals.py
├── docs/
│   ├── architecture.md
│   └── diagrams/
├── .env.example
├── Makefile
└── PLAN.md
```

---

## 6. UI Design System

### 6.1 Feel

- **Clean white, calm, confident.** Not "AI-made" — no purple gradients everywhere, no glow spam.
- **Chat-first, buttons always near.**
- **Show the agents working** — the Activity panel is a signature element.
- **Mobile-first** — most Uzbek users are on phones.

### 6.2 Colors (white default)

| Token | Hex | Use |
|---|---|---|
| `--bg` | `#FFFFFF` | page background (default) |
| `--surface` | `#F7F8FA` | cards, chat bubbles (agent) |
| `--border` | `#E6E8EC` | lines, card borders |
| `--text` | `#0F172A` | main text |
| `--text-muted` | `#64748B` | secondary text |
| `--primary` | `#2563EB` | buttons, links, user bubbles |
| `--primary-soft` | `#EFF4FF` | selected chips, hover |
| `--accent` | `#10B981` | success, match %, PASS |
| `--warning` | `#F59E0B` | medium risk, RETRY |
| `--danger` | `#EF4444` | high risk, FAIL |
| `--uz` | `#0099B5` | Uzbekistan region tag |
| `--kr` | `#CD2E3A` | Korea region tag |
| `--global` | `#6366F1` | Global region tag |

Dark mode: optional later; white is the default.

### 6.3 Typography

| Use | Font | Size |
|---|---|---|
| Latin + Cyrillic (uz, ru, en) | **Inter** | 14–16 body |
| Korean | **Pretendard** | 14–16 body |
| Headings | Inter / Pretendard, 600 | 20 / 24 / 32 |
| Numbers (scores, salary) | Inter, tabular nums | — |

### 6.4 Shape, space, motion

- Radius: 12px cards, 999px chips, 16px chat bubbles.
- Spacing scale: 4 / 8 / 12 / 16 / 24 / 32.
- Shadow: one soft shadow only (`0 1px 3px rgba(15,23,42,.06)`).
- Motion: 150–250ms ease-out. Cards fade-up. Typing dots. Score ring animates on load.
- Icons: Lucide, 20px, 1.5 stroke.

### 6.5 Components

| Component | Notes |
|---|---|
| `FeatureCard` | icon, title, 1-line text, "Start" — on home screen |
| `ChatBubble` | user (blue, right), agent (light grey, left), rich content inside |
| `QuickChips` | answer options under each question + "Skip" |
| `JobCard` | title, company, region flag tag, salary, match ring, risk badge, "Why?" |
| `JobDrawer` | slides from right (bottom sheet on mobile): full post, reasons, gaps, actions |
| `MatchRing` | circular % with green → amber → grey |
| `RiskBadge` | Safe / Check / High risk with reasons tooltip |
| `RoadmapTimeline` | weeks as vertical steps, checkboxes, progress bar |
| `CompanyBrief` | 3 tabs: Past / Now / Future, every line with source chip |
| `InterviewRoom` | question card, timer, answer box, persona chip, progress dots |
| `ScoreReport` | radar chart (5 axes), per-question feedback, model answer toggle |
| `ActivityPanel` | live list of agent events: icon, agent name, status, time |
| `LangSwitch` | UZ · RU · 한 · EN segmented control |

### 6.6 Main screens

#### Home

```
┌────────────────────────────────────────────────────────────┐
│  ◆ CV_Agent                         UZ·RU·한·EN    [👤]    │
├────────────────────────────────────────────────────────────┤
│                                                            │
│        Find your job. Build your skills. Get ready.        │
│          Uzbekistan · Korea · Worldwide                    │
│                                                            │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐        │
│  │ 🔍 Job Hub   │ │ 🗺 Roadmap    │ │ 🎯 Interview │        │
│  │ All jobs in  │ │ Plan to reach│ │ Practice for │        │
│  │ one place    │ │ your target  │ │ a company    │        │
│  └──────────────┘ └──────────────┘ └──────────────┘        │
│  ┌──────────────┐ ┌──────────────┐                         │
│  │ 🇰🇷 Korea Path│ │ 🎥 Live AI   │  soon                   │
│  └──────────────┘ └──────────────┘                         │
│                                                            │
│   How it works:  ① Tell us  →  ② We match  →  ③ Practice   │
│                                                            │
├────────────────────────────────────────────────────────────┤
│  📎  Type in any language…                           ➤     │
└────────────────────────────────────────────────────────────┘
```

#### Language picker (first screen)

```
┌────────────────────────────────────────────────────────────┐
│                         ◆ CV_Agent                         │
│                                                            │
│                  Choose your language                      │
│        Tilni tanlang · Выберите язык · 언어를 선택하세요       │
│                                                            │
│      ┌──────────────┐  ┌──────────────┐                    │
│      │ 🇺🇿 O'zbekcha │  │ 🇷🇺 Русский   │                    │
│      └──────────────┘  └──────────────┘                    │
│      ┌──────────────┐  ┌──────────────┐                    │
│      │ 🇰🇷 한국어     │  │ 🇬🇧 English   │                    │
│      └──────────────┘  └──────────────┘                    │
└────────────────────────────────────────────────────────────┘
```

#### Country scope (second question, in the chosen language)

```
┌────────────────────────────────────────────────────────────┐
│  🤖 Qayerdan ish qidirmoqchisiz?                            │
│                                                            │
│  [🇺🇿 Faqat O'zbekiston]  [🇰🇷 Faqat Koreya]                 │
│  [🌍 Boshqa davlat…]     [✅ Bir nechta]                    │
│  [🌐 Barcha davlatlar]    [💻 Faqat masofaviy]              │
└────────────────────────────────────────────────────────────┘
```

#### Chat with intake

```
┌───────────────────────────────────────┬────────────────────┐
│  🤖 Where do you want to work?         │  Agent Activity    │
│  [Tashkent] [Seoul] [Remote] [Any]    │  ● Orchestrator    │
│  [Skip]                               │    asking: city    │
│                         Seoul  🙂     │  ○ Profile         │
│  🤖 What salary do you want?          │    CV parsed ✓     │
│  [2.5M₩] [3M₩] [3.5M₩+] [Not sure]    │                    │
├───────────────────────────────────────┴────────────────────┤
│  📎  Type…                                           ➤     │
└────────────────────────────────────────────────────────────┘
```

#### Job results

```
┌────────────────────────────────────────────────────────────┐
│ Filters: [🇺🇿][🇰🇷][🌍]  Salary ▾  Visa ▾  Remote ▾  Lang ▾  │
├────────────────────────────────────────────────────────────┤
│ ┌────────────────────────────────────────────────────────┐ │
│ │ Backend Developer · Kakao          🇰🇷   ◯ 86%          │ │
│ │ Seoul · 45–55M₩ · E-7 OK          🟢 Safe              │ │
│ │ Why: Python ✓  FastAPI ✓  Docker ✓   Missing: Kafka   │ │
│ │ [Details] [Practice interview] [Add to roadmap]        │ │
│ └────────────────────────────────────────────────────────┘ │
│ ┌────────────────────────────────────────────────────────┐ │
│ │ Python Dev · from Telegram @channel  🇺🇿  ◯ 78%        │ │
│ │ Tashkent · 8–12M so'm               🟡 Check           │ │
│ └────────────────────────────────────────────────────────┘ │
└────────────────────────────────────────────────────────────┘
```

#### Interview room

```
┌────────────────────────────────────────────────────────────┐
│ Kakao · Backend · 🇰🇷 Korean · Persona: Strict   ●●●○○○○ 3/7 │
├────────────────────────────────────────────────────────────┤
│                                                            │
│   Q3 · Technical                                ⏱ 01:42    │
│   ┌──────────────────────────────────────────────────────┐ │
│   │ 카카오톡 메시지 시스템에서 Kafka를 쓴다면,              │ │
│   │ 순서 보장은 어떻게 하시겠습니까?                         │ │
│   └──────────────────────────────────────────────────────┘ │
│   Source: Kakao tech blog (2026) ↗                         │
│                                                            │
│   ┌──────────────────────────────────────────────────────┐ │
│   │ Your answer…                                         │ │
│   └──────────────────────────────────────────────────────┘ │
│              [Hint]  [Skip]  [Submit ➤]                    │
└────────────────────────────────────────────────────────────┘
```

#### Score report

```
┌────────────────────────────────────────────────────────────┐
│   Readiness  ◯ 72 / 100        "Good. Work on structure."  │
│                                                            │
│        Knowledge ▲                                         │
│     Clarity ◄──●──► Structure      (radar chart)           │
│        Company fit ▼   Confidence                          │
│                                                            │
│  Q1 Self-intro      ████████░░ 4/5   [See feedback]        │
│  Q3 Technical       █████░░░░░ 2.5/5 [Model answer]        │
│  Q6 Stress          ██████░░░░ 3/5                         │
│                                                            │
│  [Make roadmap from weak spots]   [Practice again]         │
└────────────────────────────────────────────────────────────┘
```

#### Roadmap

```
┌────────────────────────────────────────────────────────────┐
│ Target: Backend Dev @ Kakao · 60 days · 10h/week   ▓▓▓░ 35%│
├────────────────────────────────────────────────────────────┤
│ ● Week 1–2  Kafka basics            ☑ course  ☑ mini-lab   │
│ ● Week 3–4  System design           ☐ book ch.1–4 ☐ mock   │
│ ○ Week 5–6  Korean tech interview   ☐ 20 Q practice        │
│ ○ Week 7–8  Portfolio project       ☐ deploy  ☐ write-up   │
└────────────────────────────────────────────────────────────┘
```

### 6.7 Responsive rules

- < 768px: Activity panel becomes a pull-up sheet (tap "⚡ 3 agents working").
- Job drawer becomes a bottom sheet.
- Feature cards: 2 per row on mobile, 3 on desktop.
- 16px side padding; no horizontal scroll.

### 6.8 Accessibility

- Contrast ≥ 4.5:1 for text.
- Keyboard: Tab through chips, Enter to send, Esc closes drawers.
- `aria-live="polite"` on chat stream.
- Do not use color alone — risk badges also have text.

---

## 7. Environments: Local → Vercel

### 7.1 Local (Phases 0–11)

Everything in `docker-compose`:

| Service | Port |
|---|---|
| web (Next.js dev) | 3000 |
| gateway | 8000 |
| agents (each) | 8101–8115 |
| kafka (KRaft) | 9092 |
| redpanda-console | 8080 |
| postgres + pgvector | 5432 |
| redis | 6379 |
| langfuse | 3001 |

Commands (via `Makefile`):

```
make up        # start all
make down      # stop all
make topics    # create Kafka topics
make migrate   # run DB migrations
make seed      # load sample jobs + companies
make logs a=judge
make evals
```

### 7.2 Cloud (Phase 12)

**Important:** Vercel runs the **Next.js frontend** (and light API routes). It **cannot** run Kafka
or long-running Python agents. Split it:

| Part | Where |
|---|---|
| Web app | **Vercel** |
| Gateway + agents | Container host (Fly.io / Render / a small VM) |
| Kafka | Managed Kafka (Confluent Cloud or Redpanda Cloud free/dev tier) |
| Postgres + pgvector | Supabase |
| Redis | Managed Redis (free tier) |
| Tracing | Langfuse Cloud |
| Telegram bot | Same container host as agents |

`NEXT_PUBLIC_GATEWAY_URL` on Vercel points to the gateway's public URL.

---

## 8. Phase Overview

| Phase | Name | Main result | Est. time |
|---|---|---|---|
| 0 | Foundations | Repo, Docker, Kafka, DB, CI running | 3–4 days |
| 1 | Multi-Agent Core | Orchestrator + A2A + Kafka + Judge skeleton, end-to-end | 1 week |
| 2 | UI Shell + Chat | White UI, 4 languages, chat intake, feature buttons, Activity panel | 1 week |
| 3 | Profile Agent | CV upload → structured profile | 3–4 days |
| 4 | Job Hub Ingestion | UZ + KR + Telegram jobs flowing into DB | 1.5 weeks |
| 5 | Smart Match + Scam | Ranked jobs with reasons + risk badges | 1 week |
| 6 | Interview Prep | Company brief + full interview + Judge score | 1.5 weeks |
| 7 | Roadmap | Gap → plan → progress → re-plan | 1 week |
| 8 | Korea Path | Visa / EPS guide (RAG) | 1 week |
| 9 | Telegram Bot | App inside Telegram | 1 week |
| 10 | Global Sources | Adzuna / Jooble / Remotive | 3–4 days |
| 11 | Evals + Hardening | Eval suite, dashboards, security | 1 week |
| 12 | Cloud Deploy | Vercel + cloud backend live | 3–4 days |
| 13 | Voice Interview | Speak answers, delivery feedback | 1.5 weeks |
| 14 | AI Avatar | Live avatar interviewer | 2 weeks |
| 15 | Portfolio Packaging | README, diagrams, video, blog | 3–4 days |

**MVP = Phases 0–6** (≈ 6–7 weeks). Everything after is growth.

---

## Phase 0 — Foundations

### Goal
A clean repo where `make up` starts Kafka, Postgres, Redis, the gateway and one hello-world agent.

### Tasks
1. **Repo setup**
   - Monorepo layout (see 5.9).
   - `.gitignore`, `.editorconfig`, `.env.example`.
   - Python: `uv` or `poetry` workspace; shared `libs/common` package.
   - Node: `pnpm` for `apps/web`.
2. **Docker**
   - `Dockerfile` template for agents (slim Python, non-root user).
   - `docker-compose.yml` with Kafka (KRaft, no Zookeeper), Redpanda Console, Postgres + pgvector, Redis, Langfuse.
   - Health checks for each service.
3. **Kafka**
   - `infra/kafka/topics.sh` creates all topics from 5.4 (partitions: 3, replication: 1 locally).
   - Retention: `jobs.*` 7 days, `agent.events` 1 day, others 3 days.
4. **Database**
   - Migration tool (Alembic).
   - First migration: `users`, `sessions`, `verdicts`.
   - Enable `vector` extension.
5. **libs/common**
   - `Envelope` Pydantic model (5.5).
   - Kafka producer/consumer wrapper (aiokafka) with JSON serde, retries, DLQ.
   - Settings loader (pydantic-settings).
   - Logger (structured JSON).
6. **CI**
   - GitHub Actions: lint (ruff, eslint), type check (mypy, tsc), unit tests, docker build.
7. **Makefile** with the commands in 7.1.

### Deliverables
- `make up` → all containers healthy.
- Redpanda Console shows all topics.
- A test script sends an envelope to `agent.tasks` and a hello agent echoes to `agent.results`.

### Done when
- [ ] Fresh clone + `make up` works on Windows (Docker Desktop) and Linux.
- [ ] CI is green.
- [ ] Topics exist; hello round-trip works.

### Portfolio tip
Screenshot Redpanda Console with topics and messages. Use it in the README.

---

## Phase 1 — Multi-Agent Core

### Goal
A real request goes: Gateway → Orchestrator → worker (via Kafka) → Judge → Orchestrator → Gateway → user, with a live event stream.

### Tasks
1. **Gateway**
   - `POST /chat` (message, session_id, lang) → publish to `user.requests`.
   - `GET /stream/{session_id}` (SSE) or WebSocket → forward `agent.events` + final answers.
   - Session create/restore (Redis).
2. **Orchestrator (LangGraph)**
   - State: `session_id, lang, intent, slots, plan, pending_tasks, results`.
   - Nodes: `detect_language` → `detect_intent` → `fill_slots` → `plan` → `dispatch` → `wait` → `merge` → `respond`.
   - Intents: `job_search`, `roadmap`, `interview_prep`, `korea_path`, `smalltalk`, `help`.
   - Slot rules: ask **one question at a time**, return quick-reply chips, max 5 questions, skip allowed.
   - Fixed first slots (see 3.3): `lang` (chosen on first screen) → `search_scope` (one / several / all countries / remote). Later slots depend on the scope.
   - All questions and chips are generated in the session `lang`.
3. **A2A layer**
   - Each agent serves `/.well-known/agent.json` (Agent Card: name, description, skills, endpoint, input/output schema).
   - JSON-RPC endpoint `tasks/send` for sync calls.
   - Orchestrator discovers agents from a registry list in config.
4. **Judge skeleton**
   - Consumes `agent.results`, applies a simple rubric, publishes `judge.verdicts`.
   - RETRY up to 2 times with reason; then FAIL → fallback message.
5. **Events**
   - Every agent emits `agent.events` (`started`, `progress`, `done`, `error`) with short human text.
6. **Tracing**
   - OpenTelemetry: one `trace_id` across gateway → orchestrator → agents → judge.
   - Langfuse for LLM calls (prompt, tokens, latency).
7. **Dummy worker**
   - `echo_research` agent: returns a fake company brief so the full loop runs before real agents exist.

### Deliverables
- curl / small script shows the full loop with events.
- Langfuse shows one trace with 4+ spans.

### Done when
- [ ] Judge RETRY path tested (force a bad output → retry → pass).
- [ ] DLQ receives a message after max retries.
- [ ] Agent Cards return valid JSON for each agent.

### Portfolio tip
Record a 30-second GIF: request in → events stream → Judge retry → final answer.

---

## Phase 2 — UI Shell + Chat

### Goal
A beautiful white UI with chat, feature buttons, explanations, 4 languages and the live Activity panel.

### Tasks
1. **Next.js setup**
   - App Router, TypeScript, Tailwind, shadcn/ui, Lucide, Framer Motion.
   - Design tokens from 6.2 in `globals.css` and `tailwind.config`.
   - Fonts: Inter + Pretendard.
2. **i18n**
   - `next-intl` with `uz`, `ru`, `ko`, `en` message files.
   - **Language picker is the first screen** (see 3.3 and 6.6); chosen language is saved (cookie + profile).
   - LangSwitch in header to change it later.
   - If the user types in another language, suggest a switch once.
3a. **Country scope step**
   - Second question in chat: Only one country / Other country… / Pick several / All countries / Remote only.
   - Scope chip above job results (`🇺🇿 + 🇰🇷 ✎`) to edit in one tap.
   - Skipped when the user starts from Interview Prep or Roadmap.
3. **Layout**
   - Header: logo, LangSwitch, profile button.
   - Main: chat column; right: Activity panel (desktop) / pull-up sheet (mobile).
   - Bottom: input bar with 📎 CV upload.
4. **Home screen**
   - Hero line + region line.
   - FeatureCards: Job Hub, Roadmap, Interview, Korea Path, Live AI (soon).
   - Tap card → short explainer modal (what it does, what you get, ~time) → **Start**.
   - "How it works" 3-step strip.
5. **Chat**
   - Bubbles, typing dots, streaming text.
   - QuickChips + Skip under agent questions.
   - Rich blocks inside chat: JobCard list, CompanyBrief, RoadmapTimeline, ScoreReport (placeholders now).
6. **Activity panel**
   - Live list from SSE: agent icon, name, status dot, short text, time.
   - Judge verdict colors: PASS green, RETRY amber, FAIL red.
   - Toggle "Show agents" (on by default in demo mode).
7. **Empty, loading, error states** for every block.

### Deliverables
- Clickable UI connected to Phase 1 backend.
- Lighthouse: performance ≥ 90, accessibility ≥ 95.

### Done when
- [ ] Language picker shows first; every later screen and question uses that language.
- [ ] Country scope question works for all 5 options and filters results.
- [ ] All 4 languages switch fully (no English leftovers).
- [ ] Each feature button starts its own flow.
- [ ] Mobile 375px looks right; no horizontal scroll.

### Portfolio tip
Put side-by-side screenshots of Uzbek, Russian, Korean and English UI.

---

## Phase 3 — Profile Agent

### Goal
User uploads a CV (or just chats) → structured profile the other agents can use.

### Tasks
1. Upload PDF / DOCX / image (OCR fallback) → gateway → object storage (local folder / Supabase Storage).
2. Extract text → LLM extraction into schema: name, education, skills (with level), experience, projects, languages, certificates.
3. Merge with chat slots (city, salary, visa, Korean level, remote).
4. A2A skills: `get_profile`, `update_profile`, `missing_fields`.
5. UI: "Your profile" card with edit-in-place chips; privacy note; delete button.
6. Orchestrator stops asking questions the profile already answers.

### Done when
- [ ] 10 sample CVs (uz/ru/ko/en) parse with ≥ 90% field accuracy (manual check).
- [ ] User can edit and delete profile.

---

## Phase 4 — Job Hub Ingestion

### Goal
Jobs from Uzbekistan, Korea and Telegram flow through Kafka into one clean, searchable table.

### Tasks
1. **Source agents** (each runs on a schedule, publishes `jobs.raw`)
   - **UZ:** hh.uz API (Uzbekistan area), IT Market if access allowed; others as links.
   - **KR:** Saramin Open API (key needed), Work24 via data.go.kr (key needed).
   - **Telegram:** Telethon user session; list of **public** job channels in config; read new posts since last offset; store channel + message id.
   - Respect rate limits; store cursors in Redis.
2. **Normalizer agent** (`jobs.raw` → `jobs.clean`)
   - Unified schema (see `jobs` table).
   - Telegram posts: LLM extracts title, company, city, salary, contact, requirements from free text.
   - Language detect; translate title + summary into 4 languages (cache).
   - Salary parse: so'm / ₩ / $ → normalized monthly + yearly.
   - Dedup: hash on (company, title, city) + embedding similarity > threshold.
   - Embeddings (multilingual) for search.
3. **DB writer** consumes `jobs.ready` → upsert into `jobs`.
4. **Search API**: filters (country, city, salary, remote, visa, language) + semantic query.
   - Applies the session `search_scope` by default (single / multi / all / remote).
   - "All countries" results are grouped by country with counts (`🇺🇿 412 · 🇰🇷 230 · 🌍 95`).
5. **UI**: Job Hub screen with region filter chips, list of JobCards, JobDrawer, "Source: Telegram @channel ↗".

### Done when
- [ ] ≥ 1,000 jobs ingested from at least 3 sources.
- [ ] Duplicate rate < 5% (sample check).
- [ ] Search in Uzbek returns Russian/Korean posts correctly (cross-lingual).

### Portfolio tip
Show a Kafka throughput graph and a "1 Telegram post → structured job" before/after.

---

## Phase 5 — Smart Match + Scam Check

### Goal
Ranked, explained matches with a safety badge on every job.

### Tasks
1. **Smart Match agent**
   - Candidate retrieval: vector search (profile embedding vs job embeddings) + hard filters.
   - Rerank with LLM: score 0–100, top 3 reasons, missing skills.
   - Cache results in `matches`.
2. **Scam agent** (`jobs.clean` → `jobs.ready`)
   - Rules: upfront fee, passport request, "visa guaranteed", salary far above market, no company, only personal phone, crypto pay, urgent abroad.
   - LLM check for tone and red flags.
   - Output: `risk_score` (0–100), level (Safe / Check / High), reasons.
3. **Judge check** on matches: reasons must reference real job text; no invented requirements.
4. **UI**
   - MatchRing on cards, "Why?" expands reasons, "Missing" chips link to Roadmap.
   - RiskBadge with tooltip reasons; High risk cards are greyed + warning.
   - Actions: Details · Practice interview · Add to roadmap · Save.

### Done when
- [ ] Judge PASS rate on match explanations ≥ 90%.
- [ ] Scam agent catches ≥ 80% of a labeled set of 50 fake posts, with ≤ 10% false alarms.

---

## Phase 6 — Interview Prep

### Goal
The showcase feature: company-specific, source-backed, A-to-Z mock interview with Judge scoring.

### Tasks
1. **Entry points**
   - From home button (no job search needed): ask company, role or job link, language, type.
   - From a JobCard: pre-filled.
2. **Company Research agent**
   - Sources: company website, news search, DART filings (Korean companies), tech blog, job post.
   - Output: CompanyBrief — Past / Now / Future, products, values, recent news, tech stack; **every line has a source**.
   - Cache in `companies` (refresh after 14 days).
3. **Judge (quality)**: every claim must map to a source; else RETRY.
4. **Interviewer agent**
   - Builds a question plan from: job description + CV + company brief + interview type.
   - Covers the 11 sections in 3.1 (Full mode) or a subset.
   - Personas: Friendly, Strict, Stress, Panel (3 voices in text).
   - Adaptive follow-ups based on each answer (max 2 per question).
   - Korean mode uses formal 존댓말 and Korean interview customs.
5. **Judge (scoring)**
   - Rubric per answer: Knowledge, Structure (STAR), Clarity, Company fit, Confidence — 1–5 each.
   - Feedback (2–3 lines), improved model answer, tip.
   - Session readiness score (0–100) — shown as guidance, **not** a hiring prediction.
6. **UI**
   - CompanyBrief card with tabs + source chips.
   - InterviewRoom: progress dots, timer (optional), persona chip, hint, skip.
   - ScoreReport: readiness ring, radar chart, per-question bars, model answers.
   - Button: "Make roadmap from weak spots" (Phase 7 hook).

### Done when
- [ ] 5 real companies (2 UZ, 2 KR, 1 global) produce briefs with 100% sourced claims.
- [ ] Full interview runs in all 4 languages.
- [ ] Judge scores agree with a human rater within ±1 on 80% of 40 sample answers.

### Portfolio tip
This is the **demo video centerpiece**: company brief → stress question → follow-up → score report, with the Activity panel visible.

---

## Phase 7 — Career Roadmap

### Goal
Turn gaps into a realistic plan, track it, and re-plan.

### Tasks
1. Inputs: target job (title / link / from JobCard), profile skills, time (30/60/90), hours per week, budget (free / paid).
2. Gap analysis: required skills vs current (from Profile + interview weak spots).
3. Plan: weekly steps — learn (course), build (mini project), prove (certificate / portfolio), practice (interview set).
4. Resources: curated list (free first): official docs, YouTube, Coursera/edX, local options (IT Park courses), TOPIK / OPIc prep.
5. Judge check: hours fit, steps in order, resources exist.
6. Progress: checkboxes, weekly check-in message, re-plan when the target changes or the user falls behind.
7. UI: RoadmapTimeline, progress bar, "This week" card on home.

### Done when
- [ ] Plan respects hours/week (sum within ±10%).
- [ ] Re-plan works after target change.

---

## Phase 8 — Korea Path

### Goal
Clear, safe guidance for Uzbek users going to Korea.

### Tasks
1. Knowledge base (RAG) from official sources only: EPS / HRD Korea, Uzbek Migration Agency, Hi Korea, Study in Korea.
2. Paths: **E-9** (EPS-TOPIK, SPAS database), **D-2 → D-10 → E-7** (students), **E-7** direct, **F-2** points.
3. Interactive checklist: documents, test dates, steps, links to official pages.
4. EPS-TOPIK practice: vocabulary and listening-style questions (text first).
5. Korean workplace basics: 존댓말, 회식, hierarchy, interview manners.
6. Scam warnings: legal channels only; "no one can guarantee a visa for money."
7. Judge: every guidance line must cite an official source; show "last checked" date.

### Done when
- [ ] Each path has a step list with official links.
- [ ] Disclaimer: "Guidance, not legal advice. Always confirm with official sources."

---

## Phase 9 — Telegram Bot

### Goal
The full app inside Telegram — where Uzbek users already are.

### Tasks
1. aiogram bot → same Gateway API (bot is just another client).
2. `/start` follows the same first-run flow (3.3): language buttons → country scope buttons.
3. Commands: `/start`, `/jobs`, `/interview`, `/roadmap`, `/korea`, `/profile`, `/lang`.
3. Inline keyboards = QuickChips; job cards as messages with buttons.
4. CV upload as a document.
5. Daily job alerts (opt-in) — top 5 new matches.
6. Interview in chat: one question per message, score at the end, link to web report.
7. Login link: connect Telegram account to web account.

### Done when
- [ ] All 4 core flows work in Telegram.
- [ ] Alerts send only to opted-in users; easy `/stop`.

---

## Phase 10 — Global Sources

### Goal
Worldwide and remote jobs.

### Tasks
1. Global Source agent: Adzuna API, Jooble API, Remotive API (keys where needed).
2. Map countries and currencies; add `remote` flag.
3. Region filter 🌍 in UI; currency switch.
4. Visa info field ("sponsorship mentioned: yes/no").

### Done when
- [ ] Global jobs appear in search and matching with no extra code in other agents (pipeline proves reuse).

---

## Phase 11 — Evals, Observability, Hardening

### Goal
Prove quality with numbers; make it safe and stable.

### Tasks
1. **Eval datasets** (`evals/datasets/`)
   - 50 match cases, 50 scam posts, 40 interview answers with human scores, 20 company briefs, 30 multilingual chats.
2. **Eval runner**: `make evals` → JSON + HTML report: Judge pass rate, scam precision/recall, judge–human agreement, latency p50/p95, cost per session.
3. **Dashboards**: Langfuse (LLM), Redpanda Console (Kafka), simple Grafana optional.
4. **Security**
   - Auth (email magic link + Telegram login).
   - Rate limits per user (Redis).
   - Prompt-injection guard on job posts and web pages (they are untrusted data).
   - Secrets only in env; no keys in repo.
   - PII: encrypt CV files at rest; delete on request.
5. **Reliability**: idempotent consumers, DLQ replay script, graceful shutdown, retries with backoff.
6. **Tests**: unit (schemas, parsers), contract (Agent Cards), integration (docker-compose in CI), UI e2e (Playwright).

### Done when
- [ ] Eval report generated in CI on every main push.
- [ ] No critical findings in a security review.

---

## Phase 12 — Cloud Deploy (Vercel)

### Goal
Public demo: frontend on Vercel, backend in the cloud.

### Tasks
1. **Vercel**: import `apps/web`, set env (`NEXT_PUBLIC_GATEWAY_URL`, auth keys), custom domain optional.
2. **Backend host**: deploy gateway + agents + Telegram bot as containers (Fly.io / Render / VM).
3. **Managed Kafka**: create cluster + topics; SASL/SSL config in `libs/common`.
4. **Supabase**: Postgres + pgvector + Storage; run migrations.
5. **Managed Redis**, **Langfuse Cloud**.
6. CORS: allow only the Vercel domain.
7. CD: GitHub Actions → build images → deploy on main.
8. Cost guard: daily LLM budget cap; demo mode with cached sample sessions.

### Done when
- [ ] Public URL works on phone and desktop.
- [ ] Telegram bot runs 24/7.
- [ ] Monthly cost estimate written in README.

---

## Phase 13 — Voice Interview

### Goal
Speak answers; get delivery feedback.

### Tasks
1. Browser mic → streaming speech-to-text (multilingual: uz/ru/ko/en).
2. Interviewer speaks questions with text-to-speech (voice per persona).
3. Delivery metrics: words per minute, pauses, filler words ("um", "음", "anaqa", "ну"), answer length.
4. Judge adds a **Delivery** axis to the score.
5. UI: big mic button, live waveform, transcript under it, "Re-record".
6. Telegram: voice messages as answers.

### Done when
- [ ] Round-trip latency (answer end → next question audio) < 3s p50.
- [ ] Filler detection works in all 4 languages on a test set.

---

## Phase 14 — AI Avatar Interviewer

### Goal
A realistic, live interviewer.

### Tasks
1. Choose provider: managed (HeyGen / Tavus / D-ID streaming) vs open-source (SadTalker / MuseTalk self-hosted on GPU).
2. Real-time loop: STT → Interviewer agent → TTS → avatar lip-sync stream (WebRTC).
3. Personas with distinct faces, voices and styles: Friendly HR, Strict Tech Lead, Stress Panel (3 avatars).
4. Korean panel mode (3 interviewers, common in Korea).
5. Fallback to voice-only on slow networks.
6. **No face scoring.** Feedback stays on content and voice delivery only.

### Done when
- [ ] Full 10-minute avatar interview runs without breaking.
- [ ] Clear consent screen before camera/mic.

---

## Phase 15 — Portfolio Packaging

### Goal
Make the project easy to understand in 2 minutes.

### Tasks
1. **README**: one-line pitch, GIF, features, architecture diagram, tech stack, how to run locally, live link.
2. **Architecture doc** (`docs/architecture.md`): agents, A2A vs Kafka, Judge loop, data flow, trade-offs.
3. **Diagrams**: system, Kafka topics, Judge loop, LangGraph state graph.
4. **Demo video** (2–3 min): Uzbek user → Telegram jobs → match → interview → score → roadmap; Activity panel visible.
5. **Metrics section**: eval numbers from Phase 11.
6. **Blog post**: "Building a 14-agent job hub with Kafka, A2A and an LLM Judge."
7. **Talking points** for interviews:
   - Why Kafka here (fan-out ingestion, replay, retries, audit).
   - Why A2A (standard discovery, low-latency calls).
   - How the Judge avoids self-grading (separate model, rubrics, human agreement).
   - How you handle untrusted data (prompt-injection guard).

---

## 25. Legal, Privacy, Ethics

| Topic | Rule |
|---|---|
| Job site data | Prefer official APIs. Read each site's terms before any scraping. Show summary + link, not full copies. |
| Telegram | Public channels only. Credit the channel and link the original post. Ask big channels for permission before public launch. |
| Personal data | Collect only what is needed. Encrypt CVs. "Delete my data" button. |
| Uzbekistan law | Uzbekistan's personal data law has data-localization rules for citizens' data. **Check before public launch** (may need a server in Uzbekistan). |
| Korea law | Follow PIPA (Personal Information Protection Act) for Korean users. |
| Interview ethics | Practice **before** interviews only. No live-interview cheating tools. |
| Scores | Readiness score is guidance, not a hiring prediction. |
| Korea Path | "Not legal advice." Official sources only. |
| Avatar | No face/emotion scoring. Clear consent for camera and mic. |

---

## 26. Risks and Mitigations

| Risk | Impact | Mitigation |
|---|---|---|
| API keys denied (Saramin, Work24, hh) | Fewer jobs | Start with Telegram + one API; link-out mode |
| Telegram account limits | Ingestion stops | Low polling rate, few channels, backoff |
| LLM cost grows | Budget | Cache briefs/translations, small models for normalizer, daily cap |
| Uzbek language quality | Bad UX | Test early with native speakers; Uzbek prompt examples |
| Hallucinated company facts | Trust loss | Judge source check, show sources |
| Scam false positives | Hurts real employers | "Check" level instead of "High" when unsure; show reasons |
| Too much scope | Never finish | MVP = Phases 0–6; ship, then grow |
| Vercel can't run Kafka | Deploy blocked | Split hosting (7.2) |

---

## 27. Glossary

| Term | Meaning |
|---|---|
| **A2A** | Agent2Agent protocol — agents describe themselves with Agent Cards and call each other via JSON-RPC |
| **Agent Card** | JSON at `/.well-known/agent.json` describing an agent's skills and endpoint |
| **Kafka** | Durable message bus with topics, partitions and consumer groups |
| **KRaft** | Kafka mode without Zookeeper |
| **DLQ** | Dead-letter queue — where failed messages go |
| **LangGraph** | Library for building agent workflows as state graphs |
| **LLM-as-Judge** | Using an LLM with a rubric to evaluate outputs |
| **pgvector** | Postgres extension for vector search |
| **EPS / E-9** | Korea's Employment Permit System for non-professional workers |
| **E-7** | Korean visa for professional jobs |
| **D-10** | Korean job-seeking visa |
| **SPAS** | Korean database of EPS candidates selectable by employers |
| **DART** | Korea's corporate disclosure system |
| **자기소개서 / 자소서** | Korean self-introduction / cover letter |
| **압박면접** | Stress interview |
| **존댓말** | Formal polite Korean |
