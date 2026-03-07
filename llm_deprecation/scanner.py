"""Scan a project directory for deprecated or retired LLM model references."""

import re
from pathlib import Path
from typing import Optional

from llm_deprecation import DeprecationChecker
from llm_deprecation.models import DeprecationStatus, ModelInfo

# Directories to skip when scanning (same idea as .gitignore)
DEFAULT_EXCLUDE_DIRS = {
    ".git",
    "__pycache__",
    "node_modules",
    ".venv",
    "venv",
    "env",
    "dist",
    "build",
    ".tox",
    ".mypy_cache",
    ".ruff_cache",
    "site-packages",
    ".eggs",
    "*.egg-info",
}

# File extensions to scan for model IDs (code and config)
DEFAULT_SCAN_EXTENSIONS = {
    ".py",
    ".json",
    ".yaml",
    ".yml",
    ".env",
    ".toml",
    ".ini",
    ".cfg",
    ".js",
    ".ts",
    ".tsx",
    ".jsx",
    ".mjs",
    ".cjs",
    ".md",
    ".rst",
    ".txt",
}


def _should_skip_dir(path: Path, exclude_dirs: set[str]) -> bool:
    """Return True if this directory should be skipped."""
    name = path.name.lower()
    for exc in exclude_dirs:
        if exc.startswith("*"):
            if name.endswith(exc[1:]):
                return True
        elif name == exc or name == exc.lower():
            return True
    return False


def scan_project(
    root: Path,
    *,
    exclude_dirs: Optional[set[str]] = None,
    extensions: Optional[set[str]] = None,
    checker: Optional[DeprecationChecker] = None,
) -> list[tuple[Path, int, ModelInfo]]:
    """
    Scan a project directory for references to deprecated or retired LLM models.

    Returns a list of (file_path, line_number, model_info) for each occurrence.
    """
    exclude_dirs = exclude_dirs or DEFAULT_EXCLUDE_DIRS
    extensions = extensions or DEFAULT_SCAN_EXTENSIONS
    if checker is None:
        checker = DeprecationChecker()

    deprecated = checker.list_deprecated()
    # Build a map: model_id_lower -> list of ModelInfo (same id can exist for different providers in theory; we report each)
    by_id: dict[str, list[ModelInfo]] = {}
    for m in deprecated:
        key = m.model_id.lower()
        by_id.setdefault(key, []).append(m)

    if not by_id:
        return []

    # Escape model_id for regex (e.g. gpt-3.5-turbo has dots that are special)
    def pattern_for_model(model_id: str) -> str:
        escaped = re.escape(model_id)
        # Prefer word-boundary style: not part of a longer identifier (allow in quotes or after =)
        return r"(?<![a-zA-Z0-9_\-\.])" + escaped + r"(?![a-zA-Z0-9_\-\.])"

    results: list[tuple[Path, int, ModelInfo]] = []
    root = Path(root).resolve()

    for path in root.rglob("*"):
        if not path.is_file():
            continue
        if path.suffix.lower() not in extensions:
            continue
        # Skip if this file lives under an excluded directory
        try:
            rel = path.relative_to(root)
        except ValueError:
            continue
        if any(_should_skip_dir(root / p, exclude_dirs) for p in rel.parents):
            continue
        if _should_skip_dir(path.parent, exclude_dirs):
            continue

        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except Exception:
            continue

        for line_no, line in enumerate(text.splitlines(), start=1):
            line_lower = line.lower()
            for model_id_key, infos in by_id.items():
                if model_id_key not in line_lower:
                    continue
                # Check with regex to avoid substring false positives (e.g. gpt-3.5 in gpt-3.5-turbo-0301)
                pat = pattern_for_model(infos[0].model_id)
                if re.search(pat, line, re.IGNORECASE):
                    for info in infos:
                        results.append((path, line_no, info))
                    break  # one match per line per model_id family

    return results


def format_scan_output(
    findings: list[tuple[Path, int, ModelInfo]],
    root: Optional[Path] = None,
) -> str:
    """Format scan results for console output (e.g. the example in the user request)."""
    lines = []
    seen: set[tuple[str, str]] = set()  # (provider, model_id) to dedupe by line
    for file_path, line_no, info in findings:
        key = (info.provider, info.model_id)
        if key in seen:
            continue
        seen.add(key)
        status_label = "deprecated soon" if info.status == DeprecationStatus.DEPRECATED else "retired"
        lines.append(f"⚠ {info.provider}:{info.model_id} → {status_label}")
    return "\n".join(lines) if lines else ""
