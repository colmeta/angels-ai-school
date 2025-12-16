"""
Staff Agent Base Class (The "Digital Employee")
==============================================
This is the core of the "TPU" architecture.
Each Staff Agent has two modes:
1. ROUTINE (95%): Deterministic, fast, free. Uses SQL/Code.
2. CREATIVE (5%): Complex, slow, costs tokens. Uses Clarity Engine.

This ensures we fit in 512MB RAM and $10/mo budget.
"""
from typing import Any, Dict, Optional, List
from datetime import datetime
import traceback
from abc import ABC, abstractmethod

# We use the existing MCP interface for the "Creative" part
from api.core.mcp import get_mcp_client, MCPAgentRequest
from api.models.agents import AgentResponse
from api.services.database import DatabaseManager

class StaffAgent(ABC):
    def __init__(self, role: str, name: str):
        self.role = role
        self.name = name
        self.brain = get_mcp_client() # The expensive LLM connection
        # Initialize DB on demand to save connections usually, 
        # but for simplicity we can instantiate the manager (it handles pooling)
        self.db = DatabaseManager() 
        
    async def perform_task(self, task_type: str, context: Dict[str, Any]) -> AgentResponse:
        """
        The main entry point. Decides whether to use ROUTINE or CREATIVE logic.
        """
        try:
            # 1. Try Routine (Fast Path)
            result = await self.routine_logic(task_type, context)
            if result is not None:
                return AgentResponse(
                    success=True,
                    agent=f"{self.name} ({self.role})",
                    timestamp=datetime.now().isoformat(),
                    result=result,
                    error=None
                )
            
            # 2. Fallback to Creative (Slow/Expensive Path)
            # Only if routine didn't handle it
            print(f"🧠 {self.role}: Switching to Creative Mode for '{task_type}'...")
            return await self.creative_logic(task_type, context)
            
        except Exception as e:
            print(f"❌ {self.role} Error: {str(e)}")
            traceback.print_exc()
            return AgentResponse(
                success=False,
                agent=f"{self.name} ({self.role})",
                timestamp=datetime.now().isoformat(),
                result=None,
                error=str(e)
            )

    @abstractmethod
    async def routine_logic(self, task_type: str, context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Implement specialized SQL/Code logic here.
        Return None if this task requires AI.
        """
        pass

    async def creative_logic(self, task_type: str, context: Dict[str, Any]) -> AgentResponse:
        """
        Uses the Clarity Engine (MCP) to solve complex problems.
        """
        # Construct a prompt/directive for the generic engine
        directive = f"You are the {self.role} of a school. Task: {task_type}. Context: {context}"
        
        request = MCPAgentRequest(
            directive=directive,
            domain="school_management",
            context=context
        )
        
        mcp_response = self.brain.analyze(request)
        
        return AgentResponse(
            success=mcp_response.success,
            agent=f"{self.name} ({self.role}) - AI Mode",
            timestamp=datetime.now().isoformat(),
            result=mcp_response.content,
            error=None if mcp_response.success else "AI Error"
        )
