"""
Angels AI - Parent Engagement Agent Service
The Oracle - 24/7 WhatsApp/SMS parent support for African schools
"""

from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from database import *
import json
import os


class ParentEngagementService:
    """
    24/7 Parent engagement via WhatsApp/SMS
    Handles fee reminders, academic updates, event notifications
    Supports multiple African languages
    """
    
    def __init__(self, school_id: str):
        self.school_id = school_id
        self.parent_ops = get_parent_ops()
        self.student_ops = get_student_ops()
        self.fee_ops = get_fee_ops()
        self.message_ops = get_message_ops()
        self.db = get_db()
    
    # ============================================
    # FEE REMINDER SYSTEM
    # ============================================
    
    def send_fee_reminders(self, reminder_type: str = 'upcoming') -> Dict[str, Any]:
        """
        Send automated fee reminders to parents
        
        Args:
            reminder_type: 'upcoming' (7 days before), 'due' (on due date), 'overdue'
        
        Returns:
            Summary of messages sent
        """
        messages_sent = []
        
        if reminder_type == 'overdue':
            # Get all overdue fees
            overdue_fees = self.fee_ops.get_overdue_fees(self.school_id)
            
            for fee in overdue_fees:
                message = self._create_overdue_fee_message(fee)
                result = self._send_whatsapp_message(
                    parent_phone=fee['whatsapp_number'],
                    parent_id=fee.get('parent_id'),
                    student_id=fee['student_id'],
                    message_body=message,
                    message_type='fee_reminder_overdue'
                )
                messages_sent.append(result)
        
        elif reminder_type == 'due':
            # Get fees due today
            query = """
            SELECT sf.*, s.first_name, s.last_name, s.admission_number,
                   p.primary_phone, p.whatsapp_number, p.email, p.first_name as parent_first_name,
                   p.preferred_language
            FROM student_fees sf
            JOIN students s ON sf.student_id = s.id
            JOIN student_parent_relationships spr ON s.id = spr.student_id AND spr.is_primary_contact = true
            JOIN parents p ON spr.parent_id = p.id
            WHERE s.school_id = %s 
            AND sf.due_date = CURRENT_DATE
            AND sf.payment_status != 'paid'
            AND s.enrollment_status = 'active'
            """
            fees_due = self.db.execute_query(query, (self.school_id,))
            
            for fee in fees_due:
                message = self._create_due_fee_message(fee)
                result = self._send_whatsapp_message(
                    parent_phone=fee['whatsapp_number'],
                    parent_id=fee.get('parent_id'),
                    student_id=fee['student_id'],
                    message_body=message,
                    message_type='fee_reminder_due'
                )
                messages_sent.append(result)
        
        elif reminder_type == 'upcoming':
            # Get fees due in 7 days
            query = """
            SELECT sf.*, s.first_name, s.last_name, s.admission_number,
                   p.primary_phone, p.whatsapp_number, p.email, p.first_name as parent_first_name,
                   p.preferred_language
            FROM student_fees sf
            JOIN students s ON sf.student_id = s.id
            JOIN student_parent_relationships spr ON s.id = spr.student_id AND spr.is_primary_contact = true
            JOIN parents p ON spr.parent_id = p.id
            WHERE s.school_id = %s 
            AND sf.due_date = CURRENT_DATE + INTERVAL '7 days'
            AND sf.payment_status != 'paid'
            AND s.enrollment_status = 'active'
            """
            fees_upcoming = self.db.execute_query(query, (self.school_id,))
            
            for fee in fees_upcoming:
                message = self._create_upcoming_fee_message(fee)
                result = self._send_whatsapp_message(
                    parent_phone=fee['whatsapp_number'],
                    parent_id=fee.get('parent_id'),
                    student_id=fee['student_id'],
                    message_body=message,
                    message_type='fee_reminder_upcoming'
                )
                messages_sent.append(result)
        
        return {
            'reminder_type': reminder_type,
            'messages_sent': len(messages_sent),
            'successful': sum(1 for m in messages_sent if m.get('success')),
            'failed': sum(1 for m in messages_sent if not m.get('success')),
            'details': messages_sent
        }
    
    def _create_overdue_fee_message(self, fee: Dict) -> str:
        """Create overdue fee reminder message"""
        days_overdue = (datetime.now().date() - fee['due_date']).days
        
        message = f"""
Dear {fee['parent_first_name']},

⚠️ OVERDUE FEE NOTICE

Student: {fee['first_name']} {fee['last_name']}
Admission No: {fee['admission_number']}

Outstanding Balance: KES {fee['balance']:,.2f}
Due Date: {fee['due_date']}
Days Overdue: {days_overdue}

Please make payment as soon as possible to avoid late fees.

Pay via M-Pesa:
Paybill: [SCHOOL_PAYBILL]
Account: {fee['admission_number']}

For assistance, reply to this message.
        """.strip()
        
        return message
    
    def _create_due_fee_message(self, fee: Dict) -> str:
        """Create due date fee reminder"""
        message = f"""
Dear {fee['parent_first_name']},

📅 FEE DUE TODAY

Student: {fee['first_name']} {fee['last_name']}
Admission No: {fee['admission_number']}

Amount Due: KES {fee['balance']:,.2f}
Due Date: TODAY

Pay via M-Pesa:
Paybill: [SCHOOL_PAYBILL]
Account: {fee['admission_number']}

Thank you for your prompt payment!
        """.strip()
        
        return message
    
    def _create_upcoming_fee_message(self, fee: Dict) -> str:
        """Create upcoming fee reminder (7 days before)"""
        message = f"""
Dear {fee['parent_first_name']},

📌 UPCOMING FEE REMINDER

Student: {fee['first_name']} {fee['last_name']}
Admission No: {fee['admission_number']}

Amount: KES {fee['balance']:,.2f}
Due Date: {fee['due_date']} (7 days from today)

Early payment helps us serve your child better!

Pay via M-Pesa:
Paybill: [SCHOOL_PAYBILL]
Account: {fee['admission_number']}
        """.strip()
        
        return message
    
    # ============================================
    # ACADEMIC PROGRESS UPDATES
    # ============================================
    
    def send_academic_progress_report(self, student_id: str, report_data: Dict) -> Dict:
        """Send academic progress report to parents"""
        # Get student and primary parent
        student = self.student_ops.get_student_with_parents(student_id)
        
        if not student:
            return {'success': False, 'error': 'Student not found'}
        
        # Find primary parent
        primary_parent = None
        for parent in student.get('parents', []):
            if parent.get('is_primary'):
                primary_parent = parent
                break
        
        if not primary_parent:
            return {'success': False, 'error': 'No primary parent found'}
        
        # Create academic report message
        message = self._create_academic_report_message(student, report_data)
        
        return self._send_whatsapp_message(
            parent_phone=primary_parent['phone'],
            parent_id=primary_parent['parent_id'],
            student_id=student_id,
            message_body=message,
            message_type='academic_progress'
        )
    
    def _create_academic_report_message(self, student: Dict, report_data: Dict) -> str:
        """Create academic progress message"""
        message = f"""
📚 ACADEMIC PROGRESS REPORT

Student: {student['first_name']} {student['last_name']}
Grade: {student['current_grade']}
Period: {report_data.get('period', 'Current Term')}

PERFORMANCE SUMMARY:
{report_data.get('summary', 'Grades available in student portal')}

Overall Average: {report_data.get('average', 'N/A')}
Class Rank: {report_data.get('rank', 'N/A')}

Teacher Comments:
{report_data.get('teacher_comments', 'Keep up the good work!')}

For detailed report, contact the school office.
        """.strip()
        
        return message
    
    # ============================================
    # EVENT NOTIFICATIONS
    # ============================================
    
    def broadcast_event_notification(self, event_data: Dict, target_grades: List[str] = None) -> Dict:
        """
        Broadcast school event to parents
        
        Args:
            event_data: Event details (title, date, description)
            target_grades: List of grades to notify (None = all grades)
        """
        # Get parents to notify
        if target_grades:
            parents = []
            for grade in target_grades:
                grade_parents = self.parent_ops.get_parents_for_grade(self.school_id, grade)
                parents.extend(grade_parents)
            # Remove duplicates
            parents = list({p['id']: p for p in parents}.values())
        else:
            # Get all parents
            query = """
            SELECT DISTINCT p.* 
            FROM parents p
            JOIN student_parent_relationships spr ON p.id = spr.parent_id
            JOIN students s ON spr.student_id = s.id
            WHERE s.school_id = %s 
            AND s.enrollment_status = 'active'
            AND p.deleted_at IS NULL
            """
            parents = self.db.execute_query(query, (self.school_id,))
        
        message = self._create_event_message(event_data)
        
        messages_sent = []
        for parent in parents:
            result = self._send_whatsapp_message(
                parent_phone=parent['whatsapp_number'],
                parent_id=parent['id'],
                student_id=None,
                message_body=message,
                message_type='event_notification'
            )
            messages_sent.append(result)
        
        return {
            'event_title': event_data.get('title'),
            'parents_notified': len(parents),
            'messages_sent': len(messages_sent),
            'successful': sum(1 for m in messages_sent if m.get('success'))
        }
    
    def _create_event_message(self, event_data: Dict) -> str:
        """Create event notification message"""
        message = f"""
📅 SCHOOL EVENT NOTIFICATION

{event_data.get('title', 'School Event')}

Date: {event_data.get('date', 'TBA')}
Time: {event_data.get('time', 'TBA')}
Location: {event_data.get('location', 'School Campus')}

{event_data.get('description', '')}

{event_data.get('requirements', '')}

For questions, contact the school office.
        """.strip()
        
        return message
    
    # ============================================
    # EMERGENCY NOTIFICATIONS
    # ============================================
    
    def send_emergency_notification(self, student_id: str, emergency_type: str, details: str) -> Dict:
        """Send urgent notification to parents"""
        student = self.student_ops.get_student_with_parents(student_id)
        
        if not student:
            return {'success': False, 'error': 'Student not found'}
        
        message = f"""
🚨 URGENT NOTIFICATION

Student: {student['first_name']} {student['last_name']}
Admission No: {student['admission_number']}

Type: {emergency_type}

{details}

Please contact the school immediately:
Phone: [SCHOOL_PHONE]

This is an automated urgent message.
        """.strip()
        
        # Send to ALL parents (not just primary)
        results = []
        for parent in student.get('parents', []):
            result = self._send_whatsapp_message(
                parent_phone=parent['phone'],
                parent_id=parent['parent_id'],
                student_id=student_id,
                message_body=message,
                message_type='emergency',
                priority='high'
            )
            results.append(result)
        
        return {
            'success': True,
            'parents_notified': len(results),
            'student': f"{student['first_name']} {student['last_name']}"
        }
    
    # ============================================
    # MESSAGE DELIVERY
    # ============================================
    
    def _send_whatsapp_message(self, parent_phone: str, parent_id: str, 
                               student_id: Optional[str], message_body: str,
                               message_type: str, priority: str = 'normal') -> Dict:
        """
        Send WhatsApp message (placeholder - actual implementation uses WhatsApp API)
        """
        # Create message record in database
        message_record = self.message_ops.create_message({
            'school_id': self.school_id,
            'recipient_type': 'parent',
            'recipient_id': parent_id,
            'recipient_phone': parent_phone,
            'recipient_email': None,
            'message_type': 'whatsapp',
            'subject': None,
            'body': message_body,
            'template_name': message_type,
            'template_variables': json.dumps({
                'student_id': student_id,
                'message_type': message_type,
                'priority': priority
            }),
            'trigger_event': message_type,
            'triggered_by': 'ai_agent',
            'staff_id': None,
            'cost_amount': 0.01  # Estimate per message
        })
        
        # TODO: Integrate actual WhatsApp Business API
        # For now, just record the message
        
        return {
            'success': True,
            'message_id': message_record['id'],
            'recipient': parent_phone,
            'type': message_type
        }
    
    # ============================================
    # MULTI-LANGUAGE SUPPORT
    # ============================================
    
    def translate_message(self, message: str, target_language: str) -> str:
        """
        Translate message to target language
        Supports: en, sw (Swahili), fr, ha (Hausa), yo (Yoruba), ig (Igbo)
        """
        # TODO: Integrate translation API (Google Translate, DeepL, etc.)
        # For MVP, return original message
        return message
    
    # ============================================
    # PARENT INQUIRY HANDLING
    # ============================================
    
    def handle_parent_inquiry(self, parent_phone: str, inquiry_text: str) -> Dict:
        """
        Process incoming parent inquiry and provide automated response
        """
        # TODO: Implement AI-powered inquiry classification and response
        # For MVP, return acknowledgment
        
        response = """
Thank you for your message. 

We have received your inquiry and will respond within 24 hours.

For urgent matters, please call the school office.

School Office: [SCHOOL_PHONE]
Office Hours: Mon-Fri, 8AM-5PM
        """.strip()
        
        return {
            'success': True,
            'response': response,
            'inquiry_logged': True
        }


# ============================================
# CONVENIENCE FUNCTIONS
# ============================================

def send_fee_reminders(school_id: str, reminder_type: str = 'overdue') -> Dict:
    """Quick function to send fee reminders"""
    service = ParentEngagementService(school_id)
    return service.send_fee_reminders(reminder_type)

def broadcast_event(school_id: str, event_data: Dict, target_grades: List[str] = None) -> Dict:
    """Quick function to broadcast event"""
    service = ParentEngagementService(school_id)
    return service.broadcast_event_notification(event_data, target_grades)

def send_emergency_alert(school_id: str, student_id: str, emergency_type: str, details: str) -> Dict:
    """Quick function for emergency notifications"""
    service = ParentEngagementService(school_id)
    return service.send_emergency_notification(student_id, emergency_type, details)
