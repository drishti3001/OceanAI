"""Inbox-related API routes."""
from __future__ import annotations

from fastapi import APIRouter, Depends, Request

from backend.services.inbox_service import InboxService

router = APIRouter(prefix="/api", tags=["inbox"])


def get_inbox_service(request: Request) -> InboxService:
    """Resolve the inbox service from application state."""
    return request.app.state.inbox_service


@router.get("/load_inbox")
async def load_inbox(inbox: InboxService = Depends(get_inbox_service)) -> list[dict]:
    """Return the current inbox snapshot."""
    emails = inbox.list_emails()
    return [
        {
            "id": email.id,
            "sender": email.sender,
            "subject": email.subject,
            "timestamp": email.timestamp.isoformat(),
            "body": email.body,
            "category": email.category,
            "action_items": email.action_items,
            "drafts": email.drafts,
        }
        for email in emails
    ]
