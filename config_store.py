import json
from pathlib import Path

# Defaults: offline-first so Juno works with zero keys or local services.
DEFAULT_CONFIG: dict = {
    "provider": "offline",
    "api_key": "",
    "model": "gpt-4o-mini",
    "ollama_base": "http://127.0.0.1:11434",
    "ollama_model": "llama3.2",
}


def config_dir() -> Path:
    base = Path.home() / ".config" / "juno-ai"
    base.mkdir(parents=True, exist_ok=True)
    return base


def config_path() -> Path:
    return config_dir() / "config.json"


def load_config() -> dict:
    path = config_path()
    merged = DEFAULT_CONFIG.copy()
    if not path.is_file():
        return merged
    try:
        disk = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(disk, dict):
            merged.update(disk)
    except (json.JSONDecodeError, OSError):
        pass
    return merged


def save_config(data: dict) -> None:
    path = config_path()
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")
