"""
Analytics & Dashboards - Real Data Visualization
Production-ready analytics for all roles
"""
from fastapi import APIRouter, HTTPException
from typing import Optional
from datetime import datetime, timedelta

from api.services.database import get_db_manager
from api.services.clarity import ClarityClient

router = APIRouter()


@router.get("/{school_id}/analytics/overview")
async def school_overview_analytics(school_id: str):
    """
    School-wide analytics overview - for administrators
    """
    try:
        db = get_db_manager()
        
        # Enrollment trends (last 12 months)
        enrollment_query = """
        SELECT DATE_TRUNC('month', enrollment_date) as month,
               COUNT(*) as students
        FROM students
        WHERE school_id = %s
        AND enrollment_date >= CURRENT_DATE - INTERVAL '12 months'
        GROUP BY month
        ORDER BY month
        """
        enrollment_trends = db.execute_query(enrollment_query, (school_id,), fetch=True)
        
        # Fee collection trends (last 12 months)
        collection_query = """
        SELECT DATE_TRUNC('month', payment_date) as month,
               SUM(amount) as total_collected,
               COUNT(*) as payment_count
        FROM payments
        WHERE school_id = %s
        AND payment_date >= CURRENT_DATE - INTERVAL '12 months'
        GROUP BY month
        ORDER BY month
        """
        collection_trends = db.execute_query(collection_query, (school_id,), fetch=True)
        
        # Attendance trends (last 30 days)
        attendance_query = """
        SELECT date,
               COUNT(CASE WHEN status = 'present' THEN 1 END) as present,
               COUNT(CASE WHEN status = 'absent' THEN 1 END) as absent,
               COUNT(CASE WHEN status = 'late' THEN 1 END) as late
        FROM attendance a
        JOIN students s ON a.student_id = s.id
        WHERE s.school_id = %s
        AND a.date >= CURRENT_DATE - INTERVAL '30 days'
        GROUP BY date
        ORDER BY date
        """
        attendance_trends = db.execute_query(attendance_query, (school_id,), fetch=True)
        
        # Academic performance distribution
        performance_query = """
        SELECT 
            CASE 
                WHEN avg_percentage >= 90 THEN 'A (90-100)'
                WHEN avg_percentage >= 80 THEN 'B (80-89)'
                WHEN avg_percentage >= 70 THEN 'C (70-79)'
                WHEN avg_percentage >= 60 THEN 'D (60-69)'
                ELSE 'F (Below 60)'
            END as grade_range,
            COUNT(*) as student_count
        FROM (
            SELECT s.id, AVG(ar.marks_obtained / a.max_marks * 100) as avg_percentage
            FROM students s
            LEFT JOIN assessment_results ar ON s.id = ar.student_id
            LEFT JOIN assessments a ON ar.assessment_id = a.id
            WHERE s.school_id = %s
            AND a.date >= CURRENT_DATE - INTERVAL '90 days'
            GROUP BY s.id
        ) AS student_averages
        GROUP BY grade_range
        ORDER BY grade_range
        """
        performance_dist = db.execute_query(performance_query, (school_id,), fetch=True)
        
        # Incident trends
        incident_query = """
        SELECT incident_type,
               COUNT(*) as count
        FROM incidents
        WHERE school_id = %s
        AND incident_date >= CURRENT_DATE - INTERVAL '90 days'
        GROUP BY incident_type
        ORDER BY count DESC
        """
        incident_stats = db.execute_query(incident_query, (school_id,), fetch=True)
        
        return {
            "success": True,
            "enrollment_trends": enrollment_trends,
            "collection_trends": collection_trends,
            "attendance_trends": attendance_trends,
            "performance_distribution": performance_dist,
            "incident_statistics": incident_stats,
            "generated_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{school_id}/analytics/financial")
