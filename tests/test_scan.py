"""Tests for the project scanner and CLI."""

import tempfile
from pathlib import Path

import pytest

from llm_deprecation import DeprecationChecker
from llm_deprecation.models import DeprecationStatus, ModelInfo
from llm_deprecation.scanner import format_scan_output, scan_project


def test_scan_finds_deprecated_model_in_file():
    """Scanning a dir with a file that references a deprecated model returns findings."""
    checker = DeprecationChecker()
    checker.register(ModelInfo(
        provider="openai",
        model_id="test-deprecated-scan",
        status=DeprecationStatus.DEPRECATED,
        replacement="gpt-5",
    ))
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        (root / "app.py").write_text('model = "test-deprecated-scan"\n')
        findings = scan_project(root, checker=checker)
    assert len(findings) >= 1
    paths = {f[0].name for f in findings}
    assert "app.py" in paths


def test_scan_empty_dir_returns_empty():
    """Scanning a dir with no model references returns empty."""
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        (root / "readme.txt").write_text("Hello world\n")
        findings = scan_project(root)
    assert len(findings) == 0


def test_format_scan_output_dedupes():
    """format_scan_output prints each provider:model_id once."""
    from llm_deprecation.models import ModelInfo, DeprecationStatus

    info = ModelInfo(
        provider="openai",
        model_id="gpt-old",
        status=DeprecationStatus.RETIRED,
        replacement="gpt-5",
    )
    findings = [(Path("a.py"), 1, info), (Path("b.py"), 2, info)]
    out = format_scan_output(findings)
    assert out.count("openai:gpt-old") == 1
    assert "retired" in out


def test_scan_skips_excluded_dirs():
    """Scan does not search inside .git or __pycache__."""
    checker = DeprecationChecker()
    checker.register(ModelInfo(
        provider="openai",
        model_id="only-in-git",
        status=DeprecationStatus.DEPRECATED,
        replacement="gpt-5",
    ))
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        (root / "app.py").write_text("x = 1\n")  # no match
        (root / ".git").mkdir(parents=True, exist_ok=True)
        (root / ".git" / "config").write_text('model = "only-in-git"\n')
        findings = scan_project(root, checker=checker)
    # .git is excluded, so we should not find only-in-git
    model_ids = {f[2].model_id for f in findings}
    assert "only-in-git" not in model_ids
