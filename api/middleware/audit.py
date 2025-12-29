"""
Audit Logging Middleware
========================
Intercepts all sensitive write operations and logs them for security auditing.
Tracks: Who, What, When, Where (IP), and Payload.
"""

import time
import json
import logging
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.background import BackgroundTask

logger = logging.getLogger("angels.audit")

class AuditMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Skip read operations and public paths
        if request.method in ["GET", "OPTIONS"] or request.url.path.startswith(("/static", "/docs", "/openapi")):
            return await call_next(request)

        start_time = time.time()
        
        # Read request body (and restore it for the app)
        request_body = b""
        try:
            request_body = await request.body()
        except Exception:
            pass

        # Process the request
        response = await call_next(request)
        
        # Calculate duration
        duration_ms = (time.time() - start_time) * 1000
        
        # Log asynchronously in background
        response.background = BackgroundTask(
            self._log_audit_event,
            request=request,
            method=request.method,
            path=request.url.path,
            status_code=response.status_code,
            duration_ms=duration_ms,
            body=request_body
        )
        
        return response

    async def _log_audit_event(
        self, 
        request: Request, 
        method: str, 
        path: str, 
        status_code: int, 
        duration_ms: float,
        body: bytes
    ):
        """Write audit log entry (to file or DB)."""
        
        # Identify user
        user_id = getattr(request.state, "user_id", "anonymous")
        ip = request.client.host if request.client else "unknown"
        
        # Sanitize sensitive fields in payload
        payload_preview = "binary/empty"
        if body and len(body) < 2000: # Limit size
            try:
                data = json.loads(body)
                if "password" in data: data["password"] = "***"
                if "token" in data: data["token"] = "***"
                payload_preview = json.dumps(data)
            except:
                payload_preview = "raw-data"

        log_entry = (
            f"AUDIT | {time.strftime('%Y-%m-%d %H:%M:%S')} | "
            f"User:{user_id} | IP:{ip} | {method} {path} | "
            f"{status_code} | {duration_ms:.2f}ms | Payload: {payload_preview}"
        )
        
        # For now, log to system logger (can be piped to ELK/Datadog)
        logger.info(log_entry)
