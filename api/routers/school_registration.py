"""
School Registration API
Self-service signup - no manual database work needed!
"""

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, EmailStr
import uuid
from datetime import datetime
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from services.database import get_db

router = APIRouter(prefix="/api/schools", tags=["school-registration"])

class SchoolRegistration(BaseModel):
    school_name: str
    country: str
    address: str
    phone: str
    email: EmailStr
    director_first_name: str
    director_last_name: str
    director_email: EmailStr
    director_phone: str
    student_count_estimate: int
    plan: str = "starter"  # starter, professional, enterprise

class SchoolRegistrationResponse(BaseModel):
    success: bool
    school_id: str
    admin_email: str
    temporary_password: str
    login_url: str
    message: str


@router.post("/register", response_model=SchoolRegistrationResponse)
async def register_school(registration: SchoolRegistration):
    """
    Self-service school registration
    
    Anyone can sign up a new school!
    No manual database work needed.
    """
    try:
        db = get_db()
        
        with db.get_connection() as conn:
            cursor = conn.cursor()
            
            # 1. Check if school already exists
            cursor.execute(
                "SELECT id FROM schools WHERE email = %s",
                (registration.email,)
            )
            existing = cursor.fetchone()
            
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="School with this email already registered"
                )
            
            # 2. Create school record
            school_id = str(uuid.uuid4())
            cursor.execute("""
                INSERT INTO schools (id, name, address, phone, email, created_at)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (
                school_id,
                registration.school_name,
                registration.address,
                registration.phone,
                registration.email,
                datetime.now()
            ))
            
            # 3. Create default school branding
            cursor.execute("""
                INSERT INTO school_branding (id, school_id, brand_name, primary_color, secondary_color)
                VALUES (%s, %s, %s, %s, %s)
            """, (
                str(uuid.uuid4()),
                school_id,
                registration.school_name,
                '#2563eb',  # Default blue
                '#1e40af'
            ))
            
            # 4. Create director user account
            from passlib.context import CryptContext
            pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
            
            temp_password = f"Angels{school_id[:8]}"  # Temporary password
            password_hash = pwd_context.hash(temp_password)
            
            user_id = str(uuid.uuid4())
            # FIX: Included school_id and changed is_active to status
            cursor.execute("""
                INSERT INTO users (id, school_id, email, password_hash, first_name, last_name, phone, role, status)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                user_id,
                school_id,
                registration.director_email,
                password_hash,
                registration.director_first_name,
                registration.director_last_name,
                registration.director_phone,
                'admin',  # maps to Director role
                'active'
            ))
            
            # 5. Link user to school (Crucial for RLS isolation)
            cursor.execute("""
                INSERT INTO user_schools (id, user_id, school_id, role, is_primary)
                VALUES (%s, %s, %s, %s, %s)
            """, (
                str(uuid.uuid4()),
                user_id,
                school_id,
                'director',
                True
            ))
            
            # 6. Set school plan/features
            plans = {
                "starter": ["basic_dashboard", "attendance", "fees"],
                "professional": ["basic_dashboard", "attendance", "fees", "reports", "whatsapp"],
                "enterprise": ["all_features", "white_label", "custom_domain", "priority_support"],
                "pilot": ["all_features", "white_label", "custom_domain", "priority_support", "pilot_access"]
            }
            
            for feature in plans.get(registration.plan, plans["starter"]):
                cursor.execute("""
                    INSERT INTO school_feature_flags (id, school_id, feature_name, is_enabled)
                    VALUES (%s, %s, %s, %s)
                """, (
                    str(uuid.uuid4()),
                    school_id,
                    feature,
                    True
                ))
            
            # Transaction is committed automatically by db.get_connection()
            cursor.close()
        
        # 7. Send welcome email (TODO: integrate with email service)
        # send_welcome_email(registration.director_email, temp_password)
        
        return SchoolRegistrationResponse(
            success=True,
            school_id=school_id,
            admin_email=registration.director_email,
            temporary_password=temp_password,
            login_url=f"https://angels-ai.com/login?school={school_id}",
            message=f"School '{registration.school_name}' registered successfully! Check your email for login details."
        )
    
    except HTTPException:
        raise
    except Exception as e:
        # Transaction is rolled back automatically by db.get_connection()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Registration failed: {str(e)}"
        )


@router.get("/check-availability")
async def check_school_email_availability(email: str):
    """
    Check if school email is already registered
    """
    try:
        db = get_db()
        cursor = db.cursor()
        
        cursor.execute("SELECT id FROM schools WHERE email = %s", (email,))
        exists = cursor.fetchone()
        cursor.close()
        
        return {
            "available": not bool(exists),
            "message": "Email available" if not exists else "Email already registered"
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
