from __future__ import annotations
import os
import json
from typing import Dict, Any, Optional

import google.generativeai as genai
from dotenv import load_dotenv

# Load .env file from project root
load_dotenv()

# Read Google API key
API_KEY = os.getenv("Email_key")
if not API_KEY:
    raise ValueError(
        "Gemini API key not found. Make sure your `.env` file contains:\n\n"
        "Email_key=YOUR_KEY_HERE\n"
    )

# Configure Gemini client
genai.configure(api_key=API_KEY)  # type: ignore

# Default LLM model
MODEL_NAME = "models/gemini-2.5-flash"



# ---------------------------------------------------------
#  HIGH-LEVEL LLM FUNCTION
# ---------------------------------------------------------
def _run_llm(system_prompt: str, user_prompt: str) -> str:
    """
    Core wrapper that sends structured instructions to Gemini.
    Returns clean text, with safe fallback on API failure.
    """

    try:
        model = genai.GenerativeModel(MODEL_NAME)  # type: ignore

        # Gemini does NOT use role/content dicts.
        # We just send a single combined text prompt.
        full_prompt = f"{system_prompt.strip()}\n\nUSER INPUT:\n{user_prompt.strip()}"

        # You can pass a plain string directly:
        response = model.generate_content(full_prompt)

        if response and getattr(response, "text", None):
            return response.text.strip()

        return "LLM error: empty response."

    except Exception as e:
        return f"LLM error: {str(e)}"


# ---------------------------------------------------------
#  PUBLIC FUNCTION CALLED BY YOUR SERVICES
# ---------------------------------------------------------
def generate_llm_output(prompt_template: str, context: Dict[str, object]) -> str:
    """
    Main bridge for services:
    - Fills template with email/user data
    - Selects LLM mode via `_intent`
    - Executes with safety fallbacks
    """

    intent = context.get("_intent", "generic")

    # Safely inject template variables
    final_prompt = prompt_template.format_map(_SafeDict(context))

    # Dispatch based on intent
    if intent == "categorize":
        return _categorize(final_prompt)

    elif intent == "actions":
        return _extract_actions(final_prompt)

    elif intent == "draft":
        return _generate_draft(final_prompt)

    elif intent == "custom_draft":
        return _generate_custom_draft(final_prompt)

    elif intent == "agent":
        return _agent_chat(final_prompt)

    # fallback generic LLM call
    return _run_llm("You are a helpful assistant.", final_prompt)


# ---------------------------------------------------------
#   INTENT-SPECIFIC HANDLERS
# ---------------------------------------------------------

def _categorize(prompt: str) -> str:
    """
    Categorization handler — expects a single category word as output.
    """
    system_prompt = (
        "You are an email categorization AI. "
        "Respond ONLY with a single category word. "
        "No sentences, no explanation. "
        "Valid categories: important, newsletter, spam, to-do, meeting, follow-up, personal, other."
    )

    result = _run_llm(system_prompt, prompt)

    # Normalize
    result = result.lower().strip()

    # Hard sanitize unexpected outputs
    allowed = {
        "important", "newsletter", "spam", "to-do",
        "todo", "meeting", "follow-up", "personal", "other"
    }

    for cat in allowed:
        if cat in result:
            return cat.replace(" ", "-")

    return "other"  # safe fallback


def _extract_actions(prompt: str) -> str:
    """
    Extract structured tasks from an email.
    Returns JSON string.
    """
    system_prompt = (
        "You extract action items from emails. "
        "Return STRICT JSON list of task objects:\n"
        "[ {\"task\": \"...\", \"deadline\": \"...\" } ]\n"
        "If no tasks found, return an empty list []."
    )

    raw = _run_llm(system_prompt, prompt)

    # Clean off markdown fences (```json) and whitespace
    cleaned = raw.strip("` \n")

    # Try to parse it to ensure it's valid JSON format
    try:
        # If parsing succeeds, we know 'cleaned' is a valid JSON string.
        # We don't need to re-dump it, just return the string.
        json.loads(cleaned)
        return cleaned
    except Exception:
        # If parsing fails, return an empty JSON list as a robust fallback.
        # This prevents the raw, unformatted text from being passed to ActionItemService.
        return "[]"


def _generate_draft(prompt: str) -> str:
    """
    Generate a reply draft using user's auto-reply prompt.
    """
    system_prompt = (
        "You are an AI email assistant. Generate a natural, polite, well-structured reply. "
        "Include:\n- Subject line\n- Body\n- Signature\n"
        "Do NOT send the email, only draft it."
    )

    return _run_llm(system_prompt, prompt)


def _generate_custom_draft(prompt: str) -> str:
    """
    Handle user-specified instructions for drafts.
    """
    system_prompt = "You draft emails based on custom user instructions. Provide ONLY the draft content."

    return _run_llm(system_prompt, prompt)


def _agent_chat(prompt: str) -> str:
    """
    Phase 2: Email agent chatbot.
    """
    system_prompt = (
        "You are an Email Agent that can: summarize emails, show urgent tasks, "
        "find follow-ups, and explain inbox state. "
        "Always answer clearly, concisely, and based on the given context."
    )

    return _run_llm(system_prompt, prompt)


# ---------------------------------------------------------
#   SAFE TEMPLATE DICT
# ---------------------------------------------------------

class _SafeDict(dict):
    """Dict that avoids KeyError during template formatting."""
    def __missing__(self, key: str) -> str:
        return "{" + key + "}"