async def financial_analytics(school_id: str):
    """
    Financial analytics and forecasting
    """
    try:
        db = get_db_manager()
        clarity = ClarityClient()
        
        # Revenue breakdown
        revenue_query = """
        SELECT 
            fs.name as fee_type,
            SUM(sf.amount_due) as total_due,
            SUM(sf.amount_paid) as total_collected,
            SUM(sf.balance) as outstanding
        FROM student_fees sf
        JOIN fee_structures fs ON sf.fee_structure_id = fs.id
        JOIN students s ON sf.student_id = s.id
        WHERE s.school_id = %s
        GROUP BY fs.name
        ORDER BY total_due DESC
        """
        revenue_breakdown = db.execute_query(revenue_query, (school_id,), fetch=True)
        
        # Expense breakdown (last 90 days)
        expense_query = """
        SELECT category,
               SUM(amount) as total_spent,
               COUNT(*) as transaction_count
        FROM expenses
        WHERE school_id = %s
        AND expense_date >= CURRENT_DATE - INTERVAL '90 days'
        GROUP BY category
        ORDER BY total_spent DESC
        """
        expense_breakdown = db.execute_query(expense_query, (school_id,), fetch=True)
        
        # Cash flow (last 6 months, monthly)
        cashflow_query = """
        SELECT 
            TO_CHAR(month, 'YYYY-MM') as month,
            COALESCE(income, 0) as income,
            COALESCE(expenses, 0) as expenses,
            COALESCE(income, 0) - COALESCE(expenses, 0) as net
        FROM (
            SELECT DATE_TRUNC('month', d) as month
            FROM generate_series(
                CURRENT_DATE - INTERVAL '6 months',
                CURRENT_DATE,
                '1 month'::interval
            ) d
        ) months
        LEFT JOIN (
            SELECT DATE_TRUNC('month', payment_date) as month,
                   SUM(amount) as income
            FROM payments
            WHERE school_id = %s
            GROUP BY month
        ) payments ON months.month = payments.month
        LEFT JOIN (
            SELECT DATE_TRUNC('month', expense_date) as month,
                   SUM(amount) as expenses
            FROM expenses
            WHERE school_id = %s
            GROUP BY month
        ) exp ON months.month = exp.month
        ORDER BY month
        """
        cashflow = db.execute_query(cashflow_query, (school_id, school_id), fetch=True)
        
        # Use Clarity for financial forecast
        try:
            forecast = clarity.analyze(
                directive=f"""
                Based on this financial data, provide:
                1. 90-day revenue forecast
                2. Expense optimization opportunities
                3. Cash flow risk assessment
                4. Fee collection improvement strategies
                
                Data:
                Revenue: {revenue_breakdown}
                Expenses: {expense_breakdown}
                Cash Flow: {cashflow}
                """,
                domain="financial"
            )
        finally:
            clarity.close()
        
        return {
            "success": True,
            "revenue_breakdown": revenue_breakdown,
            "expense_breakdown": expense_breakdown,
            "cashflow": cashflow,
            "forecast": forecast
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{school_id}/analytics/academic")
async def academic_analytics(school_id: str, class_name: Optional[str] = None):
    """
    Academic performance analytics with AI insights
    """
    try:
        db = get_db_manager()
        clarity = ClarityClient()
        
        # Class-level performance
        if class_name:
            class_filter = "AND s.class_name = %s"
            params = (school_id, class_name)
        else:
            class_filter = ""
            params = (school_id,)
        
        # Subject performance
        subject_query = f"""
        SELECT a.subject,
               AVG(ar.marks_obtained / a.max_marks * 100) as avg_percentage,
               COUNT(DISTINCT s.id) as student_count,
               COUNT(DISTINCT a.id) as assessment_count
        FROM students s
        JOIN assessment_results ar ON s.id = ar.student_id
        JOIN assessments a ON ar.assessment_id = a.id
        WHERE s.school_id = %s
        {class_filter}
        AND a.date >= CURRENT_DATE - INTERVAL '90 days'
        GROUP BY a.subject
        ORDER BY avg_percentage DESC
        """
        subject_performance = db.execute_query(subject_query, params, fetch=True)
        
        # Improvement/decline trends
        trend_query = f"""
        SELECT s.id, s.first_name, s.last_name, s.class_name,
               AVG(CASE 
                   WHEN a.date >= CURRENT_DATE - INTERVAL '30 days' 
                   THEN ar.marks_obtained / a.max_marks * 100 
               END) as recent_avg,
               AVG(CASE 
                   WHEN a.date < CURRENT_DATE - INTERVAL '30 days' 
                   AND a.date >= CURRENT_DATE - INTERVAL '90 days'
                   THEN ar.marks_obtained / a.max_marks * 100 
               END) as older_avg
        FROM students s
        JOIN assessment_results ar ON s.id = ar.student_id
        JOIN assessments a ON ar.assessment_id = a.id
        WHERE s.school_id = %s
        {class_filter}
        AND a.date >= CURRENT_DATE - INTERVAL '90 days'
        GROUP BY s.id, s.first_name, s.last_name, s.class_name
        HAVING COUNT(DISTINCT a.id) >= 5
        """
        trend_data = db.execute_query(trend_query, params, fetch=True)
        
        # Calculate improving/declining students
        improving = []
        declining = []
        for student in trend_data:
            if student["recent_avg"] and student["older_avg"]:
                change = student["recent_avg"] - student["older_avg"]
                if change > 5:
                    improving.append({**student, "change": round(change, 1)})
                elif change < -5:
                    declining.append({**student, "change": round(change, 1)})
        
        # AI-powered insights
        try:
            insights = clarity.analyze(
                directive=f"""
                Analyze academic performance and provide insights:
                
                Subject Performance: {subject_performance}
                Improving Students: {len(improving)}
                Declining Students: {len(declining)}
                
                Provide:
                1. Strongest and weakest subjects with explanations
                2. Intervention priorities
                3. Teaching strategy recommendations
                4. Student grouping suggestions
                5. Curriculum adjustment ideas
                """,
                domain="education"
            )
        finally:
            clarity.close()
        
        return {
            "success": True,
            "subject_performance": subject_performance,
            "improving_students": improving[:10],  # Top 10
            "declining_students": declining[:10],  # Top 10
            "insights": insights
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{school_id}/analytics/teacher/{teacher_id}")
async def teacher_analytics(school_id: str, teacher_id: str):
    """
    Teacher-specific analytics dashboard
    """
    try:
        db = get_db_manager()
        
        # Classes taught and student counts
        classes_query = """
        SELECT DISTINCT class_name,
               (SELECT COUNT(*) FROM students WHERE class_name = t.class_name AND school_id = %s) as student_count
        FROM timetable t
        WHERE school_id = %s AND teacher_id = %s
        """
        classes = db.execute_query(classes_query, (school_id, school_id, teacher_id), fetch=True)
        
        # Attendance marking stats
        attendance_query = """
        SELECT DATE(marked_at) as date,
               COUNT(*) as students_marked
        FROM attendance
        WHERE marked_by = %s
        AND marked_at >= CURRENT_DATE - INTERVAL '30 days'
        GROUP BY date
        ORDER BY date DESC
        """
        attendance_stats = db.execute_query(attendance_query, (teacher_id,), fetch=True)
        
        # Assessment creation stats
        assessment_query = """
        SELECT subject, COUNT(*) as count,
               AVG((SELECT AVG(marks_obtained) FROM assessment_results WHERE assessment_id = a.id)) as avg_marks
        FROM assessments a
        WHERE created_by = %s
        AND date >= CURRENT_DATE - INTERVAL '90 days'
        GROUP BY subject
        """
        assessment_stats = db.execute_query(assessment_query, (teacher_id,), fetch=True)
        
        return {
            "success": True,
            "classes": classes,
            "attendance_marking": attendance_stats,
            "assessments": assessment_stats,
            "total_students": sum([c["student_count"] for c in classes])
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{school_id}/analytics/parent/{parent_id}")
async def parent_analytics(school_id: str, parent_id: str):
    """
    Parent-specific analytics for their children
    """
    try:
        db = get_db_manager()
        
        # Get all children
        children_query = """
        SELECT s.id, s.first_name, s.last_name, s.class_name
        FROM students s
        JOIN student_parents sp ON s.id = sp.student_id
        WHERE sp.parent_id = %s AND s.school_id = %s
        """
        children = db.execute_query(children_query, (parent_id, school_id), fetch=True)
        
        analytics_by_child = []
        
        for child in children:
            # Attendance trend (last 30 days)
            attendance = db.execute_query(
                """SELECT date, status FROM attendance 
                   WHERE student_id = %s 
                   AND date >= CURRENT_DATE - INTERVAL '30 days' 
                   ORDER BY date DESC""",
                (child["id"],), fetch=True
            )
            
            # Performance trend (last 90 days)
            performance = db.execute_query(
                """SELECT a.subject, a.date, ar.marks_obtained, a.max_marks,
                          (ar.marks_obtained / a.max_marks * 100) as percentage
                   FROM assessment_results ar
                   JOIN assessments a ON ar.assessment_id = a.id
                   WHERE ar.student_id = %s
                   AND a.date >= CURRENT_DATE - INTERVAL '90 days'
                   ORDER BY a.date DESC""",
                (child["id"],), fetch=True
            )
            
            # Calculate averages
            if performance:
                avg_performance = sum([p["percentage"] for p in performance]) / len(performance)
            else:
                avg_performance = 0
            
            attendance_rate = 0
            if attendance:
                present = len([a for a in attendance if a["status"] == "present"])
                attendance_rate = round((present / len(attendance)) * 100, 1)
            
            analytics_by_child.append({
                "student": child,
                "attendance_rate": attendance_rate,
                "avg_performance": round(avg_performance, 1),
                "recent_attendance": attendance[:10],
                "recent_assessments": performance[:5]
            })
        
        return {
            "success": True,
            "children_count": len(children),
            "analytics": analytics_by_child
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
