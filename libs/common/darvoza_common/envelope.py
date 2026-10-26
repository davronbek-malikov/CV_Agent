"""The one message format every service and agent uses on Kafka."""

from datetime import UTC, datetime
from typing import Any, Literal
from uuid import uuid4

from pydantic import BaseModel, Field

MessageType = Literal["request", "task", "result", "verdict", "event", "reply", "job"]


def new_id() -> str:
    return uuid4().hex


class Envelope(BaseModel):
    schema_version: int = 1
    message_id: str = Field(default_factory=new_id)
    trace_id: str = Field(default_factory=new_id)
    session_id: str = ""
    type: MessageType
    source_agent: str
    target_agent: str | None = None
    task: str | None = None
    task_id: str | None = None
    attempt: int = 1
    lang: str = "en"
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    payload: dict[str, Any] = Field(default_factory=dict)

    def child(self, **changes: Any) -> "Envelope":
        """A follow-up message in the same trace and session."""
        base = {
            "trace_id": self.trace_id,
            "session_id": self.session_id,
            "lang": self.lang,
            "task": self.task,
            "task_id": self.task_id,
            "attempt": self.attempt,
        }
        base.update(changes)
        return Envelope(**base)

    def to_bytes(self) -> bytes:
        return self.model_dump_json().encode()

    @classmethod
    def from_bytes(cls, raw: bytes) -> "Envelope":
        return cls.model_validate_json(raw)


class Topics:
    USER_REQUESTS = "user.requests"
    AGENT_TASKS = "agent.tasks"
    AGENT_RESULTS = "agent.results"
    JUDGE_VERDICTS = "judge.verdicts"
    AGENT_EVENTS = "agent.events"
    SESSION_REPLIES = "session.replies"
    JOBS_RAW = "jobs.raw"
    JOBS_CLEAN = "jobs.clean"
    JOBS_READY = "jobs.ready"
    DLQ = "agent.dlq"

    ALL = [
        USER_REQUESTS, AGENT_TASKS, AGENT_RESULTS, JUDGE_VERDICTS, AGENT_EVENTS,
        SESSION_REPLIES, JOBS_RAW, JOBS_CLEAN, JOBS_READY, DLQ,
    ]
