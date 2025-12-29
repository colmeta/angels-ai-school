"""
Authentication Service - JWT-based authentication with session management
Fully production-ready with password hashing, token generation, and session tracking
"""
import os
import secrets
import hashlib
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, Tuple
import jwt
from passlib.context import CryptContext

from api.core.config import get_settings
from api.services.database import get_db_manager

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT settings
settings = get_settings()
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "30"))


class AuthService:
    """Complete authentication service"""
    
    def __init__(self):
        self.db = get_db_manager()
    
    # Password Operations
    def hash_password(self, password: str) -> str:
        """Hash a password using bcrypt"""
        return pwd_context.hash(password)
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash"""
        return pwd_context.verify(plain_password, hashed_password)
    
    # User Registration
    def register_user(
        self,
        email: str,
        password: str,
        first_name: str,
        last_name: str,
        school_id: Optional[str] = None,
        role: Optional[str] = None,
        phone: Optional[str] = None,
        photo_url: Optional[str] = None,
        entity_type: Optional[str] = None,
        entity_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Register a new user
        Returns: user dict or raises ValueError
        """
        # Check if email exists
        existing = self.db.execute_query(
            "SELECT id FROM users WHERE email = %s",
            (email,),
            fetch=True
        )
        if existing:
            raise ValueError("Email already registered")
        
        # Hash password
        password_hash = self.hash_password(password)
        
        # Create user
        user = self.db.execute_query(
            """
            INSERT INTO users (school_id, email, phone, password_hash, first_name, last_name, role, photo_url)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id, school_id, email, phone, first_name, last_name, role, status, created_at, photo_url
            """,
            (school_id, email, phone, password_hash, first_name, last_name, role, photo_url),
            fetch=True
        )[0]
        
        # Link to entity if provided (teacher, parent, student)
        if entity_type and entity_id:
            self.db.execute_query(
                """
                INSERT INTO user_links (user_id, entity_type, entity_id)
                VALUES (%s, %s, %s)
                """,
                (user["id"], entity_type, entity_id)
            )
        
        # Create email verification token
        verification_token = self._create_verification_token(user["id"])
        
        return {
            **user,
            "verification_token": verification_token
        }
    
    # User Login
    def login(
        self,
        email: str,
        password: str,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Authenticate user and create session
        Returns: {user, access_token, refresh_token} or raises ValueError
        """
        # Get user
        users = self.db.execute_query(
            """
            SELECT id, school_id, email, password_hash, first_name, last_name, role, status
            FROM users WHERE email = %s
            """,
            (email,),
            fetch=True
        )
        
        if not users:
            raise ValueError("Invalid email or password")
        
        user = users[0]
        
        # Check status
        if user["status"] != "active":
            raise ValueError(f"Account is {user['status']}")
        
        # Verify password
        if not self.verify_password(password, user["password_hash"]):
            raise ValueError("Invalid email or password")
        
        # Update last login
        self.db.execute_query(
            "UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = %s",
            (user["id"],)
        )
        
        # Generate tokens
        access_token, access_jti = self._create_access_token(user)
        refresh_token, refresh_jti = self._create_refresh_token(user)
        
        # Create session
        self.db.execute_query(
            """
            INSERT INTO user_sessions (user_id, token_jti, ip_address, user_agent, expires_at)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (
                user["id"],
                access_jti,
                ip_address,
                user_agent,
                datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
            )
        )
        
        # Remove password_hash from response
        del user["password_hash"]
        
        return {
            "user": user,
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60
        }
    
    # Google/Social Login
    def google_login(
        self,
        google_id: str,
        email: str,
        first_name: str,
        last_name: str,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Authenticate or register a user via Google
        """
        # 1. Check if user exists by google_id
        users = self.db.execute_query(
            """
            SELECT id, school_id, email, first_name, last_name, role, status, google_id
            FROM users WHERE google_id = %s
            """,
            (google_id,),
            fetch=True
        )
        
        user = None
        if users:
            user = users[0]
        else:
            # 2. Check if user exists by email (to link account)
            users = self.db.execute_query(
                """
                SELECT id, school_id, email, first_name, last_name, role, status, google_id
                FROM users WHERE email = %s
                """,
                (email,),
                fetch=True
            )
            
            if users:
                user = users[0]
                # Link Google ID to existing email account
                self.db.execute_query(
                    "UPDATE users SET google_id = %s, auth_provider = 'google' WHERE id = %s",
                    (google_id, user["id"])
                )
            else:
                # Auto-register personal account (no school/role initially)
                user = self.db.execute_query(
                    """
                    INSERT INTO users (email, first_name, last_name, google_id, auth_provider, email_verified)
                    VALUES (%s, %s, %s, %s, 'google', true)
                    RETURNING id, school_id, email, first_name, last_name, role, status
                    """,
                    (email, first_name, last_name, google_id),
                    fetch=True
                )[0]
        
        # Check status
        if user["status"] != "active":
            raise ValueError(f"Account is {user['status']}")
            
        # Update last login
        self.db.execute_query(
            "UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = %s",
            (user["id"],)
        )
        
        # Generate tokens
        access_token, access_jti = self._create_access_token(user)
        refresh_token, refresh_jti = self._create_refresh_token(user)
        
        # Create session
        self.db.execute_query(
            """
            INSERT INTO user_sessions (user_id, token_jti, ip_address, user_agent, expires_at)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (
                user["id"],
                access_jti,
                ip_address,
                user_agent,
                datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
            )
        )
        
        return {
            "user": user,
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60
        }
    
    # Token Operations
    def _create_access_token(self, user: Dict) -> Tuple[str, str]:
        """Create JWT access token"""
        jti = secrets.token_urlsafe(32)
        payload = {
            "sub": user["id"],
            "email": user["email"],
            "role": user["role"],
            "school_id": user["school_id"],
            "type": "access",
            "jti": jti,
            "exp": datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
            "iat": datetime.utcnow()
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
        return token, jti
    
    def _create_refresh_token(self, user: Dict) -> Tuple[str, str]:
        """Create JWT refresh token"""
        jti = secrets.token_urlsafe(32)
        payload = {
            "sub": user["id"],
            "type": "refresh",
            "jti": jti,
            "exp": datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS),
            "iat": datetime.utcnow()
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
        return token, jti
    
    def verify_token(self, token: str) -> Dict[str, Any]:
        """
        Verify and decode JWT token
        Returns: payload or raises ValueError
        """
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            
            # Check if session is revoked
            sessions = self.db.execute_query(
                "SELECT revoked FROM user_sessions WHERE token_jti = %s",
                (payload["jti"],),
                fetch=True
            )
            
            if sessions and sessions[0]["revoked"]:
                raise ValueError("Token has been revoked")
            
            return payload
            
        except jwt.ExpiredSignatureError:
            raise ValueError("Token has expired")
        except jwt.InvalidTokenError:
            raise ValueError("Invalid token")
    
    def refresh_access_token(self, refresh_token: str) -> Dict[str, Any]:
        """
        Generate new access token from refresh token
        """
        payload = self.verify_token(refresh_token)
        
        if payload["type"] != "refresh":
            raise ValueError("Invalid token type")
        
        # Get user
        users = self.db.execute_query(
            "SELECT id, school_id, email, first_name, last_name, role, status FROM users WHERE id = %s",
            (payload["sub"],),
            fetch=True
        )
        
        if not users or users[0]["status"] != "active":
            raise ValueError("User not found or inactive")
        
        user = users[0]
        
        # Generate new access token
        access_token, access_jti = self._create_access_token(user)
        
        # Create session
        self.db.execute_query(
            """
            INSERT INTO user_sessions (user_id, token_jti, expires_at)
            VALUES (%s, %s, %s)
            """,
            (
                user["id"],
                access_jti,
                datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
            )
        )
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60
        }
    
    def logout(self, token: str) -> None:
        """Revoke a session"""
        payload = self.verify_token(token)
        self.db.execute_query(
            """
            UPDATE user_sessions
            SET revoked = true, revoked_at = CURRENT_TIMESTAMP
            WHERE token_jti = %s
            """,
            (payload["jti"],)
        )
    
    def logout_all(self, user_id: str) -> None:
        """Revoke all user sessions"""
        self.db.execute_query(
            """
            UPDATE user_sessions
            SET revoked = true, revoked_at = CURRENT_TIMESTAMP
            WHERE user_id = %s AND revoked = false
            """,
            (user_id,)
        )
    
    # Password Reset
    def request_password_reset(self, email: str) -> Optional[str]:
        """
        Create password reset token
        Returns token if user exists, None otherwise
        """
        users = self.db.execute_query(
            "SELECT id FROM users WHERE email = %s",
            (email,),
            fetch=True
        )
        
        if not users:
            return None
        
        user_id = users[0]["id"]
        token = secrets.token_urlsafe(32)
        
        self.db.execute_query(
            """
            INSERT INTO password_reset_tokens (user_id, token, expires_at)
            VALUES (%s, %s, %s)
            """,
            (user_id, token, datetime.utcnow() + timedelta(hours=24))
        )
        
        return token
    
    def reset_password(self, token: str, new_password: str) -> bool:
        """
        Reset password using token
        Returns True if successful, False otherwise
        """
        tokens = self.db.execute_query(
            """
            SELECT user_id, expires_at, used
            FROM password_reset_tokens
            WHERE token = %s
            """,
            (token,),
            fetch=True
        )
        
        if not tokens:
            return False
        
        token_data = tokens[0]
        
        if token_data["used"] or datetime.now(token_data["expires_at"].tzinfo) > token_data["expires_at"]:
            return False
        
        # Update password
        password_hash = self.hash_password(new_password)
        self.db.execute_query(
            "UPDATE users SET password_hash = %s WHERE id = %s",
            (password_hash, token_data["user_id"])
        )
        
        # Mark token as used
        self.db.execute_query(
            """
            UPDATE password_reset_tokens
            SET used = true, used_at = CURRENT_TIMESTAMP
            WHERE token = %s
            """,
            (token,)
        )
        
        # Revoke all user sessions
        self.logout_all(token_data["user_id"])
        
        return True
    
    # Email Verification
    def _create_verification_token(self, user_id: str) -> str:
        """Create email verification token"""
        token = secrets.token_urlsafe(32)
        self.db.execute_query(
            """
            INSERT INTO email_verification_tokens (user_id, token, expires_at)
            VALUES (%s, %s, %s)
            """,
            (user_id, token, datetime.utcnow() + timedelta(days=7))
        )
        return token
    
    def verify_email(self, token: str) -> bool:
        """Verify email using token"""
        tokens = self.db.execute_query(
            """
            SELECT user_id, expires_at, used
            FROM email_verification_tokens
            WHERE token = %s
            """,
            (token,),
            fetch=True
        )
        
        if not tokens:
            return False
        
        token_data = tokens[0]
        
        if token_data["used"] or datetime.now(token_data["expires_at"].tzinfo) > token_data["expires_at"]:
            return False
        
        # Mark email as verified
        self.db.execute_query(
            "UPDATE users SET email_verified = true WHERE id = %s",
            (token_data["user_id"],)
        )
        
        # Mark token as used
        self.db.execute_query(
            """
            UPDATE email_verification_tokens
            SET used = true, used_at = CURRENT_TIMESTAMP
            WHERE token = %s
            """,
            (token,)
        )
        
        return True
    
    # Audit Logging
    def log_action(
        self,
        school_id: str,
        user_id: str,
        action: str,
        entity_type: Optional[str] = None,
        entity_id: Optional[str] = None,
        changes: Optional[Dict] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> None:
        """Log user action for audit trail"""
        self.db.execute_query(
            """
            INSERT INTO audit_logs (school_id, user_id, action, entity_type, entity_id, changes, ip_address, user_agent)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (school_id, user_id, action, entity_type, entity_id, changes, ip_address, user_agent)
        )


def get_auth_service() -> AuthService:
    """Helper to get auth service instance"""
    return AuthService()
