"""
Parent Portal - Real-Time Updates and Interactions
Parents get instant notifications, view children's progress, pay fees, chat
"""
from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect
from typing import List, Optional
from datetime import datetime, timedelta

from api.services.database import get_db_manager
from api.services.mobile_money import MobileMoneyService
from api.services.notifications import NotificationService

router = APIRouter()


# WebSocket connection manager for real-time notifications
class ConnectionManager:
    def __init__(self):
        self.active_connections: dict = {}
    
    async def connect(self, websocket: WebSocket, parent_id: str):
        await websocket.accept()
        self.active_connections[parent_id] = websocket
    
    def disconnect(self, parent_id: str):
        if parent_id in self.active_connections:
            del self.active_connections[parent_id]
    
    async def send_personal_message(self, message: dict, parent_id: str):
        if parent_id in self.active_connections:
            await self.active_connections[parent_id].send_json(message)
    
    async def broadcast(self, message: dict, school_id: str):
        for parent_id, connection in self.active_connections.items():
            try:
                await connection.send_json(message)
            except:
                pass


manager = ConnectionManager()


@router.websocket("/ws/{parent_id}")
async def websocket_endpoint(websocket: WebSocket, parent_id: str):
    """
    WebSocket for real-time notifications to parent
    """
    await manager.connect(websocket, parent_id)
    try:
        while True:
            # Keep connection alive and listen for messages
            data = await websocket.receive_text()
            # Echo back for testing
            await websocket.send_json({"type": "ack", "message": "Connected"})
    except WebSocketDisconnect:
        manager.disconnect(parent_id)


