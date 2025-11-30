"""Service for extracting action items from emails."""
from __future__ import annotations

import json
from typing import List, Dict, Any

from backend.services.inbox_service import InboxService
from backend.services.prompt_brain import PromptBrain
from backend.services.llm import generate_llm_output


class ActionItemService:
    """Extracts action items using stored prompts + Gemini."""

    def __init__(self, inbox_service: InboxService, prompt_brain: PromptBrain) -> None:
        self._inbox = inbox_service
        self._prompts = prompt_brain

    def extract(self, email_id: str) -> List[str]:
        """
        Extracts structured action items using the LLM.
        Persists a simple list of human-readable action strings for UI display.
        """
        email = self._inbox.get_email(email_id)
        template = self._prompts.get_template("actions")

        # Call LLM with the correct intent
        raw_json = generate_llm_output(
            template,
            {
                "email_body": email.body,
                "subject": email.subject,
                "_intent": "actions",
            },
        )

        # Attempt to parse JSON from the LLM output
        try:
            cleaned = raw_json.strip("` \n")  # remove markdown fences if present
            parsed: List[Dict[str, Any]] = json.loads(cleaned)
        except Exception:
            # Fallback: Store a descriptive error instead of raw text if JSON fails
            parsed = [{"task": "Extraction failed: LLM output was not valid JSON.", "deadline": ""}]

        # Convert structured JSON into human-friendly action strings
        items_for_ui: List[str] = []
        for obj in parsed:
            task = obj.get("task", "").strip()
            deadline = obj.get("deadline", "").strip()

            if deadline:
                items_for_ui.append(f"{task} (deadline: {deadline})")
            else:
                items_for_ui.append(task)

        # Persist to inbox.json
        self._inbox.save_actions(email.id, items_for_ui)

        return items_for_ui
