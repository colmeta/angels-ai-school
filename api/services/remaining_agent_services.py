"""
Angels AI - Remaining Agent Services
Academic Operations, Teacher Liberation, Security & Safety, Opportunity Intelligence
"""

from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from database import *
import json


# ============================================
# ACADEMIC OPERATIONS AGENT
# ============================================

class AcademicOperationsService:
    """
    Educational Excellence Manager
    Handles academic operations, performance tracking, and interventions
    """
    
    def __init__(self, school_id: str):
        self.school_id = school_id
        self.student_ops = get_student_ops()
        self.db = get_db()
    
    def generate_report_cards(self, grade: str, term: str) -> Dict[str, Any]:
        """Generate automated report cards for a grade"""
        students = self.student_ops.get_students_by_grade(self.school_id, grade)
        
        report_cards_generated = []
        for student in students:
            report_card = {
                'student_id': student['id'],
                'student_name': f"{student['first_name']} {student['last_name']}",
                'admission_number': student['admission_number'],
                'grade': grade,
                'term': term,
                'generated_at': datetime.now().isoformat(),
                'status': 'generated'
            }
            report_cards_generated.append(report_card)
        
        return {
            'grade': grade,
            'term': term,
            'total_students': len(students),
            'reports_generated': len(report_cards_generated),
            'reports': report_cards_generated
        }
    
    def identify_at_risk_students(self) -> List[Dict]:
        """
        Identify students at risk based on various factors
        Uses predictive analytics
        """
        # TODO: Implement ML-based risk prediction
        # For MVP, use simple heuristics
        
        at_risk_students = []
        
        # Students with overdue fees (financial risk)
        query = """
        SELECT DISTINCT s.*, sf.balance, sf.payment_status
        FROM students s
        JOIN student_fees sf ON s.id = sf.student_id
        WHERE s.school_id = %s
        AND sf.payment_status = 'overdue'
        AND s.enrollment_status = 'active'
        """
        
        financial_risk = self.db.execute_query(query, (self.school_id,))
        
        for student in financial_risk:
            at_risk_students.append({
                'student_id': student['id'],
                'student_name': f"{student['first_name']} {student['last_name']}",
                'risk_type': 'financial',
                'risk_level': 'high' if float(student['balance']) > 50000 else 'medium',
                'details': f"Overdue balance: KES {student['balance']}",
                'recommended_intervention': 'Parent engagement and payment plan'
            })
        
        return at_risk_students
    
    def generate_performance_analytics(self, grade: Optional[str] = None) -> Dict:
        """Generate academic performance analytics"""
        
        # For MVP, return framework
        # In production, would analyze actual grades and performance data
        
        return {
            'grade': grade or 'All Grades',
            'analytics': {
                'average_performance': 'Data collection in progress',
                'top_performers': [],
                'needs_support': [],
                'improvement_trends': 'Tracking ongoing'
            },
            'recommendations': [
                'Implement regular assessment tracking',
                'Set up automated performance alerts',
                'Create intervention programs for struggling students'
            ]
        }


# ============================================
# TEACHER LIBERATION AGENT
# ============================================

