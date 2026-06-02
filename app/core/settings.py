from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "Video Generate System BE"
    app_env: str = "dev"
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    log_level: str = "INFO"

    qwen_api_key: str = ""
    qwen_base_url: str = "https://dashscope.aliyuncs.com/compatible-mode/v1"
    qwen_model: str = "qwen-max"
    qwen_image_model: str = "qwen-image-2.0"
    qwen_image_api_url: str = "https://dashscope.aliyuncs.com/api/v1/services/aigc/multimodal-generation/generation"
    default_image_resolution: str = "720p"
    qwen_image_size: str = "2048*2048"
    qwen_image_negative_prompt: str = (
        "低清晰度，低质量，畸形肢体，多余手指，面部崩坏，构图混乱，模糊文字，明显AI伪影"
    )

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
