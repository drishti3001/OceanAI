"""Service to categorize emails using stored prompts."""
from __future__ import annotations

from backend.services.inbox_service import InboxService
from backend.services.prompt_brain import PromptBrain
from backend.services.llm import generate_llm_output


class CategorizationService:
    """Handles automated categorization for inbox messages using Gemini + prompts."""

    VALID_CATEGORIES = {
        "important",
        "newsletter",
        "spam",
        "to-do",
        "todo",
        "meeting",
        "follow-up",
        "personal",
        "other",
    }

    def __init__(self, inbox_service: InboxService, prompt_brain: PromptBrain) -> None:
        self._inbox = inbox_service
        self._prompts = prompt_brain

    # ---------------------------------------------------------
    #   SINGLE EMAIL CATEGORIZATION
    # ---------------------------------------------------------
    def categorize_email(self, email_id: str) -> str:
        """
        Categorizes one email using:
        - The user's stored "categorize" prompt
        - Gemini output via the LLM layer
        - Safe normalization + fallback category
        """
        email = self._inbox.get_email(email_id)
        template = self._prompts.get_template("categorize")

        # Ask LLM to categorize
        raw_category = generate_llm_output(
            template,
            {
                "email_body": email.body,
                "subject": email.subject,
                "_intent": "categorize",
            },
        )

        cleaned_category = self._normalize_category(raw_category)

        # Save to inbox.json
        self._inbox.save_category(email.id, cleaned_category)
        return cleaned_category

    # ---------------------------------------------------------
    #   BULK CATEGORIZATION (OPTIONAL, helpful later)
    # ---------------------------------------------------------
    def categorize_all(self) -> None:
        """Categorizes every email in the inbox."""
        for email in self._inbox.list_emails():
            self.categorize_email(email.id)

    # ---------------------------------------------------------
    #   NORMALIZATION + FALLBACK
    # ---------------------------------------------------------
    def _normalize_category(self, category: str) -> str:
        """
        Cleans the LLM's output:
        - Lowercase
        - Trim whitespace
        - Remove punctuation
        - Match to allowed categories
        """

        if not category:
            return "other"

        cat = category.lower().strip()

        # Remove quotes, periods, unwanted punctuation
        for bad in ['"', "'", ".", ",", "\n"]:
            cat = cat.replace(bad, "")

        # Match against valid categories
        for valid in self.VALID_CATEGORIES:
            if valid in cat:
                return valid.replace(" ", "-")

        # Fallback
        return "other"
