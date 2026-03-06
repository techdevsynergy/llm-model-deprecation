"""Check whether LLM models are deprecated and retrieve status."""

from typing import Optional

from llm_deprecation.loader import load_registry
from llm_deprecation.models import DeprecationStatus, ModelInfo


class DeprecationChecker:
    """
    Check deprecation status of LLM models.
    Data is loaded from DEFAULT_DATA_URL, with fallback to built-in data in data.py.
    """

    def __init__(
        self,
        extra_models: Optional[list[ModelInfo]] = None,
        use_builtin_fallback: bool = True,
    ):
        """
        Args:
            extra_models: Additional or override entries (merged after loading).
            use_builtin_fallback: If True and DEFAULT_DATA_URL is unreachable,
                use the library's built-in registry from data.py.
        """
        registry = load_registry(fallback_to_builtin=use_builtin_fallback)
        self._models: dict[str, ModelInfo] = {}
        for info in registry:
            self._models[self._key(info.provider, info.model_id)] = info
        for info in extra_models or []:
            self._models[self._key(info.provider, info.model_id)] = info

    @staticmethod
    def _key(provider: str, model_id: str) -> str:
        return f"{provider.strip().lower()}:{model_id.strip().lower()}"

    def register(self, info: ModelInfo) -> None:
        """Register or overwrite model info."""
        self._models[self._key(info.provider, info.model_id)] = info

    def get(self, model_id: str, provider: Optional[str] = None) -> Optional[ModelInfo]:
        """
        Get ModelInfo for a model. If provider is None, search all providers
        (first match by model_id wins).
        """
        model_id = model_id.strip().lower()
        if provider is not None:
            key = self._key(provider, model_id)
            return self._models.get(key)
        for key, info in self._models.items():
            if info.model_id.lower() == model_id:
                return info
        return None

    def is_deprecated(self, model_id: str, provider: Optional[str] = None) -> bool:
        """True if the model is deprecated or retired."""
        info = self.get(model_id, provider)
        if info is None:
            return False
        return info.status in (DeprecationStatus.DEPRECATED, DeprecationStatus.RETIRED)

    def is_retired(self, model_id: str, provider: Optional[str] = None) -> bool:
        """True if the model is retired (no longer available)."""
        info = self.get(model_id, provider)
        if info is None:
            return False
        return info.status == DeprecationStatus.RETIRED

    def status(self, model_id: str, provider: Optional[str] = None) -> DeprecationStatus:
        """Return deprecation status; ACTIVE if unknown."""
        info = self.get(model_id, provider)
        if info is None:
            return DeprecationStatus.ACTIVE
        return info.status

    def list_deprecated(self, provider: Optional[str] = None) -> list[ModelInfo]:
        """List all known deprecated or retired models, optionally filtered by provider."""
        out = [
            info
            for info in self._models.values()
            if info.status in (DeprecationStatus.DEPRECATED, DeprecationStatus.RETIRED)
        ]
        if provider is not None:
            out = [i for i in out if i.provider.lower() == provider.strip().lower()]
        return sorted(out, key=lambda i: (i.provider, i.model_id))

    def list_all(self, provider: Optional[str] = None) -> list[ModelInfo]:
        """List all registered models, optionally filtered by provider."""
        out = list(self._models.values())
        if provider is not None:
            out = [i for i in out if i.provider.lower() == provider.strip().lower()]
        return sorted(out, key=lambda i: (i.provider, i.model_id))
