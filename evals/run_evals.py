"""Offline evals for the parts that run without an LLM.

    make evals          # writes evals/report.json and prints a summary

1. Scam detection: precision / recall on labeled posts (uz/ru/ko/en).
2. Answer rubric: pairwise accuracy (does the Judge score the better answer higher?).
3. Live Judge verdicts from Postgres, if the stack is running.
"""

import asyncio
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "libs" / "common"), str(ROOT)]

from agents.judge.rubric import score_answer  # noqa: E402
from agents.scam.rules import assess  # noqa: E402
from portiq_common.jobs import parse_salary  # noqa: E402

DATA = Path(__file__).parent / "datasets"


def load(name: str) -> list[dict]:
    return [json.loads(line) for line in (DATA / name).read_text(encoding="utf-8").splitlines() if line.strip()]


def scam_eval() -> dict:
    rows = load("scam_posts.jsonl")
    tp = fp = fn = tn = 0
    misses = []
    for r in rows:
        job = {**r, **{k: v for k, v in parse_salary(r["description"]).items() if v}}
        job["salary_max"] = job.pop("max", None)
        job["currency"] = job.get("currency")
        flagged = assess(job)["risk_level"] != "safe"
        is_scam = r["label"] == "scam"
        tp += flagged and is_scam
        fp += flagged and not is_scam
        fn += (not flagged) and is_scam
        tn += (not flagged) and not is_scam
        if flagged != is_scam:
            misses.append(f"{r['label']}/{r['lang']}: {r['title']}")
    precision = tp / max(tp + fp, 1)
    recall = tp / max(tp + fn, 1)
    return {"n": len(rows), "precision": round(precision, 3), "recall": round(recall, 3),
            "f1": round(2 * precision * recall / max(precision + recall, 1e-9), 3), "misses": misses}


def rubric_eval() -> dict:
    rows = load("answer_pairs.jsonl")
    wins, gaps, misses = 0, [], []
    for r in rows:
        good = score_answer(r["question"], r["better"], r["lang"], category=r["category"])["total"]
        bad = score_answer(r["question"], r["worse"], r["lang"], category=r["category"])["total"]
        wins += good > bad
        gaps.append(good - bad)
        if good <= bad:
            misses.append(f"{r['lang']}/{r['category']}: {good} vs {bad}")
    return {"n": len(rows), "pairwise_accuracy": round(wins / len(rows), 3),
            "avg_margin": round(sum(gaps) / len(gaps), 1), "misses": misses}


async def verdicts() -> dict | None:
    try:
        import asyncpg

        conn = await asyncpg.connect("postgresql://portiq:portiq@localhost:5432/portiq", timeout=3)
    except Exception:
        return None
    rows = await conn.fetch("SELECT agent, verdict, count(*) n FROM verdicts GROUP BY 1,2 ORDER BY 1,2")
    await conn.close()
    total = sum(r["n"] for r in rows)
    passed = sum(r["n"] for r in rows if r["verdict"] == "PASS")
    return {"total": total, "pass_rate": round(passed / total, 3) if total else None,
            "by_agent": [dict(r) for r in rows]}


def main() -> None:
    report = {"scam": scam_eval(), "rubric": rubric_eval(), "judge_verdicts": asyncio.run(verdicts())}
    (Path(__file__).parent / "report.json").write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    s, r, v = report["scam"], report["rubric"], report["judge_verdicts"]
    print(f"Scam check   n={s['n']}  precision={s['precision']}  recall={s['recall']}  f1={s['f1']}")
    for m in s["misses"]:
        print(f"   miss: {m}")
    print(f"Answer rubric n={r['n']}  pairwise accuracy={r['pairwise_accuracy']}  avg margin={r['avg_margin']} pts")
    for m in r["misses"]:
        print(f"   miss: {m}")
    if v:
        print(f"Judge (live)  verdicts={v['total']}  pass rate={v['pass_rate']}")


if __name__ == "__main__":
    main()
