-- Portiq schema v1. Runs once on first Postgres start; `make migrate` re-applies safely.
CREATE EXTENSION IF NOT EXISTS vector;

-- A profile belongs to a chat session until login exists (Phase 11).
CREATE TABLE IF NOT EXISTS profiles (
    session_id    TEXT PRIMARY KEY,
    name          TEXT,
    skills        TEXT[] NOT NULL DEFAULT '{}',
    education     JSONB NOT NULL DEFAULT '[]',
    experience    JSONB NOT NULL DEFAULT '[]',
    languages     TEXT[] NOT NULL DEFAULT '{}',
    wishes        JSONB NOT NULL DEFAULT '{}',
    cv_text       TEXT,
    updated_at    TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS jobs (
    id            BIGSERIAL PRIMARY KEY,
    hash          TEXT UNIQUE NOT NULL,
    source        TEXT NOT NULL,
    url           TEXT,
    title         TEXT NOT NULL,
    company       TEXT,
    city          TEXT,
    country       TEXT NOT NULL,          -- UZ | KR | GL (global)
    remote        BOOLEAN NOT NULL DEFAULT false,
    salary_min    NUMERIC,
    salary_max    NUMERIC,
    currency      TEXT,
    salary_text   TEXT,
    lang          TEXT,
    skills        TEXT[] NOT NULL DEFAULT '{}',
    description   TEXT,
    visa          TEXT,
    posted_at     TIMESTAMPTZ,
    risk_score    INT NOT NULL DEFAULT 0,
    risk_level    TEXT NOT NULL DEFAULT 'safe',
    risk_reasons  TEXT[] NOT NULL DEFAULT '{}',
    sample        BOOLEAN NOT NULL DEFAULT false,
    embedding     vector(256),
    created_at    TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS jobs_country_idx ON jobs (country);
CREATE INDEX IF NOT EXISTS jobs_embedding_idx ON jobs USING hnsw (embedding vector_cosine_ops);

CREATE TABLE IF NOT EXISTS companies (
    name          TEXT PRIMARY KEY,
    brief         JSONB NOT NULL,
    updated_at    TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS interview_turns (
    id            BIGSERIAL PRIMARY KEY,
    session_id    TEXT NOT NULL,
    company       TEXT,
    category      TEXT,
    question      TEXT NOT NULL,
    answer        TEXT NOT NULL,
    scores        JSONB NOT NULL,
    feedback      TEXT,
    created_at    TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS roadmaps (
    id            BIGSERIAL PRIMARY KEY,
    session_id    TEXT NOT NULL,
    target        TEXT NOT NULL,
    plan          JSONB NOT NULL,
    created_at    TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Every Judge decision, for evals and dashboards.
CREATE TABLE IF NOT EXISTS verdicts (
    id            BIGSERIAL PRIMARY KEY,
    trace_id      TEXT NOT NULL,
    session_id    TEXT,
    agent         TEXT NOT NULL,
    task          TEXT NOT NULL,
    verdict       TEXT NOT NULL,
    reasons       TEXT[] NOT NULL DEFAULT '{}',
    attempt       INT NOT NULL,
    model         TEXT,
    created_at    TIMESTAMPTZ NOT NULL DEFAULT now()
);
