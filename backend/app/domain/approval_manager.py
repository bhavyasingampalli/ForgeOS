from typing import List, Dict

class ApprovalManager:
    def __init__(self):
        # In a real system, this might store pending executions in DB/Redis
        self.pending_approvals = {}

    def request_approval(self, session_id: str, execution_plan: Dict):
        """
        Stores the plan and returns a preview object for the frontend
        """
        self.pending_approvals[session_id] = execution_plan
        
        # Calculate estimated duration (mock logic)
        estimated_seconds = len(execution_plan.get("tasks", [])) * 3
        
        return {
            "session_id": session_id,
            "status": "pending_approval",
            "plan": execution_plan,
            "estimated_duration_seconds": estimated_seconds
        }
        
    def approve(self, session_id: str) -> Dict:
        """
        Retrieves the plan for execution
        """
        return self.pending_approvals.pop(session_id, {})
