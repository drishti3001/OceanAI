"""Agent service that answers higher-level queries over the inbox."""
from __future__ import annotations

from typing import Dict, List, Any, Optional # Import Optional

from backend.services.inbox_service import InboxService
from backend.services.prompt_brain import PromptBrain
from backend.services.llm import generate_llm_output


class AgentService:
    """Gemini-powered inbox agent that provides summaries, insights, and task analysis."""

    def __init__(self, inbox_service: InboxService, prompt_brain: PromptBrain) -> None:
        self._inbox = inbox_service
        self._prompts = prompt_brain

    # ---------------------------------------------------------
    #   MAIN ENTRYPOINT FOR AGENT QUERIES
    # ---------------------------------------------------------
    # CRITICAL FIX: Accept optional email_id
    def run_query(self, user_query: str, email_id: Optional[str] = None) -> str:
        """
        Executes an agent query. Uses:
        - The specific email content (if email_id is provided) or the entire inbox
        - The user's stored 'agent' prompt
        - The query string typed by the user
        """
        template = self._prompts.get_template("agent")

        # --- CRITICAL CONTEXT SWITCHING LOGIC ---
        if email_id:
            # Case 1: Single Email Context (e.g., "Summarize this email")
            email = self._inbox.get_email(email_id)
            emails_serialized = [self._serialize(email)] # Send only the selected email
            context_description = "the currently selected email."
        else:
            # Case 2: Inbox-Wide Context (e.g., "Show me urgent emails")
            emails_serialized = [
                self._serialize(email)
                for email in self._inbox.list_emails()
            ]
            context_description = "the entire inbox."
        
        # Format the serialized list for the LLM prompt
        email_context_str = "\n".join([f"- {e}" for e in emails_serialized])

        # Call Gemini via the LLM wrapper
        result = generate_llm_output(
            template,
            {
                "query_type": user_query,   
                "emails": email_context_str, # Pass the formatted string
                "_intent": "agent",
                "context_description": context_description, # Optional: helps LLM understand the scope
            },
        )

        return result

    # ---------------------------------------------------------
    #   INTERNAL SERIALIZATION
    # ---------------------------------------------------------
    @staticmethod
    def _serialize(email) -> Dict[str, Any]:
        """Minimal structured snapshot of each email for the LLM."""
        return {
            "id": email.id,
            "sender": email.sender,
            "subject": email.subject,
            "body": email.body,
            "category": email.category,
            "action_items": email.action_items,
            "timestamp": email.timestamp.isoformat(),
        }