@router.get("/{school_id}/parent/{parent_id}/dashboard")
async def get_parent_dashboard(school_id: str, parent_id: str):
    """
    Parent dashboard - children, recent activity, notifications, fee status
    """
    try:
        db = get_db_manager()
        
        # Get parent info
        parent_query = """
        SELECT id, first_name, last_name, primary_phone, email
        FROM parents WHERE id = %s AND school_id = %s
        """
        parent = db.execute_query(parent_query, (parent_id, school_id), fetch=True)[0]
        
        # Get children
        children_query = """
        SELECT s.id, s.first_name, s.last_name, s.class_name, s.admission_number,
               sp.relationship, sp.is_primary
        FROM students s
        JOIN student_parents sp ON s.id = sp.student_id
        WHERE sp.parent_id = %s AND s.school_id = %s
        ORDER BY s.first_name
        """
        children = db.execute_query(children_query, (parent_id, school_id), fetch=True)
        
        # Get recent notifications (last 7 days)
        notifications_query = """
        SELECT id, notification_type, title, message, priority, is_read, created_at
        FROM notifications
        WHERE school_id = %s AND recipient_id = %s AND recipient_type = 'parent'
        AND created_at >= CURRENT_DATE - INTERVAL '7 days'
        ORDER BY created_at DESC
        LIMIT 20
        """
        notifications = db.execute_query(notifications_query, (school_id, parent_id), fetch=True)
        
        # Get fee summary for all children
        fee_summary = []
        for child in children:
            fee_query = """
            SELECT SUM(amount_due) as total_due,
                   SUM(amount_paid) as total_paid,
                   SUM(balance) as total_balance
            FROM student_fees
            WHERE student_id = %s
            """
            fees = db.execute_query(fee_query, (child["id"],), fetch=True)
            if fees and fees[0]["total_balance"]:
                fee_summary.append({
                    "student_id": child["id"],
                    "student_name": f"{child['first_name']} {child['last_name']}",
                    "total_balance": float(fees[0]["total_balance"]),
                    "total_due": float(fees[0]["total_due"]),
                    "total_paid": float(fees[0]["total_paid"])
                })
        
        # Get recent attendance for all children
        attendance_summary = []
        for child in children:
            attendance_query = """
            SELECT status, COUNT(*) as count
            FROM attendance
            WHERE student_id = %s
            AND date >= CURRENT_DATE - INTERVAL '30 days'
            GROUP BY status
            """
            attendance = db.execute_query(attendance_query, (child["id"],), fetch=True)
            
            stats = {"present": 0, "absent": 0, "late": 0}
            for record in attendance:
                stats[record["status"]] = record["count"]
            
            attendance_summary.append({
                "student_id": child["id"],
                "student_name": f"{child['first_name']} {child['last_name']}",
                "stats": stats,
                "attendance_rate": round(
                    (stats["present"] / (stats["present"] + stats["absent"] + stats["late"]) * 100)
                    if (stats["present"] + stats["absent"] + stats["late"]) > 0 else 0,
                    1
                )
            })
        
        return {
            "success": True,
            "parent": parent,
            "children": children,
            "notifications": notifications,
            "unread_notifications": len([n for n in notifications if not n["is_read"]]),
            "fee_summary": fee_summary,
            "attendance_summary": attendance_summary,
            "quick_actions": [
                {"id": "pay_fees", "label": "Pay Fees (MTN/Airtel)", "icon": "money"},
                {"id": "view_results", "label": "View Results", "icon": "chart"},
                {"id": "chat_teacher", "label": "Chat with Teacher", "icon": "message"},
                {"id": "view_timetable", "label": "View Timetable", "icon": "calendar"}
            ]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{school_id}/parent/{parent_id}/child/{student_id}/details")
async def get_child_details(school_id: str, parent_id: str, student_id: str):
    """
    Detailed view of specific child - attendance, results, health, etc.
    """
    try:
        db = get_db_manager()
        
        # Verify parent has access to this child
        verify_query = """
        SELECT 1 FROM student_parents
        WHERE student_id = %s AND parent_id = %s
        """
        if not db.execute_query(verify_query, (student_id, parent_id), fetch=True):
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Get student info
        student_query = """
        SELECT id, first_name, last_name, class_name, admission_number,
               date_of_birth, gender, enrollment_date
        FROM students WHERE id = %s AND school_id = %s
        """
        student = db.execute_query(student_query, (student_id, school_id), fetch=True)[0]
        
        # Get attendance history (last 30 days)
        attendance_query = """
        SELECT date, status, notes
        FROM attendance
        WHERE student_id = %s
        AND date >= CURRENT_DATE - INTERVAL '30 days'
        ORDER BY date DESC
        """
        attendance = db.execute_query(attendance_query, (student_id,), fetch=True)
        
        # Get recent assessment results
        results_query = """
        SELECT a.name, a.subject, a.date, a.max_marks,
               ar.marks_obtained, ar.grade, ar.remarks
        FROM assessment_results ar
        JOIN assessments a ON ar.assessment_id = a.id
        WHERE ar.student_id = %s
        ORDER BY a.date DESC
        LIMIT 10
        """
        results = db.execute_query(results_query, (student_id,), fetch=True)
        
        # Get health visits
        health_query = """
        SELECT visit_date, symptoms, diagnosis, treatment, sent_home
        FROM health_visits
        WHERE student_id = %s
        ORDER BY visit_date DESC
        LIMIT 10
        """
        health_visits = db.execute_query(health_query, (student_id,), fetch=True)
        
        # Get fee status
        fee_query = """
        SELECT fs.name, sf.amount_due, sf.amount_paid, sf.balance,
               sf.status, sf.due_date
        FROM student_fees sf
        JOIN fee_structures fs ON sf.fee_structure_id = fs.id
        WHERE sf.student_id = %s
        ORDER BY sf.due_date DESC
        """
        fees = db.execute_query(fee_query, (student_id,), fetch=True)
        
        return {
            "success": True,
            "student": student,
            "attendance": attendance,
            "recent_results": results,
            "health_visits": health_visits,
            "fees": fees
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{school_id}/parent/{parent_id}/pay-fees")
async def initiate_fee_payment(
    school_id: str,
    parent_id: str,
    student_id: str,
    amount: float,
    provider: str,  # "mtn" or "airtel"
    phone_number: str
):
    """
    Parent initiates fee payment via MTN/Airtel Money
    """
    try:
        # Verify parent has access
        db = get_db_manager()
        verify_query = """
        SELECT 1 FROM student_parents
        WHERE student_id = %s AND parent_id = %s
        """
        if not db.execute_query(verify_query, (student_id, parent_id), fetch=True):
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Initiate mobile money payment
        mm_service = MobileMoneyService(school_id)
        result = await mm_service.initiate_payment(
            student_id=student_id,
            parent_id=parent_id,
            provider=provider,
            phone_number=phone_number,
            amount=amount,
            purpose="fee_payment"
        )
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{school_id}/parent/{parent_id}/notifications")
async def get_parent_notifications(
    school_id: str,
    parent_id: str,
    limit: int = 50,
    offset: int = 0
):
    """
    Get all notifications for parent
    """
    try:
        db = get_db_manager()
        
        query = """
        SELECT id, notification_type, title, message, priority, is_read,
               created_at, related_entity_type, related_entity_id
        FROM notifications
        WHERE school_id = %s AND recipient_id = %s AND recipient_type = 'parent'
        ORDER BY created_at DESC
        LIMIT %s OFFSET %s
        """
        notifications = db.execute_query(
            query,
            (school_id, parent_id, limit, offset),
            fetch=True
        )
        
        return {
            "success": True,
            "notifications": notifications,
            "count": len(notifications)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{school_id}/parent/{parent_id}/notifications/{notification_id}/read")
async def mark_notification_read(school_id: str, parent_id: str, notification_id: str):
    """
    Mark notification as read
    """
    try:
        db = get_db_manager()
        
        query = """
        UPDATE notifications
        SET is_read = true, read_at = CURRENT_TIMESTAMP
        WHERE id = %s AND recipient_id = %s AND school_id = %s
        """
        db.execute_query(query, (notification_id, parent_id, school_id), fetch=False)
        
        return {"success": True, "message": "Notification marked as read"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{school_id}/parent/{parent_id}/chat/conversations")
async def get_parent_conversations(school_id: str, parent_id: str):
    """
    Get chatbot conversations for parent
    """
    try:
        db = get_db_manager()
        
        # Get active conversations
        query = """
        SELECT id, session_id, created_at, last_message_at, is_active
        FROM chatbot_conversations
        WHERE school_id = %s AND user_id = %s AND user_type = 'parent'
        ORDER BY last_message_at DESC
        LIMIT 10
        """
        conversations = db.execute_query(query, (school_id, parent_id), fetch=True)
        
        return {
            "success": True,
            "conversations": conversations
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{school_id}/parent/{parent_id}/chat/send")
async def send_chat_message(
    school_id: str,
    parent_id: str,
    message: str,
    conversation_id: Optional[str] = None
):
    """
    Parent sends message to chatbot - gets instant AI response
    """
    try:
        from api.services.chatbot import ChatbotService
        
        db = get_db_manager()
        
        # Create or get conversation
        if not conversation_id:
            conv_query = """
            INSERT INTO chatbot_conversations (school_id, user_type, user_id, is_active)
            VALUES (%s, 'parent', %s, true)
            RETURNING id, session_id
            """
            conv = db.execute_query(conv_query, (school_id, parent_id), fetch=True)[0]
            conversation_id = conv["id"]
        
        # Save user message
        msg_query = """
        INSERT INTO chatbot_messages (conversation_id, role, content)
        VALUES (%s, 'user', %s)
        """
        db.execute_query(msg_query, (conversation_id, message), fetch=False)
        
        # Get AI response
        chatbot = ChatbotService(school_id)
        response = await chatbot.query(
            user_query=message,
            user_type="parent",
            user_id=parent_id,
            context={"conversation_id": conversation_id}
        )
        
        # Save AI response
        db.execute_query(
            msg_query,
            (conversation_id, response.get("answer", "I couldn't process that. Please try again.")),
            fetch=False
        )
        
        # Update conversation timestamp
        update_query = """
        UPDATE chatbot_conversations
        SET last_message_at = CURRENT_TIMESTAMP
        WHERE id = %s
        """
        db.execute_query(update_query, (conversation_id,), fetch=False)
        
        return {
            "success": True,
            "conversation_id": conversation_id,
            "user_message": message,
            "ai_response": response.get("answer", ""),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
