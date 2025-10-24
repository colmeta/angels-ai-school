"""
Angels AI - Database Utilities
Handles all database connections and common operations
"""

import os
from typing import Optional, List, Dict, Any
from contextlib import contextmanager
import psycopg2
from psycopg2.extras import RealDictCursor, execute_values
from psycopg2.pool import ThreadedConnectionPool
from datetime import datetime
import json


class DatabaseManager:
    """
    Manages PostgreSQL connections using connection pooling
    Think of this as your database 'bouncer' - manages who gets in/out efficiently
    """
    
    def __init__(self, database_url: Optional[str] = None, min_conn: int = 1, max_conn: int = 10):
        """
        Initialize database connection pool
        
        Args:
            database_url: PostgreSQL connection string
            min_conn: Minimum connections to keep open
            max_conn: Maximum connections allowed
        """
        self.database_url = database_url or os.getenv('DATABASE_URL')
        if not self.database_url:
            raise ValueError("DATABASE_URL environment variable not set")
        
        # Create connection pool (think of it as a taxi stand - always have taxis ready)
        self.pool = ThreadedConnectionPool(
            min_conn,
            max_conn,
            self.database_url
        )
        print(f"✅ Database connection pool initialized ({min_conn}-{max_conn} connections)")
    
    @contextmanager
    def get_connection(self):
        """
        Context manager for getting database connections
        Usage: 
            with db.get_connection() as conn:
                # do database work
        """
        conn = self.pool.getconn()
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            self.pool.putconn(conn)
    
    @contextmanager
    def get_cursor(self, dict_cursor: bool = True):
        """
        Context manager for getting database cursor
        Usage:
            with db.get_cursor() as cur:
                cur.execute("SELECT * FROM students")
                results = cur.fetchall()
        
        Args:
            dict_cursor: If True, returns rows as dictionaries
        """
        with self.get_connection() as conn:
            cursor_factory = RealDictCursor if dict_cursor else None
            cur = conn.cursor(cursor_factory=cursor_factory)
            try:
                yield cur
            finally:
                cur.close()
    
    def execute_query(self, query: str, params: tuple = None, fetch: bool = True) -> Optional[List[Dict]]:
        """
        Execute a query and return results
        
        Args:
            query: SQL query string
            params: Query parameters (use %s placeholders)
            fetch: Whether to fetch results
        
        Returns:
            List of dictionaries (rows) if fetch=True, None otherwise
        """
        with self.get_cursor() as cur:
            cur.execute(query, params)
            if fetch:
                return cur.fetchall()
            return None
    
    def execute_many(self, query: str, data: List[tuple]) -> int:
        """
        Execute query multiple times with different parameters
        Useful for bulk inserts
        
        Args:
            query: SQL query with placeholders
            data: List of tuples containing parameters
        
        Returns:
            Number of rows affected
        """
        with self.get_cursor() as cur:
            cur.executemany(query, data)
            return cur.rowcount
    
    def close_all_connections(self):
        """Close all connections in the pool"""
        self.pool.closeall()
        print("🔒 All database connections closed")


# ============================================
# HELPER FUNCTIONS FOR COMMON OPERATIONS
# ============================================

