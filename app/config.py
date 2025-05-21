import os
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict

import yaml

CONFIG_PATH = os.getenv(
    "CONFIG_FILE", str(Path(__file__).parent.parent / "config.yaml")
)


@lru_cache()
def get_config() -> Dict[str, Any]:
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)
