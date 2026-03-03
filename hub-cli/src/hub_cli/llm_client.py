"""LLM Client for natural language processing in CLI."""

import os
import json
from typing import Any, Optional

import httpx
from pydantic import BaseModel


class LLMConfig(BaseModel):
    """LLM configuration."""
    
    provider: str = "openai"  # openai, anthropic, ollama, openrouter
    model: str = "gpt-4o-mini"
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    
    @classmethod
    def from_env(cls) -> "LLMConfig":
        """Create config from environment variables."""
        provider = os.getenv("CM_LLM_PROVIDER", "openai")
        
        config = {
            "provider": provider,
            "model": os.getenv("CM_LLM_MODEL", "gpt-4o-mini"),
        }
        
        # Get API key based on provider
        if provider == "openai":
            config["api_key"] = os.getenv("OPENAI_API_KEY")
            config["base_url"] = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
        elif provider == "anthropic":
            config["api_key"] = os.getenv("ANTHROPIC_API_KEY")
            config["base_url"] = "https://api.anthropic.com/v1"
            config["model"] = os.getenv("CM_LLM_MODEL", "claude-3-haiku-20240307")
        elif provider == "ollama":
            config["base_url"] = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1")
            config["model"] = os.getenv("CM_LLM_MODEL", "llama3.2")
        elif provider == "openrouter":
            config["api_key"] = os.getenv("OPENROUTER_API_KEY")
            config["base_url"] = "https://openrouter.ai/api/v1"
        
        return cls(**config)


class ToolCall(BaseModel):
    """Parsed tool call from LLM response."""
    
    tool_name: str
    arguments: dict[str, Any]


class LLMClient:
    """Client for interacting with LLMs to parse natural language commands."""
    
    SYSTEM_PROMPT = """You are the Context Mesh Hub CLI assistant. Your job is to parse user commands and determine which MCP tool to call.

Available tools:
- cm_help: Show available workflows and examples
- cm_status: Get project status with validation and guidance
- cm_new_project: Start a new Context Mesh project (full setup). Use for "start context new project", "init context mesh", "new project".
- cm_init: Quick minimal Context Mesh setup in current directory. Use for "quick init", "minimal setup".
- cm_list_features: List all features with status
- cm_list_decisions: List all decisions with status
- cm_add_feature: Add a new feature intent (requires: name, what, why, acceptance_criteria)
- cm_fix_bug: Document a bug (requires: title, description, impact)
- cm_create_decision: Create a technical decision (requires: number, title, context, decision, rationale)
- hub_prompts_status: Show current prompt pack (template) version. Use for "what version?", "check context version", "verify version".
- hub_prompts_install: Install a prompt pack version (requires: pack_name, version). Use after user asks to "update to latest" after checking status.

When the user gives a command, respond with a JSON object containing:
- tool_name: The MCP tool to call
- arguments: The arguments to pass to the tool (use {} when no args needed)

If you need more information from the user, respond with:
- tool_name: "ask_user"
- arguments: {"questions": ["question1", "question2"]}

Examples:

User: "start context new project" or "new project" or "init context mesh"
Response: {"tool_name": "cm_new_project", "arguments": {}}

User: "quick init" or "minimal setup"
Response: {"tool_name": "cm_init", "arguments": {}}

User: "add a feature for user authentication"
Response: {"tool_name": "cm_add_feature", "arguments": {"name": "user-auth", "what": "User authentication system", "why": "Allow users to securely access the application", "acceptance_criteria": ["Users can register", "Users can login", "Users can logout"]}}

User: "what features do we have?"
Response: {"tool_name": "cm_list_features", "arguments": {}}

User: "show me the project status"
Response: {"tool_name": "cm_status", "arguments": {}}

User: "verify if context is using the last version" or "check context version" or "what prompt pack version?"
Response: {"tool_name": "hub_prompts_status", "arguments": {}}

User: "add a feature"
Response: {"tool_name": "ask_user", "arguments": {"questions": ["What is the feature name?", "What does it do?", "Why do we need it?"]}}

Always respond with valid JSON only, no other text."""
    
    def __init__(self, config: Optional[LLMConfig] = None):
        """Initialize the LLM client.
        
        Args:
            config: LLM configuration. If None, loads from environment.
        """
        self.config = config or LLMConfig.from_env()
        self._client: Optional[httpx.AsyncClient] = None
    
    @property
    def is_configured(self) -> bool:
        """Check if LLM is configured with API key."""
        if self.config.provider == "ollama":
            return True  # Ollama doesn't need API key
        return self.config.api_key is not None
    
    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create HTTP client."""
        if self._client is None:
            self._client = httpx.AsyncClient(timeout=60.0)
        return self._client
    
    async def parse_command(self, user_input: str) -> Optional[ToolCall]:
        """Parse a natural language command into a tool call.
        
        Args:
            user_input: The user's natural language input
            
        Returns:
            ToolCall if parsing succeeded, None otherwise
        """
        if not self.is_configured:
            return None
        
        try:
            client = await self._get_client()
            
            if self.config.provider == "anthropic":
                return await self._parse_anthropic(client, user_input)
            else:
                return await self._parse_openai_compatible(client, user_input)
        except Exception as e:
            # Log error but don't crash
            print(f"LLM error: {e}")
            return None
    
    async def _parse_openai_compatible(self, client: httpx.AsyncClient, user_input: str) -> Optional[ToolCall]:
        """Parse using OpenAI-compatible API (OpenAI, Ollama, OpenRouter)."""
        headers = {"Content-Type": "application/json"}
        if self.config.api_key:
            headers["Authorization"] = f"Bearer {self.config.api_key}"
        
        response = await client.post(
            f"{self.config.base_url}/chat/completions",
            headers=headers,
            json={
                "model": self.config.model,
                "messages": [
                    {"role": "system", "content": self.SYSTEM_PROMPT},
                    {"role": "user", "content": user_input},
                ],
                "temperature": 0,
                "response_format": {"type": "json_object"},
            },
        )
        
        if response.status_code != 200:
            return None
        
        data = response.json()
        content = data["choices"][0]["message"]["content"]
        
        try:
            parsed = json.loads(content)
            return ToolCall(
                tool_name=parsed["tool_name"],
                arguments=parsed.get("arguments", {}),
            )
        except (json.JSONDecodeError, KeyError):
            return None
    
    async def _parse_anthropic(self, client: httpx.AsyncClient, user_input: str) -> Optional[ToolCall]:
        """Parse using Anthropic API."""
        response = await client.post(
            f"{self.config.base_url}/messages",
            headers={
                "Content-Type": "application/json",
                "x-api-key": self.config.api_key,
                "anthropic-version": "2023-06-01",
            },
            json={
                "model": self.config.model,
                "max_tokens": 1024,
                "system": self.SYSTEM_PROMPT,
                "messages": [
                    {"role": "user", "content": user_input},
                ],
            },
        )
        
        if response.status_code != 200:
            return None
        
        data = response.json()
        content = data["content"][0]["text"]
        
        try:
            parsed = json.loads(content)
            return ToolCall(
                tool_name=parsed["tool_name"],
                arguments=parsed.get("arguments", {}),
            )
        except (json.JSONDecodeError, KeyError):
            return None
    
    async def close(self):
        """Close the HTTP client."""
        if self._client:
            await self._client.aclose()
            self._client = None
