"""
Command Intelligence Routes - Natural Language Command Execution API
"""
from fastapi import APIRouter, HTTPException, Header
from pydantic import BaseModel
from typing import Optional

from api.services.command_intelligence import get_command_service
from api.services.auth import AuthService

router = APIRouter(tags=["Command Intelligence"])


class CommandRequest(BaseModel):
    command: str
    school_id: str


class BatchCommandRequest(BaseModel):
    commands: list[str]
    school_id: str


@router.post("/command/execute")
async def execute_command(
    payload: CommandRequest,
    authorization: Optional[str] = Header(None)
):
    """
    Execute a natural language command
    
    Examples:
    - "Mark John as present today"
    - "Record 85 marks for Mary in Math"
    - "John paid 50000 for school fees"
    - "Mary is sick with headache"
    - "Report incident: fight in playground"
    """
    try:
        # Get user from token (if authenticated)
        user_id = "system"
        user_role = "admin"
        
        if authorization and authorization.startswith("Bearer "):
            token = authorization.replace("Bearer ", "")
            auth = AuthService()
            try:
                token_data = auth.verify_token(token)
                user_id = token_data.get("sub")
                user_role = token_data.get("role", "admin")
            except:
                pass  # Allow unauthenticated for now
        
        # Execute command
        command_service = get_command_service(payload.school_id)
        result = await command_service.execute_command(
            command=payload.command,
            user_id=user_id,
            user_role=user_role
        )
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/command/execute-batch")
async def execute_batch_commands(
    payload: BatchCommandRequest,
    authorization: Optional[str] = Header(None)
):
    """
    Execute multiple commands in sequence
    
    Example:
    [
        "Mark John as present",
        "Mark Mary as present",
        "Record 85 marks for John in Math"
    ]
    """
    try:
        # Get user from token
        user_id = "system"
        user_role = "admin"
        
        if authorization and authorization.startswith("Bearer "):
            token = authorization.replace("Bearer ", "")
            auth = AuthService()
            try:
                token_data = auth.verify_token(token)
                user_id = token_data.get("sub")
                user_role = token_data.get("role", "admin")
            except:
                pass
        
        # Execute all commands
        command_service = get_command_service(payload.school_id)
        results = []
        
        for command in payload.commands:
            result = await command_service.execute_command(
                command=command,
                user_id=user_id,
                user_role=user_role
            )
            results.append(result)
        
        # Summary
        successful = sum(1 for r in results if r.get("success"))
        failed = len(results) - successful
        
        return {
            "success": True,
            "total_commands": len(results),
            "successful": successful,
            "failed": failed,
            "results": results
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/command/examples")
async def get_command_examples():
    """
    Get examples of supported natural language commands
    """
    return {
        "attendance_commands": [
            "Mark John as present",
            "Mark Mary as absent today",
            "John was late",
            "Mark all students present"
        ],
        "grade_commands": [
            "Record 85 marks for John in Math",
            "Mary scored 92 in English exam",
            "Give John 78 marks for Science test",
            "Record A grade for Mary"
        ],
        "payment_commands": [
            "John paid 50000 for school fees",
            "Record payment of 120000 from Mary's parent",
            "Mark 30000 payment for John"
        ],
        "health_commands": [
            "Mary is sick with headache",
            "John visited sickbay with fever",
            "Record health visit for Mary"
        ],
        "incident_commands": [
            "Report incident: fight in playground",
            "Create incident report for broken window",
            "John reported damage to classroom door"
        ],
        "message_commands": [
            "Send message 'School closes early tomorrow'",
            "Notify parents about sports day",
            "Tell teachers about staff meeting"
        ],
        "tips": [
            "Use student first name or full name",
            "Be specific with numbers (marks, amounts)",
            "Mention dates if not today (e.g., 'yesterday', 'last Friday')",
            "Include context (subject, reason, description)"
        ]
    }


@router.get("/command/supported-intents")
async def get_supported_intents():
    """
    Get list of supported command intents and required permissions
    """
    return {
        "intents": {
            "mark_attendance": {
                "description": "Mark student attendance (present/absent/late)",
                "permissions": ["teacher", "admin"],
                "examples": ["Mark John as present", "John was absent yesterday"]
            },
            "record_grade": {
                "description": "Record student grades/marks",
                "permissions": ["teacher", "admin"],
                "examples": ["Record 85 marks for Mary in Math", "John scored A in English"]
            },
            "record_payment": {
                "description": "Record fee payments",
                "permissions": ["admin", "staff"],
                "examples": ["John paid 50000 for fees", "Record payment of 120000"]
            },
            "record_health_visit": {
                "description": "Record sickbay/health visits",
                "permissions": ["staff", "admin"],
                "examples": ["Mary is sick with fever", "John visited sickbay"]
            },
            "create_incident": {
                "description": "Create incident reports",
                "permissions": ["teacher", "admin", "staff"],
                "examples": ["Report incident: fight in playground", "Create incident for damage"]
            },
            "send_message": {
                "description": "Send messages/notifications",
                "permissions": ["teacher", "admin"],
                "examples": ["Send message 'School closes early'", "Notify parents"]
            },
            "manage_inventory": {
                "description": "Manage inventory items",
                "permissions": ["staff", "admin"],
                "examples": ["Add 10 notebooks to inventory", "Remove 5 chairs"]
            }
        }
    }
