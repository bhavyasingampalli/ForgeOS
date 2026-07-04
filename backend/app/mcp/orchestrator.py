import asyncio
import uuid
import time
from typing import List, Dict
from app.telemetry.service import telemetry_service
from app.db.database import SessionLocal
from app.mcp.credentials import CredentialManager
from app.mcp.client import ForgeOSMCPClient

class ConnectionManager:
    def __init__(self):
        self.active_connections = []

    async def connect(self, websocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: Dict):
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                print(f"WS send error: {e}")

ws_manager = ConnectionManager()

class MCPOrchestrator:
    def __init__(self, mcp_manager):
        self.mcp_manager = mcp_manager
        
    async def execute_plan(self, plan: Dict) -> List[Dict]:
        """
        Executes the approved plan via remote MCP servers.
        Uses CredentialManager for Decryption and ProviderConfig for mapping.
        """
        results = []
        execution_id = str(uuid.uuid4())
        tasks = plan.get("tasks", [])
        
        # Mission Control: Init
        await telemetry_service.record_execution_event(
            execution_id=execution_id,
            event_type="Execution Orchestrator Initialized",
            payload={"task_count": len(tasks)}
        )
        
        db = SessionLocal()
        credential_manager = CredentialManager(db)
        
        # Generate a unique repo name for this specific execution to prevent 422 conflicts during demos
        demo_repo_name = f"ForgeOS-Demo-Repo-{execution_id[:4]}"
        
        try:
            for task in tasks:
                provider = task['platform']
                operation = task['tool']
                
                # We don't need a Capability Selected event in Mission Control
                # It clutters the UI. Just emit connecting.
                
                start_time = time.time()
                
                try:
                    # Mission Control: Connecting Provider
                    await telemetry_service.record_execution_event(
                        execution_id=execution_id,
                        event_type=f"Connecting {provider}...",
                        payload={"provider": provider}
                    )
                    
                    decrypted_credential = credential_manager.get_temporary_credential(user_id=1, provider=provider)
                    
                    # Determine friendly action name
                    action_display = operation.replace('_', ' ').title()
                    if operation == "create_repository": action_display = "Repository Created"
                    elif operation == "create_or_update_file": action_display = "README Added"
                    elif operation == "google_gmail_send": action_display = "Email Drafted"
                    elif operation == "google_drive_create": action_display = "Drive Workspace Created"
                    elif operation == "google_calendar_create": action_display = "Meeting Scheduled"

                    client = ForgeOSMCPClient(provider.lower(), decrypted_credential)
                    try:
                        await client.connect()
                        await client.initialize()
                        args = task.get('arguments', {})
                        if operation == 'create_repository':
                            if "name" not in args: args["name"] = demo_repo_name
                            if "description" not in args: args["description"] = "Created by ForgeOS Command Center"
                            if "autoInit" not in args: args["autoInit"] = True
                        elif operation == 'create_or_update_file':
                            if "owner" not in args: args["owner"] = "AguruKrishnavamsi" 
                            if "repo" not in args: args["repo"] = demo_repo_name 
                            if "path" not in args: args["path"] = "README.md"
                            if "content" not in args: args["content"] = f"# {args.get('repo', demo_repo_name)}\nThis repo was created by an AI!" 
                            if "message" not in args: args["message"] = "Initial commit"
                            if "branch" not in args: args["branch"] = "main"
                            
                        result = await client.call_tool(operation, arguments=args)
                        
                        if getattr(result, 'isError', False):
                            error_text = result.content[0].text if result.content else "Unknown error from tool"
                            raise Exception(f"Tool returned error: {error_text}")
                            
                        await client.close()
                    except Exception as client_err:
                        print(f"Error calling tool {operation} on {provider}: {client_err}")
                        if client:
                            await client.close()
                        raise client_err
                                
                    # Mission Control: Action Success
                    await telemetry_service.record_execution_event(
                        execution_id=execution_id,
                        event_type=f"{action_display}",
                        payload={"status": "success"}
                    )
                                
                    latency = (time.time() - start_time) * 1000
                    await telemetry_service.record_audit_event(
                        user_id=1, session_id="mock_session", capability="Generic", tool="GenericMCP",
                        operation=operation, execution_id=execution_id, provider=provider,
                        status="SUCCESS", latency_ms=latency
                    )
                    
                    results.append({"task_id": task["id"], "status": "COMPLETED"})
                                
                except Exception as e:
                    # Log Failure
                    latency = (time.time() - start_time) * 1000
                    await telemetry_service.record_audit_event(
                        user_id=1, session_id="mock_session", capability="Generic", tool="GenericMCP",
                        operation=operation, execution_id=execution_id, provider=provider,
                        status="FAILED", latency_ms=latency, error=str(e)
                    )
                    raise e
                    
        except Exception as e:
            await telemetry_service.record_execution_event(
                execution_id=execution_id,
                event_type="Execution Failed",
                payload={"error": str(e)}
            )
            return results
        finally:
            db.close()
            
        # Mission Control: Completed
        await telemetry_service.record_execution_event(
            execution_id=execution_id,
            event_type="Completed",
            payload={"status": "Success"}
        )
            
        return results
