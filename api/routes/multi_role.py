"""
Multi-Role Routes
API endpoints for users with multiple roles (teacher + parent, etc.)
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

from api.services.multi_role import get_multi_role_service

router = APIRouter(tags=["Multi-Role"])


# ============================================================================
# REQUEST MODELS
# ============================================================================

class SwitchRoleRequest(BaseModel):
    school_id: str
    new_role: str


# ============================================================================
# ROLE DETECTION
# ============================================================================

@router.get("/multi-role/user/{user_id}/roles/all")
async def get_all_roles(user_id: str):
    """
    Get all roles across all schools for a user
    
    Example Response:
    {
        "user_id": "user-123",
        "schools": [
            {
                "school_id": "school-a",
                "school_name": "Angels Primary",
                "roles": ["teacher", "parent"],
                "role_count": 2
            }
        ],
        "has_multiple_roles": true
    }
    """
    try:
        service = get_multi_role_service(user_id)
        summary = service.get_user_summary()
        return summary
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/multi-role/user/{user_id}/school/{school_id}/roles")
async def get_roles_at_school(user_id: str, school_id: str):
    """
    Get all roles a user has at a specific school
    
    Example Response:
    {
        "user_id": "user-123",
        "school_id": "school-a",
        "roles": ["teacher", "parent"],
        "has_multiple_roles": true,
        "preferred_role": "teacher"
    }
    """
    try:
        service = get_multi_role_service(user_id)
        roles = service.get_roles_at_school(school_id)
        has_multiple = len(roles) > 1
        preferred = service.get_preferred_role(school_id) if has_multiple else None
        
        return {
            "user_id": user_id,
            "school_id": school_id,
            "roles": roles,
            "has_multiple_roles": has_multiple,
            "preferred_role": preferred or roles[0] if roles else None
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# ROLE SWITCHING
# ============================================================================

@router.post("/multi-role/user/{user_id}/switch-role")
async def switch_role(user_id: str, payload: SwitchRoleRequest):
    """
    Switch to a different role at the same school
    
    Example: Mr. Mukasa switches from Teacher Mode to Parent Mode
    
    Request:
    {
        "school_id": "school-123",
        "new_role": "parent"
    }
    
    Response:
    {
        "success": true,
        "new_role": "parent",
        "school_id": "school-123"
    }
    """
    try:
        service = get_multi_role_service(user_id)
        result = service.switch_role(payload.school_id, payload.new_role)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/multi-role/user/{user_id}/school/{school_id}/preferred-role")
async def get_preferred_role(user_id: str, school_id: str):
    """
    Get user's preferred role at a school
    
    Returns the last role they used, or their set preference
    """
    try:
        service = get_multi_role_service(user_id)
        preferred = service.get_preferred_role(school_id)
        
        return {
            "user_id": user_id,
            "school_id": school_id,
            "preferred_role": preferred
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# DASHBOARD DATA
# ============================================================================

@router.get("/multi-role/user/{user_id}/school/{school_id}/dashboard")
async def get_dashboard_for_role(
    user_id: str,
    school_id: str,
    role: Optional[str] = None
):
    """
    Get appropriate dashboard data based on role
    
    If role not specified, uses preferred role
    
    Example:
    GET /multi-role/user/123/school/456/dashboard?role=teacher
    → Returns teacher dashboard (classes, students, timetable)
    
    GET /multi-role/user/123/school/456/dashboard?role=parent
    → Returns parent dashboard (children, fees, notifications)
    """
    try:
        service = get_multi_role_service(user_id)
        
        # If role not specified, use preferred
        if not role:
            role = service.get_preferred_role(school_id)
        
        # Verify user has this role
        roles = service.get_roles_at_school(school_id)
        if role not in roles:
            raise HTTPException(
                status_code=403,
                detail=f"User does not have role '{role}' at this school"
            )
        
        dashboard = service.get_dashboard_for_role(school_id, role)
        return dashboard
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# EXAMPLES & DOCUMENTATION
# ============================================================================

@router.get("/multi-role/examples")
async def get_multi_role_examples():
    """Get examples of multi-role scenarios"""
    return {
        "scenario_1": {
            "description": "Teacher + Parent in SAME school",
            "example": {
                "user": "Mr. Mukasa",
                "school": "Angels Primary",
                "roles": ["teacher", "parent"],
                "children": ["Mary (Class 5)"],
                "usage": {
                    "step_1": "Login → System detects 2 roles",
                    "step_2": "Shows RoleSwitcher: Teacher Mode | Parent Mode",
                    "step_3": "Select Teacher Mode → See classes, mark attendance",
                    "step_4": "Switch to Parent Mode → See Mary's progress, pay fees"
                }
            },
            "apis": {
                "get_roles": "GET /multi-role/user/{user_id}/school/{school_id}/roles",
                "switch_role": "POST /multi-role/user/{user_id}/switch-role",
                "get_dashboard": "GET /multi-role/user/{user_id}/school/{school_id}/dashboard?role=teacher"
            }
        },
        "scenario_2": {
            "description": "Teacher + Parent in DIFFERENT schools",
            "example": {
                "user": "Mr. Mukasa",
                "schools": [
                    {
                        "name": "Angels Primary",
                        "role": "teacher"
                    },
                    {
                        "name": "St. Joseph Secondary",
                        "role": "parent",
                        "children": ["John (Form 2)"]
                    }
                ],
                "usage": {
                    "step_1": "Login → SchoolSwitcher shows 2 schools",
                    "step_2": "At Angels Primary → Automatically shows Teacher Dashboard",
                    "step_3": "At St. Joseph → Automatically shows Parent Dashboard",
                    "step_4": "No role switching needed (different roles at different schools)"
                }
            },
            "apis": {
                "get_all_roles": "GET /multi-role/user/{user_id}/roles/all",
                "switch_school": "POST /multi-school/user/{user_id}/switch-school",
                "get_dashboard": "GET /multi-role/user/{user_id}/school/{school_id}/dashboard"
            }
        },
        "usage_flow": {
            "login": {
                "step": "User logs in",
                "api": "POST /auth/login",
                "result": "JWT token + user_id"
            },
            "detect_roles": {
                "step": "Detect if user has multiple roles",
                "api": "GET /multi-role/user/{user_id}/roles/all",
                "result": {
                    "has_multiple_roles": True,
                    "schools": [
                        {
                            "school_id": "school-a",
                            "roles": ["teacher", "parent"]
                        }
                    ]
                }
            },
            "show_role_switcher": {
                "step": "If has_multiple_roles at school, show RoleSwitcher UI",
                "component": "RoleSwitcher.tsx"
            },
            "switch_role": {
                "step": "User clicks 'Parent Mode'",
                "api": "POST /multi-role/user/{user_id}/switch-role",
                "payload": {
                    "school_id": "school-a",
                    "new_role": "parent"
                }
            },
            "load_dashboard": {
                "step": "Load appropriate dashboard",
                "api": "GET /multi-role/user/{user_id}/school/{school_id}/dashboard?role=parent",
                "result": "Parent dashboard with children, fees, etc."
            }
        }
    }
