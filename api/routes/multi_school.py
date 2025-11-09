"""
Multi-School Routes
API endpoints for cross-school access and management
"""
from fastapi import APIRouter, HTTPException, Header
from pydantic import BaseModel
from typing import Optional

from api.services.multi_school import get_multi_school_service
from api.services.auth import AuthService

router = APIRouter(tags=["Multi-School"])


# ============================================================================
# REQUEST MODELS
# ============================================================================

class LinkSchoolRequest(BaseModel):
    school_id: str
    role: str  # parent, teacher, admin, staff
    access_code: Optional[str] = None


class LinkChildRequest(BaseModel):
    child_student_id: str
    school_id: str
    relationship: str = 'parent'  # father, mother, guardian, sponsor
    is_primary: bool = False


class SwitchSchoolRequest(BaseModel):
    school_id: str


# ============================================================================
# SCHOOL ACCESS ENDPOINTS
# ============================================================================

@router.get("/multi-school/user/{user_id}/schools")
async def get_user_schools(
    user_id: str,
    authorization: Optional[str] = Header(None)
):
    """
    Get all schools a user has access to
    
    Returns list of schools with role, children count, last accessed
    """
    try:
        # Verify authentication
        if authorization and authorization.startswith("Bearer "):
            token = authorization.replace("Bearer ", "")
            auth = AuthService()
            token_data = auth.verify_token(token)
            
            # Verify user is accessing their own data or is admin
            if token_data.get("user_id") != user_id and token_data.get("role") != "admin":
                raise HTTPException(status_code=403, detail="Access denied")
        
        multi_school = get_multi_school_service(user_id)
        schools = multi_school.get_user_schools()
        
        return schools
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/multi-school/user/{user_id}/dashboard/combined")
async def get_combined_dashboard(
    user_id: str,
    authorization: Optional[str] = Header(None)
):
    """
    Get combined dashboard for all schools
    
    Shows all children, notifications, fees across all schools in one view
    Perfect for parents with children in different schools
    """
    try:
        multi_school = get_multi_school_service(user_id)
        dashboard = multi_school.get_combined_dashboard()
        
        return dashboard
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/multi-school/user/{user_id}/switch-school")
async def switch_school(
    user_id: str,
    payload: SwitchSchoolRequest,
    authorization: Optional[str] = Header(None)
):
    """
    Switch user's active school
    
    Updates last accessed time and sets as default school
    """
    try:
        multi_school = get_multi_school_service(user_id)
        result = multi_school.switch_school(payload.school_id)
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/multi-school/user/{user_id}/link-school")
async def link_school(
    user_id: str,
    payload: LinkSchoolRequest,
    authorization: Optional[str] = Header(None)
):
    """
    Link user to a new school
    
    Used when parent wants to add access to another school
    Optional access code for verification
    """
    try:
        multi_school = get_multi_school_service(user_id)
        result = multi_school.link_school(
            school_id=payload.school_id,
            role=payload.role,
            access_code=payload.access_code
        )
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/multi-school/user/{user_id}/unlink-school/{school_id}")
async def unlink_school(
    user_id: str,
    school_id: str,
    authorization: Optional[str] = Header(None)
):
    """
    Remove user's access to a school
    
    Soft delete - sets is_active to false
    """
    try:
        multi_school = get_multi_school_service(user_id)
        result = multi_school.unlink_school(school_id)
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# PARENT-CHILD MANAGEMENT (CROSS-SCHOOL)
# ============================================================================

@router.post("/multi-school/user/{user_id}/link-child")
async def link_child(
    user_id: str,
    payload: LinkChildRequest,
    authorization: Optional[str] = Header(None)
):
    """
    Link a child to parent (works across schools)
    
    Example: Parent at School A wants to link child at School B
    """
    try:
        multi_school = get_multi_school_service(user_id)
        result = multi_school.link_child(
            child_student_id=payload.child_student_id,
            school_id=payload.school_id,
            relationship=payload.relationship,
            is_primary=payload.is_primary
        )
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/multi-school/user/{user_id}/children/all")
async def get_all_children(
    user_id: str,
    authorization: Optional[str] = Header(None)
):
    """
    Get all children across all schools
    
    Returns children grouped by school
    """
    try:
        multi_school = get_multi_school_service(user_id)
        children = multi_school.get_all_children()
        
        return {
            "user_id": user_id,
            "total_children": sum(len(school['children']) for school in children),
            "schools": children
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# EXAMPLES & DOCUMENTATION
# ============================================================================

@router.get("/multi-school/examples")
async def get_multi_school_examples():
    """Get examples of multi-school scenarios"""
    return {
        "scenario_1": {
            "description": "Parent with children in same school",
            "example": {
                "parent": "Mrs. Nakato",
                "school": "Angels Primary",
                "children": ["Mary (5A)", "John (P3)", "Peter (Baby)"],
                "status": "✅ Works perfectly now",
                "api": "GET /api/{school_id}/parent/{parent_id}/dashboard"
            }
        },
        "scenario_2": {
            "description": "Teacher with multiple roles",
            "example": {
                "teacher": "Mr. Mukasa",
                "school": "Angels Primary",
                "roles": ["Teacher (Science)", "Inventory Manager"],
                "status": "✅ Works perfectly now",
                "api": "GET /api/users/{user_id}/roles"
            }
        },
        "scenario_3": {
            "description": "Parent with children in different schools",
            "example": {
                "parent": "Mrs. Nakato",
                "schools": [
                    {
                        "name": "Angels Primary",
                        "children": ["Mary (5A)"]
                    },
                    {
                        "name": "St. Joseph Secondary",
                        "children": ["John (Form 2)"]
                    }
                ],
                "status": "✅ NEW - Just built!",
                "apis": {
                    "get_schools": "GET /api/multi-school/user/{user_id}/schools",
                    "combined_view": "GET /api/multi-school/user/{user_id}/dashboard/combined",
                    "switch_school": "POST /api/multi-school/user/{user_id}/switch-school",
                    "link_school": "POST /api/multi-school/user/{user_id}/link-school"
                }
            }
        },
        "usage_flow": {
            "step_1": {
                "action": "Parent registers at School A",
                "api": "POST /api/auth/register",
                "result": "Creates user account, links to School A"
            },
            "step_2": {
                "action": "Parent enrolls child at School B",
                "api": "POST /api/multi-school/user/{user_id}/link-school",
                "payload": {
                    "school_id": "school-b-id",
                    "role": "parent",
                    "access_code": "optional-code"
                },
                "result": "User now has access to both schools"
            },
            "step_3": {
                "action": "Parent links child at School B",
                "api": "POST /api/multi-school/user/{user_id}/link-child",
                "payload": {
                    "child_student_id": "student-id",
                    "school_id": "school-b-id",
                    "relationship": "mother"
                },
                "result": "Child linked to parent across schools"
            },
            "step_4": {
                "action": "Parent views combined dashboard",
                "api": "GET /api/multi-school/user/{user_id}/dashboard/combined",
                "result": "Sees all children from all schools in one view"
            }
        }
    }
