"""Inbox service responsible for loading mock data, categorization, and drafts."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Optional

from backend.models.email import Email


class InboxService:
    """Manages inbox persistence and higher-level operations."""

    def __init__(self, inbox_path: Path) -> None:
        self._path = inbox_path
        self._emails: Dict[str, Email] = {}
        self._load()

    def _load(self) -> None:
        """Load the inbox dataset from disk."""
        if not self._path.exists():
            raise FileNotFoundError(f"Inbox file not found: {self._path}")
        with self._path.open("r", encoding="utf-8") as handle:
            payload = json.load(handle)
        self._emails = {
            raw["id"]: Email.from_dict(raw)
            for raw in payload.get("emails", [])
        }

    def _persist(self) -> None:
        """Persist current inbox state to disk."""
        data = {
            "emails": [email.to_dict() for email in self._emails.values()]
        }
        with self._path.open("w", encoding="utf-8") as handle:
            json.dump(data, handle, indent=2)

    def list_emails(self) -> List[Email]:
        """Return all emails sorted by timestamp descending."""
        return sorted(self._emails.values(), key=lambda e: e.timestamp, reverse=True)

    def get_email(self, email_id: str) -> Email:
        """Return an email by id."""
        if email_id not in self._emails:
            raise KeyError(f"Email {email_id} not found")
        return self._emails[email_id]

    def update_email(self, email: Email) -> None:
        """Persist updates to a single email record."""
        self._emails[email.id] = email
        self._persist()

    def save_category(self, email_id: str, category: str) -> Email:
        """Update the category field for an email."""
        email = self.get_email(email_id)
        email.category = category
        self.update_email(email)
        return email

    def save_actions(self, email_id: str, actions: List[str]) -> Email:
        """Update extracted action items for an email."""
        email = self.get_email(email_id)
        email.action_items = actions
        self.update_email(email)
        return email

    def append_draft(self, email_id: str, draft_text: str) -> Email:
        """Append a new draft to the email's draft list."""
        email = self.get_email(email_id)
        email.drafts.append(draft_text)
        self.update_email(email)
        return email

    def search_by_category(self, category: Optional[str] = None) -> List[Email]:
        """Filter emails by category."""
        if not category:
            return self.list_emails()
        return [email for email in self._emails.values() if email.category == category]
