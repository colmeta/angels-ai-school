"""
USSD Service
Handles USSD sessions for basic phone access (*123#)
Allows parents without smartphones to access school info
"""
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
import uuid

from api.services.database import get_db_manager


class USSDService:
    """Service for USSD (*123#) functionality"""
    
    def __init__(self):
        self.db = get_db_manager()
    
    # ============================================================================
    # SESSION MANAGEMENT
    # ============================================================================
    
    def start_session(self, phone_number: str, session_id: str) -> Dict[str, Any]:
        """
        Start a new USSD session
        
        Returns initial menu
        """
        # Create session
        query = """
        INSERT INTO ussd_sessions (
            session_id, phone_number, current_menu, status
        ) VALUES (%s, %s, 'main_menu', 'active')
        RETURNING id
        """
        
        result = self.db.execute_query(query, (session_id, phone_number), fetch=True)
        
        # Return main menu
        return {
            "session_id": session_id,
            "response": self._get_main_menu(),
            "continues": True
        }
    
    def handle_input(
        self,
        session_id: str,
        user_input: str
    ) -> Dict[str, Any]:
        """
        Handle user input in USSD session
        
        Returns next menu or result
        """
        # Get current session
        session_query = """
        SELECT 
            id, phone_number, school_id, user_id, 
            current_menu, session_data
        FROM ussd_sessions
        WHERE session_id = %s AND status = 'active'
        """
        
        session = self.db.execute_query(session_query, (session_id,), fetch=True)
        
        if not session:
            return {
                "session_id": session_id,
                "response": "END Session expired. Please dial again.",
                "continues": False
            }
        
        session = session[0]
        current_menu = session['current_menu']
        phone_number = session['phone_number']
        session_data = session['session_data'] or {}
        
        # Route based on current menu
        if current_menu == 'main_menu':
            return self._handle_main_menu(session_id, user_input, phone_number)
        
        elif current_menu == 'select_school':
            return self._handle_school_selection(session_id, user_input, phone_number, session_data)
        
        elif current_menu == 'select_child':
            return self._handle_child_selection(session_id, user_input, phone_number, session_data)
        
        elif current_menu == 'attendance':
            return self._show_attendance(session_id, session_data)
        
        elif current_menu == 'fees':
            return self._show_fees(session_id, session_data)
        
        elif current_menu == 'grades':
            return self._show_grades(session_id, session_data)
        
        elif current_menu == 'pay_fees':
            return self._handle_fee_payment(session_id, user_input, session_data)
        
        else:
            return {
                "session_id": session_id,
                "response": "END Invalid menu. Please try again.",
                "continues": False
            }
    
    # ============================================================================
    # MENU HANDLERS
    # ============================================================================
    
    def _get_main_menu(self) -> str:
        """Main menu"""
        return (
            "CON Welcome to Angels AI\n"
            "1. Check Attendance\n"
            "2. Check Fees\n"
            "3. Check Grades\n"
            "4. Pay Fees\n"
            "5. Requirements\n"
            "0. Exit"
        )
    
    def _handle_main_menu(
        self,
        session_id: str,
        user_input: str,
        phone_number: str
    ) -> Dict[str, Any]:
        """Handle main menu selection"""
        
        # Map input to action
        menu_map = {
            '1': 'check_attendance',
            '2': 'check_fees',
            '3': 'check_grades',
            '4': 'pay_fees',
            '5': 'check_requirements',
            '0': 'exit'
        }
        
        action = menu_map.get(user_input)
        
        if not action:
            return {
                "session_id": session_id,
                "response": "END Invalid selection. Please try again.",
                "continues": False
            }
        
        if action == 'exit':
            self._end_session(session_id)
            return {
                "session_id": session_id,
                "response": "END Thank you for using Angels AI.",
                "continues": False
            }
        
        # Check if user has children
        children = self._get_user_children(phone_number)
        
        if not children:
            return {
                "session_id": session_id,
                "response": "END No children found for this number. Please contact school.",
                "continues": False
            }
        
        # If only 1 child, skip selection
        if len(children) == 1:
            child = children[0]
            return self._route_to_action(session_id, action, child['student_id'], child['school_id'])
        
        # Multiple children - show selection
        self._update_session(
            session_id,
            'select_child',
            {'action': action, 'children': children}
        )
        
        response = "CON Select child:\n"
        for i, child in enumerate(children, 1):
            response += f"{i}. {child['first_name']} {child['last_name']} ({child['class_name']})\n"
        response += "0. Back"
        
        return {
            "session_id": session_id,
            "response": response,
            "continues": True
        }
    
    def _handle_child_selection(
        self,
        session_id: str,
        user_input: str,
        phone_number: str,
        session_data: Dict
    ) -> Dict[str, Any]:
        """Handle child selection"""
        
        if user_input == '0':
            self._update_session(session_id, 'main_menu', {})
            return {
                "session_id": session_id,
                "response": self._get_main_menu(),
                "continues": True
            }
        
        try:
            index = int(user_input) - 1
            children = session_data.get('children', [])
            
            if index < 0 or index >= len(children):
                return {
                    "session_id": session_id,
                    "response": "END Invalid selection.",
                    "continues": False
                }
            
            child = children[index]
            action = session_data.get('action')
            
            return self._route_to_action(session_id, action, child['student_id'], child['school_id'])
            
        except (ValueError, IndexError):
            return {
                "session_id": session_id,
                "response": "END Invalid input.",
                "continues": False
            }
    
    def _route_to_action(
        self,
        session_id: str,
        action: str,
        student_id: str,
        school_id: str
    ) -> Dict[str, Any]:
        """Route to specific action"""
        
        session_data = {
            'student_id': student_id,
            'school_id': school_id
        }
        
        if action == 'check_attendance':
            self._update_session(session_id, 'attendance', session_data)
            return self._show_attendance(session_id, session_data)
        
        elif action == 'check_fees':
            self._update_session(session_id, 'fees', session_data)
            return self._show_fees(session_id, session_data)
        
        elif action == 'check_grades':
            self._update_session(session_id, 'grades', session_data)
            return self._show_grades(session_id, session_data)
        
        elif action == 'pay_fees':
            self._update_session(session_id, 'pay_fees', session_data)
            return self._initiate_payment(session_id, session_data)
        
        elif action == 'check_requirements':
            self._update_session(session_id, 'requirements', session_data)
            return self._show_requirements(session_id, session_data)
        
        else:
            return {
                "session_id": session_id,
                "response": "END Invalid action.",
                "continues": False
            }
    
    # ============================================================================
    # DATA FETCHERS
    # ============================================================================
    
    def _get_user_children(self, phone_number: str) -> list:
        """Get children for parent's phone number"""
        query = """
        SELECT DISTINCT
            s.id as student_id,
            s.first_name,
            s.last_name,
            s.class_name,
            s.school_id
        FROM students s
        JOIN student_parents sp ON sp.student_id = s.id
        JOIN parents p ON p.id = sp.parent_id
        WHERE p.phone = %s AND s.status = 'active'
        ORDER BY s.first_name
        """
        
        return self.db.execute_query(query, (phone_number,), fetch=True)
    
    def _show_attendance(self, session_id: str, session_data: Dict) -> Dict[str, Any]:
        """Show attendance for last 5 days"""
        student_id = session_data['student_id']
        
        query = """
        SELECT 
            s.first_name, s.last_name, s.class_name,
            a.date, a.status
        FROM students s
        LEFT JOIN attendance a ON a.student_id = s.id
        WHERE s.id = %s
        AND a.date >= CURRENT_DATE - INTERVAL '5 days'
        ORDER BY a.date DESC
        LIMIT 5
        """
        
        rows = self.db.execute_query(query, (student_id,), fetch=True)
        
        if not rows:
            response = "END No attendance data available."
        else:
            student = rows[0]
            response = f"END {student['first_name']} {student['last_name']} ({student['class_name']})\n\n"
            response += "Last 5 days:\n"
            for row in rows:
                status_icon = "✓" if row['status'] == 'present' else "✗"
                response += f"{row['date']}: {status_icon} {row['status'].title()}\n"
        
        self._end_session(session_id)
        return {
            "session_id": session_id,
            "response": response,
            "continues": False
        }
    
    def _show_fees(self, session_id: str, session_data: Dict) -> Dict[str, Any]:
        """Show fee balance"""
        student_id = session_data['student_id']
        
        query = """
        SELECT 
            s.first_name, s.last_name, s.class_name,
            COALESCE(SUM(sf.balance), 0) as total_balance
        FROM students s
        LEFT JOIN student_fees sf ON sf.student_id = s.id
        WHERE s.id = %s
        GROUP BY s.id, s.first_name, s.last_name, s.class_name
        """
        
        rows = self.db.execute_query(query, (student_id,), fetch=True)
        
        if rows:
            student = rows[0]
            balance = float(student['total_balance'])
            response = (
                f"END {student['first_name']} {student['last_name']} ({student['class_name']})\n\n"
                f"Fee Balance: {balance:,.0f} UGX\n\n"
                "To pay, dial *123*789# and select Pay Fees"
            )
        else:
            response = "END No fee data available."
        
        self._end_session(session_id)
        return {
            "session_id": session_id,
            "response": response,
            "continues": False
        }
    
    def _show_grades(self, session_id: str, session_data: Dict) -> Dict[str, Any]:
        """Show recent grades"""
        student_id = session_data['student_id']
        
        query = """
        SELECT 
            s.first_name, s.last_name, s.class_name,
            a.name as assessment_name,
            a.subject,
            ar.marks_obtained,
            a.max_marks,
            ar.grade
        FROM students s
        JOIN assessment_results ar ON ar.student_id = s.id
        JOIN assessments a ON a.id = ar.assessment_id
        WHERE s.id = %s
        ORDER BY a.date DESC
        LIMIT 5
        """
        
        rows = self.db.execute_query(query, (student_id,), fetch=True)
        
        if not rows:
            response = "END No grades available yet."
        else:
            student = rows[0]
            response = f"END {student['first_name']} {student['last_name']} ({student['class_name']})\n\n"
            response += "Recent Results:\n"
            for row in rows:
                response += f"{row['subject']}: {row['marks_obtained']}/{row['max_marks']} ({row['grade']})\n"
        
        self._end_session(session_id)
        return {
            "session_id": session_id,
            "response": response,
            "continues": False
        }
    
    def _show_requirements(self, session_id: str, session_data: Dict) -> Dict[str, Any]:
        """Show pending requirements"""
        student_id = session_data['student_id']
        
        query = """
        SELECT 
            sr.name,
            sr.requirement_type,
            sr.quantity_required,
            sr.unit,
            sr.amount_required,
            sr.due_date,
            CASE 
                WHEN srs.id IS NOT NULL THEN 'Submitted'
                ELSE 'Pending'
            END as status
        FROM school_requirements sr
        LEFT JOIN student_requirement_submissions srs ON (
            srs.requirement_id = sr.id AND srs.student_id = %s
        )
        WHERE sr.is_active = true
        AND (sr.applies_to = 'all_students' OR sr.applies_to = (
            SELECT class_name FROM students WHERE id = %s
        ))
        ORDER BY sr.due_date ASC
        LIMIT 5
        """
        
        rows = self.db.execute_query(query, (student_id, student_id), fetch=True)
        
        if not rows:
            response = "END No pending requirements."
        else:
            response = "END Pending Requirements:\n\n"
            for row in rows:
                status_icon = "✓" if row['status'] == 'Submitted' else "⏳"
                if row['requirement_type'] == 'supply':
                    response += f"{status_icon} {row['name']} ({row['quantity_required']} {row['unit']})\n"
                else:
                    response += f"{status_icon} {row['name']} ({row['amount_required']:,.0f} UGX)\n"
        
        self._end_session(session_id)
        return {
            "session_id": session_id,
            "response": response,
            "continues": False
        }
    
    def _initiate_payment(self, session_id: str, session_data: Dict) -> Dict[str, Any]:
        """Initiate mobile money payment"""
        student_id = session_data['student_id']
        
        # Get fee balance
        query = """
        SELECT COALESCE(SUM(balance), 0) as balance
        FROM student_fees WHERE student_id = %s
        """
        
        result = self.db.execute_query(query, (student_id,), fetch=True)
        balance = float(result[0]['balance']) if result else 0
        
        if balance <= 0:
            response = "END No fees due. Thank you!"
        else:
            # In production, integrate with MTN/Airtel API here
            response = (
                f"END Fee Balance: {balance:,.0f} UGX\n\n"
                "You will receive a Mobile Money prompt shortly.\n"
                "Enter your PIN to complete payment."
            )
            
            # TODO: Trigger mobile money prompt
            # self._trigger_mobile_money_prompt(phone_number, balance)
        
        self._end_session(session_id)
        return {
            "session_id": session_id,
            "response": response,
            "continues": False
        }
    
    # ============================================================================
    # SESSION UTILITIES
    # ============================================================================
    
    def _update_session(
        self,
        session_id: str,
        new_menu: str,
        session_data: Dict
    ) -> None:
        """Update session state"""
        query = """
        UPDATE ussd_sessions
        SET current_menu = %s,
            session_data = %s,
            last_activity = CURRENT_TIMESTAMP
        WHERE session_id = %s
        """
        
        self.db.execute_query(query, (new_menu, session_data, session_id))
    
    def _end_session(self, session_id: str) -> None:
        """End USSD session"""
        query = """
        UPDATE ussd_sessions
        SET status = 'completed',
            last_activity = CURRENT_TIMESTAMP
        WHERE session_id = %s
        """
        
        self.db.execute_query(query, (session_id,))
    
    def clean_expired_sessions(self) -> int:
        """Clean up expired sessions (older than 5 minutes)"""
        query = """
        UPDATE ussd_sessions
        SET status = 'expired'
        WHERE status = 'active'
        AND expires_at < CURRENT_TIMESTAMP
        """
        
        self.db.execute_query(query)
        return 0  # Return count if needed


def get_ussd_service() -> USSDService:
    """Helper to get USSD service instance"""
    return USSDService()
