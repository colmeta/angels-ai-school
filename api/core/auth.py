"""
Core Authentication Dependencies
Used by routers to enforce JWT authentication
"""
from fastapi import Header, HTTPException, Depends
from typing import Optional, Dict, Any
from api.services.auth import get_auth_service, AuthService

async def get_current_user(
    authorization: Optional[str] = Header(None),
    auth: AuthService = Depends(get_auth_service)
) -> Dict[str, Any]:
    """
    FastAPI dependency to protect routes with JWT.
    Extracts user info from token or raises 401.
    """
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=401, 
            detail="Missing or invalid authorization header"
        )
    
    token = authorization.replace("Bearer ", "")
    
    try:
        # Verify token and return payload
        payload = auth.verify_token(token)
        
        # Return structured user data that routes expect
        return {
            "id": payload["sub"],
            "email": payload["email"],
            "role": payload["role"],
            "school_id": payload["school_id"]
        }
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal authentication error")