class StudentOperations:
    """All student-related database operations"""
    
    def __init__(self, db: DatabaseManager):
        self.db = db
    
    def create_student(self, student_data: Dict[str, Any]) -> Dict:
        """
        Create a new student record
        
        Args:
            student_data: Dictionary containing student information
        
        Returns:
            Created student record with ID
        """
        query = """
        INSERT INTO students (
            school_id, admission_number, first_name, middle_name, last_name,
            date_of_birth, gender, current_grade, current_class, admission_date,
            enrollment_status, home_address, county_state, city,
            primary_phone, email, blood_group, allergies, medical_conditions,
            emergency_contact_name, emergency_contact_phone, emergency_contact_relationship
        ) VALUES (
            %(school_id)s, %(admission_number)s, %(first_name)s, %(middle_name)s, %(last_name)s,
            %(date_of_birth)s, %(gender)s, %(current_grade)s, %(current_class)s, %(admission_date)s,
            %(enrollment_status)s, %(home_address)s, %(county_state)s, %(city)s,
            %(primary_phone)s, %(email)s, %(blood_group)s, %(allergies)s, %(medical_conditions)s,
            %(emergency_contact_name)s, %(emergency_contact_phone)s, %(emergency_contact_relationship)s
        )
        RETURNING *;
        """
        
        with self.db.get_cursor() as cur:
            cur.execute(query, student_data)
            result = cur.fetchone()
            print(f"✅ Student created: {result['first_name']} {result['last_name']} ({result['admission_number']})")
            return dict(result)
    
    def get_student_by_admission_number(self, admission_number: str, school_id: str) -> Optional[Dict]:
        """Get student by admission number"""
        query = """
        SELECT * FROM students 
        WHERE admission_number = %s AND school_id = %s AND deleted_at IS NULL
        """
        results = self.db.execute_query(query, (admission_number, school_id))
        return dict(results[0]) if results else None
    
    def get_students_by_grade(self, school_id: str, grade: str) -> List[Dict]:
        """Get all students in a specific grade"""
        query = """
        SELECT * FROM students 
        WHERE school_id = %s AND current_grade = %s 
        AND enrollment_status = 'active' AND deleted_at IS NULL
        ORDER BY last_name, first_name
        """
        results = self.db.execute_query(query, (school_id, grade))
        return [dict(r) for r in results]
    
    def update_student(self, student_id: str, updates: Dict[str, Any]) -> Dict:
        """Update student information"""
        # Build dynamic UPDATE query
        set_clause = ", ".join([f"{key} = %s" for key in updates.keys()])
        values = list(updates.values()) + [student_id]
        
        query = f"""
        UPDATE students 
        SET {set_clause}, updated_at = NOW()
        WHERE id = %s
        RETURNING *;
        """
        
        with self.db.get_cursor() as cur:
            cur.execute(query, values)
            return dict(cur.fetchone())
    
    def get_student_with_parents(self, student_id: str) -> Dict:
        """Get student with all parent information"""
        query = """
        SELECT 
            s.*,
            json_agg(
                json_build_object(
                    'parent_id', p.id,
                    'parent_name', p.first_name || ' ' || p.last_name,
                    'phone', p.primary_phone,
                    'email', p.email,
                    'relationship', spr.relationship_type,
                    'is_primary', spr.is_primary_contact,
                    'is_fee_payer', spr.is_fee_payer
                )
            ) as parents
        FROM students s
        LEFT JOIN student_parent_relationships spr ON s.id = spr.student_id
        LEFT JOIN parents p ON spr.parent_id = p.id
        WHERE s.id = %s AND s.deleted_at IS NULL
        GROUP BY s.id
        """
        results = self.db.execute_query(query, (student_id,))
        return dict(results[0]) if results else None


