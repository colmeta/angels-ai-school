"""
Email Service - SendGrid Integration
Handles all transactional emails (welcome, password reset, reports, etc.)
"""

import os
from typing import Optional, List
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Email, To, Content, Attachment, FileContent, FileName, FileType, Disposition
import base64

class EmailService:
    def __init__(self):
        self.api_key = os.getenv('SENDGRID_API_KEY')
        self.from_email = os.getenv('FROM_EMAIL', 'noreply@angels-ai.com')
        self.from_name = os.getenv('FROM_NAME', 'Angels AI School')
        self.client = SendGridAPIClient(self.api_key) if self.api_key else None
    
    def send_welcome_email(self, to_email: str, school_name: str, temp_password: str, login_url: str):
        """Send welcome email to new school admin"""
        subject = f"Welcome to Angels AI - {school_name}"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
                .content {{ background: #f8fafc; padding: 30px; border-radius: 0 0 10px 10px; }}
                .credentials {{ background: white; padding: 20px; border-left: 4px solid #3b82f6; margin: 20px 0; }}
                .button {{ display: inline-block; background: #3b82f6; color: white; padding: 12px 30px; text-decoration: none; border-radius: 6px; margin: 20px 0; }}
                .footer {{ text-align: center; color: #64748b; font-size: 14px; margin-top: 30px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🎓 Welcome to Angels AI!</h1>
                    <p>Your school management platform is ready</p>
                </div>
                <div class="content">
                    <h2>Hello {school_name}!</h2>
                    <p>Thank you for joining Angels AI. We're excited to help you transform your school administration.</p>
                    
                    <div class="credentials">
                        <h3>Your Login Credentials</h3>
                        <p><strong>Email:</strong> {to_email}</p>
                        <p><strong>Temporary Password:</strong> {temp_password}</p>
                        <p style="color: #dc2626; font-size: 14px;">⚠️ Please change your password after first login</p>
                    </div>
                    
                    <a href="{login_url}" class="button">Login to Your Dashboard</a>
                    
                    <h3>What's Next?</h3>
                    <ul>
                        <li>📊 Import your existing student data (takes 5 minutes)</li>
                        <li>🎨 Customize your school branding</li>
                        <li>📱 Set up WhatsApp notifications</li>
                        <li>👥 Invite your staff members</li>
                    </ul>
                    
                    <p>Need help? Watch our <a href="https://angels-ai.com/tutorials">quick-start video</a> or contact support.</p>
                    
                    <div class="footer">
                        <p>Angels AI - Empowering African Education</p>
                        <p>Questions? Email support@angels-ai.com</p>
                    </div>
                </div>
            </div>
        </body>
        </html>
        """
        
        return self._send(to_email, subject, html_content)
    
    def send_password_reset(self, to_email: str, reset_link: str):
        """Send password reset email"""
        subject = "Reset Your Password - Angels AI"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
            <h2>Password Reset Request</h2>
            <p>You requested to reset your password. Click the button below to set a new password:</p>
            <a href="{reset_link}" style="display: inline-block; background: #3b82f6; color: white; padding: 12px 30px; text-decoration: none; border-radius: 6px; margin: 20px 0;">
                Reset Password
            </a>
            <p>This link expires in 1 hour.</p>
            <p>If you didn't request this, please ignore this email.</p>
        </body>
        </html>
        """
        
        return self._send(to_email, subject, html_content)
    
    def send_report_card(self, to_email: str, student_name: str, pdf_data: bytes, filename: str):
        """Send report card via email with PDF attachment"""
        subject = f"Report Card for {student_name}"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
            <h2>Report Card Ready</h2>
            <p>Dear Parent/Guardian,</p>
            <p>Please find attached the report card for <strong>{student_name}</strong>.</p>
            <p>Review the report and contact the school if you have any questions.</p>
            <br>
            <p>Best regards,<br>School Administration</p>
        </body>
        </html>
        """
        
        # Create attachment
        encoded_file = base64.b64encode(pdf_data).decode()
        attachment = Attachment(
            FileContent(encoded_file),
            FileName(filename),
            FileType('application/pdf'),
            Disposition('attachment')
        )
        
        return self._send(to_email, subject, html_content, attachments=[attachment])
    
    def send_fee_reminder(self, to_email: str, student_name: str, amount_due: float, due_date: str):
        """Send fee payment reminder"""
        subject = f"Fee Payment Reminder - {student_name}"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
            <h2>Fee Payment Reminder</h2>
            <p>Dear Parent/Guardian,</p>
            <p>This is a friendly reminder that school fees for <strong>{student_name}</strong> are due.</p>
            <div style="background: #fef2f2; border-left: 4px solid #dc2626; padding: 15px; margin: 20px 0;">
                <p style="margin: 0;"><strong>Amount Due:</strong> ${amount_due:,.2f}</p>
                <p style="margin: 10px 0 0;"><strong>Due Date:</strong> {due_date}</p>
            </div>
            <p>Please make payment via:</p>
            <ul>
                <li>Mobile Money (MTN/Airtel)</li>
                <li>School portal</li>
                <li>Visit school office</li>
            </ul>
            <p>Thank you for your cooperation.</p>
        </body>
        </html>
        """
        
        return self._send(to_email, subject, html_content)
    
    def _send(self, to_email: str, subject: str, html_content: str, attachments: Optional[List] = None):
        """Internal method to send email"""
        if not self.client:
            # Fallback: Log email (for development without SendGrid)
            print(f"\n=== EMAIL (SendGrid Not Configured) ===")
            print(f"To: {to_email}")
            print(f"Subject: {subject}")
            print(f"Body: {html_content[:200]}...")
            print("=" * 40)
            return {"status": "development_mode", "logged": True}
        
        try:
            message = Mail(
                from_email=Email(self.from_email, self.from_name),
                to_emails=To(to_email),
                subject=subject,
                html_content=Content("text/html", html_content)
            )
            
            if attachments:
                for attachment in attachments:
                    message.add_attachment(attachment)
            
            response = self.client.send(message)
            
            return {
                "status": "sent",
                "status_code": response.status_code,
                "message_id": response.headers.get('X-Message-Id')
            }
        
        except Exception as e:
            print(f"Email send error: {str(e)}")
            return {"status": "error", "error": str(e)}


# Singleton instance
email_service = EmailService()
