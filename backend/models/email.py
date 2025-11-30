"""Domain models for email records used by the productivity agent."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Any, Dict


@dataclass
class Email:
    """Represents an email stored in the mock inbox."""

    id: str
    sender: str
    subject: str
    timestamp: datetime
    body: str
    category: str = "Other"
    action_items: List[str] = field(default_factory=list)
    drafts: List[str] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Email":
        """Create an Email instance from a raw dictionary payload."""

        # FIX 1: Support both 'sender' and 'from'
        sender = data.get("sender") or data.get("from")
        if not sender:
            sender = "unknown"

        # FIX 2: Safe timestamp parsing
        raw_ts = data.get("timestamp", "")
        try:
            ts = datetime.fromisoformat(raw_ts.replace("Z", "+00:00"))
        except Exception:
            ts = datetime.utcnow()

        return cls(
            id=data["id"],
            sender=sender,
            subject=data.get("subject", "(no subject)"),
            timestamp=ts,
            body=data.get("body", ""),
            category=data.get("category", "Other"),
            action_items=data.get("action_items", []) or [],
            drafts=data.get("drafts", []) or [],
        )

    def to_dict(self) -> dict:
        """Serialize the Email model back into a JSON-compatible dictionary."""
        return {
            "id": self.id,
            "sender": self.sender,
            "subject": self.subject,
            "timestamp": self.timestamp.isoformat().replace("+00:00", "Z"),
            "body": self.body,
            "category": self.category,
            "action_items": self.action_items,
            "drafts": self.drafts,
        }
