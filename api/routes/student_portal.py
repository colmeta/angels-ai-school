"""
Student Portal - Student-Facing Features
Students view grades, attendance, schedule, assignments, achievements
"""
from fastapi import APIRouter, HTTPException
from typing import Optional

from api.services.database import get_db_manager

router = APIRouter()


@router.get("/{school_id}/student/{student_id}/dashboard")
async def get_student_dashboard(school_id: str, student_id: str):
    """
    Student dashboard - attendance, grades, schedule, achievements
    """
    try:
        db = get_db_manager()
        
        # Get student info
        student_query = """
        SELECT id, first_name, last_name, class_name, admission_number,
               photo_url, email
        FROM students WHERE id = %s AND school_id = %s
        """
        student = db.execute_query(student_query, (student_id, school_id), fetch=True)[0]
        
        # Get today's schedule
        schedule_query = """
        SELECT day_of_week, start_time, end_time, subject, room
        FROM timetable
        WHERE school_id = %s AND class_name = %s
        AND day_of_week = EXTRACT(ISODOW FROM CURRENT_DATE)
        ORDER BY start_time
        """
        todays_schedule = db.execute_query(
            schedule_query,
            (school_id, student["class_name"]),
            fetch=True
        )
        
        # Get attendance summary (current month)
        attendance_query = """
        SELECT status, COUNT(*) as count
        FROM attendance
        WHERE student_id = %s
        AND EXTRACT(MONTH FROM date) = EXTRACT(MONTH FROM CURRENT_DATE)
        AND EXTRACT(YEAR FROM date) = EXTRACT(YEAR FROM CURRENT_DATE)
        GROUP BY status
        """
        attendance = db.execute_query(attendance_query, (student_id,), fetch=True)
        
        attendance_stats = {"present": 0, "absent": 0, "late": 0}
        for record in attendance:
            attendance_stats[record["status"]] = record["count"]
        
        total_days = sum(attendance_stats.values())
        attendance_rate = round(
            (attendance_stats["present"] / total_days * 100) if total_days > 0 else 0,
            1
        )
        
        # Get recent grades
        grades_query = """
        SELECT a.name, a.subject, a.date, a.max_marks,
               ar.marks_obtained, ar.grade
        FROM assessment_results ar
        JOIN assessments a ON ar.assessment_id = a.id
        WHERE ar.student_id = %s
        ORDER BY a.date DESC
        LIMIT 5
        """
        recent_grades = db.execute_query(grades_query, (student_id,), fetch=True)
        
        # Calculate GPA/average
        gpa_query = """
        SELECT AVG(ar.marks_obtained / a.max_marks * 100) as average
        FROM assessment_results ar
        JOIN assessments a ON ar.assessment_id = a.id
        WHERE ar.student_id = %s
        AND a.date >= CURRENT_DATE - INTERVAL '90 days'
        """
        gpa_result = db.execute_query(gpa_query, (student_id,), fetch=True)
        average = round(gpa_result[0]["average"], 1) if gpa_result and gpa_result[0]["average"] else 0
        
        # Get achievements/badges
        achievements = [
            {"id": "perfect_attendance", "name": "Perfect Attendance", "unlocked": attendance_stats["absent"] == 0},
            {"id": "honor_roll", "name": "Honor Roll", "unlocked": average >= 80},
            {"id": "improved", "name": "Most Improved", "unlocked": False}
        ]
        
        return {
            "success": True,
            "student": student,
            "todays_schedule": todays_schedule,
            "attendance": {
                "stats": attendance_stats,
                "rate": attendance_rate,
                "total_days": total_days
            },
            "recent_grades": recent_grades,
            "average": average,
            "achievements": [a for a in achievements if a["unlocked"]],
            "quick_actions": [
                {"id": "view_timetable", "label": "View Timetable", "icon": "calendar"},
                {"id": "view_grades", "label": "View All Grades", "icon": "chart"},
                {"id": "library", "label": "Library Books", "icon": "book"},
                {"id": "report_issue", "label": "Report Issue", "icon": "alert"}
            ]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{school_id}/student/{student_id}/grades")
async def get_student_grades(school_id: str, student_id: str, subject: Optional[str] = None):
    """
    Get all grades for student, optionally filtered by subject
    """
    try:
        db = get_db_manager()
        
        if subject:
            query = """
            SELECT a.id, a.name, a.subject, a.date, a.max_marks, a.type,
                   ar.marks_obtained, ar.grade, ar.remarks
            FROM assessment_results ar
            JOIN assessments a ON ar.assessment_id = a.id
            WHERE ar.student_id = %s AND a.subject = %s
            ORDER BY a.date DESC
            """
            grades = db.execute_query(query, (student_id, subject), fetch=True)
        else:
            query = """
            SELECT a.id, a.name, a.subject, a.date, a.max_marks, a.type,
                   ar.marks_obtained, ar.grade, ar.remarks
            FROM assessment_results ar
            JOIN assessments a ON ar.assessment_id = a.id
            WHERE ar.student_id = %s
            ORDER BY a.date DESC
            """
            grades = db.execute_query(query, (student_id,), fetch=True)
        
        # Calculate subject-wise averages
        subject_query = """
        SELECT a.subject, 
               AVG(ar.marks_obtained / a.max_marks * 100) as average,
               COUNT(*) as assessment_count
        FROM assessment_results ar
        JOIN assessments a ON ar.assessment_id = a.id
        WHERE ar.student_id = %s
        GROUP BY a.subject
        """
        subject_averages = db.execute_query(subject_query, (student_id,), fetch=True)
        
        return {
            "success": True,
            "grades": grades,
            "subject_averages": subject_averages
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{school_id}/student/{student_id}/timetable")
async def get_student_timetable(school_id: str, student_id: str):
    """
    Get full week timetable for student
    """
    try:
        db = get_db_manager()
        
        # Get student's class
        student_query = "SELECT class_name FROM students WHERE id = %s"
        student = db.execute_query(student_query, (student_id,), fetch=True)[0]
        
        # Get full timetable
        timetable_query = """
        SELECT day_of_week, start_time, end_time, subject, room,
               t.first_name as teacher_first_name, t.last_name as teacher_last_name
        FROM timetable tt
        LEFT JOIN teachers t ON tt.teacher_id = t.id
        WHERE tt.school_id = %s AND tt.class_name = %s
        ORDER BY day_of_week, start_time
        """
        timetable = db.execute_query(
            timetable_query,
            (school_id, student["class_name"]),
            fetch=True
        )
        
        # Organize by day
        week_schedule = {i: [] for i in range(1, 8)}  # 1=Monday, 7=Sunday
        for entry in timetable:
            week_schedule[entry["day_of_week"]].append(entry)
        
        return {
            "success": True,
            "class_name": student["class_name"],
            "week_schedule": week_schedule,
            "timetable": timetable
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{school_id}/student/{student_id}/library")
async def get_student_library(school_id: str, student_id: str):
    """
    Get books borrowed by student
    """
    try:
        db = get_db_manager()
        
        # Get currently borrowed books
        borrowed_query = """
        SELECT lt.id, lb.title, lb.author, lb.isbn,
               lt.borrow_date, lt.due_date, lt.status,
               CASE 
                   WHEN lt.due_date < CURRENT_DATE AND lt.status = 'active' 
                   THEN CURRENT_DATE - lt.due_date 
                   ELSE 0 
               END as days_overdue
        FROM library_transactions lt
        JOIN library_books lb ON lt.book_id = lb.id
        WHERE lt.student_id = %s AND lt.status = 'active'
        ORDER BY lt.borrow_date DESC
        """
        borrowed_books = db.execute_query(borrowed_query, (student_id,), fetch=True)
        
        # Get history
        history_query = """
        SELECT lt.id, lb.title, lb.author,
               lt.borrow_date, lt.return_date, lt.fine_amount
        FROM library_transactions lt
        JOIN library_books lb ON lt.book_id = lb.id
        WHERE lt.student_id = %s AND lt.status = 'returned'
        ORDER BY lt.return_date DESC
        LIMIT 10
        """
        history = db.execute_query(history_query, (student_id,), fetch=True)
        
        return {
            "success": True,
            "borrowed_books": borrowed_books,
            "history": history,
            "total_borrowed": len(borrowed_books),
            "overdue_count": len([b for b in borrowed_books if b["days_overdue"] > 0])
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{school_id}/student/{student_id}/report-concern")
async def report_student_concern(
    school_id: str,
    student_id: str,
    concern_type: str,
    description: str
):
    """
    Student reports a concern/issue (bullying, safety, health, etc.)
    """
    try:
        from api.services.notifications import NotificationService
        
        db = get_db_manager()
        
        # Create incident record
        incident_query = """
        INSERT INTO incidents (
            school_id, student_id, incident_type, severity, title,
            description, incident_date, reported_by, status
        ) VALUES (%s, %s, %s, 'medium', %s, %s, CURRENT_TIMESTAMP, %s, 'open')
        RETURNING id
        """
        incident = db.execute_query(
            incident_query,
            (school_id, student_id, concern_type, f"Student-reported: {concern_type}", 
             description, f"Student:{student_id}"),
            fetch=True
        )[0]
        
        # Notify school admin
        notification_service = NotificationService()
        await notification_service.send_notification(
            school_id=school_id,
            recipient_id="admin",  # Would be actual admin ID
            recipient_type="admin",
            notification_type="incident",
            title=f"Student Reported {concern_type}",
            message=f"A student has reported a concern. Please review immediately.",
            channels=["app"],
            priority="high",
            related_entity_type="incident",
            related_entity_id=incident["id"]
        )
        
        return {
            "success": True,
            "message": "Your concern has been reported. A staff member will review it soon.",
            "incident_id": incident["id"]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{school_id}/student/{student_id}/performance-analytics")
async def get_student_performance_analytics(school_id: str, student_id: str):
    """
    AI-powered performance analytics for student
    """
    try:
        from api.services.clarity import ClarityClient
        
        db = get_db_manager()
        
        # Gather performance data
        performance_query = """
        SELECT a.subject, a.date, a.max_marks, ar.marks_obtained,
               (ar.marks_obtained / a.max_marks * 100) as percentage
        FROM assessment_results ar
        JOIN assessments a ON ar.assessment_id = a.id
        WHERE ar.student_id = %s
        AND a.date >= CURRENT_DATE - INTERVAL '6 months'
        ORDER BY a.date ASC
        """
        performance_data = db.execute_query(performance_query, (student_id,), fetch=True)
        
        # Use Clarity to analyze performance trends
        clarity = ClarityClient()
        try:
            analysis = clarity.analyze(
                directive=f"""
                Analyze this student's academic performance over 6 months.
                Identify strengths, weaknesses, trends, and provide specific recommendations.
                Be encouraging but honest. Format for student reading level.
                
                Performance data: {performance_data}
                """,
                domain="education"
            )
        finally:
            clarity.close()
        
        # Calculate trend (improving/declining/stable)
        if len(performance_data) >= 5:
            recent_avg = sum([d["percentage"] for d in performance_data[-5:]]) / 5
            older_avg = sum([d["percentage"] for d in performance_data[:5]]) / 5
            if recent_avg > older_avg + 5:
                trend = "improving"
            elif recent_avg < older_avg - 5:
                trend = "declining"
            else:
                trend = "stable"
        else:
            trend = "insufficient_data"
        
        return {
            "success": True,
            "trend": trend,
            "analysis": analysis,
            "performance_data": performance_data
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