class ParentOperations:
    """All parent-related database operations"""
    
    def __init__(self, db: DatabaseManager):
        self.db = db
    
    def create_parent(self, parent_data: Dict[str, Any]) -> Dict:
        """Create a new parent record"""
        query = """
        INSERT INTO parents (
            school_id, first_name, middle_name, last_name, gender,
            primary_phone, secondary_phone, email, whatsapp_number,
            preferred_language, occupation, employer, work_phone,
            home_address, county_state, city,
            preferred_contact_method, opt_in_notifications
        ) VALUES (
            %(school_id)s, %(first_name)s, %(middle_name)s, %(last_name)s, %(gender)s,
            %(primary_phone)s, %(secondary_phone)s, %(email)s, %(whatsapp_number)s,
            %(preferred_language)s, %(occupation)s, %(employer)s, %(work_phone)s,
            %(home_address)s, %(county_state)s, %(city)s,
            %(preferred_contact_method)s, %(opt_in_notifications)s
        )
        RETURNING *;
        """
        
        with self.db.get_cursor() as cur:
            cur.execute(query, parent_data)
            result = cur.fetchone()
            print(f"✅ Parent created: {result['first_name']} {result['last_name']} ({result['primary_phone']})")
            return dict(result)
    
    def link_parent_to_student(self, student_id: str, parent_id: str, 
                               relationship_type: str, is_primary: bool = False,
                               is_fee_payer: bool = False) -> Dict:
        """Link a parent to a student"""
        query = """
        INSERT INTO student_parent_relationships (
            student_id, parent_id, relationship_type, 
            is_primary_contact, is_fee_payer
        ) VALUES (%s, %s, %s, %s, %s)
        RETURNING *;
        """
        
        with self.db.get_cursor() as cur:
            cur.execute(query, (student_id, parent_id, relationship_type, is_primary, is_fee_payer))
            result = cur.fetchone()
            print(f"✅ Parent-Student relationship created: {relationship_type}")
            return dict(result)
    
    def get_parents_for_grade(self, school_id: str, grade: str) -> List[Dict]:
        """Get all parents of students in a specific grade"""
        query = """
        SELECT DISTINCT p.*, s.current_grade, s.first_name as student_first_name, 
               s.last_name as student_last_name, s.admission_number
        FROM parents p
        JOIN student_parent_relationships spr ON p.id = spr.parent_id
        JOIN students s ON spr.student_id = s.id
        WHERE p.school_id = %s AND s.current_grade = %s 
        AND s.enrollment_status = 'active' AND s.deleted_at IS NULL
        AND p.deleted_at IS NULL
        ORDER BY p.last_name, p.first_name
        """
        results = self.db.execute_query(query, (school_id, grade))
        return [dict(r) for r in results]


