import json
from pathlib import Path


def config_dir() -> Path:
    base = Path.home() / ".config" / "juno-ai"
    base.mkdir(parents=True, exist_ok=True)
    return base


def config_path() -> Path:
    return config_dir() / "config.json"


def load_config() -> dict:
    path = config_path()
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}


def save_config(data: dict) -> None:
    path = config_path()
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")
