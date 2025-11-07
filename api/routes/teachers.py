"""
Teacher Workflows - Real Photo-Based Data Entry
Teachers use phones to snap photos of attendance, results, etc.
"""
from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from typing import Optional, List
from datetime import date, datetime
import base64

from api.services.ocr import OCRService
from api.services.notifications import NotificationService
from api.services.database import get_db_manager

router = APIRouter()


@router.post("/{school_id}/attendance/photo")
async def process_attendance_photo(
    school_id: str,
    class_name: str = Form(...),
    section: Optional[str] = Form(None),
    date_str: str = Form(...),
    teacher_id: str = Form(...),
    photo: UploadFile = File(...)
):
    """
    Teacher snaps photo of attendance sheet - system auto-digitizes and notifies parents
    
    This is the REAL implementation - no simulation
    """
    try:
        # Read uploaded photo
        photo_bytes = await photo.read()
        photo_b64 = base64.b64encode(photo_bytes).decode()
        
        # Process with OCR
        ocr_service = OCRService()
        result = ocr_service.process_attendance_sheet(
            image_data=photo_b64,
            class_info={
                "class_name": class_name,
                "section": section,
                "date": date_str
            }
        )
        
        if not result["success"]:
            raise HTTPException(status_code=400, detail=result.get("error", "OCR failed"))
        
        # Save to database and notify parents
        db = get_db_manager()
        notification_service = NotificationService()
        
        saved_records = []
        notification_results = []
        
        for record in result["attendance"]:
            student_name = record["student_name"]
            status = record["status"]
            
            # Find student by name and class
            student_query = """
            SELECT id, first_name, last_name 
            FROM students 
            WHERE school_id = %s 
            AND class_name = %s
            AND (first_name || ' ' || last_name) ILIKE %s
            LIMIT 1
            """
            students = db.execute_query(
                student_query,
                (school_id, class_name, f"%{student_name}%"),
                fetch=True
            )
            
            if not students:
                continue
            
            student = students[0]
            student_id = student["id"]
            
            # Save attendance record
            attendance_query = """
            INSERT INTO attendance (
                school_id, student_id, date, status, marked_by, notes, marked_at
            ) VALUES (%s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP)
            ON CONFLICT (student_id, date) 
            DO UPDATE SET status = EXCLUDED.status, marked_by = EXCLUDED.marked_by
            RETURNING id
            """
            attendance_result = db.execute_query(
                attendance_query,
                (school_id, student_id, date_str, status, teacher_id, record.get("notes", "")),
                fetch=True
            )
            
            saved_records.append({
                "student_id": student_id,
                "student_name": f"{student['first_name']} {student['last_name']}",
                "status": status,
                "attendance_id": attendance_result[0]["id"] if attendance_result else None
            })
            
            # Get parents and notify them
            parent_query = """
            SELECT p.id, p.first_name, p.last_name, p.primary_phone
            FROM parents p
            JOIN student_parents sp ON p.id = sp.parent_id
            WHERE sp.student_id = %s
            """
            parents = db.execute_query(parent_query, (student_id,), fetch=True)
            
            for parent in parents:
                notif_result = await notification_service.notify_parent_attendance(
                    school_id=school_id,
                    student_id=student_id,
                    parent_id=parent["id"],
                    status=status,
                    date=date_str
                )
                notification_results.append({
                    "parent_id": parent["id"],
                    "student_id": student_id,
                    "status": notif_result.get("success", False)
                })
        
        return {
            "success": True,
            "message": "Attendance processed from photo",
            "class_name": class_name,
            "date": date_str,
            "records_saved": len(saved_records),
            "parents_notified": len(notification_results),
            "ocr_confidence": result.get("ocr_confidence", 0),
            "details": saved_records,
            "raw_text": result.get("raw_text", "")
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{school_id}/results/photo")
async def process_exam_results_photo(
    school_id: str,
    subject: str = Form(...),
    exam_name: str = Form(...),
    class_name: str = Form(...),
    max_marks: float = Form(...),
    teacher_id: str = Form(...),
    photo: UploadFile = File(...)
):
    """
    Teacher snaps photo of exam results - system auto-enters marks for each student
    
    This is the REAL implementation - no simulation
    """
    try:
        # Read uploaded photo
        photo_bytes = await photo.read()
        photo_b64 = base64.b64encode(photo_bytes).decode()
        
        # Process with OCR
        ocr_service = OCRService()
        result = ocr_service.process_exam_results(
            image_data=photo_b64,
            exam_info={
                "subject": subject,
                "exam_name": exam_name,
                "class_name": class_name,
                "max_marks": max_marks
            }
        )
        
        if not result["success"]:
            raise HTTPException(status_code=400, detail=result.get("error", "OCR failed"))
        
        db = get_db_manager()
        
        # Create or get assessment
        assessment_query = """
        INSERT INTO assessments (
            school_id, name, type, subject, class_name, max_marks, date, created_by
        ) VALUES (%s, %s, 'exam', %s, %s, %s, CURRENT_DATE, %s)
        ON CONFLICT (school_id, name, class_name, date) DO UPDATE 
        SET max_marks = EXCLUDED.max_marks
        RETURNING id
        """
        assessment_result = db.execute_query(
            assessment_query,
            (school_id, exam_name, subject, class_name, max_marks, teacher_id),
            fetch=True
        )
        
        assessment_id = assessment_result[0]["id"]
        
        # Save results for each student
        saved_results = []
        
        for exam_result in result["results"]:
            student_name = exam_result["student_name"]
            marks = exam_result.get("marks_obtained", 0)
            grade = exam_result.get("grade", "")
            
            # Find student
            student_query = """
            SELECT id, first_name, last_name 
            FROM students 
            WHERE school_id = %s 
            AND class_name = %s
            AND (first_name || ' ' || last_name) ILIKE %s
            LIMIT 1
            """
            students = db.execute_query(
                student_query,
                (school_id, class_name, f"%{student_name}%"),
                fetch=True
            )
            
            if not students:
                continue
            
            student = students[0]
            student_id = student["id"]
            
            # Calculate grade if not provided
            if not grade:
                percentage = (marks / max_marks) * 100
                if percentage >= 90:
                    grade = "A"
                elif percentage >= 80:
                    grade = "B"
                elif percentage >= 70:
                    grade = "C"
                elif percentage >= 60:
                    grade = "D"
                else:
                    grade = "F"
            
            # Save result
            result_query = """
            INSERT INTO assessment_results (
                assessment_id, student_id, marks_obtained, grade, remarks
            ) VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (assessment_id, student_id)
            DO UPDATE SET marks_obtained = EXCLUDED.marks_obtained, grade = EXCLUDED.grade
            RETURNING id
            """
            db.execute_query(
                result_query,
                (assessment_id, student_id, marks, grade, exam_result.get("remarks", "")),
                fetch=False
            )
            
            saved_results.append({
                "student_id": student_id,
                "student_name": f"{student['first_name']} {student['last_name']}",
                "marks": marks,
                "grade": grade
            })
        
        return {
            "success": True,
            "message": "Exam results processed from photo",
            "subject": subject,
            "exam_name": exam_name,
            "class_name": class_name,
            "assessment_id": assessment_id,
            "results_saved": len(saved_results),
            "ocr_confidence": result.get("ocr_confidence", 0),
            "details": saved_results,
            "raw_text": result.get("raw_text", "")
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{school_id}/sickbay/photo")
async def process_sickbay_photo(
    school_id: str,
    date_str: str = Form(...),
    staff_id: str = Form(...),
    photo: UploadFile = File(...)
):
    """
    Health staff snaps photo of sickbay register - system auto-records and notifies parents
    """
    try:
        photo_bytes = await photo.read()
        photo_b64 = base64.b64encode(photo_bytes).decode()
        
        ocr_service = OCRService()
        result = ocr_service.process_sickbay_register(
            image_data=photo_b64,
            date=date_str
        )
        
        if not result["success"]:
            raise HTTPException(status_code=400, detail=result.get("error", "OCR failed"))
        
        db = get_db_manager()
        notification_service = NotificationService()
        
        saved_visits = []
        notifications_sent = []
        
        for visit in result["visits"]:
            student_name = visit["student_name"]
            symptoms = visit["symptoms"]
            treatment = visit.get("treatment", "Under observation")
            
            # Find student
            student_query = """
            SELECT id, first_name, last_name 
            FROM students 
            WHERE school_id = %s 
            AND (first_name || ' ' || last_name) ILIKE %s
            LIMIT 1
            """
            students = db.execute_query(
                student_query,
                (school_id, f"%{student_name}%"),
                fetch=True
            )
            
            if not students:
                continue
            
            student = students[0]
            student_id = student["id"]
            
            # Save health visit
            visit_query = """
            INSERT INTO health_visits (
                school_id, student_id, visit_date, symptoms, treatment, attended_by
            ) VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING id
            """
            visit_result = db.execute_query(
                visit_query,
                (school_id, student_id, f"{date_str} {visit.get('visit_time', '00:00:00')}", 
                 symptoms, treatment, staff_id),
                fetch=True
            )
            
            visit_id = visit_result[0]["id"] if visit_result else None
            
            saved_visits.append({
                "student_id": student_id,
                "student_name": f"{student['first_name']} {student['last_name']}",
                "symptoms": symptoms,
                "visit_id": visit_id
            })
            
            # Notify parents
            parent_query = """
            SELECT p.id FROM parents p
            JOIN student_parents sp ON p.id = sp.parent_id
            WHERE sp.student_id = %s
            """
            parents = db.execute_query(parent_query, (student_id,), fetch=True)
            
            for parent in parents:
                notif_result = await notification_service.notify_parent_health(
                    school_id=school_id,
                    student_id=student_id,
                    parent_id=parent["id"],
                    symptoms=symptoms,
                    treatment=treatment
                )
                notifications_sent.append(notif_result)
        
        return {
            "success": True,
            "message": "Sickbay register processed",
            "date": date_str,
            "visits_recorded": len(saved_visits),
            "parents_notified": len(notifications_sent),
            "details": saved_visits
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{school_id}/teacher/{teacher_id}/dashboard")
async def get_teacher_dashboard(school_id: str, teacher_id: str):
    """
    Teacher dashboard - view classes, recent activity, pending tasks
    """
    try:
        db = get_db_manager()
        
        # Get teacher info
        teacher_query = """
        SELECT id, first_name, last_name, email, subject_specialization
        FROM teachers WHERE id = %s AND school_id = %s
        """
        teacher = db.execute_query(teacher_query, (teacher_id, school_id), fetch=True)[0]
        
        # Get assigned classes
        classes_query = """
        SELECT DISTINCT class_name, COUNT(DISTINCT student_id) as student_count
        FROM timetable t
        WHERE t.school_id = %s AND t.teacher_id = %s
        GROUP BY class_name
        """
        classes = db.execute_query(classes_query, (school_id, teacher_id), fetch=True)
        
        # Get today's attendance stats
        attendance_query = """
        SELECT COUNT(*) as total_marked
        FROM attendance
        WHERE school_id = %s AND marked_by = %s AND date = CURRENT_DATE
        """
        attendance_stats = db.execute_query(attendance_query, (school_id, teacher_id), fetch=True)
        
        # Get recent assessments
        assessments_query = """
        SELECT id, name, subject, class_name, date, max_marks
        FROM assessments
        WHERE school_id = %s AND created_by = %s
        ORDER BY date DESC
        LIMIT 5
        """
        recent_assessments = db.execute_query(assessments_query, (school_id, teacher_id), fetch=True)
        
        return {
            "success": True,
            "teacher": teacher,
            "classes": classes,
            "attendance_today": attendance_stats[0] if attendance_stats else {"total_marked": 0},
            "recent_assessments": recent_assessments,
            "quick_actions": [
                {"id": "mark_attendance", "label": "Mark Attendance (Photo)", "icon": "camera"},
                {"id": "enter_results", "label": "Enter Results (Photo)", "icon": "camera"},
                {"id": "view_timetable", "label": "View Timetable", "icon": "calendar"},
                {"id": "parent_messages", "label": "Parent Messages", "icon": "message"}
            ]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{school_id}/teacher/{teacher_id}/generate-report")
async def generate_teacher_report(
    school_id: str,
    teacher_id: str,
    report_type: str,
    class_name: Optional[str] = None,
    subject: Optional[str] = None
):
    """
    Teacher asks AI agent to generate reports - no manual work
    """
    try:
        from api.services.clarity import ClarityClient
        
        db = get_db_manager()
        
        # Gather data for report
        if report_type == "class_performance":
            # Get class performance data
            performance_query = """
            SELECT s.first_name, s.last_name, 
                   AVG(ar.marks_obtained) as avg_marks,
                   COUNT(DISTINCT a.id) as total_assessments
            FROM students s
            LEFT JOIN assessment_results ar ON s.id = ar.student_id
            LEFT JOIN assessments a ON ar.assessment_id = a.id
            WHERE s.school_id = %s AND s.class_name = %s
            AND a.subject = %s
            GROUP BY s.id, s.first_name, s.last_name
            ORDER BY avg_marks DESC
            """
            data = db.execute_query(
                performance_query,
                (school_id, class_name, subject),
                fetch=True
            )
        elif report_type == "attendance_summary":
            # Get attendance summary
            attendance_query = """
            SELECT s.first_name, s.last_name,
                   COUNT(CASE WHEN a.status = 'present' THEN 1 END) as present,
                   COUNT(CASE WHEN a.status = 'absent' THEN 1 END) as absent,
                   COUNT(CASE WHEN a.status = 'late' THEN 1 END) as late
            FROM students s
            LEFT JOIN attendance a ON s.id = a.student_id
            WHERE s.school_id = %s AND s.class_name = %s
            AND a.date >= CURRENT_DATE - INTERVAL '30 days'
            GROUP BY s.id, s.first_name, s.last_name
            """
            data = db.execute_query(attendance_query, (school_id, class_name), fetch=True)
        else:
            data = []
        
        # Use Clarity to generate professional report
        clarity = ClarityClient()
        try:
            report = clarity.analyze(
                directive=f"""
                Generate a professional {report_type} report for {class_name} - {subject}.
                Include insights, trends, and actionable recommendations.
                Format as a polished report ready for school leadership.
                
                Data: {data}
                """,
                domain="education"
            )
        finally:
            clarity.close()
        
        return {
            "success": True,
            "report_type": report_type,
            "report": report,
            "generated_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
