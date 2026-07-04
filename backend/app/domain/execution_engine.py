from typing import List, Dict
from app.domain.ai_planning_engine import ExecutionIntent

class ExecutionEngine:
    def __init__(self):
        pass
        
    def generate_execution_plan(self, intent: ExecutionIntent) -> Dict:
        """
        Validates, orders, and groups tasks.
        Transforms the LLM intent into a deterministic execution plan ready for approval.
        """
        plan_tasks = []
        # Sort by dependencies or just sequence them
        # In a real system, this would map the AI's blueprint to specific MCP endpoints
        for idx, task in enumerate(intent.blueprint):
            # Extract platform guess from explicit field instead of tool_name split
            platform = getattr(task, 'platform', 'Unknown')
            
            plan_tasks.append({
                "id": idx + 1,
                "platform": platform,
                "tool": task.tool_name,
                "action": task.action_description,
                "arguments": getattr(task, 'arguments', {}),
                "status": "Queued"
            })
            
        return {
            "message": intent.message,
            "goal": intent.goal,
            "dependencies": intent.dependencies,
            "estimated_duration": intent.estimated_duration,
            "confidence": intent.confidence,
            "tasks": plan_tasks
        }
