"""API helper functions for communicating with the backend FastAPI server."""
from __future__ import annotations

import os
from typing import Any, Dict, List, Optional

import requests
import streamlit as st # Ensure streamlit is imported for caching

# Base URL for backend (can be overridden via environment variable)
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")


def _make_request(method: str, endpoint: str, **kwargs) -> Any:
    """Perform a backend API request with error handling."""
    url = f"{API_BASE_URL}{endpoint}"
    try:
        response = requests.request(method, url, **kwargs)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.ConnectionError as e:
        raise Exception(f"Cannot connect to backend at {url}. Is the server running? Error: {str(e)}")
    except requests.exceptions.HTTPError as e:
        raise Exception(f"HTTP error {response.status_code}: {response.text}")
    except requests.exceptions.RequestException as e:
        raise Exception(f"API request failed: {str(e)}")


# ------------------ Inbox ------------------
@st.cache_data(ttl=5)
def load_inbox() -> List[Dict[str, Any]]:
    """Fetch inbox emails. Ensures consistent list return type."""
    data = _make_request("GET", "/api/load_inbox")
    return data if isinstance(data, list) else []


# ------------------ Email Processing ------------------
def categorize_email(email_id: str) -> Dict[str, Any]:
    """Categorize an email by ID."""
    return _make_request("POST", "/api/categorize", json={"email_id": email_id})


def extract_actions(email_id: str) -> Dict[str, Any]:
    """Extract action items from an email."""
    return _make_request("POST", "/api/extract_actions", json={"email_id": email_id})


def generate_reply(email_id: str, persona: Optional[str] = None) -> Dict[str, Any]:
    """Generate a reply draft for an email."""
    payload = {"email_id": email_id}
    if persona:
        payload["persona"] = persona
    return _make_request("POST", "/api/generate_reply", json=payload)


def draft_email(email_id: str, instructions: str) -> Dict[str, Any]:
    """Create a custom draft based on instructions."""
    return _make_request(
        "POST",
        "/api/draft_email",
        json={"email_id": email_id, "instructions": instructions},
    )


# ------------------ Prompt Brain ------------------
@st.cache_data(ttl=60)
def list_prompts() -> List[Dict[str, Any]]:
    """Retrieve all prompt templates."""
    data = _make_request("GET", "/api/prompts")
    return data if isinstance(data, list) else []


def update_prompt(prompt_id: str, prompt_data: Dict[str, Any]) -> Dict[str, Any]:
    """Update a single prompt by ID."""
    return _make_request("PUT", f"/api/prompts/{prompt_id}", json=prompt_data)

def delete_prompt(prompt_id: str) -> Dict[str, Any]: 
    """Delete a prompt by ID."""
    return _make_request("DELETE", f"/api/prompts/{prompt_id}")


# ------------------ Agent Queries ------------------
# CRITICAL FIX: Updated signature to accept email_id
def agent_query(query_type: str, email_id: Optional[str] = None) -> Dict[str, Any]:
    """Execute a predefined inbox query."""
    payload = {"query_type": query_type}
    if email_id:
        payload["email_id"] = email_id
    return _make_request("POST", "/api/agent_query", json=payload)


def delete_draft(email_id: str, draft_index: int) -> Dict[str, Any]:
    """Delete a specific draft by index."""
    return _make_request(
        "DELETE",
        "/api/drafts",
        json={"email_id": email_id, "draft_index": draft_index},
    )