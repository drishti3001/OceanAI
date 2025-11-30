"""FastAPI entrypoint for the Prompt-Driven Email Productivity Agent."""
from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI

from backend.routes import agent as agent_routes
from backend.routes import drafts as drafts_routes
from backend.routes import inbox as inbox_routes
from backend.routes import prompts as prompts_routes
from backend.services.action_item_service import ActionItemService
from backend.services.agent_service import AgentService
from backend.services.auto_reply_service import AutoReplyService
from backend.services.categorization_service import CategorizationService
from backend.services.inbox_service import InboxService
from backend.services.prompt_brain import PromptBrain

BASE_DIR = Path(__file__).resolve().parent.parent

app = FastAPI(title="Email Productivity Agent", version="0.1.0")

prompt_brain = PromptBrain(BASE_DIR / "prompts.json")
inbox_service = InboxService(BASE_DIR / "data" / "inbox.json")
categorization_service = CategorizationService(inbox_service, prompt_brain)
action_service = ActionItemService(inbox_service, prompt_brain)
auto_reply_service = AutoReplyService(inbox_service, prompt_brain)
agent_service = AgentService(inbox_service, prompt_brain)

app.state.prompt_brain = prompt_brain
app.state.inbox_service = inbox_service
app.state.categorization_service = categorization_service
app.state.action_service = action_service
app.state.auto_reply_service = auto_reply_service
app.state.agent_service = agent_service

app.include_router(inbox_routes.router)
app.include_router(prompts_routes.router)
app.include_router(agent_routes.router)
app.include_router(drafts_routes.router)


@app.get("/api/health")
def health() -> dict:
    """Simple readiness check."""
    return {"status": "ok"}
