from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    app_name: str = "Video Generate System BE"
    app_env: str = "dev"
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    log_level: str = "INFO"

    qwen_api_key: str = ""
    qwen_base_url: str = "https://dashscope.aliyuncs.com/compatible-mode/v1"
    qwen_model: str = "qwen-max"

    ffmpeg_bin: str = "ffmpeg"

    assets_dir: str = "./assets"
    storage_dir: str = "./storage"
    logs_dir: str = "./logs"

    target_duration_sec: int = 60
    max_retry_per_stage: int = 2
    workflow_timeout_sec: int = 1800
    top_k_candidates: int = 3
    consistency_threshold: float = 0.78

    redis_url: str = "redis://localhost:6379/0"
    database_url: str = "sqlite:///./storage/app.db"


@lru_cache
def get_settings() -> Settings:
    return Settings()
