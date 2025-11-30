"""Prompt model definitions."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Prompt:
    """Represents a user-editable prompt template."""

    id: str
    name: str
    description: str
    template: str

    @classmethod
    def from_dict(cls, data: dict) -> "Prompt":
        """Instantiate Prompt from a JSON dictionary."""
        return cls(
            id=data["id"],
            name=data["name"],
            description=data.get("description", ""),
            template=data["template"],
        )

    def to_dict(self) -> dict:
        """Serialize prompt for persistence."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "template": self.template,
        }
