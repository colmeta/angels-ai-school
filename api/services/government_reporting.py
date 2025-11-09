"""
Government Reporting Service
Annual school census, student enrollment reports, teacher data, infrastructure reports
"""
from typing import Dict, Any, List, Optional
from datetime import datetime

from api.services.database import get_db_manager


class GovernmentReportingService:
    """Service for government reporting and compliance"""
    
    def __init__(self, school_id: str):
        self.school_id = school_id
        self.db = get_db_manager()
    
    # ============================================================================
    # REPORT GENERATION
    # ============================================================================
    
    def generate_annual_census(self, year: int) -> Dict[str, Any]:
        """
        Generate annual school census report
        (Required by Ministry of Education)
        """
        # Student enrollment by class
        enrollment_query = """
        SELECT 
            class_name,
            COUNT(*) as total_students,
            COUNT(CASE WHEN gender = 'male' THEN 1 END) as male_count,
            COUNT(CASE WHEN gender = 'female' THEN 1 END) as female_count
        FROM students
        WHERE school_id = %s
        AND status = 'active'
        AND EXTRACT(YEAR FROM created_at) <= %s
        GROUP BY class_name
        ORDER BY class_name
        """
        enrollment = self.db.execute_query(enrollment_query, (self.school_id, year), fetch=True)
        
        # Teacher statistics
        teachers_query = """
        SELECT 
            COUNT(*) as total_teachers,
            COUNT(CASE WHEN gender = 'male' THEN 1 END) as male_teachers,
            COUNT(CASE WHEN gender = 'female' THEN 1 END) as female_teachers,
            COUNT(CASE WHEN qualification = 'degree' THEN 1 END) as degree_holders,
            COUNT(CASE WHEN qualification = 'diploma' THEN 1 END) as diploma_holders
        FROM teachers
        WHERE school_id = %s AND employment_status = 'active'
        """
        teachers = self.db.execute_query(teachers_query, (self.school_id,), fetch=True)
        
        # Infrastructure (from school data)
        infrastructure_query = """
        SELECT 
            name,
            value
        FROM school_metadata
        WHERE school_id = %s
        AND name IN ('classrooms', 'toilets', 'libraries', 'laboratories', 'dormitories')
        """
        infrastructure = self.db.execute_query(infrastructure_query, (self.school_id,), fetch=True)
        
        # Calculate totals
        total_students = sum(e['total_students'] for e in enrollment)
        total_male = sum(e['male_count'] for e in enrollment)
        total_female = sum(e['female_count'] for e in enrollment)
        
        return {
            "success": True,
            "report_type": "annual_census",
            "year": year,
            "generated_at": datetime.now().isoformat(),
            "enrollment": {
                "total_students": total_students,
                "male": total_male,
                "female": total_female,
                "by_class": enrollment
            },
            "teachers": teachers[0] if teachers else {},
            "infrastructure": {item['name']: item['value'] for item in infrastructure}
        }
    
    def generate_enrollment_report(
        self,
        start_date: str,
        end_date: str
    ) -> Dict[str, Any]:
        """Generate student enrollment report for a period"""
        query = """
        SELECT 
            DATE_TRUNC('month', created_at) as month,
            COUNT(*) as new_enrollments,
            COUNT(CASE WHEN gender = 'male' THEN 1 END) as male,
            COUNT(CASE WHEN gender = 'female' THEN 1 END) as female
        FROM students
        WHERE school_id = %s
        AND created_at BETWEEN %s AND %s
        GROUP BY DATE_TRUNC('month', created_at)
        ORDER BY month
        """
        
        data = self.db.execute_query(query, (self.school_id, start_date, end_date), fetch=True)
        
        return {
            "success": True,
            "report_type": "enrollment",
            "period": f"{start_date} to {end_date}",
            "data": data,
            "total_new_enrollments": sum(d['new_enrollments'] for d in data)
        }
    
    def generate_teacher_data_report(self) -> Dict[str, Any]:
        """Generate teacher qualification and employment report"""
        query = """
        SELECT 
            t.id,
            t.first_name,
            t.last_name,
            t.gender,
            t.qualification,
            t.subjects,
            t.employment_status,
            t.hire_date,
            COALESCE(
                (SELECT COUNT(DISTINCT class_name) 
                 FROM attendance 
                 WHERE teacher_id = t.id 
                 AND date >= CURRENT_DATE - INTERVAL '30 days'), 
                0
            ) as classes_taught_last_month
        FROM teachers t
        WHERE t.school_id = %s
        ORDER BY t.last_name, t.first_name
        """
        
        teachers = self.db.execute_query(query, (self.school_id,), fetch=True)
        
        return {
            "success": True,
            "report_type": "teacher_data",
            "generated_at": datetime.now().isoformat(),
            "total_teachers": len(teachers),
            "teachers": teachers
        }
    
    def generate_infrastructure_report(self) -> Dict[str, Any]:
        """Generate infrastructure and facilities report"""
        # Get school metadata
        metadata_query = """
        SELECT name, value
        FROM school_metadata
        WHERE school_id = %s
        """
        metadata = self.db.execute_query(metadata_query, (self.school_id,), fetch=True)
        
        # Get dormitory data
        dorm_query = """
        SELECT 
            COUNT(*) as total_dormitories,
            SUM(capacity) as total_capacity,
            SUM(capacity) - COUNT(DISTINCT db.student_id) as available_capacity
        FROM dormitories d
        LEFT JOIN dormitory_beds db ON db.dormitory_id = d.id
        WHERE d.school_id = %s
        """
        dorms = self.db.execute_query(dorm_query, (self.school_id,), fetch=True)
        
        # Get library data
        library_query = """
        SELECT 
            COUNT(*) as total_books,
            COUNT(CASE WHEN status = 'available' THEN 1 END) as available_books,
            COUNT(CASE WHEN status = 'borrowed' THEN 1 END) as borrowed_books
        FROM library_books
        WHERE school_id = %s
        """
        library = self.db.execute_query(library_query, (self.school_id,), fetch=True)
        
        return {
            "success": True,
            "report_type": "infrastructure",
            "generated_at": datetime.now().isoformat(),
            "metadata": {item['name']: item['value'] for item in metadata},
            "dormitories": dorms[0] if dorms else {},
            "library": library[0] if library else {}
        }
    
    def generate_financial_summary_report(
        self,
        start_date: str,
        end_date: str
    ) -> Dict[str, Any]:
        """Generate financial summary for government audit"""
        # Fee collection
        fees_query = """
        SELECT 
            SUM(total_amount) as total_fees_charged,
            SUM(amount_paid) as total_collected,
            SUM(balance) as outstanding_balance
        FROM student_fees
        WHERE school_id = %s
        AND term_start_date BETWEEN %s AND %s
        """
        fees = self.db.execute_query(fees_query, (self.school_id, start_date, end_date), fetch=True)
        
        # Expenses
        expenses_query = """
        SELECT 
            category,
            SUM(amount) as total
        FROM expenses
        WHERE school_id = %s
        AND expense_date BETWEEN %s AND %s
        GROUP BY category
        """
        expenses = self.db.execute_query(expenses_query, (self.school_id, start_date, end_date), fetch=True)
        
        # Payroll
        payroll_query = """
        SELECT 
            SUM(gross_salary) as total_payroll
        FROM payroll_transactions
        WHERE school_id = %s
        AND payment_date BETWEEN %s AND %s
        """
        payroll = self.db.execute_query(payroll_query, (self.school_id, start_date, end_date), fetch=True)
        
        return {
            "success": True,
            "report_type": "financial_summary",
            "period": f"{start_date} to {end_date}",
            "revenue": fees[0] if fees else {},
            "expenses_by_category": expenses,
            "total_payroll": payroll[0]['total_payroll'] if payroll else 0
        }
    
    # ============================================================================
    # REPORT STORAGE & SUBMISSION
    # ============================================================================
    
    def save_report(
        self,
        report_type: str,
        report_year: int,
        report_data: Dict[str, Any],
        submitted_by: str
    ) -> Dict[str, Any]:
        """Save generated report to database"""
        query = """
        INSERT INTO government_reports (
            school_id, report_type, report_year, report_data, submitted_by
        ) VALUES (%s, %s, %s, %s, %s)
        RETURNING id
        """
        
        result = self.db.execute_query(
            query,
            (self.school_id, report_type, report_year, report_data, submitted_by),
            fetch=True
        )
        
        return {
            "success": True,
            "report_id": result[0]['id'],
            "report_type": report_type,
            "report_year": report_year
        }
    
    def mark_report_submitted(
        self,
        report_id: str,
        submission_date: str
    ) -> Dict[str, Any]:
        """Mark report as submitted to government"""
        query = """
        UPDATE government_reports
        SET submission_date = %s,
            status = 'submitted'
        WHERE id = %s
        """
        
        self.db.execute_query(query, (submission_date, report_id))
        
        return {
            "success": True,
            "report_id": report_id,
            "status": "submitted"
        }
    
    def get_reports(
        self,
        report_type: Optional[str] = None,
        year: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Get all reports"""
        query = """
        SELECT 
            id,
            report_type,
            report_year,
            submission_date,
            status,
            submitted_by,
            created_at
        FROM government_reports
        WHERE school_id = %s
        """
        
        params = [self.school_id]
        
        if report_type:
            query += " AND report_type = %s"
            params.append(report_type)
        
        if year:
            query += " AND report_year = %s"
            params.append(year)
        
        query += " ORDER BY created_at DESC"
        
        return self.db.execute_query(query, tuple(params), fetch=True)
    
    def get_report_by_id(self, report_id: str) -> Optional[Dict[str, Any]]:
        """Get full report data by ID"""
        query = """
        SELECT 
            id,
            report_type,
            report_year,
            report_data,
            submission_date,
            status,
            submitted_by,
            created_at
        FROM government_reports
        WHERE id = %s
        """
        
        result = self.db.execute_query(query, (report_id,), fetch=True)
        return result[0] if result else None


def get_government_reporting_service(school_id: str) -> GovernmentReportingService:
    """Helper to get government reporting service instance"""
    return GovernmentReportingService(school_id)
