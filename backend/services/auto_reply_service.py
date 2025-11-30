"""Service for generating reply drafts."""
from __future__ import annotations

from backend.services.inbox_service import InboxService
from backend.services.prompt_brain import PromptBrain
from backend.services.llm import generate_llm_output


class AutoReplyService:
    """Creates polished AI-generated draft replies using Gemini and stored prompts."""

    def __init__(self, inbox_service: InboxService, prompt_brain: PromptBrain) -> None:
        self._inbox = inbox_service
        self._prompts = prompt_brain

    # ---------------------------------------------------------
    #   STANDARD AUTO-REPLY (Assignment Requirement)
    # ---------------------------------------------------------
    def generate_reply(self, email_id: str, persona: str | None = None) -> str:
        """
        Generates a natural, contextual reply draft using:
        - The user's stored auto-reply prompt
        - The email's subject & body
        - The user's chosen persona (optional)
        """
        email = self._inbox.get_email(email_id)
        template = self._prompts.get_template("draft")

        # Prepare context for the LLM
        draft_text = generate_llm_output(
            template,
            {
                "email_body": email.body,
                "subject": email.subject,
                "sender": email.sender,
                "persona": persona or "Email Agent",
                "_intent": "draft",
            },
        )

        # Save as a draft (never send automatically)
        self._inbox.append_draft(email.id, draft_text)
        return draft_text

    # ---------------------------------------------------------
    #   CUSTOM REPLY DRAFT (Ad-hoc instructions)
    # ---------------------------------------------------------
    def create_custom_draft(self, email_id: str, instructions: str) -> str:
        """
        Creates a custom draft using extra user instructions.
        This still uses the auto-reply template but gives the LLM
        an additional directive (e.g., "make it formal", "make it shorter",
        "respond only with bullet points").
        """
        email = self._inbox.get_email(email_id)
        template = self._prompts.get_template("draft")

        draft_text = generate_llm_output(
            template,
            {
                "subject": email.subject,
                "email_body": email.body,
                "instructions": instructions,
                "_intent": "custom_draft",
            },
        )

        self._inbox.append_draft(email.id, draft_text)
        return draft_text
    # ---------------------------------------------------------
    #   DRAFT DELETION
    # ---------------------------------------------------------
    def delete_draft(self, email_id: str, draft_index: int) -> bool:
        """
        Deletes a specific draft from an email's draft list by index.
        Returns True if deletion was successful, False otherwise.
        """
        email = self._inbox.get_email(email_id)
        if 0 <= draft_index < len(email.drafts):
            # Remove the draft at the specified index
            del email.drafts[draft_index]
            self._inbox.update_email(email)
            return True
        return False