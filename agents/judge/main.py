"""Judge agent.

A) Quality guard: every agent result on `agent.results` is checked. Weak
   output is sent back to the agent with reasons (RETRY, up to max_retries);
   then the verdict goes to the orchestrator on `judge.verdicts`.
B) Answer scorer: scores interview answers with a rubric (A2A skill).
"""

from typing import Any

from portiq_common import db, llm
from portiq_common.agent import Agent
from portiq_common.envelope import Envelope, Topics
from portiq_common.settings import get_settings

from .checks import judge_output
from .rubric import score_answer

SCORE_PROMPT = (
    "You are an interview judge. Score the candidate's answer 1-5 on knowledge, structure (STAR), clarity, "
    "and company fit. Be strict; 3 is average. Reply in language {lang}: "
    '{"scores": {"knowledge": n, "structure": n, "clarity": n, "fit": n}, "feedback": str (max 2 sentences), '
    '"model_answer": str (a better answer, max 5 sentences)}'
)


class JudgeAgent(Agent):
    name = "judge"
    description = "Checks every agent output before users see it (PASS/RETRY/FAIL) and scores interview answers."
    skills = [
        {"id": "score_answer", "name": "Score answer", "description": "Rubric scores, feedback and a better answer."},
        {"id": "check", "name": "Check output", "description": "Run the quality check for a task output."},
    ]

    def consumers(self):
        return [([Topics.AGENT_RESULTS], "judge", self.on_result)]

    async def record(self, env: Envelope, agent: str, verdict: str, reasons: list[str]) -> None:
        await (await db.pool()).execute(
            "INSERT INTO verdicts (trace_id, session_id, agent, task, verdict, reasons, attempt, model) "
            "VALUES ($1,$2,$3,$4,$5,$6,$7,$8)",
            env.trace_id, env.session_id, agent, env.task or "", verdict, reasons, env.attempt, "rules")

    async def on_result(self, env: Envelope) -> None:
        agent = env.payload.get("agent", env.source_agent)
        out, inp = env.payload.get("output", {}), env.payload.get("task_input", {})
        verdict, hard, soft = judge_output(env.task or "", out, inp)

        if verdict == "RETRY" and env.attempt <= get_settings().max_retries:
            await self.record(env, agent, "RETRY", hard)
            await self.emit(env, f"RETRY {agent}: {', '.join(hard)}", "verdict", verdict="RETRY")
            await self.bus.publish(Topics.AGENT_TASKS, env.child(
                type="task", source_agent=self.name, target_agent=agent, attempt=env.attempt + 1,
                payload={**inp, "judge_feedback": hard}))
            return
        if verdict == "RETRY":
            verdict = "FAIL"
        await self.record(env, agent, verdict, hard + soft)
        await self.emit(env, f"{verdict} {agent}" + (f" ({', '.join(soft)})" if soft else ""), "verdict", verdict=verdict)
        await self.bus.publish(Topics.JUDGE_VERDICTS, env.child(
            type="verdict", source_agent=self.name, target_agent="orchestrator",
            payload={"verdict": verdict, "agent": agent, "reasons": hard, "warnings": soft, "output": out,
                     "task_input": inp}))

    async def score(self, inp: dict[str, Any]) -> dict[str, Any]:
        lang = inp.get("lang", "en")
        base = score_answer(inp.get("question", ""), inp.get("answer", ""), lang, inp.get("company", ""),
                            inp.get("brief_terms"), inp.get("category", ""))

        def fb() -> dict:
            return base

        data, model = await llm.complete_json(
            SCORE_PROMPT.replace("{lang}", lang),
            f"Company: {inp.get('company')}\nQuestion: {inp.get('question')}\nAnswer: {inp.get('answer')}",
            fb, judge=True)
        if model not in ("mock", "fallback"):
            s = {k: float(data.get("scores", {}).get(k, base["scores"][k])) for k in base["scores"]}
            data = {**base, "scores": s, "total": round(sum(s.values()) / 20 * 100),
                    "feedback": data.get("feedback", base["feedback"]), "model_answer": data.get("model_answer")}
        data["model"] = model
        if inp.get("session_id"):
            await (await db.pool()).execute(
                "INSERT INTO interview_turns (session_id, company, category, question, answer, scores, feedback) "
                "VALUES ($1,$2,$3,$4,$5,$6,$7)",
                inp["session_id"], inp.get("company"), inp.get("category"), inp.get("question", ""),
                inp.get("answer", ""), data["scores"], data["feedback"])
        return data

    async def skill(self, skill_id: str, input: dict[str, Any], trace_id: str | None) -> Any:
        if skill_id == "score_answer":
            return await self.score(input)
        if skill_id == "check":
            v, hard, soft = judge_output(input.get("task", ""), input.get("output", {}), input.get("input", {}))
            return {"verdict": v, "reasons": hard, "warnings": soft}
        return await super().skill(skill_id, input, trace_id)


if __name__ == "__main__":
    JudgeAgent().run()
