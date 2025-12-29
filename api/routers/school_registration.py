"""
School Registration API
Self-service signup - no manual database work needed!
"""

from typing import Optional
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
    student_count_estimate: int
    plan: str = "starter"  # starter, professional, enterprise
    creator_user_id: Optional[str] = None # Linking the creator if logged in

class SchoolRegistrationResponse(BaseModel):
    success: bool
    school_id: str
    school_code: str
    message: str


import random
import string

def generate_school_code(length=8):
    """Generate a readable 8-character code (ABCD-1234 format)"""
    chars = string.ascii_uppercase
    nums = string.digits
    part1 = ''.join(random.choice(chars) for _ in range(4))
    part2 = ''.join(random.choice(nums) for _ in range(4))
    return f"{part1}-{part2}"

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
            
            # 2. Create school record with unique code
            school_id = str(uuid.uuid4())
            
            # Generate unique code with retry logic
            school_code = generate_school_code()
            for _ in range(5):
                cursor.execute("SELECT id FROM schools WHERE school_code = %s", (school_code,))
                if not cursor.fetchone():
                    break
                school_code = generate_school_code()

            cursor.execute("""
                INSERT INTO schools (id, name, address, phone, email, school_code, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (
                school_id,
                registration.school_name,
                registration.address,
                registration.phone,
                registration.email,
                school_code,
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
            
            # 4. Link creator if provided
            if registration.creator_user_id:
                cursor.execute("""
                    INSERT INTO user_school_roles (user_id, school_id, role, status, is_primary)
                    VALUES (%s, %s, %s, %s, %s)
                """, (
                    registration.creator_user_id,
                    school_id,
                    'director',
                    'active',
                    True
                ))
            
            # 6. Set school plan/features (100% Free - All Features Enabled)
            all_features = [
                "basic_dashboard", "attendance", "fees", "reports", "whatsapp",
                "all_features", "white_label", "custom_domain", "priority_support", 
                "pilot_access", "ai_magic_box", "universal_import"
            ]
            
            for feature in all_features:
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
            school_code=school_code,
            message=f"School '{registration.school_name}' registered successfully! Your school code is {school_code}."
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
