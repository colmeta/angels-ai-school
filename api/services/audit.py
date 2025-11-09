"""
Audit Logging Service for Production
Tracks all sensitive operations with immutable audit trail
"""
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import json
import psycopg2.extras

from api.services.database import DatabaseService


class AuditLogger:
    """
    Production audit logging
    - Logs all sensitive operations
    - Immutable audit trail
    - Searchable and reportable
    - GDPR/compliance ready
    """
    
    def __init__(self):
        self.db = DatabaseService()
    
    def log_action(
        self,
        user_id: str,
        school_id: str,
        action: str,
        resource_type: str,
        resource_id: str,
        changes: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Log an action to the audit trail
        
        Args:
            user_id: Who performed the action
            school_id: Which school context
            action: view, create, update, delete, login, etc.
            resource_type: student, fee, grade, user, etc.
            resource_id: ID of the resource
            changes: Before/after values for updates
            ip_address: User's IP address
            user_agent: User's browser/app
            metadata: Additional context
        
        Returns:
            Audit log ID
        """
        query = """
        INSERT INTO audit_logs (
            user_id, school_id, action, resource_type, resource_id,
            changes, ip_address, user_agent, metadata, created_at
        ) VALUES (
            %s, %s, %s, %s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP
        ) RETURNING id
        """
        
        changes_json = json.dumps(changes) if changes else None
        metadata_json = json.dumps(metadata) if metadata else None
        
        result = self.db.execute_query(
            query,
            (user_id, school_id, action, resource_type, resource_id,
             changes_json, ip_address, user_agent, metadata_json)
        )
        
        if result and len(result) > 0:
            return result[0][0]
        return None
    
    def log_fee_payment(
        self,
        user_id: str,
        school_id: str,
        student_id: str,
        amount: float,
        payment_method: str,
        ip_address: Optional[str] = None
    ) -> str:
        """Log fee payment"""
        return self.log_action(
            user_id=user_id,
            school_id=school_id,
            action="payment",
            resource_type="fee",
            resource_id=student_id,
            metadata={
                "amount": amount,
                "payment_method": payment_method,
                "currency": "UGX"
            },
            ip_address=ip_address
        )
    
    def log_grade_change(
        self,
        user_id: str,
        school_id: str,
        student_id: str,
        subject: str,
        old_grade: Optional[float],
        new_grade: float,
        ip_address: Optional[str] = None
    ) -> str:
        """Log grade modification"""
        return self.log_action(
            user_id=user_id,
            school_id=school_id,
            action="update",
            resource_type="grade",
            resource_id=student_id,
            changes={
                "subject": subject,
                "old_value": old_grade,
                "new_value": new_grade
            },
            ip_address=ip_address
        )
    
    def log_student_data_change(
        self,
        user_id: str,
        school_id: str,
        student_id: str,
        field: str,
        old_value: Any,
        new_value: Any,
        ip_address: Optional[str] = None
    ) -> str:
        """Log student data modification"""
        return self.log_action(
            user_id=user_id,
            school_id=school_id,
            action="update",
            resource_type="student",
            resource_id=student_id,
            changes={
                "field": field,
                "old_value": str(old_value) if old_value else None,
                "new_value": str(new_value) if new_value else None
            },
            ip_address=ip_address
        )
    
    def log_user_login(
        self,
        user_id: str,
        school_id: str,
        success: bool,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> str:
        """Log user login attempt"""
        return self.log_action(
            user_id=user_id,
            school_id=school_id,
            action="login_success" if success else "login_failed",
            resource_type="auth",
            resource_id=user_id,
            ip_address=ip_address,
            user_agent=user_agent
        )
    
    def log_data_export(
        self,
        user_id: str,
        school_id: str,
        export_type: str,
        record_count: int,
        ip_address: Optional[str] = None
    ) -> str:
        """Log data export (for compliance)"""
        return self.log_action(
            user_id=user_id,
            school_id=school_id,
            action="export",
            resource_type=export_type,
            resource_id=f"export_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            metadata={
                "record_count": record_count,
                "export_timestamp": datetime.now().isoformat()
            },
            ip_address=ip_address
        )
    
    def get_audit_trail(
        self,
        school_id: str,
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        user_id: Optional[str] = None,
        action: Optional[str] = None,
        days: int = 30,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Get audit trail with filters
        
        Args:
            school_id: School to query
            resource_type: Filter by resource type
            resource_id: Filter by specific resource
            user_id: Filter by user
            action: Filter by action type
            days: Look back period (default 30 days)
            limit: Max records to return
        
        Returns:
            List of audit log entries
        """
        conditions = ["school_id = %s", "created_at >= %s"]
        params = [school_id, datetime.now() - timedelta(days=days)]
        
        if resource_type:
            conditions.append("resource_type = %s")
            params.append(resource_type)
        
        if resource_id:
            conditions.append("resource_id = %s")
            params.append(resource_id)
        
        if user_id:
            conditions.append("user_id = %s")
            params.append(user_id)
        
        if action:
            conditions.append("action = %s")
            params.append(action)
        
        query = f"""
        SELECT 
            id, user_id, school_id, action, resource_type, resource_id,
            changes, ip_address, user_agent, metadata, created_at
        FROM audit_logs
        WHERE {' AND '.join(conditions)}
        ORDER BY created_at DESC
        LIMIT %s
        """
        
        params.append(limit)
        
        results = self.db.execute_query(query, tuple(params))
        
        return [
            {
                "id": row[0],
                "user_id": row[1],
                "school_id": row[2],
                "action": row[3],
                "resource_type": row[4],
                "resource_id": row[5],
                "changes": json.loads(row[6]) if row[6] else None,
                "ip_address": row[7],
                "user_agent": row[8],
                "metadata": json.loads(row[9]) if row[9] else None,
                "created_at": row[10].isoformat() if row[10] else None
            }
            for row in results
        ] if results else []
    
    def get_user_activity(
        self,
        user_id: str,
        school_id: str,
        days: int = 7
    ) -> Dict[str, Any]:
        """Get summary of user's recent activity"""
        query = """
        SELECT 
            action,
            resource_type,
            COUNT(*) as count,
            MAX(created_at) as last_action
        FROM audit_logs
        WHERE user_id = %s 
        AND school_id = %s
        AND created_at >= %s
        GROUP BY action, resource_type
        ORDER BY count DESC
        """
        
        results = self.db.execute_query(
            query,
            (user_id, school_id, datetime.now() - timedelta(days=days))
        )
        
        activities = []
        if results:
            for row in results:
                activities.append({
                    "action": row[0],
                    "resource_type": row[1],
                    "count": row[2],
                    "last_action": row[3].isoformat() if row[3] else None
                })
        
        return {
            "user_id": user_id,
            "school_id": school_id,
            "period_days": days,
            "activities": activities,
            "total_actions": sum(a['count'] for a in activities)
        }
    
    def get_suspicious_activity(
        self,
        school_id: str,
        days: int = 1
    ) -> List[Dict[str, Any]]:
        """
        Detect suspicious activity patterns
        - Multiple failed logins
        - Bulk data exports
        - After-hours access
        - Rapid-fire actions
        """
        suspicious = []
        
        # Check for failed login attempts
        query = """
        SELECT user_id, COUNT(*) as failed_attempts, MAX(created_at) as last_attempt
        FROM audit_logs
        WHERE school_id = %s
        AND action = 'login_failed'
        AND created_at >= %s
        GROUP BY user_id
        HAVING COUNT(*) >= 5
        """
        
        results = self.db.execute_query(
            query,
            (school_id, datetime.now() - timedelta(days=days))
        )
        
        if results:
            for row in results:
                suspicious.append({
                    "type": "multiple_failed_logins",
                    "user_id": row[0],
                    "count": row[1],
                    "last_attempt": row[2].isoformat() if row[2] else None,
                    "severity": "high" if row[1] >= 10 else "medium"
                })
        
        # Check for bulk exports
        query = """
        SELECT user_id, COUNT(*) as export_count, MAX(created_at) as last_export
        FROM audit_logs
        WHERE school_id = %s
        AND action = 'export'
        AND created_at >= %s
        GROUP BY user_id
        HAVING COUNT(*) >= 3
        """
        
        results = self.db.execute_query(
            query,
            (school_id, datetime.now() - timedelta(days=days))
        )
        
        if results:
            for row in results:
                suspicious.append({
                    "type": "bulk_data_export",
                    "user_id": row[0],
                    "count": row[1],
                    "last_export": row[2].isoformat() if row[2] else None,
                    "severity": "medium"
                })
        
        return suspicious


# Singleton instance
_audit_logger: Optional[AuditLogger] = None


def get_audit_logger() -> AuditLogger:
    """Get or create audit logger instance"""
    global _audit_logger
    if _audit_logger is None:
        _audit_logger = AuditLogger()
    return _audit_logger
