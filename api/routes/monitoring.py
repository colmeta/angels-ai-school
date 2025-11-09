"""
Monitoring and Health Check Endpoints
Production monitoring, metrics, and alerts
"""
from fastapi import APIRouter, HTTPException
from typing import Dict, Any

from api.services.monitoring import get_monitoring_service
from api.services.audit import get_audit_logger


router = APIRouter(tags=["Monitoring"])


@router.get("/health")
async def health_check() -> Dict[str, Any]:
    """
    **Production Health Check**
    
    Returns status of all critical services:
    - Database connectivity
    - Clarity API availability
    - Disk space
    - Overall system health
    
    Use this for:
    - Load balancer health checks
    - Uptime monitoring (UptimeRobot, Pingdom)
    - CI/CD deployment verification
    """
    monitoring = get_monitoring_service()
    return await monitoring.health_check()


@router.get("/health/simple")
async def simple_health() -> Dict[str, str]:
    """
    Simple health check for load balancers
    Returns 200 OK if service is running
    """
    return {"status": "ok"}


@router.get("/metrics")
async def get_metrics() -> Dict[str, Any]:
    """
    **Application Metrics**
    
    Returns:
    - Uptime
    - Start time
    - Current time
    
    Future: Request count, error rate, response times
    """
    monitoring = get_monitoring_service()
    return monitoring.get_metrics()


@router.get("/audit/recent")
async def get_recent_audit_logs(
    school_id: str,
    limit: int = 20
) -> Dict[str, Any]:
    """
    Get recent audit logs for a school
    
    Requires authentication in production
    """
    audit = get_audit_logger()
    
    logs = audit.get_audit_trail(
        school_id=school_id,
        limit=limit
    )
    
    return {
        "success": True,
        "school_id": school_id,
        "logs": logs,
        "total": len(logs)
    }


@router.get("/audit/suspicious")
async def get_suspicious_activity(
    school_id: str
) -> Dict[str, Any]:
    """
    Get suspicious activity for security monitoring
    
    Detects:
    - Multiple failed logins
    - Bulk data exports
    - Unusual access patterns
    """
    audit = get_audit_logger()
    
    suspicious = audit.get_suspicious_activity(
        school_id=school_id,
        days=1
    )
    
    return {
        "success": True,
        "school_id": school_id,
        "suspicious_activities": suspicious,
        "total": len(suspicious),
        "requires_attention": len([s for s in suspicious if s.get('severity') == 'high']) > 0
    }


@router.get("/audit/user/{user_id}")
async def get_user_activity(
    user_id: str,
    school_id: str,
    days: int = 7
) -> Dict[str, Any]:
    """
    Get user activity summary
    
    Shows what a user has been doing:
    - Logins
    - Data changes
    - Exports
    - Views
    """
    audit = get_audit_logger()
    
    activity = audit.get_user_activity(
        user_id=user_id,
        school_id=school_id,
        days=days
    )
    
    return {
        "success": True,
        **activity
    }