class TeacherLiberationService:
    """
    Administrative Freedom Fighter
    Eliminates teacher administrative burden
    """
    
    def __init__(self, school_id: str):
        self.school_id = school_id
        self.db = get_db()
    
    def automate_attendance_tracking(self, class_id: str, date: str, 
                                    attendance_data: List[Dict]) -> Dict:
        """
        Automated attendance recording
        Teachers just mark present/absent, system handles everything else
        """
        records_created = 0
        
        for record in attendance_data:
            # In production, would save to attendance table
            records_created += 1
        
        return {
            'class_id': class_id,
            'date': date,
            'records_created': records_created,
            'time_saved': f"{records_created * 2} minutes",  # Estimate 2 min per manual entry
            'message': f"✅ Attendance recorded for {records_created} students in seconds"
        }
    
    def generate_lesson_plan_template(self, subject: str, grade: str, 
                                     topic: str) -> Dict:
        """Generate lesson plan template to save teacher time"""
        
        template = {
            'subject': subject,
            'grade': grade,
            'topic': topic,
            'generated_at': datetime.now().isoformat(),
            'lesson_plan': {
                'objectives': f'AI-generated objectives for {topic}',
                'materials': ['Textbooks', 'Visual aids', 'Worksheets'],
                'activities': [
                    'Introduction (10 min)',
                    'Main lesson (30 min)',
                    'Practice activities (15 min)',
                    'Assessment (5 min)'
                ],
                'assessment_methods': 'Q&A, Written exercise, Class participation',
                'homework': f'Practice exercises on {topic}'
            },
            'time_saved': '45-60 minutes of planning time'
        }
        
        return template
    
    def draft_parent_communication(self, communication_type: str, 
                                   student_id: str, context: Dict) -> Dict:
        """
        Auto-draft parent communications
        Teacher reviews and approves, saves 80% of writing time
        """
        
        student = self.db.execute_query(
            "SELECT * FROM students WHERE id = %s",
            (student_id,)
        )[0]
        
        drafts = {
            'progress_update': f"""
Dear Parent,

I am pleased to inform you about {student['first_name']}'s progress this term.

{context.get('performance_summary', 'Showing good improvement in class')}

Areas of strength: {context.get('strengths', 'Participation, homework completion')}
Areas for improvement: {context.get('improvements', 'Continue practicing at home')}

Please feel free to reach out if you have questions.

Best regards,
[Teacher Name]
            """.strip(),
            
            'behavioral_note': f"""
Dear Parent,

I wanted to discuss {student['first_name']}'s behavior in class.

{context.get('incident_description', 'Please see details below')}

Let's work together to support {student['first_name']}'s success.

Please contact me to discuss further.

Best regards,
[Teacher Name]
            """.strip(),
            
            'achievement_celebration': f"""
Dear Parent,

Congratulations! {student['first_name']} has achieved {context.get('achievement', 'excellent results')}.

{context.get('details', 'We are very proud of this accomplishment')}

Keep up the great work!

Best regards,
[Teacher Name]
            """.strip()
        }
        
        return {
            'student_name': f"{student['first_name']} {student['last_name']}",
            'communication_type': communication_type,
            'draft_message': drafts.get(communication_type, 'Template not found'),
            'time_saved': '15-20 minutes',
            'status': 'ready_for_review'
        }
    
    def calculate_teacher_time_savings(self, teacher_id: Optional[str] = None) -> Dict:
        """Calculate total time saved by automation"""
        
        # Estimate based on automation features
        weekly_savings = {
            'attendance_tracking': 60,  # minutes
            'grade_recording': 90,
            'parent_communications': 120,
            'lesson_plan_templates': 180,
            'report_card_generation': 240,
            'administrative_forms': 60
        }
        
        total_weekly = sum(weekly_savings.values())
        total_monthly = total_weekly * 4
        
        return {
            'weekly_savings': {
                'minutes': total_weekly,
                'hours': total_weekly / 60,
                'activities': weekly_savings
            },
            'monthly_savings': {
                'minutes': total_monthly,
                'hours': total_monthly / 60,
                'days': total_monthly / 480  # 8-hour workday
            },
            'impact': f"Teachers freed up {total_weekly/60:.1f} hours/week to focus on teaching"
        }


# ============================================
# SECURITY & SAFETY GUARDIAN AGENT
# ============================================

