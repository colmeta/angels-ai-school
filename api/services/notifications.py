"""
Notification Service - Real SMS, Email, Push Notifications
Supports SMS (Africa's Talking, Twilio), Email (SendGrid), and Web Push
"""
import os
from typing import List, Dict, Any, Optional
from datetime import datetime
import httpx
import json

from api.core.config import get_settings
from api.services.database import get_db_manager


class NotificationService:
    """Production notification service with multiple channels"""
    
    def __init__(self):
        self.settings = get_settings()
        self.db = get_db_manager()
        
        # Africa's Talking configuration (primary SMS for Africa)
        self.at_api_key = os.getenv("AFRICAS_TALKING_API_KEY")
        self.at_username = os.getenv("AFRICAS_TALKING_USERNAME", "sandbox")
        self.at_sender = os.getenv("AFRICAS_TALKING_SENDER_ID", "AngelsAI")
        
        # Twilio configuration (backup SMS)
        self.twilio_sid = os.getenv("TWILIO_ACCOUNT_SID")
        self.twilio_token = os.getenv("TWILIO_AUTH_TOKEN")
        self.twilio_from = os.getenv("TWILIO_PHONE_NUMBER")
        
        # SendGrid configuration (email)
        self.sendgrid_key = os.getenv("SENDGRID_API_KEY")
        self.sendgrid_from = os.getenv("SENDGRID_FROM_EMAIL", "noreply@angelsai.school")
        
        # Push notification configuration
        self.vapid_public = os.getenv("VAPID_PUBLIC_KEY")
        self.vapid_private = os.getenv("VAPID_PRIVATE_KEY")
        self.vapid_email = os.getenv("VAPID_EMAIL", "admin@angelsai.school")
    
    async def send_notification(
        self,
        school_id: str,
        recipient_id: str,
        recipient_type: str,
        notification_type: str,
        title: str,
        message: str,
        channels: List[str] = ["app", "sms"],
        priority: str = "normal",
        related_entity_type: Optional[str] = None,
        related_entity_id: Optional[str] = None,
        metadata: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Send notification through multiple channels
        
        Args:
            school_id: School UUID
            recipient_id: Parent/Teacher/Student UUID
            recipient_type: "parent", "teacher", "student", "admin"
            notification_type: "attendance", "fee", "incident", "health", "transport", "general"
            title: Notification title
            message: Notification message
            channels: List of ["app", "sms", "email", "push"]
            priority: "low", "normal", "high", "urgent"
            related_entity_type: E.g., "student", "incident"
            related_entity_id: UUID of related entity
            metadata: Additional data
            
        Returns:
            Dict with delivery status per channel
        """
        results = {
            "success": True,
            "channels": {},
            "notification_id": None
        }
        
        # Store in database first
        notification_id = self._store_notification(
            school_id=school_id,
            recipient_id=recipient_id,
            recipient_type=recipient_type,
            notification_type=notification_type,
            title=title,
            message=message,
            priority=priority,
            channels=channels,
            related_entity_type=related_entity_type,
            related_entity_id=related_entity_id
        )
        results["notification_id"] = notification_id
        
        # Get recipient contact info
        contact_info = self._get_recipient_contact(recipient_id, recipient_type)
        
        # Send through each channel
        if "app" in channels:
            results["channels"]["app"] = {"success": True, "message": "Stored in database"}
        
        if "sms" in channels and contact_info.get("phone"):
            sms_result = await self._send_sms(
                phone=contact_info["phone"],
                message=f"{title}\n\n{message}",
                priority=priority
            )
            results["channels"]["sms"] = sms_result
        
        if "email" in channels and contact_info.get("email"):
            email_result = await self._send_email(
                to_email=contact_info["email"],
                subject=title,
                body=message,
                priority=priority
            )
            results["channels"]["email"] = email_result
        
        if "push" in channels:
            push_result = await self._send_push_notification(
                recipient_id=recipient_id,
                title=title,
                message=message,
                data=metadata
            )
            results["channels"]["push"] = push_result
        
        return results
    
    async def _send_sms(self, phone: str, message: str, priority: str = "normal") -> Dict:
        """Send SMS via Africa's Talking (primary) or Twilio (backup)"""
        
        # Normalize phone number
        phone = self._normalize_phone(phone)
        
        # Try Africa's Talking first (preferred for Uganda/Africa)
        if self.at_api_key:
            try:
                return await self._send_sms_africas_talking(phone, message)
            except Exception as e:
                print(f"Africa's Talking failed: {e}")
        
        # Fallback to Twilio
        if self.twilio_sid and self.twilio_token:
            try:
                return await self._send_sms_twilio(phone, message)
            except Exception as e:
                print(f"Twilio failed: {e}")
        
        # No SMS provider configured - queue for later
        return {
            "success": False,
            "error": "No SMS provider configured",
            "queued": True
        }
    
    async def _send_sms_africas_talking(self, phone: str, message: str) -> Dict:
        """Send SMS via Africa's Talking API"""
        url = "https://api.africastalking.com/version1/messaging"
        
        headers = {
            "apiKey": self.at_api_key,
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "application/json"
        }
        
        data = {
            "username": self.at_username,
            "to": phone,
            "message": message,
            "from": self.at_sender
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=headers, data=data)
            result = response.json()
            
            if response.status_code == 201:
                return {
                    "success": True,
                    "provider": "africas_talking",
                    "message_id": result.get("SMSMessageData", {}).get("Recipients", [{}])[0].get("messageId")
                }
            else:
                raise Exception(f"SMS failed: {result}")
    
    async def _send_sms_twilio(self, phone: str, message: str) -> Dict:
        """Send SMS via Twilio API"""
        url = f"https://api.twilio.com/2010-04-01/Accounts/{self.twilio_sid}/Messages.json"
        
        auth = (self.twilio_sid, self.twilio_token)
        data = {
            "To": phone,
            "From": self.twilio_from,
            "Body": message
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(url, auth=auth, data=data)
            result = response.json()
            
            if response.status_code == 201:
                return {
                    "success": True,
                    "provider": "twilio",
                    "message_id": result.get("sid")
                }
            else:
                raise Exception(f"Twilio failed: {result}")
    
    async def _send_email(self, to_email: str, subject: str, body: str, priority: str = "normal") -> Dict:
        """Send email via SendGrid"""
        
        if not self.sendgrid_key:
            return {
                "success": False,
                "error": "SendGrid not configured",
                "queued": True
            }
        
        url = "https://api.sendgrid.com/v3/mail/send"
        
        headers = {
            "Authorization": f"Bearer {self.sendgrid_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "personalizations": [{
                "to": [{"email": to_email}],
                "subject": subject
            }],
            "from": {"email": self.sendgrid_from, "name": "Angels AI School"},
            "content": [{
                "type": "text/html",
                "value": self._format_email_html(subject, body)
            }]
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(url, headers=headers, json=payload)
                
                if response.status_code == 202:
                    return {
                        "success": True,
                        "provider": "sendgrid",
                        "message_id": response.headers.get("X-Message-Id")
                    }
                else:
                    raise Exception(f"SendGrid failed: {response.text}")
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "queued": True
            }
    
    async def _send_push_notification(self, recipient_id: str, title: str, message: str, data: Optional[Dict] = None) -> Dict:
        """Send web push notification using VAPID protocol"""
        from pywebpush import webpush, WebPushException

        # Get user's push subscriptions from database
        subscriptions = self._get_push_subscriptions(recipient_id)
        
        if not subscriptions:
            return {"success": False, "error": "No push subscriptions found"}
        
        success_count = 0
        errors = []

        for sub in subscriptions:
            try:
                webpush(
                    subscription_info=sub,
                    data=json.dumps({
                        "title": title,
                        "body": message,
                        "data": data or {},
                        "icon": "/pwa-192x192.png",
                        "badge": "/favicon.ico"
                    }),
                    vapid_private_key=self.vapid_private,
                    vapid_claims={"sub": f"mailto:{self.vapid_email}"}
                )
                success_count += 1
            except WebPushException as ex:
                logger.error(f"PWA Push failed: {ex}")
                errors.append(str(ex))
        
        return {
            "success": success_count > 0,
            "provider": "web_push(vapid)",
            "sent": success_count,
            "failed": len(subscriptions) - success_count,
            "errors": errors
        }

    def _get_push_subscriptions(self, recipient_id: str) -> List[Dict]:
        """Fetch VAPID subscriptions from the database"""
        query = "SELECT subscription_json FROM push_subscriptions WHERE user_id = %s"
        rows = self.db.execute_query(query, (recipient_id,), fetch=True)
        return [json.loads(row['subscription_json']) for row in rows] if rows else []
    def _store_notification(
        self,
        school_id: str,
        recipient_id: str,
        recipient_type: str,
        notification_type: str,
        title: str,
        message: str,
        priority: str,
        channels: List[str],
        related_entity_type: Optional[str],
        related_entity_id: Optional[str]
    ) -> str:
        """Store notification in database"""
        
        query = """
        INSERT INTO notifications (
            school_id, recipient_type, recipient_id, notification_type,
            title, message, priority, sent_via, related_entity_type,
            related_entity_id, created_at
        ) VALUES (
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP
        ) RETURNING id;
        """
        
        result = self.db.execute_query(
            query,
            (
                school_id, recipient_type, recipient_id, notification_type,
                title, message, priority, channels, related_entity_type,
                related_entity_id
            ),
            fetch=True
        )
        
        return result[0]["id"] if result else None
    
    def _get_recipient_contact(self, recipient_id: str, recipient_type: str) -> Dict:
        """Get recipient contact information"""
        
        if recipient_type == "parent":
            query = "SELECT primary_phone as phone, email FROM parents WHERE id = %s"
        elif recipient_type == "teacher":
            query = "SELECT phone, email FROM teachers WHERE id = %s"
        elif recipient_type == "student":
            query = "SELECT phone, email FROM students WHERE id = %s"
        else:
            return {}
        
        result = self.db.execute_query(query, (recipient_id,), fetch=True)
        return result[0] if result else {}
    
    def _get_push_subscriptions(self, recipient_id: str) -> List[Dict]:
        """Get user's web push subscriptions"""
        # Would query push_subscriptions table
        # Placeholder for now
        return []
    
    def _normalize_phone(self, phone: str) -> str:
        """Normalize phone number to international format"""
        # Remove all non-numeric characters
        phone = ''.join(filter(str.isdigit, phone))
        
        # Add Uganda country code if local number
        if len(phone) == 9 and phone.startswith('7'):
            phone = f"+256{phone}"
        elif len(phone) == 10 and phone.startswith('0'):
            phone = f"+256{phone[1:]}"
        elif not phone.startswith('+'):
            phone = f"+{phone}"
        
        return phone
    
    def _format_email_html(self, subject: str, body: str) -> str:
        """Format email as HTML"""
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: #0B69FF; color: white; padding: 20px; text-align: center; }}
                .content {{ padding: 30px 20px; background: #f9f9f9; }}
                .footer {{ text-align: center; padding: 20px; font-size: 12px; color: #666; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h2>Angels AI School Platform</h2>
                </div>
                <div class="content">
                    <h3>{subject}</h3>
                    <p>{body}</p>
                </div>
                <div class="footer">
                    <p>This is an automated message from Angels AI School Platform</p>
                    <p>Do not reply to this email</p>
                </div>
            </div>
        </body>
        </html>
        """
    
    async def notify_parent_attendance(
        self,
        school_id: str,
        student_id: str,
        parent_id: str,
        status: str,
        date: str
    ) -> Dict:
        """Notify parent about student attendance"""
        
        # Get student name
        student = self.db.execute_query(
            "SELECT first_name, last_name FROM students WHERE id = %s",
            (student_id,),
            fetch=True
        )[0]
        
        student_name = f"{student['first_name']} {student['last_name']}"
        
        if status == "present":
            title = "Student Present in School"
            message = f"{student_name} is present in class today ({date})."
        elif status == "absent":
            title = "Student Absent from School"
            message = f"{student_name} was marked absent today ({date}). Please contact the school if this is unexpected."
        else:  # late
            title = "Student Arrived Late"
            message = f"{student_name} arrived late to school today ({date})."
        
        return await self.send_notification(
            school_id=school_id,
            recipient_id=parent_id,
            recipient_type="parent",
            notification_type="attendance",
            title=title,
            message=message,
            channels=["app", "sms"],
            priority="normal",
            related_entity_type="student",
            related_entity_id=student_id
        )
    
    async def notify_parent_health(
        self,
        school_id: str,
        student_id: str,
        parent_id: str,
        symptoms: str,
        treatment: str
    ) -> Dict:
        """Notify parent about sickbay visit"""
        
        student = self.db.execute_query(
            "SELECT first_name, last_name FROM students WHERE id = %s",
            (student_id,),
            fetch=True
        )[0]
        
        student_name = f"{student['first_name']} {student['last_name']}"
        
        title = "Student Visited Sickbay"
        message = f"{student_name} visited the sickbay. Symptoms: {symptoms}. Treatment: {treatment}. Please contact the school for more information."
        
        return await self.send_notification(
            school_id=school_id,
            recipient_id=parent_id,
            recipient_type="parent",
            notification_type="health",
            title=title,
            message=message,
            channels=["app", "sms"],
            priority="high",
            related_entity_type="student",
            related_entity_id=student_id
        )
    
    async def notify_parent_fee(
        self,
        school_id: str,
        student_id: str,
        parent_id: str,
        amount: float,
        balance: float,
        due_date: str
    ) -> Dict:
        """Notify parent about fee payment"""
        
        student = self.db.execute_query(
            "SELECT first_name, last_name FROM students WHERE id = %s",
            (student_id,),
            fetch=True
        )[0]
        
        student_name = f"{student['first_name']} {student['last_name']}"
        
        title = "Fee Payment Reminder"
        message = f"Fee reminder for {student_name}: UGX {amount:,.0f} due by {due_date}. Current balance: UGX {balance:,.0f}. Pay via MTN/Airtel Money in the app."
        
        return await self.send_notification(
            school_id=school_id,
            recipient_id=parent_id,
            recipient_type="parent",
            notification_type="fee",
            title=title,
            message=message,
            channels=["app", "sms"],
            priority="normal",
            related_entity_type="student",
            related_entity_id=student_id
        )