class FeeOperations:
    """All fee-related database operations"""
    
    def __init__(self, db: DatabaseManager):
        self.db = db
    
    def create_fee_structure(self, fee_data: Dict[str, Any]) -> Dict:
        """Create a fee structure for a grade/term"""
        query = """
        INSERT INTO fee_structures (
            school_id, name, grade_level, academic_term, academic_year,
            tuition_amount, additional_fees, total_amount, due_date,
            late_fee_amount, late_fee_starts_after_days, is_active
        ) VALUES (
            %(school_id)s, %(name)s, %(grade_level)s, %(academic_term)s, %(academic_year)s,
            %(tuition_amount)s, %(additional_fees)s, %(total_amount)s, %(due_date)s,
            %(late_fee_amount)s, %(late_fee_starts_after_days)s, %(is_active)s
        )
        RETURNING *;
        """
        
        with self.db.get_cursor() as cur:
            cur.execute(query, fee_data)
            result = cur.fetchone()
            print(f"✅ Fee structure created: {result['name']} - {result['total_amount']}")
            return dict(result)
    
    def assign_fee_to_student(self, student_id: str, fee_structure_id: str,
                             discount_percentage: float = 0.0,
                             discount_reason: str = None) -> Dict:
        """Assign a fee structure to a student"""
        # First get the fee structure to calculate final amount
        fee_structure = self.db.execute_query(
            "SELECT * FROM fee_structures WHERE id = %s",
            (fee_structure_id,)
        )[0]
        
        total = float(fee_structure['total_amount'])
        final_amount = total * (1 - discount_percentage / 100)
        
        query = """
        INSERT INTO student_fees (
            student_id, fee_structure_id, discount_percentage, discount_reason,
            custom_amount, final_amount, balance, due_date
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING *;
        """
        
        with self.db.get_cursor() as cur:
            cur.execute(query, (
                student_id, fee_structure_id, discount_percentage, discount_reason,
                None, final_amount, final_amount, fee_structure['due_date']
            ))
            result = cur.fetchone()
            print(f"✅ Fee assigned to student: {final_amount} (discount: {discount_percentage}%)")
            return dict(result)
    
    def record_payment(self, payment_data: Dict[str, Any]) -> Dict:
        """Record a fee payment"""
        query = """
        INSERT INTO fee_payments (
            student_fee_id, student_id, school_id, amount,
            payment_method, payment_reference, phone_number,
            transaction_id, notes, received_by
        ) VALUES (
            %(student_fee_id)s, %(student_id)s, %(school_id)s, %(amount)s,
            %(payment_method)s, %(payment_reference)s, %(phone_number)s,
            %(transaction_id)s, %(notes)s, %(received_by)s
        )
        RETURNING *;
        """
        
        with self.db.get_cursor() as cur:
            cur.execute(query, payment_data)
            result = cur.fetchone()
            print(f"✅ Payment recorded: {result['amount']} via {result['payment_method']}")
            return dict(result)
    
    def get_overdue_fees(self, school_id: str) -> List[Dict]:
        """Get all overdue fees with student and parent information"""
        query = """
        SELECT 
            sf.*,
            s.first_name, s.last_name, s.admission_number, s.current_grade,
            p.primary_phone, p.whatsapp_number, p.email,
            p.first_name as parent_first_name, p.last_name as parent_last_name,
            p.preferred_language, p.preferred_contact_method
        FROM student_fees sf
        JOIN students s ON sf.student_id = s.id
        JOIN student_parent_relationships spr ON s.id = spr.student_id AND spr.is_primary_contact = true
        JOIN parents p ON spr.parent_id = p.id
        WHERE s.school_id = %s 
        AND sf.payment_status = 'overdue'
        AND s.enrollment_status = 'active'
        AND s.deleted_at IS NULL
        ORDER BY sf.due_date ASC
        """
        results = self.db.execute_query(query, (school_id,))
        return [dict(r) for r in results]
    
    def get_fee_collection_summary(self, school_id: str, academic_term: str = None) -> Dict:
        """Get fee collection statistics"""
        term_filter = "AND fs.academic_term = %s" if academic_term else ""
        params = (school_id, academic_term) if academic_term else (school_id,)
        
        query = f"""
        SELECT 
            COUNT(DISTINCT sf.id) as total_fees_assigned,
            SUM(sf.final_amount) as total_expected,
            SUM(sf.amount_paid) as total_collected,
            SUM(sf.balance) as total_outstanding,
            COUNT(CASE WHEN sf.payment_status = 'paid' THEN 1 END) as fully_paid_count,
            COUNT(CASE WHEN sf.payment_status = 'partial' THEN 1 END) as partial_paid_count,
            COUNT(CASE WHEN sf.payment_status = 'overdue' THEN 1 END) as overdue_count,
            COUNT(CASE WHEN sf.payment_status = 'pending' THEN 1 END) as pending_count,
            ROUND(
                (SUM(sf.amount_paid) / NULLIF(SUM(sf.final_amount), 0) * 100), 2
            ) as collection_rate_percentage
        FROM student_fees sf
        JOIN students s ON sf.student_id = s.id
        JOIN fee_structures fs ON sf.fee_structure_id = fs.id
        WHERE s.school_id = %s {term_filter}
        AND s.enrollment_status = 'active'
        AND s.deleted_at IS NULL
        """
        
        results = self.db.execute_query(query, params)
        return dict(results[0]) if results else {}


