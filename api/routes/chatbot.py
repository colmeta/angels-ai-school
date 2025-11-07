from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from api.services.chatbot import ChatbotGateway


class ChatMessage(BaseModel):
    role: str = Field(..., description="Role of the speaker (user/assistant/system).")
    content: str = Field(..., description="Message content.")


class ChatbotRequest(BaseModel):
    school_id: str
    messages: List[ChatMessage]
    locale: Optional[str] = Field(default="en")
    channel: Optional[str] = Field(default="parent_app")


router = APIRouter(tags=["Chatbot"])


@router.post("/chatbot/query")
def chatbot_query(payload: ChatbotRequest) -> Dict[str, Any]:
    try:
        gateway = ChatbotGateway(payload.school_id)
        result = gateway.send_message(
            [message.dict() for message in payload.messages],
            locale=payload.locale or "en",
            channel=payload.channel or "parent_app",
        )
        return {"success": True, **result}
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
