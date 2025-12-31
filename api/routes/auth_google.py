from fastapi import APIRouter, Depends, HTTPException, status, Request
from pydantic import BaseModel
from typing import Optional
import httpx
from api.services.auth import get_auth_service, AuthService
from api.core.config import get_settings

router = APIRouter(prefix="/auth/google", tags=["Authentication"])
settings = get_settings()

class GoogleLoginRequest(BaseModel):
    token: Optional[str] = None
    credential: Optional[str] = None

    def get_token(self) -> str:
        t = self.token or self.credential
        if not t:
            from fastapi import HTTPException
            raise HTTPException(status_code=400, detail="token or credential is required")
        return t

class GoogleRegisterRequest(GoogleLoginRequest):
    phone: str

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
            token = request.get_token()
            response = await client.get(
                f"https://oauth2.googleapis.com/tokeninfo?id_token={token}"
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

@router.post("/register")
async def google_register(
    request: GoogleRegisterRequest,
    req: Request,
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    Handle Google Sign-Up with phone number
    1. Verify Google credential 
    2. Register user with phone
    3. Generate app JWT tokens
    """
    try:
        # Verify token with Google
        async with httpx.AsyncClient() as client:
            token = request.get_token()
            response = await client.get(
                f"https://oauth2.googleapis.com/tokeninfo?id_token={token}"
            )
            
            if response.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid Google token"
                )
            
            google_data = response.json()
            
            # Validate token audience
            if settings.google_client_id and google_data.get("aud") != settings.google_client_id:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token audience mismatch"
                )

            # Log user in (auto-registers if new) via AuthService
            login_result = auth_service.google_login(
                google_id=google_data["sub"],
                email=google_data["email"],
                first_name=google_data.get("given_name", ""),
                last_name=google_data.get("family_name", ""),
                ip_address=req.client.host if req.client else None,
                user_agent=req.headers.get("user-agent")
            )
            
            # Update phone number after registration
            from api.services.database import get_db_manager
            db = get_db_manager()
            db.execute_query(
                "UPDATE users SET phone = %s WHERE id = %s",
                (request.phone, login_result["user"]["id"]),
                fetch=False
            )
            
            return login_result

    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Google registration failed: {str(e)}"
        )
