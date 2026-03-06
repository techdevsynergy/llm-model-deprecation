"""Load deprecation data from DEFAULT_DATA_URL or built-in data."""

import json
from pathlib import Path
from typing import Union

from llm_deprecation.models import ModelInfo

# Default external data URL: community-maintained registry (OpenAI, Anthropic, Gemini, etc.).
# First priority; falls back to built-in data in data.py if unreachable.
DEFAULT_DATA_URL = "https://raw.githubusercontent.com/techdevsynergy/llm-deprecation-data/refs/heads/main/llm_deprecation_data.json"


def _parse_data(data: object) -> list[dict]:
    """Normalize loaded JSON to a list of model objects."""
    if isinstance(data, list):
        return data
    if isinstance(data, dict):
        return data.get("models", data.get("deprecations", data.get("entries", [])))
    return []


def load_json(path: Union[str, Path]) -> list[ModelInfo]:
    """
    Load a list of ModelInfo from a JSON file.
    Expected format: list of objects with provider, model_id, status,
    and optional deprecated_date, sunset_date, replacement, notes.
    """
    path = Path(path)
    raw = json.loads(path.read_text())
    entries = _parse_data(raw)
    return [ModelInfo.from_dict(e) for e in entries]


def load_from_url(url: str) -> list[ModelInfo]:
    """Load deprecation list from a URL (uses urllib; optional requests)."""
    try:
        import urllib.request

        with urllib.request.urlopen(url, timeout=30) as resp:
            raw = json.loads(resp.read().decode())
    except Exception:
        try:
            import requests

            resp = requests.get(url, timeout=30)
            resp.raise_for_status()
            raw = resp.json()
        except ImportError:
            raise ImportError("Loading from URL requires 'requests' or stdlib urllib")
    entries = _parse_data(raw)
    return [ModelInfo.from_dict(e) for e in entries]


def load_registry(fallback_to_builtin: bool = True) -> list[ModelInfo]:
    """
    Load the model registry: DEFAULT_DATA_URL first, else built-in data from data.py.

    Resolution:
      1. Try DEFAULT_DATA_URL (community-maintained JSON from GitHub).
      2. If that fails and fallback_to_builtin is True, return the built-in registry.
      3. Else return an empty list.
    """
    from llm_deprecation.data import get_builtin_registry

    try:
        return load_from_url(DEFAULT_DATA_URL)
    except Exception:
        pass
    return get_builtin_registry() if fallback_to_builtin else []


def export_builtin_to_json(path: Union[str, Path]) -> None:
    """
    Write the built-in registry to a JSON file. Use this to create your own
    external data file, then edit it and pass its path to DeprecationChecker.
    """
    from llm_deprecation.data import get_builtin_registry

    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    data = [m.to_dict() for m in get_builtin_registry()]
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")
