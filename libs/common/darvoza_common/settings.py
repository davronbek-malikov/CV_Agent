from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    kafka_bootstrap: str = "localhost:9092"
    redis_url: str = "redis://localhost:6379/0"
    database_url: str = "postgresql://darvoza:darvoza@localhost:5432/darvoza"

    # LLM: "auto" picks the first provider with a key, else "mock".
    llm_provider: str = "auto"  # auto | anthropic | gemini | ollama | mock
    llm_model: str = ""
    llm_judge_model: str = ""  # judge runs on a different model when set
    anthropic_api_key: str = ""
    gemini_api_key: str = ""
    ollama_url: str = ""

    # Job sources (off until a key is set)
    saramin_api_key: str = ""
    hh_access_token: str = ""
    tg_api_id: str = ""
    tg_api_hash: str = ""
    tg_session: str = "darvoza"
    tg_channels: str = ""  # comma-separated public channel usernames
    remotive_enabled: bool = True
    seed_enabled: bool = True
    source_interval_min: int = 60

    # Agents call each other over A2A at http://<name>:8000 unless overridden.
    a2a_host_pattern: str = "http://{name}:8000"
    agent_port: int = 8000

    max_retries: int = 2
    otel_endpoint: str = ""  # e.g. http://jaeger:4318
    cors_origins: str = "http://localhost:3000,https://darvoza-eight.vercel.app"


@lru_cache
def get_settings() -> Settings:
    return Settings()
