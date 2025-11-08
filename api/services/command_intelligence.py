"""
Command Intelligence Service - Natural Language Command Execution
Converts natural language to executable actions (fully autonomous)

Examples:
- "Mark John as present today" → Marks attendance
- "Record 85 marks for Mary in Math exam" → Records grade
- "John paid 50000 for school fees" → Records payment
"""
import re
from typing import Dict, Any, List, Optional
from datetime import datetime, date
from uuid import uuid4

from api.services.clarity import ClarityClient
from api.services.database import get_db_manager
from api.services.notifications import NotificationService


class CommandIntelligenceService:
    """Autonomous command execution from natural language"""
    
    def __init__(self, school_id: str):
        self.school_id = school_id
        self.db = get_db_manager()
        self.clarity = ClarityClient()
        self.notification_service = NotificationService()
    
    async def execute_command(self, command: str, user_id: str, user_role: str) -> Dict[str, Any]:
        """
        Main entry point: Parse and execute natural language command
        
        Args:
            command: Natural language command (e.g., "Mark John as present")
            user_id: User executing the command
            user_role: Role (teacher, admin, etc.)
        
        Returns:
            Execution result with success status and details
        """
        try:
            # Step 1: Parse command with Clarity AI
            parsed = self._parse_command(command)
            
            # Step 2: Identify intent and extract entities
            intent = parsed.get("intent")
            entities = parsed.get("entities", {})
            
            # Step 3: Validate permissions
            if not self._check_permissions(intent, user_role):
                return {
                    "success": False,
                    "error": f"Permission denied: {user_role} cannot perform {intent}",
                    "command": command
                }
            
            # Step 4: Execute based on intent
            result = await self._execute_intent(intent, entities, user_id)
            
            # Step 5: Log action for audit
            self._log_command(command, intent, entities, result, user_id)
            
            return {
                "success": True,
                "command": command,
                "intent": intent,
                "entities": entities,
                "result": result,
                "executed_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "success": False,
                "command": command,
                "error": str(e),
                "executed_at": datetime.now().isoformat()
            }
    
    def _parse_command(self, command: str) -> Dict[str, Any]:
        """Parse natural language command using Clarity AI"""
        try:
            response = self.clarity.analyze(
                directive=f"""
                Parse this command and extract:
                1. Intent (what action to perform)
                2. Entities (student names, values, dates, etc.)
                
                Command: "{command}"
                
                Return JSON format:
                {{
                    "intent": "mark_attendance|record_grade|record_payment|create_incident|send_message",
                    "entities": {{
                        "student_name": "name",
                        "status": "present|absent|late",
                        "subject": "subject name",
                        "marks": number,
                        "amount": number,
                        "date": "YYYY-MM-DD",
                        "message": "message text"
                    }}
                }}
                """,
                domain="data-science"
            )
            
            # Extract from Clarity response
            analysis = response.get("analysis", {})
            summary = analysis.get("summary", "")
            
            # Parse intent from command keywords
            intent = self._extract_intent(command.lower())
            entities = self._extract_entities(command, intent)
            
            return {
                "intent": intent,
                "entities": entities,
                "clarity_analysis": summary
            }
            
        finally:
            self.clarity.close()
    
    def _extract_intent(self, command: str) -> str:
        """Extract intent from command using keywords"""
        command_lower = command.lower()
        
        # Attendance intents
        if any(word in command_lower for word in ["mark", "present", "absent", "attendance", "late"]):
            return "mark_attendance"
        
        # Grade/marks intents
        if any(word in command_lower for word in ["grade", "marks", "score", "result", "exam", "test"]):
            return "record_grade"
        
        # Payment intents
        if any(word in command_lower for word in ["pay", "paid", "payment", "fee", "money"]):
            return "record_payment"
        
        # Health/sickbay intents
        if any(word in command_lower for word in ["sick", "sickbay", "health", "ill", "unwell"]):
            return "record_health_visit"
        
        # Incident intents
        if any(word in command_lower for word in ["incident", "report", "issue", "problem", "fight", "damage"]):
            return "create_incident"
        
        # Message intents
        if any(word in command_lower for word in ["send", "message", "notify", "tell", "inform"]):
            return "send_message"
        
        # Inventory intents
        if any(word in command_lower for word in ["inventory", "stock", "supply", "add item", "remove item"]):
            return "manage_inventory"
        
        return "unknown"
    
    def _extract_entities(self, command: str, intent: str) -> Dict[str, Any]:
        """Extract entities from command based on intent"""
        entities = {}
        
        # Extract student name (capitalized words)
        name_pattern = r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b'
        names = re.findall(name_pattern, command)
        if names:
            entities["student_name"] = names[0]
        
        # Extract status for attendance
        if intent == "mark_attendance":
            if "present" in command.lower():
                entities["status"] = "present"
            elif "absent" in command.lower():
                entities["status"] = "absent"
            elif "late" in command.lower():
                entities["status"] = "late"
        
        # Extract numbers (marks, amounts)
        numbers = re.findall(r'\b(\d+(?:\.\d+)?)\b', command)
        if numbers:
            if intent == "record_grade":
                entities["marks"] = float(numbers[0])
            elif intent == "record_payment":
                entities["amount"] = float(numbers[0])
        
        # Extract subject (words after "in" or "for")
        subject_pattern = r'(?:in|for)\s+([A-Za-z\s]+?)(?:\s+exam|\s+test|$)'
        subject_match = re.search(subject_pattern, command, re.IGNORECASE)
        if subject_match:
            entities["subject"] = subject_match.group(1).strip()
        
        # Extract date (today, yesterday, or specific date)
        if "today" in command.lower():
            entities["date"] = date.today().isoformat()
        elif "yesterday" in command.lower():
            from datetime import timedelta
            entities["date"] = (date.today() - timedelta(days=1)).isoformat()
        
        # Extract message content (text after "send" or "tell")
        message_pattern = r'(?:send|tell|notify).*?["\'](.*?)["\']'
        message_match = re.search(message_pattern, command, re.IGNORECASE)
        if message_match:
            entities["message"] = message_match.group(1)
        
        return entities
    
    def _check_permissions(self, intent: str, user_role: str) -> bool:
        """Check if user role has permission for intent"""
        permissions = {
            "mark_attendance": ["teacher", "admin"],
            "record_grade": ["teacher", "admin"],
            "record_payment": ["admin", "staff"],
            "record_health_visit": ["staff", "admin"],
            "create_incident": ["teacher", "admin", "staff"],
            "send_message": ["teacher", "admin"],
            "manage_inventory": ["staff", "admin"],
        }
        
        allowed_roles = permissions.get(intent, ["admin"])
        return user_role in allowed_roles
    
    async def _execute_intent(self, intent: str, entities: Dict, user_id: str) -> Dict[str, Any]:
        """Execute the parsed intent"""
        
        if intent == "mark_attendance":
            return await self._mark_attendance(entities)
        
        elif intent == "record_grade":
            return await self._record_grade(entities)
        
        elif intent == "record_payment":
            return await self._record_payment(entities)
        
        elif intent == "record_health_visit":
            return await self._record_health_visit(entities)
        
        elif intent == "create_incident":
            return await self._create_incident(entities, user_id)
        
        elif intent == "send_message":
            return await self._send_message(entities, user_id)
        
        elif intent == "manage_inventory":
            return await self._manage_inventory(entities)
        
        else:
            return {"error": f"Unknown intent: {intent}"}
    
    async def _mark_attendance(self, entities: Dict) -> Dict[str, Any]:
        """Mark student attendance"""
        student_name = entities.get("student_name")
        status = entities.get("status", "present")
        attendance_date = entities.get("date", date.today().isoformat())
        
        # Find student by name
        students = self.db.execute_query(
            """
            SELECT id, first_name, last_name FROM students
            WHERE school_id = %s
            AND (CONCAT(first_name, ' ', last_name) ILIKE %s OR first_name ILIKE %s OR last_name ILIKE %s)
            LIMIT 1
            """,
            (self.school_id, f"%{student_name}%", f"%{student_name}%", f"%{student_name}%"),
            fetch=True
        )
        
        if not students:
            return {"error": f"Student '{student_name}' not found"}
        
        student = students[0]
        student_id = student["id"]
        
        # Mark attendance
        attendance_id = str(uuid4())
        self.db.execute_query(
            """
            INSERT INTO attendance (id, school_id, student_id, date, status)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (student_id, date) 
            DO UPDATE SET status = EXCLUDED.status, updated_at = CURRENT_TIMESTAMP
            """,
            (attendance_id, self.school_id, student_id, attendance_date, status)
        )
        
        # Get parent IDs
        parents = self.db.execute_query(
            """
            SELECT p.id, p.email, p.phone_number
            FROM parents p
            JOIN student_parents sp ON sp.parent_id = p.id
            WHERE sp.student_id = %s
            """,
            (student_id,),
            fetch=True
        )
        
        # Notify parents
        for parent in parents:
            await self.notification_service.notify_parent_attendance(
                school_id=self.school_id,
                student_id=student_id,
                parent_id=parent["id"],
                status=status,
                date=attendance_date
            )
        
        return {
            "action": "attendance_marked",
            "student": f"{student['first_name']} {student['last_name']}",
            "status": status,
            "date": attendance_date,
            "parents_notified": len(parents)
        }
    
    async def _record_grade(self, entities: Dict) -> Dict[str, Any]:
        """Record student grade/marks"""
        student_name = entities.get("student_name")
        marks = entities.get("marks")
        subject = entities.get("subject", "General")
        
        if not marks:
            return {"error": "Marks not specified"}
        
        # Find student
        students = self.db.execute_query(
            """
            SELECT id, first_name, last_name FROM students
            WHERE school_id = %s
            AND (CONCAT(first_name, ' ', last_name) ILIKE %s OR first_name ILIKE %s)
            LIMIT 1
            """,
            (self.school_id, f"%{student_name}%", f"%{student_name}%"),
            fetch=True
        )
        
        if not students:
            return {"error": f"Student '{student_name}' not found"}
        
        student = students[0]
        student_id = student["id"]
        
        # Calculate grade
        grade = self._calculate_grade(marks)
        
        # Create assessment if doesn't exist
        assessment_id = str(uuid4())
        self.db.execute_query(
            """
            INSERT INTO assessments (id, school_id, name, subject, max_marks, date)
            VALUES (%s, %s, %s, %s, %s, CURRENT_DATE)
            ON CONFLICT DO NOTHING
            """,
            (assessment_id, self.school_id, f"Quick Entry - {subject}", subject, 100)
        )
        
        # Record result
        result_id = str(uuid4())
        self.db.execute_query(
            """
            INSERT INTO assessment_results (id, assessment_id, student_id, marks_obtained, grade)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (result_id, assessment_id, student_id, marks, grade)
        )
        
        # Notify parents
        parents = self.db.execute_query(
            "SELECT p.id FROM parents p JOIN student_parents sp ON sp.parent_id = p.id WHERE sp.student_id = %s",
            (student_id,),
            fetch=True
        )
        
        for parent in parents:
            await self.notification_service.send_notification(
                school_id=self.school_id,
                recipient_id=parent["id"],
                recipient_type="parent",
                notification_type="academic",
                title=f"New Grade for {student['first_name']}",
                message=f"{student['first_name']} scored {marks}/100 ({grade}) in {subject}",
                channels=["app", "email"]
            )
        
        return {
            "action": "grade_recorded",
            "student": f"{student['first_name']} {student['last_name']}",
            "subject": subject,
            "marks": marks,
            "grade": grade,
            "parents_notified": len(parents)
        }
    
    async def _record_payment(self, entities: Dict) -> Dict[str, Any]:
        """Record fee payment"""
        student_name = entities.get("student_name")
        amount = entities.get("amount")
        
        if not amount:
            return {"error": "Amount not specified"}
        
        # Find student
        students = self.db.execute_query(
            """
            SELECT id, first_name, last_name FROM students
            WHERE school_id = %s
            AND (CONCAT(first_name, ' ', last_name) ILIKE %s OR first_name ILIKE %s)
            LIMIT 1
            """,
            (self.school_id, f"%{student_name}%", f"%{student_name}%"),
            fetch=True
        )
        
        if not students:
            return {"error": f"Student '{student_name}' not found"}
        
        student = students[0]
        student_id = student["id"]
        
        # Record payment
        payment_id = str(uuid4())
        self.db.execute_query(
            """
            INSERT INTO payments (id, school_id, student_id, amount, payment_method, status, payment_date)
            VALUES (%s, %s, %s, %s, %s, %s, CURRENT_DATE)
            """,
            (payment_id, self.school_id, student_id, amount, "manual_entry", "completed")
        )
        
        # Update student fees
        self.db.execute_query(
            """
            UPDATE student_fees
            SET amount_paid = amount_paid + %s,
                balance = amount_due - (amount_paid + %s),
                updated_at = CURRENT_TIMESTAMP
            WHERE student_id = %s AND school_id = %s
            """,
            (amount, amount, student_id, self.school_id)
        )
        
        return {
            "action": "payment_recorded",
            "student": f"{student['first_name']} {student['last_name']}",
            "amount": amount,
            "payment_id": payment_id
        }
    
    async def _record_health_visit(self, entities: Dict) -> Dict[str, Any]:
        """Record sickbay/health visit"""
        student_name = entities.get("student_name")
        symptoms = entities.get("message", "Not specified")
        
        # Find student
        students = self.db.execute_query(
            """
            SELECT id, first_name, last_name FROM students
            WHERE school_id = %s
            AND (CONCAT(first_name, ' ', last_name) ILIKE %s OR first_name ILIKE %s)
            LIMIT 1
            """,
            (self.school_id, f"%{student_name}%", f"%{student_name}%"),
            fetch=True
        )
        
        if not students:
            return {"error": f"Student '{student_name}' not found"}
        
        student = students[0]
        student_id = student["id"]
        
        # Record health visit
        visit_id = str(uuid4())
        self.db.execute_query(
            """
            INSERT INTO health_visits (id, school_id, student_id, visit_date, symptoms)
            VALUES (%s, %s, %s, CURRENT_TIMESTAMP, %s)
            """,
            (visit_id, self.school_id, student_id, symptoms)
        )
        
        # Notify parents
        parents = self.db.execute_query(
            "SELECT p.id FROM parents p JOIN student_parents sp ON sp.parent_id = p.id WHERE sp.student_id = %s",
            (student_id,),
            fetch=True
        )
        
        for parent in parents:
            await self.notification_service.notify_parent_health(
                school_id=self.school_id,
                student_id=student_id,
                parent_id=parent["id"],
                symptoms=symptoms,
                treatment="Under observation"
            )
        
        return {
            "action": "health_visit_recorded",
            "student": f"{student['first_name']} {student['last_name']}",
            "symptoms": symptoms,
            "parents_notified": len(parents)
        }
    
    async def _create_incident(self, entities: Dict, user_id: str) -> Dict[str, Any]:
        """Create incident report"""
        student_name = entities.get("student_name")
        description = entities.get("message", "Incident reported via command")
        
        incident_id = str(uuid4())
        
        # Find student if mentioned
        student_id = None
        if student_name:
            students = self.db.execute_query(
                """
                SELECT id FROM students
                WHERE school_id = %s
                AND (CONCAT(first_name, ' ', last_name) ILIKE %s OR first_name ILIKE %s)
                LIMIT 1
                """,
                (self.school_id, f"%{student_name}%", f"%{student_name}%"),
                fetch=True
            )
            if students:
                student_id = students[0]["id"]
        
        # Create incident
        self.db.execute_query(
            """
            INSERT INTO incidents (id, school_id, title, description, severity, status, reported_by, reported_date)
            VALUES (%s, %s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP)
            """,
            (incident_id, self.school_id, "Quick Report", description, "medium", "open", user_id)
        )
        
        return {
            "action": "incident_created",
            "incident_id": incident_id,
            "description": description
        }
    
    async def _send_message(self, entities: Dict, user_id: str) -> Dict[str, Any]:
        """Send message/notification"""
        message = entities.get("message", "")
        
        if not message:
            return {"error": "No message specified"}
        
        # For now, create a general notification
        # Could be enhanced to parse recipient from command
        return {
            "action": "message_queued",
            "message": message,
            "note": "Message queuing not fully implemented yet"
        }
    
    async def _manage_inventory(self, entities: Dict) -> Dict[str, Any]:
        """Manage inventory items"""
        # Placeholder for inventory management
        return {
            "action": "inventory_management",
            "note": "Inventory management via commands coming soon"
        }
    
    def _calculate_grade(self, marks: float) -> str:
        """Calculate grade from marks"""
        if marks >= 90:
            return "A+"
        elif marks >= 80:
            return "A"
        elif marks >= 70:
            return "B+"
        elif marks >= 60:
            return "B"
        elif marks >= 50:
            return "C"
        elif marks >= 40:
            return "D"
        else:
            return "F"
    
    def _log_command(self, command: str, intent: str, entities: Dict, result: Dict, user_id: str):
        """Log command execution for audit trail"""
        try:
            self.db.execute_query(
                """
                INSERT INTO audit_logs (school_id, user_id, action, entity_type, changes)
                VALUES (%s, %s, %s, %s, %s)
                """,
                (
                    self.school_id,
                    user_id,
                    f"command_executed: {intent}",
                    "command",
                    {
                        "command": command,
                        "intent": intent,
                        "entities": entities,
                        "result": result
                    }
                )
            )
        except Exception as e:
            # Don't fail the command if logging fails
            print(f"Warning: Could not log command: {e}")


def get_command_service(school_id: str) -> CommandIntelligenceService:
    """Helper to get command service instance"""
    return CommandIntelligenceService(school_id)
