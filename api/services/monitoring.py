"""
Production Monitoring Service
Health checks, metrics, and alerting
"""
import os
import time
from typing import Dict, Any, Optional
from datetime import datetime
import httpx
import psycopg2

from api.core.config import get_settings


class MonitoringService:
    """
    Production monitoring and health checks
    - Database connectivity
    - External API status (Clarity, Mobile Money, etc.)
    - System metrics
    - Performance tracking
    """
    
    def __init__(self):
        self.settings = get_settings()
        self.start_time = time.time()
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Comprehensive health check
        Returns status of all critical services
        """
        checks = {
            "timestamp": datetime.now().isoformat(),
            "uptime_seconds": int(time.time() - self.start_time),
            "status": "healthy",
            "checks": {}
        }
        
        # Check database
        db_status = self._check_database()
        checks["checks"]["database"] = db_status
        
        # Check Clarity API
        clarity_status = await self._check_clarity_api()
        checks["checks"]["clarity_api"] = clarity_status
        
        # Check disk space (if available)
        disk_status = self._check_disk_space()
        if disk_status:
            checks["checks"]["disk"] = disk_status
        
        # Overall status
        if not db_status["healthy"]:
            checks["status"] = "unhealthy"
        elif not clarity_status["healthy"]:
            checks["status"] = "degraded"
        
        return checks
    
    def _check_database(self) -> Dict[str, Any]:
        """Check database connectivity and response time"""
        start = time.time()
        
        try:
            conn = psycopg2.connect(self.settings.database_url)
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            cursor.close()
            conn.close()
            
            response_time = (time.time() - start) * 1000  # ms
            
            return {
                "healthy": True,
                "response_time_ms": round(response_time, 2),
                "status": "connected"
            }
        except Exception as e:
            return {
                "healthy": False,
                "error": str(e),
                "status": "disconnected"
            }
    
    async def _check_clarity_api(self) -> Dict[str, Any]:
        """Check Clarity API availability"""
        start = time.time()
        
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(
                    "https://veritas-engine-zae0.onrender.com/instant/health"
                )
                
                response_time = (time.time() - start) * 1000  # ms
                
                if response.status_code == 200:
                    return {
                        "healthy": True,
                        "response_time_ms": round(response_time, 2),
                        "status": "available"
                    }
                else:
                    return {
                        "healthy": False,
                        "status_code": response.status_code,
                        "status": "degraded"
                    }
        except httpx.TimeoutException:
            return {
                "healthy": False,
                "error": "timeout",
                "status": "timeout"
            }
        except Exception as e:
            return {
                "healthy": False,
                "error": str(e),
                "status": "unavailable"
            }
    
    def _check_disk_space(self) -> Optional[Dict[str, Any]]:
        """Check available disk space"""
        try:
            import shutil
            stat = shutil.disk_usage("/")
            
            total_gb = stat.total / (1024**3)
            used_gb = stat.used / (1024**3)
            free_gb = stat.free / (1024**3)
            percent_used = (stat.used / stat.total) * 100
            
            return {
                "healthy": percent_used < 90,
                "total_gb": round(total_gb, 2),
                "used_gb": round(used_gb, 2),
                "free_gb": round(free_gb, 2),
                "percent_used": round(percent_used, 2)
            }
        except Exception:
            return None
    
    def get_metrics(self) -> Dict[str, Any]:
        """
        Get application metrics
        - Uptime
        - Request count (if tracked)
        - Error rate
        """
        return {
            "uptime_seconds": int(time.time() - self.start_time),
            "uptime_hours": round((time.time() - self.start_time) / 3600, 2),
            "start_time": datetime.fromtimestamp(self.start_time).isoformat(),
            "current_time": datetime.now().isoformat()
        }
    
    async def send_alert(
        self,
        alert_type: str,
        message: str,
        severity: str = "high"
    ):
        """
        Send alert (email, SMS, Slack, etc.)
        
        Args:
            alert_type: database_down, api_error, etc.
            message: Alert message
            severity: low, medium, high, critical
        """
        # TODO: Integrate with notification service
        print(f"🚨 ALERT [{severity}]: {alert_type} - {message}")
        
        # In production, send to Sentry, PagerDuty, etc.
        # if os.getenv('SENTRY_DSN'):
        #     sentry_sdk.capture_message(message, level=severity)


# Singleton instance
_monitoring_service: Optional[MonitoringService] = None


def get_monitoring_service() -> MonitoringService:
    """Get or create monitoring service instance"""
    global _monitoring_service
    if _monitoring_service is None:
        _monitoring_service = MonitoringService()
    return _monitoring_service
