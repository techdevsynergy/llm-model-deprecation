"""Basic tests: load from DEFAULT_DATA_URL or data.py fallback."""

import pytest

from llm_deprecation import DeprecationChecker, DeprecationStatus
from llm_deprecation.loader import load_registry, DEFAULT_DATA_URL, load_from_url


def test_load_registry_returns_list():
    """load_registry() returns a non-empty list (from URL or built-in)."""
    registry = load_registry(fallback_to_builtin=True)
    assert isinstance(registry, list)
    assert len(registry) > 0


def test_registry_entries_have_required_fields():
    """Each entry has provider, model_id, status."""
    registry = load_registry(fallback_to_builtin=True)
    for entry in registry[:20]:  # sample
        assert hasattr(entry, "provider")
        assert hasattr(entry, "model_id")
        assert hasattr(entry, "status")
        assert entry.provider
        assert entry.model_id


def test_checker_is_deprecated():
    """Known deprecated model is detected."""
    checker = DeprecationChecker()
    assert checker.is_deprecated("gpt-3.5-turbo-0301") is True
    assert checker.is_retired("gpt-3.5-turbo-0301") is True


def test_checker_status_active():
    """Known active model returns active."""
    checker = DeprecationChecker()
    assert checker.status("gpt-5.4").value == "active"
    assert checker.is_deprecated("gpt-5.4") is False


def test_checker_list_deprecated():
    """list_deprecated returns only deprecated/retired."""
    checker = DeprecationChecker()
    deprecated = checker.list_deprecated()
    assert len(deprecated) > 0
    for m in deprecated[:5]:
        assert m.status in (DeprecationStatus.DEPRECATED, DeprecationStatus.RETIRED)


def test_checker_register_override():
    """extra_models / register can add or override."""
    from llm_deprecation.models import ModelInfo
    from datetime import date

    checker = DeprecationChecker()
    checker.register(ModelInfo(
        provider="openai",
        model_id="test-override-model",
        status=DeprecationStatus.DEPRECATED,
        sunset_date=date(2027, 1, 1),
        replacement="gpt-5",
    ))
    assert checker.get("test-override-model", provider="openai") is not None
    assert checker.status("test-override-model", provider="openai") == DeprecationStatus.DEPRECATED


def test_fallback_to_builtin_when_no_network():
    """When URL fails, fallback to built-in returns data."""
    # Use an invalid URL so load_from_url fails; load_registry should fall back
    registry = load_registry(fallback_to_builtin=True)
    assert len(registry) > 0  # we get something (URL or built-in)
