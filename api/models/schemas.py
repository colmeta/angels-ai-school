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
    address: Optional[str] = None
    county: Optional[str] = None
    city: Optional[str] = None
    phone: Optional[str] = None

class ParentBase(BaseModel):
    first_name: str
    last_name: str
    phone: str
    email: Optional[str] = None
    whatsapp: Optional[str] = None
    relationship: str
    is_primary: bool = False
    is_fee_payer: bool = False

class EmergencyContact(BaseModel):
    name: str
    phone: str
    relationship: str

class StudentRegistrationRequest(BaseModel):
    school_id: str
    student: StudentBase
    parents: List[ParentBase]
    emergency: EmergencyContact
