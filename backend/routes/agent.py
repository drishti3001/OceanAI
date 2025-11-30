"""Agent-related API routes."""
from __future__ import annotations

from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel
from typing import Optional # Import Optional

from backend.services.action_item_service import ActionItemService
from backend.services.agent_service import AgentService
from backend.services.categorization_service import CategorizationService

router = APIRouter(prefix="/api", tags=["agent"])


def get_categorization_service(request: Request) -> CategorizationService:
    return request.app.state.categorization_service


def get_action_service(request: Request) -> ActionItemService:
    return request.app.state.action_service


def get_agent_service(request: Request) -> AgentService:
    return request.app.state.agent_service


class EmailRequest(BaseModel):
    email_id: str


# CRITICAL FIX: Update schema to accept optional email_id
class AgentQueryRequest(BaseModel):
    query_type: str
    email_id: Optional[str] = None # New optional field


@router.post("/categorize")
async def categorize_email(
    payload: EmailRequest,
    service: CategorizationService = Depends(get_categorization_service),
) -> dict:
    """Categorize the selected email."""
    category = service.categorize_email(payload.email_id)
    return {"email_id": payload.email_id, "category": category}


@router.post("/extract_actions")
async def extract_actions(
    payload: EmailRequest,
    service: ActionItemService = Depends(get_action_service),
) -> dict:
    """Extract and persist action items."""
    actions = service.extract(payload.email_id)
    return {"email_id": payload.email_id, "action_items": actions}


@router.post("/agent_query")
async def agent_query(
    payload: AgentQueryRequest,
    service: AgentService = Depends(get_agent_service),
) -> dict:
    """Run a higher-level inbox query."""
    # CRITICAL FIX: Pass the email_id to the service layer
    response = service.run_query(payload.query_type, payload.email_id) 
    return {"query_type": payload.query_type, "response": response}