import os
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict

import yaml
from pydantic_settings import BaseSettings

CONFIG_PATH = os.getenv(
    "CONFIG_FILE", str(Path(__file__).parent.parent / "config.yaml")
)


@lru_cache()
def get_config() -> Dict[str, Any]:
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


class Settings(BaseSettings):
    LOG_LEVEL: str = "INFO"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
