"""
Angels AI - Executive Assistant Agent Service
Handles all executive-level administrative tasks:
- Student registration & admission automation
- Meeting scheduling
- Report generation
- Strategic coordination
"""

from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from database import *
import json


class ExecutiveAssistantService:
    """
    Think of this as your digital Chief of Staff
    Handles everything an executive assistant would do, but 10x faster
    """
    
    def __init__(self, school_id: str):
        self.school_id = school_id
        self.student_ops = get_student_ops()
        self.parent_ops = get_parent_ops()
        self.fee_ops = get_fee_ops()
        self.message_ops = get_message_ops()
        self.db = get_db()
    
    # ============================================
    # STUDENT REGISTRATION & ADMISSION
    # ============================================
    
    def process_student_registration(self, registration_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Automated student registration workflow
        This replaces 2-3 hours of manual data entry
        
        Args:
            registration_data: All student and parent information
        
        Returns:
            Complete registration result with student ID, parent ID, fee assignment
        """
        try:
            # Step 1: Generate admission number
            admission_number = self._generate_admission_number()
            
            # Step 2: Create student record
            student_data = {
                'school_id': self.school_id,
                'admission_number': admission_number,
                'first_name': registration_data['student']['first_name'],
                'middle_name': registration_data['student'].get('middle_name'),
                'last_name': registration_data['student']['last_name'],
                'date_of_birth': registration_data['student']['date_of_birth'],
                'gender': registration_data['student']['gender'],
                'current_grade': registration_data['student']['grade'],
                'current_class': registration_data['student'].get('class'),
                'admission_date': datetime.now().date(),
                'enrollment_status': 'active',
                'home_address': registration_data['student'].get('address'),
                'county_state': registration_data['student'].get('county'),
                'city': registration_data['student'].get('city'),
                'primary_phone': registration_data['student'].get('phone'),
                'email': registration_data['student'].get('email'),
                'blood_group': registration_data['student'].get('blood_group'),
                'allergies': registration_data['student'].get('allergies'),
                'medical_conditions': registration_data['student'].get('medical_conditions'),
                'emergency_contact_name': registration_data.get('emergency', {}).get('name'),
                'emergency_contact_phone': registration_data.get('emergency', {}).get('phone'),
                'emergency_contact_relationship': registration_data.get('emergency', {}).get('relationship')
            }
            
            student = self.student_ops.create_student(student_data)
            
            # Step 3: Create parent/guardian records
            parent_ids = []
            for parent_info in registration_data.get('parents', []):
                parent_data = {
                    'school_id': self.school_id,
                    'first_name': parent_info['first_name'],
                    'middle_name': parent_info.get('middle_name'),
                    'last_name': parent_info['last_name'],
                    'gender': parent_info.get('gender'),
                    'primary_phone': parent_info['phone'],
                    'secondary_phone': parent_info.get('secondary_phone'),
                    'email': parent_info.get('email'),
                    'whatsapp_number': parent_info.get('whatsapp', parent_info['phone']),
                    'preferred_language': parent_info.get('language', 'en'),
                    'occupation': parent_info.get('occupation'),
                    'employer': parent_info.get('employer'),
                    'work_phone': parent_info.get('work_phone'),
                    'home_address': parent_info.get('address'),
                    'county_state': parent_info.get('county'),
                    'city': parent_info.get('city'),
                    'preferred_contact_method': parent_info.get('contact_method', 'whatsapp'),
                    'opt_in_notifications': parent_info.get('opt_in_notifications', True)
                }
                
                parent = self.parent_ops.create_parent(parent_data)
                parent_ids.append(parent['id'])
                
                # Link parent to student
                self.parent_ops.link_parent_to_student(
                    student_id=student['id'],
                    parent_id=parent['id'],
                    relationship_type=parent_info.get('relationship', 'parent'),
                    is_primary=parent_info.get('is_primary', False),
                    is_fee_payer=parent_info.get('is_fee_payer', False)
                )
            
            # Step 4: Assign appropriate fee structure
            fee_assignment = self._auto_assign_fees(
                student_id=student['id'],
                grade=registration_data['student']['grade']
            )
            
            # Step 5: Send welcome messages to parents
            self._send_registration_confirmation(student, parent_ids)
            
            # Step 6: Log activity
            self._log_analytics_event(
                event_type='student_enrolled',
                event_category='academic',
                event_data={
                    'student_id': student['id'],
                    'admission_number': admission_number,
                    'grade': registration_data['student']['grade'],
                    'parent_count': len(parent_ids)
                }
            )
            
            return {
                'success': True,
                'student': student,
                'parents': parent_ids,
                'fee_assignment': fee_assignment,
                'admission_number': admission_number,
                'message': f"✅ Student {student['first_name']} {student['last_name']} registered successfully!"
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': f"❌ Registration failed: {str(e)}"
            }
    
    def _generate_admission_number(self) -> str:
        """Generate unique admission number for new student"""
        # Get current year and count of students
        year = datetime.now().year
        
        query = """
        SELECT COUNT(*) as count FROM students 
        WHERE school_id = %s AND deleted_at IS NULL
        """
        result = self.db.execute_query(query, (self.school_id,))
        count = result[0]['count'] + 1 if result else 1
        
        return f"ADM{year}{count:04d}"  # e.g., ADM20250001
    
    def _auto_assign_fees(self, student_id: str, grade: str) -> Optional[Dict]:
        """Automatically assign appropriate fee structure to new student"""
        # Find active fee structure for this grade and current term
        current_year = datetime.now().year
        
        query = """
        SELECT * FROM fee_structures
        WHERE school_id = %s 
        AND grade_level = %s
        AND academic_year = %s
        AND is_active = true
        ORDER BY created_at DESC
        LIMIT 1
        """
        
        results = self.db.execute_query(query, (self.school_id, grade, str(current_year)))
        
        if results:
            fee_structure = results[0]
            return self.fee_ops.assign_fee_to_student(
                student_id=student_id,
                fee_structure_id=fee_structure['id']
            )
        
        return None
    
    def _send_registration_confirmation(self, student: Dict, parent_ids: List[str]):
        """Send welcome message to parents after successful registration"""
        for parent_id in parent_ids:
            # Get parent details
            query = "SELECT * FROM parents WHERE id = %s"
            parent_result = self.db.execute_query(query, (parent_id,))
            
            if parent_result:
                parent = parent_result[0]
                
                message_body = f"""
Welcome to our school! 🎓

Your child {student['first_name']} {student['last_name']} has been successfully registered.

📝 Admission Number: {student['admission_number']}
📚 Grade: {student['current_grade']}
📅 Admission Date: {student['admission_date']}

You will receive fee information and other important updates via WhatsApp.

Thank you for choosing us!
                """.strip()
                
                # Record message (actual sending handled by Parent Engagement Agent)
                self.message_ops.create_message({
                    'school_id': self.school_id,
                    'recipient_type': 'parent',
                    'recipient_id': parent_id,
                    'recipient_phone': parent['primary_phone'],
                    'recipient_email': parent['email'],
                    'message_type': 'whatsapp',
                    'subject': None,
                    'body': message_body,
                    'template_name': 'registration_confirmation',
                    'template_variables': json.dumps({
                        'student_name': f"{student['first_name']} {student['last_name']}",
                        'admission_number': student['admission_number'],
                        'grade': student['current_grade']
                    }),
                    'trigger_event': 'student_registration',
                    'triggered_by': 'ai_agent',
                    'staff_id': None,
                    'cost_amount': 0.01  # Estimate
                })
    
    # ============================================
    # ENROLLMENT ANALYTICS & REPORTS
    # ============================================
    
    def get_enrollment_statistics(self, time_period: str = 'week') -> Dict[str, Any]:
        """
        Generate enrollment statistics for executive dashboard
        
        Args:
            time_period: 'day', 'week', 'month', 'year'
        
        Returns:
            Comprehensive enrollment analytics
        """
        time_filters = {
            'day': "created_at >= CURRENT_DATE",
            'week': "created_at >= CURRENT_DATE - INTERVAL '7 days'",
            'month': "created_at >= CURRENT_DATE - INTERVAL '30 days'",
            'year': "created_at >= CURRENT_DATE - INTERVAL '1 year'"
        }
        
        time_filter = time_filters.get(time_period, time_filters['week'])
        
        # Total students
        total_query = """
        SELECT 
            COUNT(*) as total_students,
            COUNT(CASE WHEN enrollment_status = 'active' THEN 1 END) as active_students,
            COUNT(CASE WHEN gender = 'male' THEN 1 END) as male_count,
            COUNT(CASE WHEN gender = 'female' THEN 1 END) as female_count
        FROM students
        WHERE school_id = %s AND deleted_at IS NULL
        """
        total_stats = self.db.execute_query(total_query, (self.school_id,))[0]
        
        # Recent enrollments
        recent_query = f"""
        SELECT 
            COUNT(*) as new_enrollments,
            json_agg(
                json_build_object(
                    'name', first_name || ' ' || last_name,
                    'admission_number', admission_number,
                    'grade', current_grade,
                    'date', admission_date
                )
            ) as recent_students
        FROM students
        WHERE school_id = %s AND {time_filter} AND deleted_at IS NULL
        """
        recent_stats = self.db.execute_query(recent_query, (self.school_id,))[0]
        
        # By grade distribution
        grade_query = """
        SELECT 
            current_grade,
            COUNT(*) as student_count
        FROM students
        WHERE school_id = %s AND enrollment_status = 'active' AND deleted_at IS NULL
        GROUP BY current_grade
        ORDER BY current_grade
        """
        grade_distribution = self.db.execute_query(grade_query, (self.school_id,))
        
        return {
            'period': time_period,
            'total_students': total_stats['total_students'],
            'active_students': total_stats['active_students'],
            'gender_distribution': {
                'male': total_stats['male_count'],
                'female': total_stats['female_count']
            },
            'new_enrollments': recent_stats['new_enrollments'] or 0,
            'recent_students': recent_stats['recent_students'] or [],
            'grade_distribution': [dict(g) for g in grade_distribution],
            'generated_at': datetime.now().isoformat()
        }
    
    def generate_executive_report(self, report_type: str = 'daily') -> Dict[str, Any]:
        """
        Generate comprehensive executive report
        This is what the Digital CEO uses for strategic briefings
        
        Args:
            report_type: 'daily', 'weekly', 'monthly'
        
        Returns:
            Complete executive report with all key metrics
        """
        enrollment_stats = self.get_enrollment_statistics(
            'day' if report_type == 'daily' else 'week' if report_type == 'weekly' else 'month'
        )
        
        fee_stats = self.fee_ops.get_fee_collection_summary(self.school_id)
        
        # Parent engagement metrics
        message_query = f"""
        SELECT 
            COUNT(*) as messages_sent,
            COUNT(CASE WHEN status = 'delivered' THEN 1 END) as delivered_count,
            COUNT(CASE WHEN status = 'read' THEN 1 END) as read_count,
            COUNT(CASE WHEN status = 'failed' THEN 1 END) as failed_count,
            SUM(cost_amount) as total_communication_cost
        FROM messages
        WHERE school_id = %s 
        AND created_at >= CURRENT_DATE - INTERVAL '7 days'
        """
        message_stats = self.db.execute_query(message_query, (self.school_id,))[0]
        
        return {
            'report_type': report_type,
            'school_id': self.school_id,
            'generated_at': datetime.now().isoformat(),
            
            # Academic Overview
            'enrollment': enrollment_stats,
            
            # Financial Overview
            'finances': {
                'total_expected': float(fee_stats.get('total_expected', 0)),
                'total_collected': float(fee_stats.get('total_collected', 0)),
                'total_outstanding': float(fee_stats.get('total_outstanding', 0)),
                'collection_rate': float(fee_stats.get('collection_rate_percentage', 0)),
                'overdue_count': fee_stats.get('overdue_count', 0)
            },
            
            # Communication Overview
            'communications': {
                'messages_sent': message_stats['messages_sent'] or 0,
                'delivery_rate': (
                    (message_stats['delivered_count'] / message_stats['messages_sent'] * 100)
                    if message_stats['messages_sent'] else 0
                ),
                'read_rate': (
                    (message_stats['read_count'] / message_stats['messages_sent'] * 100)
                    if message_stats['messages_sent'] else 0
                ),
                'failed_messages': message_stats['failed_count'] or 0,
                'total_cost': float(message_stats['total_communication_cost'] or 0)
            },
            
            # Executive Summary
            'summary': self._generate_executive_summary(
                enrollment_stats, fee_stats, message_stats
            )
        }
    
    def _generate_executive_summary(self, enrollment, fees, messages) -> List[str]:
        """Generate AI-powered executive summary insights"""
        insights = []
        
        # Enrollment insights
        if enrollment['new_enrollments'] > 0:
            insights.append(
                f"✅ {enrollment['new_enrollments']} new student(s) enrolled this period"
            )
        
        # Financial insights
        collection_rate = fees.get('collection_rate_percentage', 0)
        if collection_rate >= 90:
            insights.append(f"💰 Excellent fee collection rate: {collection_rate}%")
        elif collection_rate < 70:
            insights.append(
                f"⚠️ Low fee collection rate: {collection_rate}% - Recommend increased follow-up"
            )
        
        if fees.get('overdue_count', 0) > 0:
            insights.append(
                f"⏰ {fees['overdue_count']} students with overdue fees - Automated reminders active"
            )
        
        # Communication insights
        delivery_rate = (
            (messages['delivered_count'] / messages['messages_sent'] * 100)
            if messages['messages_sent'] else 100
        )
        
        if delivery_rate < 90:
            insights.append(
                f"📱 Communication delivery rate: {delivery_rate:.1f}% - Check phone numbers"
            )
        
        if not insights:
            insights.append("✨ All systems operating smoothly - No critical issues detected")
        
        return insights
    
    # ============================================
    # MEETING & SCHEDULE MANAGEMENT
    # ============================================
    
    def schedule_parent_teacher_meeting(self, meeting_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Automatically schedule parent-teacher meetings
        Sends invitations to all parties
        """
        # Implementation would go here
        # For MVP, we'll track this as a task
        pass
    
    # ============================================
    # ANALYTICS & LOGGING
    # ============================================
    
    def _log_analytics_event(self, event_type: str, event_category: str, 
                            event_data: Dict[str, Any]):
        """Log events for Digital CEO analysis"""
        query = """
        INSERT INTO analytics_events (
            school_id, event_type, event_category, event_data, 
            actor_type, event_timestamp
        ) VALUES (%s, %s, %s, %s, %s, NOW())
        """
        
        self.db.execute_query(
            query,
            (
                self.school_id,
                event_type,
                event_category,
                json.dumps(event_data),
                'ai_agent'
            ),
            fetch=False
        )


# ============================================
# CONVENIENCE FUNCTIONS
# ============================================

def process_registration(school_id: str, registration_data: Dict) -> Dict:
    """Quick function to process a registration"""
    service = ExecutiveAssistantService(school_id)
    return service.process_student_registration(registration_data)

def get_executive_dashboard(school_id: str) -> Dict:
    """Quick function to get executive dashboard data"""
    service = ExecutiveAssistantService(school_id)
    return service.generate_executive_report('daily')
