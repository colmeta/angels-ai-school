"""
UNEB Service
Uganda National Examinations Board integration
Handles PLE, UCE, UACE registration, results, and report cards
"""
from typing import Dict, Any, List, Optional
from datetime import datetime

from api.services.database import get_db_manager


class UNEBService:
    """Service for UNEB exam management"""
    
    def __init__(self, school_id: str):
        self.school_id = school_id
        self.db = get_db_manager()
    
    # ============================================================================
    # CANDIDATE REGISTRATION
    # ============================================================================
    
    def register_candidate(
        self,
        student_id: str,
        exam_type: str,  # PLE, UCE, UACE
        exam_year: int,
        subjects: List[str],
        index_number: Optional[str] = None,
        center_number: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Register student for UNEB exam
        
        Args:
            student_id: Student ID
            exam_type: PLE, UCE, or UACE
            exam_year: Year of examination
            subjects: List of subjects
            index_number: UNEB index number (if available)
            center_number: Examination center number
        """
        # Verify student exists
        student_query = "SELECT first_name, last_name FROM students WHERE id = %s"
        student = self.db.execute_query(student_query, (student_id,), fetch=True)
        
        if not student:
            return {"success": False, "error": "Student not found"}
        
        # Insert registration
        query = """
        INSERT INTO uneb_registrations (
            school_id, student_id, exam_type, exam_year,
            subjects, index_number, center_number, status
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, 'pending')
        RETURNING id
        """
        
        result = self.db.execute_query(
            query,
            (self.school_id, student_id, exam_type, exam_year, subjects, index_number, center_number),
            fetch=True
        )
        
        return {
            "success": True,
            "registration_id": result[0]['id'],
            "student": f"{student[0]['first_name']} {student[0]['last_name']}",
            "exam_type": exam_type,
            "exam_year": exam_year,
            "subjects": subjects
        }
    
    def get_registrations(
        self,
        exam_type: Optional[str] = None,
        exam_year: Optional[int] = None,
        status: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get all exam registrations"""
        query = """
        SELECT 
            ur.id,
            ur.exam_type,
            ur.exam_year,
            ur.index_number,
            ur.subjects,
            ur.status,
            s.first_name,
            s.last_name,
            s.class_name
        FROM uneb_registrations ur
        JOIN students s ON s.id = ur.student_id
        WHERE ur.school_id = %s
        """
        
        params = [self.school_id]
        
        if exam_type:
            query += " AND ur.exam_type = %s"
            params.append(exam_type)
        
        if exam_year:
            query += " AND ur.exam_year = %s"
            params.append(exam_year)
        
        if status:
            query += " AND ur.status = %s"
            params.append(status)
        
        query += " ORDER BY ur.exam_year DESC, s.first_name"
        
        return self.db.execute_query(query, tuple(params), fetch=True)
    
    def submit_to_uneb(self, registration_id: str) -> Dict[str, Any]:
        """
        Mark registration as submitted to UNEB
        
        In production, this would integrate with UNEB API
        """
        query = """
        UPDATE uneb_registrations
        SET status = 'submitted',
            submitted_to_uneb = true,
            submitted_at = CURRENT_TIMESTAMP
        WHERE id = %s
        RETURNING student_id, exam_type
        """
        
        result = self.db.execute_query(query, (registration_id,), fetch=True)
        
        if result:
            return {
                "success": True,
                "registration_id": registration_id,
                "status": "submitted"
            }
        
        return {"success": False, "error": "Registration not found"}
    
    # ============================================================================
    # RESULTS MANAGEMENT
    # ============================================================================
    
    def import_results(
        self,
        student_id: str,
        exam_type: str,
        exam_year: int,
        index_number: str,
        subject_results: Dict[str, str]  # {subject: grade}
    ) -> Dict[str, Any]:
        """
        Import UNEB results for a student
        
        Args:
            student_id: Student ID
            exam_type: PLE, UCE, UACE
            exam_year: Year
            index_number: UNEB index number
            subject_results: {subject: grade} e.g., {"English": "D1", "Math": "D2"}
        """
        # Calculate aggregate
        aggregate = self._calculate_aggregate(exam_type, subject_results)
        division = self._get_division(exam_type, aggregate)
        
        # Count distinctions, credits, passes
        counts = self._count_grades(exam_type, subject_results)
        
        # Get registration
        reg_query = """
        SELECT id FROM uneb_registrations
        WHERE student_id = %s AND exam_type = %s AND exam_year = %s
        LIMIT 1
        """
        reg = self.db.execute_query(reg_query, (student_id, exam_type, exam_year), fetch=True)
        registration_id = reg[0]['id'] if reg else None
        
        # Insert results
        query = """
        INSERT INTO uneb_results (
            school_id, student_id, registration_id, exam_type, exam_year,
            index_number, subject_results, aggregate, division,
            distinction_count, credit_count, pass_count, fail_count
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (student_id, exam_type, exam_year)
        DO UPDATE SET
            subject_results = EXCLUDED.subject_results,
            aggregate = EXCLUDED.aggregate,
            division = EXCLUDED.division,
            distinction_count = EXCLUDED.distinction_count,
            credit_count = EXCLUDED.credit_count,
            pass_count = EXCLUDED.pass_count,
            fail_count = EXCLUDED.fail_count
        RETURNING id
        """
        
        result = self.db.execute_query(
            query,
            (
                self.school_id, student_id, registration_id, exam_type, exam_year,
                index_number, subject_results, aggregate, division,
                counts['distinctions'], counts['credits'], counts['passes'], counts['fails']
            ),
            fetch=True
        )
        
        return {
            "success": True,
            "result_id": result[0]['id'],
            "exam_type": exam_type,
            "aggregate": aggregate,
            "division": division,
            **counts
        }
    
    def get_results(
        self,
        student_id: Optional[str] = None,
        exam_type: Optional[str] = None,
        exam_year: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Get UNEB results"""
        query = """
        SELECT 
            ur.id,
            ur.exam_type,
            ur.exam_year,
            ur.index_number,
            ur.subject_results,
            ur.aggregate,
            ur.division,
            ur.distinction_count,
            ur.credit_count,
            s.first_name,
            s.last_name,
            s.class_name
        FROM uneb_results ur
        JOIN students s ON s.id = ur.student_id
        WHERE ur.school_id = %s
        """
        
        params = [self.school_id]
        
        if student_id:
            query += " AND ur.student_id = %s"
            params.append(student_id)
        
        if exam_type:
            query += " AND ur.exam_type = %s"
            params.append(exam_type)
        
        if exam_year:
            query += " AND ur.exam_year = %s"
            params.append(exam_year)
        
        query += " ORDER BY ur.exam_year DESC, ur.aggregate ASC"
        
        return self.db.execute_query(query, tuple(params), fetch=True)
    
    def generate_report_card(
        self,
        student_id: str,
        exam_type: str,
        exam_year: int
    ) -> Dict[str, Any]:
        """
        Generate UNEB report card
        
        Returns formatted report card data
        """
        query = """
        SELECT 
            s.first_name,
            s.last_name,
            s.class_name,
            ur.index_number,
            ur.exam_type,
            ur.exam_year,
            ur.subject_results,
            ur.aggregate,
            ur.division,
            ur.distinction_count,
            ur.credit_count,
            sch.name as school_name
        FROM uneb_results ur
        JOIN students s ON s.id = ur.student_id
        JOIN schools sch ON sch.id = ur.school_id
        WHERE ur.student_id = %s
        AND ur.exam_type = %s
        AND ur.exam_year = %s
        """
        
        result = self.db.execute_query(query, (student_id, exam_type, exam_year), fetch=True)
        
        if not result:
            return {"success": False, "error": "Results not found"}
        
        data = result[0]
        
        # Format subject results with grades
        subjects_formatted = []
        subject_results = data['subject_results']
        
        for subject, grade in subject_results.items():
            # Get grade details
            grade_info = self._get_grade_info(exam_type, grade)
            subjects_formatted.append({
                "subject": subject,
                "grade": grade,
                "points": grade_info['points'] if grade_info else None,
                "description": grade_info['description'] if grade_info else None
            })
        
        return {
            "success": True,
            "report_card": {
                "student_name": f"{data['first_name']} {data['last_name']}",
                "index_number": data['index_number'],
                "school_name": data['school_name'],
                "exam_type": data['exam_type'],
                "exam_year": data['exam_year'],
                "subjects": subjects_formatted,
                "aggregate": data['aggregate'],
                "division": data['division'],
                "distinctions": data['distinction_count'],
                "credits": data['credit_count']
            }
        }
    
    # ============================================================================
    # GRADE CALCULATIONS
    # ============================================================================
    
    def _calculate_aggregate(self, exam_type: str, subject_results: Dict[str, str]) -> int:
        """Calculate aggregate score from grades"""
        total_points = 0
        
        for subject, grade in subject_results.items():
            grade_info = self._get_grade_info(exam_type, grade)
            if grade_info:
                total_points += grade_info['points']
        
        return total_points
    
    def _get_division(self, exam_type: str, aggregate: int) -> str:
        """Get division based on aggregate"""
        if exam_type == 'PLE':
            if aggregate <= 12:
                return 'Division 1'
            elif aggregate <= 23:
                return 'Division 2'
            elif aggregate <= 31:
                return 'Division 3'
            elif aggregate <= 35:
                return 'Division 4'
            else:
                return 'Ungraded'
        
        elif exam_type == 'UCE':
            if aggregate <= 12:
                return 'Division 1'
            elif aggregate <= 23:
                return 'Division 2'
            elif aggregate <= 31:
                return 'Division 3'
            elif aggregate <= 35:
                return 'Division 4'
            else:
                return 'Fail'
        
        elif exam_type == 'UACE':
            # A-Level uses points system
            if aggregate >= 15:
                return 'Grade 1'
            elif aggregate >= 12:
                return 'Grade 2'
            elif aggregate >= 9:
                return 'Grade 3'
            elif aggregate >= 6:
                return 'Grade 4'
            else:
                return 'Fail'
        
        return 'Unknown'
    
    def _count_grades(self, exam_type: str, subject_results: Dict[str, str]) -> Dict[str, int]:
        """Count distinctions, credits, passes, fails"""
        counts = {
            'distinctions': 0,
            'credits': 0,
            'passes': 0,
            'fails': 0
        }
        
        for subject, grade in subject_results.items():
            if exam_type in ['PLE', 'UCE']:
                if grade in ['D1', 'D2']:
                    counts['distinctions'] += 1
                elif grade in ['C3', 'C4', 'C5', 'C6']:
                    counts['credits'] += 1
                elif grade in ['P7', 'P8']:
                    counts['passes'] += 1
                elif grade == 'F9':
                    counts['fails'] += 1
            
            elif exam_type == 'UACE':
                if grade in ['A', 'B', 'C']:
                    counts['distinctions'] += 1
                elif grade in ['D', 'E']:
                    counts['credits'] += 1
                elif grade == 'O':
                    counts['passes'] += 1
                elif grade == 'F':
                    counts['fails'] += 1
        
        return counts
    
    def _get_grade_info(self, exam_type: str, grade: str) -> Optional[Dict]:
        """Get grade information from database"""
        query = """
        SELECT points, description
        FROM uneb_grade_mapping
        WHERE exam_type = %s AND grade = %s
        LIMIT 1
        """
        
        result = self.db.execute_query(query, (exam_type, grade), fetch=True)
        
        if result:
            return result[0]
        
        return None
    
    # ============================================================================
    # ANALYTICS
    # ============================================================================
    
    def get_school_performance(
        self,
        exam_type: str,
        exam_year: int
    ) -> Dict[str, Any]:
        """Get school performance statistics"""
        query = """
        SELECT 
            COUNT(*) as total_candidates,
            AVG(aggregate) as average_aggregate,
            COUNT(CASE WHEN division LIKE 'Division 1%' OR division = 'Grade 1' THEN 1 END) as division_1,
            COUNT(CASE WHEN division LIKE 'Division 2%' OR division = 'Grade 2' THEN 1 END) as division_2,
            COUNT(CASE WHEN division LIKE 'Division 3%' OR division = 'Grade 3' THEN 1 END) as division_3,
            COUNT(CASE WHEN division LIKE 'Division 4%' OR division = 'Grade 4' THEN 1 END) as division_4,
            SUM(distinction_count) as total_distinctions,
            SUM(credit_count) as total_credits
        FROM uneb_results
        WHERE school_id = %s
        AND exam_type = %s
        AND exam_year = %s
        """
        
        result = self.db.execute_query(query, (self.school_id, exam_type, exam_year), fetch=True)
        
        if result:
            return {
                "success": True,
                "exam_type": exam_type,
                "exam_year": exam_year,
                **result[0]
            }
        
        return {"success": False, "error": "No data found"}


def get_uneb_service(school_id: str) -> UNEBService:
    """Helper to get UNEB service instance"""
    return UNEBService(school_id)
