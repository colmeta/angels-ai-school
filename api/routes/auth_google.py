from fastapi import APIRouter, Depends, HTTPException, status, Request
from pydantic import BaseModel
from typing import Optional
import httpx
from api.services.auth import get_auth_service, AuthService
from api.core.config import get_settings

router = APIRouter(prefix="/auth/google", tags=["Authentication"])
settings = get_settings()

class GoogleLoginRequest(BaseModel):
    token: str

@router.post("/login")
async def google_login(
    request: GoogleLoginRequest,
    req: Request,
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    Handle Google Sign-In
    1. Verify Google tokeninfo
    2. Sync user profile
    3. Generate app JWT tokens
    """
    try:
        # Verify token with Google
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"https://oauth2.googleapis.com/tokeninfo?id_token={request.token}"
            )
            
            if response.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid Google token"
                )
            
            google_data = response.json()
            
            # Basic validation
            # Check the 'aud' matches GOOGLE_CLIENT_ID to prevent token substitution attacks
            if settings.google_client_id and google_data.get("aud") != settings.google_client_id:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED, 
                    detail="Token audience mismatch"
                )

            # Log user in via AuthService
            login_result = auth_service.google_login(
                google_id=google_data["sub"],
                email=google_data["email"],
                first_name=google_data.get("given_name", ""),
                last_name=google_data.get("family_name", ""),
                ip_address=req.client.host if req.client else None,
                user_agent=req.headers.get("user-agent")
            )
            
            return login_result

    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Google authentication failed: {str(e)}"
        )
