"""Indexer agent: jobs.ready -> Postgres (with embedding for search)."""

from datetime import datetime

from portiq_common import db
from portiq_common.agent import Agent
from portiq_common.embed import embed, to_pgvector
from portiq_common.envelope import Envelope, Topics

UPSERT = """
INSERT INTO jobs (hash, source, url, title, company, city, country, remote, salary_min, salary_max, currency,
                  salary_text, lang, skills, description, visa, posted_at, risk_score, risk_level, risk_reasons,
                  sample, embedding)
VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9,$10,$11,$12,$13,$14,$15,$16,$17,$18,$19,$20,$21,$22::vector)
ON CONFLICT (hash) DO UPDATE SET
  url = EXCLUDED.url, salary_text = EXCLUDED.salary_text, risk_score = EXCLUDED.risk_score,
  risk_level = EXCLUDED.risk_level, risk_reasons = EXCLUDED.risk_reasons, embedding = EXCLUDED.embedding
"""


def _ts(v):
    if not v:
        return None
    try:
        return datetime.fromisoformat(str(v).replace("Z", "+00:00"))
    except ValueError:
        return None


class IndexerAgent(Agent):
    name = "indexer"
    description = "Stores ready jobs in Postgres with vectors for semantic search."

    def consumers(self):
        return [([Topics.JOBS_READY], "indexer", self.on_ready)]

    async def on_ready(self, j: Envelope) -> None:
        p = j.payload
        vec = to_pgvector(embed(f"{p['title']} {' '.join(p['skills'])} {p.get('description', '')[:1000]}"))
        pool = await db.pool()
        await pool.execute(
            UPSERT, p["hash"], p["source"], p.get("url"), p["title"], p.get("company"), p.get("city"), p["country"],
            p.get("remote", False), p.get("salary_min"), p.get("salary_max"), p.get("currency"), p.get("salary_text"),
            p.get("lang"), p.get("skills", []), p.get("description"), p.get("visa"), _ts(p.get("posted_at")),
            p.get("risk_score", 0), p.get("risk_level", "safe"), p.get("risk_reasons", []), p.get("sample", False), vec,
        )


if __name__ == "__main__":
    IndexerAgent().run()
