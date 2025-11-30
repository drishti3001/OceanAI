"""Prompt management routes."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel

from backend.services.prompt_brain import PromptBrain

router = APIRouter(prefix="/api", tags=["prompts"])


def get_prompt_brain(request: Request) -> PromptBrain:
    """Return the shared prompt brain instance."""
    return request.app.state.prompt_brain


class PromptPayload(BaseModel):
    """Schema for prompt updates."""

    id: str
    name: str
    description: str = ""
    template: str


@router.get("/prompts")
async def list_prompts(prompt_brain: PromptBrain = Depends(get_prompt_brain)) -> list[dict]:
    """Return all prompts so the UI can display/edit them."""
    return [prompt.to_dict() for prompt in prompt_brain.list_prompts()]


@router.put("/prompts/{prompt_id}")
async def upsert_prompt(
    prompt_id: str,
    payload: PromptPayload,
    prompt_brain: PromptBrain = Depends(get_prompt_brain),
) -> dict:
    """Update an existing prompt template (Handles both Create and Edit)."""
    if prompt_id != payload.id:
        raise HTTPException(status_code=400, detail="Prompt id mismatch")
    prompt = prompt_brain.upsert_prompt(payload.dict())
    return prompt.to_dict()


@router.delete("/prompts/{prompt_id}")
async def delete_prompt_route(
    prompt_id: str,
    prompt_brain: PromptBrain = Depends(get_prompt_brain),
) -> dict:
    """Delete a prompt by its ID."""
    success = prompt_brain.delete_prompt(prompt_id) 
    
    if not success:
        raise HTTPException(status_code=404, detail=f"Prompt ID '{prompt_id}' not found")
        
    return {"id": prompt_id, "success": True}