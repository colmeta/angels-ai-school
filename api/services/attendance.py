"""
Attendance Service
Handles storage of batch attendance records from Frontend AI Worker
"""
from typing import List, Dict, Any, Optional
from datetime import datetime
from api.services.database import get_db_manager

class AttendanceService:
    def __init__(self, school_id: str):
        self.school_id = school_id
        self.db = get_db_manager()

    def record_subject_attendance_batch(self, records: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Batch insert subject attendance records
        Designed to be lightweight - logic happens on frontend
        """
        if not records:
            return {"count": 0}

        query = """
        INSERT INTO subject_attendance (
            school_id, student_id, subject, class_name, teacher_id,
            date, status, mode, notes
        ) VALUES (
            %(school_id)s, %(student_id)s, %(subject)s, %(class_name)s, %(teacher_id)s,
            %(date)s, %(status)s, %(mode)s, %(notes)s
        )
        ON CONFLICT (school_id, student_id, subject, date, start_time) 
        DO UPDATE SET
            status = EXCLUDED.status,
            mode = EXCLUDED.mode,
            notes = EXCLUDED.notes,
            updated_at = NOW()
        """

        # Add school_id to all records
        for r in records:
            r['school_id'] = self.school_id
            if 'notes' not in r:
                r['notes'] = None
            if 'teacher_id' not in r:
                r['teacher_id'] = None # Allow generic recording

        count = self.db.execute_many(query, [
            (
                r['school_id'], r['student_id'], r['subject'], r['class_name'], r.get('teacher_id'),
                r.get('date', datetime.now().date()), r['status'], r['mode'], r.get('notes')
            )
            for r in records
        ])
        
        return {"count": count, "message": "Records synced successfully"}

    def record_exam_attendance_batch(self, records: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Batch insert exam attendance"""
        if not records:
            return {"count": 0}

        query = """
        INSERT INTO exam_attendance (
            school_id, student_id, exam_name, subject, class_name,
            supervisor_id, date, status, mode, booklet_number
        ) VALUES (
            %(school_id)s, %(student_id)s, %(exam_name)s, %(subject)s, %(class_name)s,
            %(supervisor_id)s, %(date)s, %(status)s, %(mode)s, %(booklet_number)s
        )
        ON CONFLICT (school_id, student_id, exam_name, subject)
        DO UPDATE SET
            status = EXCLUDED.status,
            mode = EXCLUDED.mode,
            booklet_number = EXCLUDED.booklet_number,
            updated_at = NOW()
        """

        for r in records:
            r['school_id'] = self.school_id

        count = self.db.execute_many(query, [
            (
                r['school_id'], r['student_id'], r['exam_name'], r['subject'], r['class_name'],
                r.get('supervisor_id'), r.get('date', datetime.now().date()), r['status'], 
                r['mode'], r.get('booklet_number')
            )
            for r in records
        ])

        return {"count": count}

def get_attendance_service(school_id: str) -> AttendanceService:
    return AttendanceService(school_id)
