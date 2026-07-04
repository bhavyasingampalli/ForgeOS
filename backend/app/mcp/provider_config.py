from typing import Dict

class ProviderConfig:
    """
    Maps capability providers to the environment variables required by their respective MCP servers.
    This ensures the Orchestrator remains completely agnostic to specific providers (like GitHub).
    """
    
    # Provider Name -> { Environment Variable Name -> Internal Key }
    _ENV_MAP: Dict[str, Dict[str, str]] = {
        "GitHub": {
            "GITHUB_PERSONAL_ACCESS_TOKEN": "access_token"
        },
        "Google": {
            "GOOGLE_ACCESS_TOKEN": "access_token"
        },
        "Slack": {
            "SLACK_BOT_TOKEN": "access_token"
        }
    }

    @classmethod
    def get_environment_mapping(cls, provider: str, decrypted_credential: str) -> Dict[str, str]:
        """
        Returns the environment dictionary required to initialize an MCP server for a given provider.
        """
        provider_map = cls._ENV_MAP.get(provider, {})
        env_dict = {}
        
        for env_var, internal_key in provider_map.items():
            if internal_key == "access_token":
                env_dict[env_var] = decrypted_credential
                
        return env_dict
