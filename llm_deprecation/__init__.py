"""
LLM Model Deprecation — track and check deprecation status of LLM provider models.
"""

from llm_deprecation.checker import DeprecationChecker
from llm_deprecation.models import DeprecationStatus, ModelInfo

__version__ = "1.2.0"
__all__ = ["DeprecationChecker", "DeprecationStatus", "ModelInfo"]