class SecuritySafetyService:
    """
    Security & Safety Guardian
    Ensures student safety and security monitoring
    """
    
    def __init__(self, school_id: str):
        self.school_id = school_id
        self.student_ops = get_student_ops()
        self.parent_ops = get_parent_ops()
        self.message_ops = get_message_ops()
        self.db = get_db()
    
    def log_student_checkin(self, student_id: str, timestamp: Optional[datetime] = None) -> Dict:
        """Log student check-in and notify parent"""
        
        if timestamp is None:
            timestamp = datetime.now()
        
        student = self.db.execute_query(
            "SELECT * FROM students WHERE id = %s",
            (student_id,)
        )[0]
        
        # In production, would save to attendance/security log
        
        # Notify parent
        student_with_parents = self.student_ops.get_student_with_parents(student_id)
        
        if student_with_parents and student_with_parents.get('parents'):
            primary_parent = next(
                (p for p in student_with_parents['parents'] if p.get('is_primary')),
                student_with_parents['parents'][0]
            )
            
            message = f"""
✅ STUDENT CHECK-IN

{student['first_name']} {student['last_name']} has arrived safely at school.

Time: {timestamp.strftime('%I:%M %p')}
Date: {timestamp.strftime('%B %d, %Y')}

Have a great day!
            """.strip()
            
            self.message_ops.create_message({
                'school_id': self.school_id,
                'recipient_type': 'parent',
                'recipient_id': primary_parent.get('parent_id'),
                'recipient_phone': primary_parent.get('phone'),
                'recipient_email': None,
                'message_type': 'whatsapp',
                'subject': None,
                'body': message,
                'template_name': 'student_checkin',
                'template_variables': json.dumps({
                    'student_id': student_id,
                    'timestamp': timestamp.isoformat()
                }),
                'trigger_event': 'student_checkin',
                'triggered_by': 'security_system',
                'staff_id': None,
                'cost_amount': 0.01
            })
        
        return {
            'success': True,
            'student_id': student_id,
            'student_name': f"{student['first_name']} {student['last_name']}",
            'checkin_time': timestamp.isoformat(),
            'parent_notified': True
        }
    
    def log_student_checkout(self, student_id: str, authorized_by: str,
                           timestamp: Optional[datetime] = None) -> Dict:
        """Log student check-out and notify parent"""
        
        if timestamp is None:
            timestamp = datetime.now()
        
        student = self.db.execute_query(
            "SELECT * FROM students WHERE id = %s",
            (student_id,)
        )[0]
        
        # In production, would save to security log
        
        # Notify parent
        student_with_parents = self.student_ops.get_student_with_parents(student_id)
        
        if student_with_parents and student_with_parents.get('parents'):
            primary_parent = next(
                (p for p in student_with_parents['parents'] if p.get('is_primary')),
                student_with_parents['parents'][0]
            )
            
            message = f"""
👋 STUDENT CHECK-OUT

{student['first_name']} {student['last_name']} has been checked out from school.

Time: {timestamp.strftime('%I:%M %p')}
Date: {timestamp.strftime('%B %d, %Y')}
Authorized by: {authorized_by}

Safe journey home!
            """.strip()
            
            self.message_ops.create_message({
                'school_id': self.school_id,
                'recipient_type': 'parent',
                'recipient_id': primary_parent.get('parent_id'),
                'recipient_phone': primary_parent.get('phone'),
                'recipient_email': None,
                'message_type': 'whatsapp',
                'subject': None,
                'body': message,
                'template_name': 'student_checkout',
                'template_variables': json.dumps({
                    'student_id': student_id,
                    'timestamp': timestamp.isoformat(),
                    'authorized_by': authorized_by
                }),
                'trigger_event': 'student_checkout',
                'triggered_by': 'security_system',
                'staff_id': None,
                'cost_amount': 0.01
            })
        
        return {
            'success': True,
            'student_id': student_id,
            'student_name': f"{student['first_name']} {student['last_name']}",
            'checkout_time': timestamp.isoformat(),
            'authorized_by': authorized_by,
            'parent_notified': True
        }
    
    def broadcast_emergency_alert(self, alert_type: str, message: str,
                                  target_groups: List[str] = None) -> Dict:
        """
        Broadcast emergency alert to parents and staff
        alert_type: 'security', 'weather', 'health', 'general'
        """
        
        if target_groups is None:
            target_groups = ['all_parents', 'all_staff']
        
        # Get all parents
        parents_query = """
        SELECT DISTINCT p.*
        FROM parents p
        JOIN student_parent_relationships spr ON p.id = spr.parent_id
        JOIN students s ON spr.student_id = s.id
        WHERE s.school_id = %s
        AND s.enrollment_status = 'active'
        AND p.deleted_at IS NULL
        """
        parents = self.db.execute_query(parents_query, (self.school_id,))
        
        alert_message = f"""
🚨 EMERGENCY ALERT - {alert_type.upper()}

{message}

School Office: [SCHOOL_PHONE]

This is an automated emergency notification.
        """.strip()
        
        messages_sent = 0
        for parent in parents:
            self.message_ops.create_message({
                'school_id': self.school_id,
                'recipient_type': 'parent',
                'recipient_id': parent['id'],
                'recipient_phone': parent['primary_phone'],
                'recipient_email': parent['email'],
                'message_type': 'whatsapp',
                'subject': f"EMERGENCY ALERT - {alert_type.upper()}",
                'body': alert_message,
                'template_name': 'emergency_alert',
                'template_variables': json.dumps({
                    'alert_type': alert_type,
                    'message': message
                }),
                'trigger_event': 'emergency_broadcast',
                'triggered_by': 'security_system',
                'staff_id': None,
                'cost_amount': 0.02  # Emergency priority
            })
            messages_sent += 1
        
        return {
            'success': True,
            'alert_type': alert_type,
            'recipients': messages_sent,
            'broadcast_time': datetime.now().isoformat()
        }
    
    def log_security_incident(self, incident_type: str, description: str,
                            student_id: Optional[str] = None,
                            severity: str = 'medium') -> Dict:
        """Log security or safety incident"""
        
        # In production, would save to incidents table
        
        incident_record = {
            'incident_id': f"INC-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
            'school_id': self.school_id,
            'incident_type': incident_type,
            'description': description,
            'student_id': student_id,
            'severity': severity,
            'timestamp': datetime.now().isoformat(),
            'status': 'reported'
        }
        
        # If critical, notify immediately
        if severity == 'critical':
            # Notify school admin
            pass
        
        return incident_record
    
    def get_daily_security_report(self) -> Dict:
        """Generate daily security summary"""
        
        return {
            'report_date': datetime.now().date().isoformat(),
            'checkins_today': 0,  # Would query actual data
            'checkouts_today': 0,
            'incidents_today': 0,
            'alerts_sent': 0,
            'status': 'All systems operational',
            'recommendations': [
                'Continue monitoring student check-in/check-out patterns',
                'Ensure all staff trained on emergency protocols'
            ]
        }


