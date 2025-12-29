"""
Authentication Routes - Complete authentication system
"""
from fastapi import APIRouter, HTTPException, Depends, Header
from pydantic import BaseModel, EmailStr, Field
from typing import Optional

from api.services.auth import AuthService, get_auth_service

router = APIRouter(tags=["Authentication"])


# Request Models
class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)
    first_name: str
    last_name: str
    school_id: Optional[str] = None
    role: Optional[str] = Field(None, pattern="^(admin|teacher|parent|student|staff)$")
    phone: Optional[str] = None
    photo_url: Optional[str] = None
    entity_type: Optional[str] = None
    entity_id: Optional[str] = None


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class PasswordResetRequest(BaseModel):
    email: EmailStr


class PasswordResetConfirm(BaseModel):
    token: str
    new_password: str = Field(..., min_length=8)


class EmailVerifyRequest(BaseModel):
    token: str


# Routes
@router.post("/auth/register")
async def register(
    payload: RegisterRequest,
    auth: AuthService = Depends(get_auth_service)
):
    """Register a new user and return access tokens"""
    try:
        user = auth.register_user(
            email=payload.email,
            password=payload.password,
            first_name=payload.first_name,
            last_name=payload.last_name,
            school_id=payload.school_id,
            role=payload.role,
            phone=payload.phone,
            photo_url=payload.photo_url,
            entity_type=payload.entity_type,
            entity_id=payload.entity_id
        )
        
        # Generate tokens for immediate login
        login_result = auth.login(
            email=payload.email,
            password=payload.password
        )
        
        return {
            "success": True,
            "user_id": user["id"],
            "access_token": login_result["access_token"],
            "refresh_token": login_result["refresh_token"],
            "token_type": "bearer",
            "message": "Registration successful"
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/auth/login")
async def login(
    payload: LoginRequest,
    x_forwarded_for: Optional[str] = Header(None),
    user_agent: Optional[str] = Header(None),
    auth: AuthService = Depends(get_auth_service)
):
    """Login user and get tokens"""
    try:
        result = auth.login(
            email=payload.email,
            password=payload.password,
            ip_address=x_forwarded_for,
            user_agent=user_agent
        )
        return {
            "success": True,
            **result
        }
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/auth/refresh")
async def refresh_token(
    payload: RefreshTokenRequest,
    auth: AuthService = Depends(get_auth_service)
):
    """Refresh access token"""
    try:
        result = auth.refresh_access_token(payload.refresh_token)
        return {
            "success": True,
            **result
        }
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/auth/logout")
async def logout(
    authorization: Optional[str] = Header(None),
    auth: AuthService = Depends(get_auth_service)
):
    """Logout (revoke session)"""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid authorization header")
    
    token = authorization.replace("Bearer ", "")
    
    try:
        auth.logout(token)
        return {"success": True, "message": "Logged out successfully"}
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/auth/logout-all")
async def logout_all(
    authorization: Optional[str] = Header(None),
    auth: AuthService = Depends(get_auth_service)
):
    """Logout from all devices"""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid authorization header")
    
    token = authorization.replace("Bearer ", "")
    
    try:
        payload = auth.verify_token(token)
        auth.logout_all(payload["sub"])
        return {"success": True, "message": "Logged out from all devices"}
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/auth/password-reset/request")
async def request_password_reset(
    payload: PasswordResetRequest,
    auth: AuthService = Depends(get_auth_service)
):
    """Request password reset"""
    try:
        token = auth.request_password_reset(payload.email)
        # Always return success (don't reveal if email exists)
        return {
            "success": True,
            "message": "If the email exists, you will receive a password reset link."
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/auth/password-reset/confirm")
async def confirm_password_reset(
    payload: PasswordResetConfirm,
    auth: AuthService = Depends(get_auth_service)
):
    """Confirm password reset"""
    try:
        success = auth.reset_password(payload.token, payload.new_password)
        if not success:
            raise HTTPException(status_code=400, detail="Invalid or expired token")
        
        return {
            "success": True,
            "message": "Password reset successful. Please login with your new password."
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/auth/email/verify")
async def verify_email(
    payload: EmailVerifyRequest,
    auth: AuthService = Depends(get_auth_service)
):
    """Verify email address"""
    try:
        success = auth.verify_email(payload.token)
        if not success:
            raise HTTPException(status_code=400, detail="Invalid or expired token")
        
        return {
            "success": True,
            "message": "Email verified successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/auth/me")
async def get_current_user(
    authorization: Optional[str] = Header(None),
    auth: AuthService = Depends(get_auth_service)
):
    """Get current user info"""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid authorization header")
    
    token = authorization.replace("Bearer ", "")
    
    try:
        payload = auth.verify_token(token)
        return {
            "success": True,
            "user": {
                "id": payload["sub"],
                "email": payload["email"],
                "role": payload["role"],
                "school_id": payload["school_id"]
            }
        }
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
