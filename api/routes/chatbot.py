"""
Chatbot API Routes - Clarity Pearl AI Powered
Production-ready chatbot with 10 AI domains
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List

from api.services.chatbot import get_chatbot_service


router = APIRouter(tags=["Chatbot"])


# ============================================================================
# REQUEST MODELS
# ============================================================================

class ChatMessageNew(BaseModel):
    message: str = Field(..., description="User's question or message")
    school_id: str = Field(..., description="School ID for context")
    user_id: Optional[str] = Field(None, description="User ID")
    user_role: Optional[str] = Field(None, description="parent, teacher, admin, student")
    student_id: Optional[str] = Field(None, description="Student ID if asking about specific student")
    context: Optional[Dict[str, Any]] = Field(None, description="Additional context")
    domain: str = Field("education", description="Clarity domain: education, financial, legal, etc.")


class ContextualHelpRequest(BaseModel):
    user_role: str = Field(..., description="User role")
    page: str = Field(..., description="Current page user is on")
    school_id: Optional[str] = None


class StudentQueryRequest(BaseModel):
    student_id: str
    question: str
    school_id: str


# Legacy support for old chatbot format
class ChatMessage(BaseModel):
    role: str = Field(..., description="Role of the speaker (user/assistant/system).")
    content: str = Field(..., description="Message content.")


class ChatbotRequest(BaseModel):
    school_id: str
    messages: List[ChatMessage]
    locale: Optional[str] = Field(default="en")
    channel: Optional[str] = Field(default="parent_app")


# ============================================================================
# ENDPOINTS
# ============================================================================

@router.post("/chatbot/message")
async def send_message(data: ChatMessageNew):
    """
    **Clarity Pearl AI Chatbot** - Send message and get intelligent response
    
    **Supports 10 AI Domains:**
    - `education`: Curriculum, student performance, accreditation
    - `financial`: Financial analysis, fee tracking, budgets
    - `legal`: Contract review, compliance, policies  
    - `healthcare`: Student health records, medical compliance
    - `data-science`: Analytics, predictions, insights
    - `expenses`: Expense tracking, cost optimization
    - `data-entry`: OCR, data extraction, validation
    - `security`: Safety, compliance audits
    - `ngo`: Grant writing, impact assessment
    - `proposals`: Documentation, report generation
    
    **Example Questions:**
    - "What's my child's fee balance?"
    - "How many days was John absent this month?"
    - "Show me John's grade trends"
    - "Generate a report on Class 5 performance"
    - "How do I pay fees via Mobile Money?"
    """
    chatbot = get_chatbot_service()
    
    # Build context
    context = data.context or {}
    context.update({
        "school_id": data.school_id,
        "user_id": data.user_id,
        "user_role": data.user_role,
        "student_id": data.student_id
    })
    
    result = await chatbot.chat(
        user_message=data.message,
        context=context,
        domain=data.domain
    )
    
    return result


@router.post("/chatbot/help")
async def get_contextual_help(data: ContextualHelpRequest):
    """
    Get contextual help based on where user is in the app
    
    Returns helpful tips, quick actions, and suggestions based on:
    - User role (parent, teacher, admin, student)
    - Current page they're viewing
    - School context
    
    **Example**: Parent on fees page gets fee payment help
    """
    chatbot = get_chatbot_service()
    
    result = await chatbot.get_contextual_help(
        user_role=data.user_role,
        page=data.page,
        school_id=data.school_id
    )
    
    return result


@router.post("/chatbot/ask-about-student")
async def ask_about_student(data: StudentQueryRequest):
    """
    Ask AI questions about a specific student
    
    Uses Clarity Education Intelligence to analyze student data
    
    **Example Questions:**
    - "How is John performing this term?"
    - "What are John's attendance trends?"
    - "Is John at risk of failing?"
    - "Show me John's strengths and weaknesses"
    """
    chatbot = get_chatbot_service()
    
    result = await chatbot.ask_about_student(
        student_id=data.student_id,
        question=data.question,
        school_id=data.school_id
    )
    
    return result


@router.get("/chatbot/domains")
async def get_available_domains():
    """
    Get all available Clarity AI domains
    
    Returns list of 10 specialized AI domains that power the chatbot
    """
    chatbot = get_chatbot_service()
    
    return {
        "success": True,
        "domains": chatbot.domains,
        "total": len(chatbot.domains),
        "api_status": "production_ready"
    }


# ============================================================================
# LEGACY ENDPOINT (for backward compatibility)
# ============================================================================

@router.post("/chatbot/query")
async def chatbot_query_legacy(payload: ChatbotRequest) -> Dict[str, Any]:
    """
    Legacy chatbot endpoint - maintained for backward compatibility
    
    **Recommendation**: Use `/chatbot/message` for new implementations
    """
    try:
        # Convert legacy format to new format
        if payload.messages:
            last_message = payload.messages[-1]
            
            chatbot = get_chatbot_service()
            result = await chatbot.chat(
                user_message=last_message.content,
                context={"school_id": payload.school_id},
                domain="education"
            )
            
            return {"success": True, **result}
        else:
            return {
                "success": False,
                "error": "No messages provided"
            }
    
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