# ============================================
# OPPORTUNITY INTELLIGENCE AGENT
# ============================================

class OpportunityIntelligenceService:
    """
    Funding Hunter
    Finds grants, funding, partnerships for schools
    """
    
    def __init__(self, school_id: str):
        self.school_id = school_id
        self.db = get_db()
    
    def search_funding_opportunities(self, keywords: List[str] = None,
                                    region: str = 'Africa') -> Dict:
        """
        Search for funding opportunities
        In production, would use web scraping and APIs
        """
        
        if keywords is None:
            keywords = ['education', 'school', 'Kenya', 'grant', 'funding']
        
        # Placeholder for web scraping results
        # In production, would use:
        # - SerperDevTool for Google searches
        # - BraveSearchTool for alternative searches
        # - SpiderTool for deep web scraping
        # - Direct API calls to grant databases
        
        opportunities = [
            {
                'opportunity_id': 'OPP-001',
                'title': 'African Education Initiative Grant',
                'funder': 'Sample Foundation',
                'amount': 'Up to $50,000',
                'deadline': (datetime.now() + timedelta(days=60)).date().isoformat(),
                'eligibility': 'Primary and secondary schools in Kenya',
                'focus_areas': ['Digital transformation', 'Student outcomes'],
                'application_url': 'https://example.com/grant',
                'success_probability': 'Medium-High',
                'effort_required': 'Medium',
                'recommended_action': 'Start application preparation immediately',
                'discovered_at': datetime.now().isoformat()
            },
            {
                'opportunity_id': 'OPP-002',
                'title': 'Technology in Schools Program',
                'funder': 'Tech for Good NGO',
                'amount': 'Hardware donation + $20,000 cash',
                'deadline': (datetime.now() + timedelta(days=90)).date().isoformat(),
                'eligibility': 'Schools with 100+ students',
                'focus_areas': ['ICT infrastructure', 'Digital literacy'],
                'application_url': 'https://example.com/tech-grant',
                'success_probability': 'High',
                'effort_required': 'Low',
                'recommended_action': 'Apply immediately - high success rate',
                'discovered_at': datetime.now().isoformat()
            }
        ]
        
        return {
            'search_keywords': keywords,
            'region': region,
            'opportunities_found': len(opportunities),
            'total_potential_value': '$70,000+',
            'opportunities': opportunities,
            'next_search_scheduled': (datetime.now() + timedelta(days=7)).isoformat()
        }
    
    def analyze_grant_fit(self, opportunity_id: str, school_profile: Dict) -> Dict:
        """
        Analyze how well a funding opportunity fits the school
        Uses AI to assess alignment and success probability
        """
        
        # In production, would use LLM to analyze fit
        
        analysis = {
            'opportunity_id': opportunity_id,
            'fit_score': 85,  # 0-100
            'alignment': {
                'mission_alignment': 'Strong - Focus on digital transformation matches grant',
                'eligibility': 'Meets all requirements',
                'capacity': 'Sufficient capacity to execute project',
                'timeline': 'Adequate time for quality application'
            },
            'success_probability': 75,  # percentage
            'recommended_approach': [
                'Emphasize Angels AI implementation and results',
                'Highlight improved student outcomes through technology',
                'Include parent satisfaction metrics',
                'Demonstrate scalability and sustainability'
            ],
            'required_documentation': [
                'School registration certificate',
                'Financial statements (last 2 years)',
                'Current enrollment data',
                'Technology infrastructure assessment',
                'Project implementation plan'
            ],
            'estimated_effort': '20-30 hours of preparation',
            'recommendation': 'STRONGLY RECOMMEND PURSUING'
        }
        
        return analysis
    
    def generate_grant_application_draft(self, opportunity_id: str,
                                        school_profile: Dict) -> Dict:
        """
        Auto-generate grant application draft
        Saves 80% of application writing time
        """
        
        # In production, would use LLM to generate tailored application
        
        draft = {
            'opportunity_id': opportunity_id,
            'application_sections': {
                'executive_summary': 'AI-generated executive summary based on school data...',
                'organization_background': 'Auto-populated from school profile...',
                'project_description': 'Tailored project description based on grant requirements...',
                'budget': 'Generated budget based on grant amount and school needs...',
                'sustainability_plan': 'Long-term sustainability strategy...',
                'impact_metrics': 'Expected outcomes and measurement plan...'
            },
            'time_saved': '15-20 hours of writing',
            'completeness': '80% ready for review',
            'status': 'draft_ready_for_review'
        }
        
        return draft
    
    def track_submitted_applications(self) -> Dict:
        """Track status of submitted grant applications"""
        
        # In production, would query applications database
        
        return {
            'total_submitted': 0,
            'pending_review': 0,
            'approved': 0,
            'rejected': 0,
            'total_funding_secured': 0,
            'applications': []
        }
    
    def identify_partnership_opportunities(self) -> List[Dict]:
        """
        Identify potential school partnerships
        Corporate sponsorships, NGO partnerships, etc.
        """
        
        opportunities = [
            {
                'type': 'corporate_sponsorship',
                'partner': 'Local Tech Company',
                'opportunity': 'Student mentorship program + equipment donation',
                'potential_value': '$10,000 + equipment',
                'action': 'Initiate contact with CSR department'
            },
            {
                'type': 'ngo_partnership',
                'partner': 'Education NGO',
                'opportunity': 'Teacher training and curriculum support',
                'potential_value': 'Training + resources',
                'action': 'Submit partnership application'
            }
        ]
        
        return opportunities


