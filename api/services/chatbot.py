"""
Clarity Pearl AI Chatbot Service
Integrated intelligent chatbot using Clarity Engine
"""
from typing import Dict, Any, Optional, List
import httpx
from datetime import datetime

from api.core.config import get_settings


class ClarityChatbotService:
    """
    Clarity Pearl AI Chatbot - Production Ready
    Supports all 10 domains for comprehensive school assistance
    """
    
    def __init__(self):
        self.settings = get_settings()
        self.api_key = "cp_live_demo_2024_clarity_pearl_ai_test_key_001"
        self.base_url = "https://veritas-engine-zae0.onrender.com"
        self.timeout = 30.0
        
        # Available domains
        self.domains = {
            "education": "Curriculum analysis, student performance, accreditation",
            "financial": "Financial analysis, fee tracking, budgets",
            "legal": "Contract review, compliance, policies",
            "data-science": "Analytics, predictions, insights",
            "healthcare": "Student health records, medical compliance",
            "expenses": "Expense tracking, cost optimization",
            "data-entry": "OCR, data extraction, validation",
            "security": "Safety, compliance audits",
            "ngo": "Grant writing, impact assessment",
            "proposals": "Documentation, report generation"
        }
    
    async def chat(
        self,
        user_message: str,
        context: Optional[Dict[str, Any]] = None,
        domain: str = "education"
    ) -> Dict[str, Any]:
        """
        Main chatbot endpoint - handles all user queries
        
        Args:
            user_message: User's question
            context: Optional context (school_id, user_id, student_id, etc.)
            domain: Which Clarity domain to use
        
        Returns:
            Chatbot response with analysis and suggestions
        """
        try:
            # Build directive with context
            directive = self._build_directive(user_message, context)
            
            # Call Clarity API
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/instant/analyze",
                    json={
                        "directive": directive,
                        "domain": domain
                    },
                    headers={
                        "Content-Type": "application/json",
                        "Authorization": f"Bearer {self.api_key}"
                    }
                )
                
                if response.status_code == 200:
                    result = response.json()
                    return {
                        "success": True,
                        "response": self._format_response(result),
                        "raw_analysis": result.get("analysis", {}),
                        "confidence": result.get("analysis", {}).get("confidence", 0),
                        "domain": domain,
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
    
    def _build_directive(self, user_message: str, context: Optional[Dict] = None) -> str:
        """Build enhanced directive with context"""
        if not context:
            return user_message
        
        # Add context to help Clarity understand the query better
        context_str = ""
        if context.get("school_id"):
            context_str += f"School ID: {context['school_id']}. "
        if context.get("user_role"):
            context_str += f"User role: {context['user_role']}. "
        if context.get("student_name"):
            context_str += f"Student: {context['student_name']}. "
        
        return f"{context_str}{user_message}"
    
    def _format_response(self, raw_result: Dict) -> str:
        """Format Clarity response for user consumption"""
        analysis = raw_result.get("analysis", {})
        summary = analysis.get("summary", "")
        findings = analysis.get("findings", [])
        next_steps = analysis.get("next_steps", "")
        
        response = summary
        
        if findings:
            response += "\n\n📊 Key Points:\n"
            for finding in findings[:3]:  # Top 3 findings
                response += f"• {finding}\n"
        
        if next_steps:
            response += f"\n💡 Suggestion: {next_steps}"
        
        return response
    
    def _get_fallback_response(self, user_message: str) -> str:
        """Provide helpful fallback responses"""
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
        # In production, fetch actual student data from database
        # For now, use Clarity to analyze the question
        
        context = {
            "student_id": student_id,
            "school_id": school_id,
            "data_type": "student_query"
        }
        
        directive = f"Student query: {question}. Provide helpful insights and suggestions."
        
        return await self.chat(
            user_message=directive,
            context=context,
            domain="education"
        )
    
    async def generate_report_summary(
        self,
        report_type: str,
        data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Use Clarity to generate professional report summaries
        
        Args:
            report_type: attendance, grades, financial, etc.
            data: Report data to summarize
        
        Returns:
            AI-generated summary and insights
        """
        directive = f"Summarize this {report_type} report professionally: {data}"
        
        domain = "education" if report_type in ["attendance", "grades"] else "financial"
        
        return await self.chat(
            user_message=directive,
            domain=domain
        )


def get_chatbot_service() -> ClarityChatbotService:
    """Get chatbot service instance"""
    return ClarityChatbotService()
