"""
Pydantic Models for AI Agents
Defines strict contracts for interacting with the 9 Angel AI Agents.
"""
from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any, Union
from enum import Enum

# ==========================================
# Generic / Shared
# ==========================================
class AgentResponse(BaseModel):
    success: bool
    agent: str
    timestamp: str
    result: Optional[Any] = None
    error: Optional[str] = None

# ==========================================
# Command Intelligence
# ==========================================
class CommandStartRequest(BaseModel):
    directive: str = Field(..., description="The natural language command (e.g., 'Analyze grade trends').")

# ==========================================
# Document Intelligence
# ==========================================
class DocumentItem(BaseModel):
    id: str
    image_data: str = Field(..., description="Base64 encoded image or URL")
    type: str = Field(default="base64", pattern="^(base64|url)$")

class DocumentBatchRequest(BaseModel):
    documents: List[DocumentItem]

# ==========================================
# Teacher Liberation
# ==========================================
class TaskType(str, Enum):
    LESSON_PLAN = "generate_lesson_plan"
    PARENT_LETTERS = "generate_parent_letters"
    GRADE_ANALYSIS = "grade_analysis"

class LessonPlanParams(BaseModel):
    subject: str
    topic: str
    class_name: str
    duration: int = 40

class ParentLetterParams(BaseModel):
    purpose: str
    student_ids: Optional[List[str]] = None

class GradeAnalysisParams(BaseModel):
    grades_data: List[Dict[str, Any]]

class AutomateTaskRequest(BaseModel):
    teacher_id: str
    task_type: TaskType
    # We use a union or generic dict here, but strictly typed above for validation 
    # if we used a discriminated union. For simplicity in this refactor keeping dict 
    # but strictly documenting usage.
    task_data: Dict[str, Any] 

# ==========================================
# Parent Engagement
# ==========================================
class ParentQueryRequest(BaseModel):
    parent_id: str
    query: str

# ==========================================
# Digital CEO (No input params usually, just context)
# ==========================================
# No specific request model needed for GET-like POSTs unless parameters are added.