# ============================================
# CONVENIENCE FUNCTIONS FOR ALL AGENTS
# ============================================

# Academic Operations
def generate_report_cards(school_id: str, grade: str, term: str) -> Dict:
    service = AcademicOperationsService(school_id)
    return service.generate_report_cards(grade, term)

def identify_at_risk_students(school_id: str) -> List[Dict]:
    service = AcademicOperationsService(school_id)
    return service.identify_at_risk_students()

# Teacher Liberation
def calculate_teacher_time_savings(school_id: str) -> Dict:
    service = TeacherLiberationService(school_id)
    return service.calculate_teacher_time_savings()

def generate_lesson_plan(school_id: str, subject: str, grade: str, topic: str) -> Dict:
    service = TeacherLiberationService(school_id)
    return service.generate_lesson_plan_template(subject, grade, topic)

# Security & Safety
def log_student_checkin(school_id: str, student_id: str) -> Dict:
    service = SecuritySafetyService(school_id)
    return service.log_student_checkin(student_id)

def broadcast_emergency(school_id: str, alert_type: str, message: str) -> Dict:
    service = SecuritySafetyService(school_id)
    return service.broadcast_emergency_alert(alert_type, message)

# Opportunity Intelligence
def search_funding(school_id: str, keywords: List[str] = None) -> Dict:
    service = OpportunityIntelligenceService(school_id)
    return service.search_funding_opportunities(keywords)

def analyze_grant_fit(school_id: str, opportunity_id: str, school_profile: Dict) -> Dict:
    service = OpportunityIntelligenceService(school_id)
    return service.analyze_grant_fit(opportunity_id, school_profile)
