import asyncio
import os
import contextlib
from typing import Dict, Any, List, Optional
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from mcp.client.sse import sse_client
import yaml

class ProviderConfigLoader:
    _cache = None

    @classmethod
    def load(cls) -> Dict[str, Any]:
        if cls._cache is None:
            config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'providers.yaml')
            if not os.path.exists(config_path):
                return {"providers": {}}
            with open(config_path, 'r') as f:
                cls._cache = yaml.safe_load(f)
        return cls._cache

    @classmethod
    def get_provider(cls, name: str) -> Optional[Dict[str, Any]]:
        registry = cls.load()
        return registry.get("providers", {}).get(name.lower())

class TransportFactory:
    @staticmethod
    @contextlib.asynccontextmanager
    async def create_session(provider_config: Dict[str, Any], access_token: str = None):
        transport = provider_config.get('transport', 'streamable_http')
        
        if transport in ['streamable_http', 'sse']:
            endpoint = provider_config.get('endpoint')
            headers = {}
            if access_token:
                headers["Authorization"] = f"Bearer {access_token}"
            
            async with sse_client(endpoint, headers=headers) as (read, write):
                async with ClientSession(read, write) as session:
                    yield session
                    
        elif transport == 'stdio':
            # Fallback for local development or reference servers
            command = provider_config.get('command', 'npx')
            args = provider_config.get('args', [])
            env = os.environ.copy()
            if access_token:
                env['GITHUB_PERSONAL_ACCESS_TOKEN'] = access_token
                
            server_params = StdioServerParameters(command=command, args=args, env=env)
            async with stdio_client(server_params) as (read, write):
                async with ClientSession(read, write) as session:
                    yield session
        else:
            raise ValueError(f"Unsupported transport: {transport}")

class ForgeOSMCPClient:
    def __init__(self, provider_name: str, access_token: str = None):
        self.provider_name = provider_name
        self.access_token = access_token
        self.config = ProviderConfigLoader.get_provider(provider_name)
        if not self.config:
            raise ValueError(f"Provider {provider_name} not found in registry")
            
        self._session_context = None
        self.session = None

    async def connect(self):
        self._session_context = TransportFactory.create_session(self.config, self.access_token)
        self.session = await self._session_context.__aenter__()

    async def initialize(self):
        if not self.session:
            raise RuntimeError("Client not connected")
        await self.session.initialize()

    async def list_tools(self) -> List[Dict[str, Any]]:
        if not self.session:
            raise RuntimeError("Client not connected")
        result = await self.session.list_tools()
        return [{"name": t.name, "description": t.description} for t in result.tools]

    async def list_resources(self) -> List[Dict[str, Any]]:
        if not self.session:
            raise RuntimeError("Client not connected")
        # Ensure fallback if server doesn't support resources
        try:
            result = await self.session.list_resources()
            return [{"uri": r.uri, "name": r.name} for r in result.resources]
        except Exception:
            return []

    async def list_prompts(self) -> List[Dict[str, Any]]:
        if not self.session:
            raise RuntimeError("Client not connected")
        try:
            result = await self.session.list_prompts()
            return [{"name": p.name, "description": p.description} for p in result.prompts]
        except Exception:
            return []

    async def call_tool(self, name: str, arguments: dict = None) -> Any:
        if not self.session:
            raise RuntimeError("Client not connected")
        return await self.session.call_tool(name, arguments or {})

    async def close(self):
        if self._session_context:
            await self._session_context.__aexit__(None, None, None)
            self._session_context = None
            self.session = None
