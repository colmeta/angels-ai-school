"""
Clarity Pearl AI Chatbot Service - PRODUCTION
Integrated intelligent chatbot using Clarity Pearl AI API
"""
from typing import Dict, Any, Optional, List
import httpx
from datetime import datetime
import os

from api.core.config import get_settings


class ClarityPearlChatbotService:
    """
    Clarity Pearl AI Chatbot - Production Ready
    For parent/teacher/student queries and assistance
    """
    
    def __init__(self):
        self.settings = get_settings()
        # Clarity Pearl AI (Chatbot)
        self.api_key = os.getenv('CLARITY_PEARL_API_KEY')  # Set in environment variables
        self.base_url = os.getenv('CLARITY_PEARL_API_URL', 'https://clarity-pearl-ai-api.onrender.com')
        self.timeout = 30.0
        
        if not self.api_key:
            raise ValueError("CLARITY_PEARL_API_KEY environment variable is required")
    
    async def chat(
        self,
        user_message: str,
        context: Optional[Dict[str, Any]] = None,
        customer_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Main chatbot endpoint - handles all user queries
        
        Args:
            user_message: User's question
            context: Optional context (school_id, user_id, student_id, etc.)
            customer_id: Unique ID for the user/customer
        
        Returns:
            Chatbot response with AI-generated answer
        """
        try:
            # Build request for Clarity Pearl AI
            context = context or {}
            customer_id = customer_id or context.get('user_id', 'anonymous')
            
            # Enhance message with context
            enhanced_message = self._build_message_with_context(user_message, context)
            
            # Call Clarity Pearl AI
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/v1/chat",
                    json={
                        "message": enhanced_message,
                        "customer_id": customer_id,
                        "channel": "school_system",
                        "metadata": {
                            "school_id": context.get('school_id'),
                            "user_role": context.get('user_role'),
                            "student_id": context.get('student_id'),
                            "timestamp": datetime.now().isoformat()
                        }
                    },
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    }
                )
                
                if response.status_code == 200:
                    result = response.json()
                    return {
                        "success": True,
                        "response": result.get("response", "I'm here to help! How can I assist you?"),
                        "conversation_id": result.get("conversation_id"),
                        "confidence": result.get("confidence", 0.9),
                        "ai_model": result.get("ai_model", "clarity-pearl"),
                        "tokens_used": result.get("tokens_used"),
                        "response_time_ms": result.get("response_time_ms"),
                        "timestamp": datetime.now().isoformat()
                    }
                else:
                    return {
                        "success": False,
                        "error": f"API error: {response.status_code}",
                        "fallback_response": self._get_fallback_response(user_message)
                    }
        
        except httpx.TimeoutException:
            return {
                "success": False,
                "error": "Request timeout",
                "fallback_response": "I'm currently experiencing delays. Please try again in a moment."
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "fallback_response": self._get_fallback_response(user_message)
            }
    
    def _build_message_with_context(self, user_message: str, context: Dict) -> str:
        """Build enhanced message with context"""
        if not context:
            return user_message
        
        # Add context to help AI understand better
        context_str = ""
        
        if context.get("school_id"):
            context_str += f"[School Context] "
        if context.get("user_role"):
            context_str += f"User is a {context['user_role']}. "
        if context.get("student_name"):
            context_str += f"Asking about student: {context['student_name']}. "
        
        if context_str:
            return f"{context_str}\n\nQuestion: {user_message}"
        
        return user_message
    
    def _get_fallback_response(self, user_message: str) -> str:
        """Provide helpful fallback responses when API fails"""
        message_lower = user_message.lower()
        
        if any(word in message_lower for word in ["fee", "payment", "balance", "pay"]):
            return "You can check fee balances by going to the Fees section or asking your school administrator."
        
        elif any(word in message_lower for word in ["attendance", "absent", "present"]):
            return "Attendance records can be viewed in the Attendance section of your dashboard."
        
        elif any(word in message_lower for word in ["grade", "marks", "result", "exam"]):
            return "Grades and exam results are available in the Academic Performance section."
        
        elif any(word in message_lower for word in ["homework", "assignment"]):
            return "You can view homework assignments in the Homework section."
        
        else:
            return "I'm here to help! You can ask me about fees, attendance, grades, homework, or any other school-related queries."
    
    async def get_contextual_help(
        self,
        user_role: str,
        page: str,
        school_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Provide contextual help based on where user is in the app
        
        Args:
            user_role: parent, teacher, admin, student
            page: Current page user is on
            school_id: School context
        
        Returns:
            Helpful tips and suggestions
        """
        role_page_help = {
            "parent": {
                "dashboard": "View your child's attendance, grades, and fee balance. Ask me anything!",
                "fees": "You can pay fees via Mobile Money (MTN or Airtel). Need help?",
                "attendance": "Check which days your child was present or absent. I can provide insights!",
                "grades": "View your child's exam results and performance trends."
            },
            "teacher": {
                "dashboard": "Take photos of attendance sheets or results - I'll process them automatically!",
                "attendance": "Upload a photo of your attendance register, and I'll enter the data.",
                "grading": "Upload exam results via photo, and I'll calculate grades automatically.",
                "homework": "Create assignments quickly. I can help generate homework questions!"
            },
            "admin": {
                "dashboard": "View school-wide analytics and insights. What would you like to know?",
                "reports": "Generate government reports automatically. I'll format everything!",
                "finances": "Track fee collection, expenses, and financial health.",
                "analytics": "Get AI-powered insights about your school's performance."
            },
            "student": {
                "dashboard": "Check your grades, homework, and upcoming events!",
                "homework": "View assignments and submit your work online.",
                "grades": "See your exam results and track your progress.",
                "library": "Check which books you've borrowed and due dates."
            }
        }
        
        help_text = role_page_help.get(user_role, {}).get(page, "How can I help you today?")
        
        return {
            "success": True,
            "help_text": help_text,
            "quick_actions": self._get_quick_actions(user_role, page),
            "tips": self._get_tips(user_role)
        }
    
    def _get_quick_actions(self, user_role: str, page: str) -> List[str]:
        """Get quick action suggestions"""
        actions = {
            "parent": ["Check fees", "View attendance", "See grades", "Pay fees"],
            "teacher": ["Take attendance photo", "Upload results", "Assign homework"],
            "admin": ["Generate report", "View analytics", "Manage fees"],
            "student": ["Check homework", "View grades", "Library books"]
        }
        return actions.get(user_role, [])
    
    def _get_tips(self, user_role: str) -> List[str]:
        """Get helpful tips for user role"""
        tips = {
            "parent": [
                "💡 Pay fees early to get 5% discount!",
                "📱 Enable notifications to get instant updates",
                "🎓 Check homework daily to track your child's progress"
            ],
            "teacher": [
                "📸 Take photos instead of manual entry - save hours!",
                "🤖 Use AI to generate report cards automatically",
                "⚡ Bulk operations let you mark entire class at once"
            ],
            "admin": [
                "📊 Generate government reports in 1 click",
                "💰 Track fee collection rate to improve cash flow",
                "🎯 Use analytics to identify at-risk students"
            ],
            "student": [
                "📚 Borrow library books online",
                "✅ Submit homework early to get bonus points",
                "📊 Track your performance trends"
            ]
        }
        return tips.get(user_role, [])
    
    async def ask_about_student(
        self,
        student_id: str,
        question: str,
        school_id: str
    ) -> Dict[str, Any]:
        """
        Answer questions about a specific student
        Uses AI to analyze student data and provide insights
        """
        context = {
            "student_id": student_id,
            "school_id": school_id,
            "data_type": "student_query"
        }
        
        enhanced_question = f"Student query about student ID {student_id}: {question}. Provide helpful insights and suggestions."
        
        return await self.chat(
            user_message=enhanced_question,
            context=context,
            customer_id=f"student_{student_id}"
        )


# Singleton instance
_chatbot_service: Optional[ClarityPearlChatbotService] = None


def get_chatbot_service() -> ClarityPearlChatbotService:
    """Get chatbot service instance"""
    global _chatbot_service
    if _chatbot_service is None:
        _chatbot_service = ClarityPearlChatbotService()
    return _chatbot_service
