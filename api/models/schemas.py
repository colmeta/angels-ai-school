"""
Pydantic Models for API
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from datetime import date, datetime

class StudentBase(BaseModel):
    first_name: str
    middle_name: Optional[str] = None
    last_name: str
    date_of_birth: str
    gender: str
    grade: str
    admission_number: Optional[str] = None
    current_class: Optional[str] = None
    admission_date: Optional[str] = None
    enrollment_status: Optional[str] = "pending"
    address: Optional[str] = None
    county: Optional[str] = None
    city: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    blood_group: Optional[str] = None
    allergies: Optional[str] = None
    medical_conditions: Optional[str] = None

class ParentBase(BaseModel):
    first_name: str
    middle_name: Optional[str] = None
    last_name: str
    gender: Optional[str] = None
    phone: str
    secondary_phone: Optional[str] = None
    email: Optional[str] = None
    whatsapp: Optional[str] = None
    relationship: str
    is_primary: bool = False
    is_fee_payer: bool = False
    preferred_language: Optional[str] = None
    occupation: Optional[str] = None
    employer: Optional[str] = None
    work_phone: Optional[str] = None
    home_address: Optional[str] = None
    county: Optional[str] = None
    city: Optional[str] = None
    preferred_contact_method: Optional[str] = "sms"
    opt_in_notifications: Optional[bool] = True

class EmergencyContact(BaseModel):
    name: str
    phone: str
    relationship: str

class StudentRegistrationRequest(BaseModel):
    school_id: str
    student: StudentBase
    parents: List[ParentBase]
    emergency: EmergencyContact
