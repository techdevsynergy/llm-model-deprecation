"""Data models for LLM deprecation tracking."""

from dataclasses import dataclass, field
from datetime import date
from enum import Enum
from typing import Optional


class DeprecationStatus(str, Enum):
    """Status of a model in its lifecycle."""

    ACTIVE = "active"
    LEGACY = "legacy"  # Still supported, prefer newer
    DEPRECATED = "deprecated"  # Will be retired, migration advised
    RETIRED = "retired"  # No longer available


@dataclass
class ModelInfo:
    """Information about an LLM model's deprecation state."""

    provider: str
    model_id: str
    status: DeprecationStatus
    deprecated_date: Optional[date] = None
    sunset_date: Optional[date] = None
    replacement: Optional[str] = None
    notes: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "provider": self.provider,
            "model_id": self.model_id,
            "status": self.status.value,
            "deprecated_date": self.deprecated_date.isoformat() if self.deprecated_date else None,
            "sunset_date": self.sunset_date.isoformat() if self.sunset_date else None,
            "replacement": self.replacement,
            "notes": self.notes,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "ModelInfo":
        deprecated = data.get("deprecated_date")
        sunset = data.get("sunset_date")
        if isinstance(deprecated, str):
            deprecated = date.fromisoformat(deprecated)
        if isinstance(sunset, str):
            sunset = date.fromisoformat(sunset)
        return cls(
            provider=data["provider"],
            model_id=data["model_id"],
            status=DeprecationStatus(data.get("status", "active")),
            deprecated_date=deprecated,
            sunset_date=sunset,
            replacement=data.get("replacement"),
            notes=data.get("notes"),
        )