class MessageOperations:
    """All messaging-related database operations"""
    
    def __init__(self, db: DatabaseManager):
        self.db = db
    
    def create_message(self, message_data: Dict[str, Any]) -> Dict:
        """Record a message sent to parent/staff"""
        query = """
        INSERT INTO messages (
            school_id, recipient_type, recipient_id, recipient_phone, recipient_email,
            message_type, subject, body, template_name, template_variables,
            trigger_event, triggered_by, staff_id, cost_amount
        ) VALUES (
            %(school_id)s, %(recipient_type)s, %(recipient_id)s, %(recipient_phone)s, %(recipient_email)s,
            %(message_type)s, %(subject)s, %(body)s, %(template_name)s, %(template_variables)s,
            %(trigger_event)s, %(triggered_by)s, %(staff_id)s, %(cost_amount)s
        )
        RETURNING *;
        """
        
        with self.db.get_cursor() as cur:
            cur.execute(query, message_data)
            result = cur.fetchone()
            print(f"✅ Message created: {result['message_type']} to {result['recipient_phone']}")
            return dict(result)
    
    def update_message_status(self, message_id: str, status: str, 
                             external_id: str = None, error: str = None) -> Dict:
        """Update message delivery status"""
        updates = {'status': status}
        
        if status == 'sent':
            updates['sent_at'] = datetime.now()
        elif status == 'delivered':
            updates['delivered_at'] = datetime.now()
        elif status == 'read':
            updates['read_at'] = datetime.now()
        elif status == 'failed':
            updates['failed_reason'] = error
        
        if external_id:
            updates['external_message_id'] = external_id
        
        set_clause = ", ".join([f"{k} = %s" for k in updates.keys()])
        values = list(updates.values()) + [message_id]
        
        query = f"""
        UPDATE messages 
        SET {set_clause}
        WHERE id = %s
        RETURNING *;
        """
        
        with self.db.get_cursor() as cur:
            cur.execute(query, values)
            return dict(cur.fetchone())


class DocumentOperations:
    """All document-related database operations"""
    
    def __init__(self, db: DatabaseManager):
        self.db = db
    
    def create_document_record(self, document_data: Dict[str, Any]) -> Dict:
        """Create a document record after upload"""
        query = """
        INSERT INTO documents (
            school_id, document_type, category, original_filename,
            file_size, mime_type, storage_url, processing_status,
            uploaded_by, student_id, parent_id
        ) VALUES (
            %(school_id)s, %(document_type)s, %(category)s, %(original_filename)s,
            %(file_size)s, %(mime_type)s, %(storage_url)s, %(processing_status)s,
            %(uploaded_by)s, %(student_id)s, %(parent_id)s
        )
        RETURNING *;
        """
        
        with self.db.get_cursor() as cur:
            cur.execute(query, document_data)
            result = cur.fetchone()
            print(f"✅ Document record created: {result['original_filename']}")
            return dict(result)
    
    def update_document_processing(self, document_id: str, 
                                  ocr_text: str, extracted_data: Dict,
                                  ocr_confidence: float, routed_to: str) -> Dict:
        """Update document after OCR processing"""
        query = """
        UPDATE documents 
        SET ocr_text = %s,
            extracted_data = %s,
            ocr_confidence = %s,
            routed_to = %s,
            processing_status = 'completed',
            processed_at = NOW()
        WHERE id = %s
        RETURNING *;
        """
        
        with self.db.get_cursor() as cur:
            cur.execute(query, (
                ocr_text, 
                json.dumps(extracted_data),
                ocr_confidence,
                routed_to,
                document_id
            ))
            result = cur.fetchone()
            print(f"✅ Document processed: {result['original_filename']} → {routed_to}")
            return dict(result)


# ============================================
# INITIALIZE DATABASE MANAGER (SINGLETON)
# ============================================

# Global database instance
_db_instance = None

def get_db() -> DatabaseManager:
    """Get or create database manager instance"""
    global _db_instance
    if _db_instance is None:
        _db_instance = DatabaseManager()
    return _db_instance

# Helper to get operation classes
def get_student_ops() -> StudentOperations:
    return StudentOperations(get_db())

def get_parent_ops() -> ParentOperations:
    return ParentOperations(get_db())

def get_fee_ops() -> FeeOperations:
    return FeeOperations(get_db())

def get_message_ops() -> MessageOperations:
    return MessageOperations(get_db())

def get_document_ops() -> DocumentOperations:
    return DocumentOperations(get_db())
