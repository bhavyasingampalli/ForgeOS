from typing import List, Dict
from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import PydanticOutputParser
from app.utils.config import settings
from typing import Any

class ExecutionBlueprintItem(BaseModel):
    platform: str = Field(description="The provider platform (e.g., 'Github', 'Google')")
    tool_name: str = Field(description="The exact capability name from the Capability Registry")
    action_description: str = Field(description="Detailed execution step")
    arguments: Dict[str, Any] = Field(default_factory=dict, description="JSON object containing required tool arguments extracted from user prompt")

class ExecutionIntent(BaseModel):
    message: str = Field(description="A friendly response to the user. Use this to answer questions or explain the plan.")
    goal: str = Field(description="High-level description of what we are trying to achieve. Leave empty if just answering a question.")
    capabilities_needed: List[str] = Field(description="List of capability names required")
    dependencies: List[str] = Field(description="List of prerequisites or dependencies")
    blueprint: List[ExecutionBlueprintItem] = Field(description="The structured execution blueprint steps. Leave empty if just answering a question.")
    estimated_duration: str = Field(description="Estimated time to complete (e.g., '10 seconds', '2 minutes')")
    confidence: int = Field(description="Confidence score from 0 to 100 on how accurately this plan addresses the request")

class AIPlanningEngine:
    def __init__(self):
        self.parser = PydanticOutputParser(pydantic_object=ExecutionIntent)
        self.llm = None
        
        # Determine which LLM to use, prioritizing Gemini
        if settings.GEMINI_API_KEY and settings.GEMINI_API_KEY != "mock":
            try:
                from langchain_google_genai import ChatGoogleGenerativeAI
                self.llm = ChatGoogleGenerativeAI(
                    model="gemini-2.5-flash",
                    google_api_key=settings.GEMINI_API_KEY,
                    temperature=0,
                    max_retries=0
                )
            except ImportError:
                print("langchain_google_genai not installed. Falling back to deterministic rules.")
        elif settings.OPENAI_API_KEY and settings.OPENAI_API_KEY != "mock":
            try:
                from langchain_openai import ChatOpenAI
                self.llm = ChatOpenAI(
                    model="gpt-4o-mini",
                    openai_api_key=settings.OPENAI_API_KEY,
                    temperature=0
                )
            except ImportError:
                print("langchain_openai not installed. Falling back to deterministic rules.")

    def generate_plan(self, user_request: str, available_capabilities: List[Dict], chat_history: List = None) -> ExecutionIntent:
        if self.llm:
            return self._llm_generate_plan(user_request, available_capabilities, chat_history or [])
        else:
            return self._fallback_generate_plan(user_request, available_capabilities)
            
    def _llm_generate_plan(self, user_request: str, available_capabilities: List[Dict], chat_history: List) -> ExecutionIntent:
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are the AI Planning Engine for ForgeOS, an AI Operating System for Knowledge Work.
Your goal is to orchestrate complex, cross-platform workflows by mapping user intent to the available capabilities in their workspace.

### CRITICAL RULES FOR INTENT DETECTION:
1. ACTION GOALS: If the user gives a goal to execute or create something (e.g., "Create a new project", "Schedule a bug fix meeting"), you MUST generate a comprehensive Execution Blueprint. Break the goal down into logical steps across different platforms and go step by step.
2. CONVERSATIONAL QUESTIONS: If the user is just asking a question (e.g., "what are the list of tools", "how does this work?"), YOU MUST LEAVE THE BLUEPRINT ARRAY COMPLETELY EMPTY (`[]`). DO NOT generate any tasks. Instead, answer their question naturally in the `message` field based on the conversation history.
3. OUTPUT FORMAT: YOU MUST ALWAYS RETURN VALID JSON MATCHING THE SCHEMA. NEVER return plain text, markdown blocks, or conversational greetings outside of the JSON structure. Even if you are just answering a simple question, wrap your reply inside the `message` field of the JSON object.

Available Capabilities in the Workspace:
{available_capabilities}

If a required capability is not in the list, ignore that part of the request.
Output your execution plan exactly in the following JSON format:
{format_instructions}
"""),
            MessagesPlaceholder(variable_name="chat_history"),
            ("user", "{user_request}")
        ])
        
        chain = prompt | self.llm | self.parser
        
        try:
            return chain.invoke({
                "available_capabilities": str(available_capabilities),
                "user_request": user_request,
                "chat_history": chat_history,
                "format_instructions": self.parser.get_format_instructions()
            })
        except Exception as e:
            print(f"LLM Planning failed: {e}. Falling back to rules engine.")
            return self._fallback_generate_plan(user_request, available_capabilities)
            
    def _fallback_generate_plan(self, user_request: str, available_capabilities: List[Dict]) -> ExecutionIntent:
        """
        Deterministic fallback engine used when no API key is provided or the LLM fails.
        Provides a highly realistic mock execution plan by scanning keywords.
        """
        req_lower = user_request.lower()
        blueprint = []
        capabilities = []
        dependencies = []
        
        # GitHub Logic
        import re
        repo_name = "ForgeOS-Demo-Repo"
        match = re.search(r'(?:repo|repository)\s+(?:called|named)\s+([a-zA-Z0-9_-]+)', req_lower)
        if match:
            repo_name = match.group(1)
            
        if "repo" in req_lower or "project" in req_lower:
            blueprint.append(ExecutionBlueprintItem(
                platform="Github",
                tool_name="create_repository",
                action_description=f"Create GitHub Repository '{repo_name}'",
                arguments={"name": repo_name, "description": "Created by ForgeOS"}
            ))
            capabilities.append("create_repository")
            
        if "readme" in req_lower or "setup" in req_lower:
            blueprint.append(ExecutionBlueprintItem(
                platform="Github",
                tool_name="create_or_update_file",
                action_description="Initialize the README.md file",
                arguments={"repo": repo_name, "path": "README.md"}
            ))
            capabilities.append("create_or_update_file")
            dependencies.append("create_repository")
            
        # Google Workspace Logic
        if "email" in req_lower or "team" in req_lower:
            blueprint.append(ExecutionBlueprintItem(
                platform="Google",
                tool_name="google_gmail_send",
                action_description="Draft and send project initialization email to the team"
            ))
            capabilities.append("google_gmail_send")
            
        if "drive" in req_lower or "folder" in req_lower:
            blueprint.append(ExecutionBlueprintItem(
                platform="Google",
                tool_name="google_drive_create",
                action_description="Create a Google Drive workspace folder"
            ))
            capabilities.append("google_drive_create")
            
        if "calendar" in req_lower or "meeting" in req_lower:
            blueprint.append(ExecutionBlueprintItem(
                platform="Google",
                tool_name="google_calendar_create",
                action_description="Schedule a kickoff meeting"
            ))
            capabilities.append("google_calendar_create")
            

        return ExecutionIntent(
            message="Here is the execution blueprint for your request." if blueprint else "Hello! I am ForgeOS. How can I help you orchestrate your workspace today?",
            goal=user_request[:50] + "..." if len(user_request) > 50 else user_request,
            capabilities_needed=capabilities,
            dependencies=dependencies,
            blueprint=blueprint,
            estimated_duration=f"{len(blueprint) * 2} seconds",
            confidence=96
        )
