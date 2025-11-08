"""
WhatsApp Service
Handles WhatsApp notifications and messaging (NO chatbot - user will provide API)
Sends attendance, fees, grades, and other notifications via WhatsApp
"""
from typing import Dict, Any, List, Optional
from datetime import datetime
import json

from api.services.database import get_db_manager


class WhatsAppService:
    """Service for WhatsApp messaging (notifications only)"""
    
    def __init__(self, school_id: str):
        self.school_id = school_id
        self.db = get_db_manager()
        # TODO: User will provide WhatsApp API key
        self.api_key = None  # Will be set from environment
        self.api_url = None  # Will be set from environment
    
    # ============================================================================
    # SEND MESSAGES
    # ============================================================================
    
    def send_message(
        self,
        recipient_phone: str,
        message: str,
        recipient_name: Optional[str] = None,
        message_type: str = 'text',
        media_url: Optional[str] = None,
        template_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Send WhatsApp message to individual
        
        Args:
            recipient_phone: Phone number (e.g., +256700123456)
            message: Message text
            message_type: text, image, document
            media_url: URL for media (if type is image/document)
            template_name: Pre-approved template name
        """
        # Queue message in database
        query = """
        INSERT INTO whatsapp_messages (
            school_id, recipient_type, recipient_phone, recipient_name,
            message_type, message_content, media_url, template_name, status
        ) VALUES (%s, 'individual', %s, %s, %s, %s, %s, %s, 'pending')
        RETURNING id
        """
        
        result = self.db.execute_query(
            query,
            (self.school_id, recipient_phone, recipient_name, message_type, message, media_url, template_name),
            fetch=True
        )
        
        message_id = result[0]['id']
        
        # TODO: Actually send via WhatsApp API (user will provide)
        # For now, just queue it
        # success = self._send_via_api(recipient_phone, message, media_url)
        
        return {
            "success": True,
            "message_id": message_id,
            "status": "queued",
            "note": "Message queued. Will be sent via WhatsApp API."
        }
    
    def send_attendance_notification(
        self,
        student_id: str,
        status: str,
        date: str
    ) -> Dict[str, Any]:
        """
        Send attendance notification to parent
        
        Example: "Mary is present today"
        """
        # Get student and parent info
        query = """
        SELECT 
            s.first_name, s.last_name, s.class_name,
            p.phone, p.first_name as parent_name
        FROM students s
        JOIN student_parents sp ON sp.student_id = s.id
        JOIN parents p ON p.id = sp.parent_id
        WHERE s.id = %s
        """
        
        rows = self.db.execute_query(query, (student_id,), fetch=True)
        
        if not rows:
            return {"success": False, "error": "Student or parent not found"}
        
        results = []
        for row in rows:
            student_name = f"{row['first_name']} {row['last_name']}"
            class_name = row['class_name']
            
            # Message template
            if status == 'present':
                message = f"✅ {student_name} ({class_name}) is present today."
            elif status == 'absent':
                message = f"❌ {student_name} ({class_name}) is absent today."
            else:
                message = f"ℹ️ {student_name} ({class_name}) - Status: {status}"
            
            result = self.send_message(
                recipient_phone=row['phone'],
                message=message,
                recipient_name=row['parent_name'],
                template_name='attendance_update'
            )
            results.append(result)
        
        return {
            "success": True,
            "sent_to": len(results),
            "results": results
        }
    
    def send_fee_notification(
        self,
        student_id: str,
        balance: float,
        due_date: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Send fee balance notification to parent
        
        Example: "Mary's fee balance is 50,000 UGX. Due: Jan 31"
        """
        # Get student and parent info
        query = """
        SELECT 
            s.first_name, s.last_name, s.class_name,
            p.phone, p.first_name as parent_name
        FROM students s
        JOIN student_parents sp ON sp.student_id = s.id
        JOIN parents p ON p.id = sp.parent_id
        WHERE s.id = %s
        """
        
        rows = self.db.execute_query(query, (student_id,), fetch=True)
        
        if not rows:
            return {"success": False, "error": "Student or parent not found"}
        
        results = []
        for row in rows:
            student_name = f"{row['first_name']} {row['last_name']}"
            
            message = f"💰 Fee Balance for {student_name}:\n\n"
            message += f"Amount: {balance:,.0f} UGX\n"
            if due_date:
                message += f"Due Date: {due_date}\n"
            message += f"\nPay via Mobile Money or dial *123*789#"
            
            result = self.send_message(
                recipient_phone=row['phone'],
                message=message,
                recipient_name=row['parent_name'],
                template_name='fee_reminder'
            )
            results.append(result)
        
        return {
            "success": True,
            "sent_to": len(results),
            "results": results
        }
    
    def send_grades_notification(
        self,
        student_id: str,
        assessment_name: str,
        subject: str,
        marks: float,
        max_marks: float,
        grade: str
    ) -> Dict[str, Any]:
        """
        Send grades notification to parent
        
        Example: "Mary scored 85/100 (A) in Math - Mid-Term Exam"
        """
        query = """
        SELECT 
            s.first_name, s.last_name, s.class_name,
            p.phone, p.first_name as parent_name
        FROM students s
        JOIN student_parents sp ON sp.student_id = s.id
        JOIN parents p ON p.id = sp.parent_id
        WHERE s.id = %s
        """
        
        rows = self.db.execute_query(query, (student_id,), fetch=True)
        
        if not rows:
            return {"success": False, "error": "Student or parent not found"}
        
        results = []
        for row in rows:
            student_name = f"{row['first_name']} {row['last_name']}"
            
            message = f"📚 {assessment_name} - {subject}\n\n"
            message += f"Student: {student_name}\n"
            message += f"Score: {marks}/{max_marks} ({grade})\n"
            message += f"\nView full report card in parent portal."
            
            result = self.send_message(
                recipient_phone=row['phone'],
                message=message,
                recipient_name=row['parent_name'],
                template_name='grades_update'
            )
            results.append(result)
        
        return {
            "success": True,
            "sent_to": len(results),
            "results": results
        }
    
    def send_broadcast(
        self,
        recipients: List[str],
        message: str,
        media_url: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Send broadcast message to multiple recipients
        
        Example: School announcement to all parents
        """
        results = []
        
        for phone in recipients:
            result = self.send_message(
                recipient_phone=phone,
                message=message,
                media_url=media_url
            )
            results.append(result)
        
        return {
            "success": True,
            "sent_to": len(results),
            "results": results
        }
    
    # ============================================================================
    # TEMPLATES
    # ============================================================================
    
    def create_template(
        self,
        name: str,
        category: str,
        template_text: str,
        language: str = 'en',
        parameters: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Create WhatsApp message template
        
        Templates must be pre-approved by WhatsApp
        """
        query = """
        INSERT INTO whatsapp_templates (
            school_id, name, category, language, template_text, parameters
        ) VALUES (%s, %s, %s, %s, %s, %s)
        ON CONFLICT (school_id, name, language)
        DO UPDATE SET
            template_text = EXCLUDED.template_text,
            parameters = EXCLUDED.parameters,
            updated_at = CURRENT_TIMESTAMP
        RETURNING id
        """
        
        result = self.db.execute_query(
            query,
            (self.school_id, name, category, language, template_text, parameters or []),
            fetch=True
        )
        
        return {
            "success": True,
            "template_id": result[0]['id'],
            "name": name,
            "note": "Template created. Submit to WhatsApp for approval."
        }
    
    def get_templates(self, category: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get all templates for school"""
        query = """
        SELECT id, name, category, language, template_text, is_approved
        FROM whatsapp_templates
        WHERE school_id = %s AND is_active = true
        """
        
        params = [self.school_id]
        
        if category:
            query += " AND category = %s"
            params.append(category)
        
        query += " ORDER BY category, name"
        
        return self.db.execute_query(query, tuple(params), fetch=True)
    
    # ============================================================================
    # MESSAGE STATUS
    # ============================================================================
    
    def get_message_status(self, message_id: str) -> Dict[str, Any]:
        """Get status of sent message"""
        query = """
        SELECT 
            id, recipient_phone, message_content, status,
            sent_at, delivered_at, read_at, error_message
        FROM whatsapp_messages
        WHERE id = %s
        """
        
        result = self.db.execute_query(query, (message_id,), fetch=True)
        
        if not result:
            return {"success": False, "error": "Message not found"}
        
        return {
            "success": True,
            **result[0]
        }
    
    def get_pending_messages(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get pending messages to be sent"""
        query = """
        SELECT 
            id, recipient_phone, message_type, message_content, 
            media_url, template_name, created_at
        FROM whatsapp_messages
        WHERE school_id = %s 
        AND status = 'pending'
        AND (scheduled_at IS NULL OR scheduled_at <= CURRENT_TIMESTAMP)
        ORDER BY created_at ASC
        LIMIT %s
        """
        
        return self.db.execute_query(query, (self.school_id, limit), fetch=True)
    
    def mark_message_sent(
        self,
        message_id: str,
        whatsapp_message_id: Optional[str] = None
    ) -> None:
        """Mark message as sent"""
        query = """
        UPDATE whatsapp_messages
        SET status = 'sent',
            sent_at = CURRENT_TIMESTAMP,
            whatsapp_message_id = %s
        WHERE id = %s
        """
        
        self.db.execute_query(query, (whatsapp_message_id, message_id))
    
    def mark_message_failed(self, message_id: str, error: str) -> None:
        """Mark message as failed"""
        query = """
        UPDATE whatsapp_messages
        SET status = 'failed',
            error_message = %s,
            updated_at = CURRENT_TIMESTAMP
        WHERE id = %s
        """
        
        self.db.execute_query(query, (error, message_id))


def get_whatsapp_service(school_id: str) -> WhatsAppService:
    """Helper to get WhatsApp service instance"""
    return WhatsAppService(school_id)
