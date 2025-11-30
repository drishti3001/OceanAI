from __future__ import annotations
from typing import Optional
from fastapi import APIRouter, Depends, Request , HTTPException
from pydantic import BaseModel
from backend.services.auto_reply_service import AutoReplyService

router = APIRouter(prefix="/api", tags=["drafts"])


def get_auto_reply_service(request: Request) -> AutoReplyService:
    return request.app.state.auto_reply_service


class ReplyRequest(BaseModel):
    email_id: str
    subject: Optional[str] = None
    body: Optional[str] = None
    persona: Optional[str] = None


class CustomDraftRequest(BaseModel):
    email_id: str
    instructions: str


@router.post("/generate_reply")
async def generate_reply(
    payload: ReplyRequest,
    service: AutoReplyService = Depends(get_auto_reply_service),
) -> dict:
    """Generate a draft reply for the selected email."""
    draft = service.generate_reply(payload.email_id, payload.persona)
    return {"email_id": payload.email_id, "draft": draft}


@router.post("/draft_email")
async def draft_email(
    payload: CustomDraftRequest,
    service: AutoReplyService = Depends(get_auto_reply_service),
) -> dict:
    """Create a draft based on custom instructions."""
    draft = service.create_custom_draft(payload.email_id, payload.instructions)
    return {"email_id": payload.email_id, "draft": draft}

class DeleteDraftRequest(BaseModel):
    email_id: str
    draft_index: int  # The index of the draft to delete (e.g., 0 for Draft 1)

# Add the new DELETE route
@router.delete("/drafts")
async def delete_draft_route(
    payload: DeleteDraftRequest,
    service: AutoReplyService = Depends(get_auto_reply_service),
) -> dict:
    """Delete a draft by index from the email record."""
    success = service.delete_draft(payload.email_id, payload.draft_index)
    if not success:
        raise HTTPException(status_code=404, detail="Draft not found or invalid index")
    return {"email_id": payload.email_id, "success": True}
