"""Agent detection and integration for CLI.

Detects and uses external AI agents (Gemini CLI, Codex, Claude, etc.)
so the CLI doesn't need its own API key.
"""

import asyncio
import json
import shutil
import subprocess
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Optional


class AgentType(str, Enum):
    """Supported AI agent types."""
    
    GEMINI_CLI = "gemini"
    CODEX_CLI = "codex"
    CLAUDE_CLI = "claude"
    CURSOR_CLI = "cursor"  # IDE with MCP support, not a chat CLI
    AIDER = "aider"
    OPENAI_CLI = "openai"
    OLLAMA = "ollama"
    # API-based (fallback)
    OPENAI_API = "openai-api"
    ANTHROPIC_API = "anthropic-api"


# Agents that support direct chat via CLI (can receive prompts and return responses)
CHAT_CAPABLE_AGENTS = {
    AgentType.GEMINI_CLI,
    AgentType.CODEX_CLI,
    AgentType.CLAUDE_CLI,
    AgentType.AIDER,
    AgentType.OLLAMA,
}

# IDE agents - have MCP support but don't work as chat CLIs
IDE_AGENTS = {
    AgentType.CURSOR_CLI,
}


def is_chat_capable(agent_type: AgentType) -> bool:
    """Check if agent type supports direct CLI chat."""
    return agent_type in CHAT_CAPABLE_AGENTS


def is_ide_agent(agent_type: AgentType) -> bool:
    """Check if agent is an IDE (has MCP but no CLI chat)."""
    return agent_type in IDE_AGENTS


@dataclass
class AgentInfo:
    """Information about an AI agent (for installation help)."""
    
    type: AgentType
    display_name: str
    install_command: Optional[str]
    install_url: str
    description: str


# Agent installation information
AGENT_INFO: dict[AgentType, AgentInfo] = {
    # === TERMINAL CHAT CLIs (can send prompts, get responses) ===
    AgentType.GEMINI_CLI: AgentInfo(
        type=AgentType.GEMINI_CLI,
        display_name="Google Gemini CLI",
        install_command="npm install -g @anthropic-ai/gemini-cli",
        install_url="https://github.com/google-gemini/gemini-cli",
        description="Google's Gemini AI in your terminal (FREE)",
    ),
    AgentType.CLAUDE_CLI: AgentInfo(
        type=AgentType.CLAUDE_CLI,
        display_name="Claude Code",
        install_command="npm install -g @anthropic-ai/claude-code",
        install_url="https://docs.anthropic.com/en/docs/claude-code",
        description="Claude AI coding assistant in your terminal",
    ),
    # === IDEs with MCP SUPPORT (use MCP in editor, not terminal chat) ===
    AgentType.CURSOR_CLI: AgentInfo(
        type=AgentType.CURSOR_CLI,
        display_name="Cursor",
        install_command="curl -fsSL https://cursor.com/install | bash",
        install_url="https://www.cursor.com/",
        description="AI code editor - use MCP directly in editor",
    ),
    # === OTHER (lower priority) ===
    AgentType.CODEX_CLI: AgentInfo(
        type=AgentType.CODEX_CLI,
        display_name="OpenAI Codex CLI",
        install_command="npm install -g @openai/codex",
        install_url="https://github.com/openai/codex",
        description="OpenAI's coding assistant CLI",
    ),
    AgentType.AIDER: AgentInfo(
        type=AgentType.AIDER,
        display_name="Aider",
        install_command="pip install aider-chat",
        install_url="https://aider.chat/",
        description="AI pair programming in your terminal",
    ),
    AgentType.OLLAMA: AgentInfo(
        type=AgentType.OLLAMA,
        display_name="Ollama (local)",
        install_command="curl -fsSL https://ollama.com/install.sh | sh",
        install_url="https://ollama.com/",
        description="Run LLMs locally - no API key, no cloud",
    ),
    AgentType.OPENAI_CLI: AgentInfo(
        type=AgentType.OPENAI_CLI,
        display_name="OpenAI CLI",
        install_command="pip install openai",
        install_url="https://platform.openai.com/docs/quickstart",
        description="OpenAI's official CLI (requires API key)",
    ),
}


def get_agent_info(agent_type: AgentType) -> Optional[AgentInfo]:
    """Get installation info for an agent type."""
    return AGENT_INFO.get(agent_type)


@dataclass
class Agent:
    """Detected AI agent."""
    
    type: AgentType
    name: str
    command: str
    version: Optional[str] = None
    path: Optional[str] = None
    requires_api_key: bool = False
    
    @property
    def display_name(self) -> str:
        """Human-readable name."""
        info = get_agent_info(self.type)
        if info:
            return info.display_name
        return self.name
    
    @property
    def info(self) -> Optional[AgentInfo]:
        """Get installation info."""
        return get_agent_info(self.type)


# Agent detection configurations
AGENT_CONFIGS = [
    {
        "type": AgentType.GEMINI_CLI,
        "commands": ["gemini"],
        "version_flag": "--version",
        "requires_api_key": False,
    },
    {
        "type": AgentType.CODEX_CLI,
        "commands": ["codex"],
        "version_flag": "--version",
        "requires_api_key": False,
    },
    {
        "type": AgentType.CLAUDE_CLI,
        "commands": ["claude"],
        "version_flag": "--version",
        "requires_api_key": False,
    },
    {
        "type": AgentType.CURSOR_CLI,
        "commands": ["cursor"],
        "version_flag": "--version",
        "requires_api_key": False,
    },
    {
        "type": AgentType.AIDER,
        "commands": ["aider"],
        "version_flag": "--version",
        "requires_api_key": False,  # Uses user's configured API
    },
    {
        "type": AgentType.OPENAI_CLI,
        "commands": ["openai"],
        "version_flag": "--version",
        "requires_api_key": True,
    },
    {
        "type": AgentType.OLLAMA,
        "commands": ["ollama"],
        "version_flag": "--version",
        "requires_api_key": False,
    },
]


def detect_agent(agent_type: AgentType) -> Optional[Agent]:
    """Detect a specific agent."""
    for config in AGENT_CONFIGS:
        if config["type"] == agent_type:
            for cmd in config["commands"]:
                path = shutil.which(cmd)
                if path:
                    # Try to get version
                    version = None
                    try:
                        result = subprocess.run(
                            [cmd, config["version_flag"]],
                            capture_output=True,
                            text=True,
                            timeout=5,
                        )
                        if result.returncode == 0:
                            version = result.stdout.strip().split("\n")[0]
                    except Exception:
                        pass
                    
                    return Agent(
                        type=agent_type,
                        name=cmd,
                        command=cmd,
                        version=version,
                        path=path,
                        requires_api_key=config["requires_api_key"],
                    )
    return None


def detect_all_agents() -> list[Agent]:
    """Detect all available AI agents."""
    agents = []
    
    for config in AGENT_CONFIGS:
        agent = detect_agent(config["type"])
        if agent:
            agents.append(agent)
    
    return agents


def get_preferred_agent(agents: list[Agent], for_chat: bool = False) -> Optional[Agent]:
    """Get the preferred agent from a list.
    
    Args:
        agents: List of detected agents
        for_chat: If True, only consider chat-capable agents (excludes IDEs like Cursor)
    """
    candidates = agents
    
    if for_chat:
        # Filter to only chat-capable agents
        candidates = [a for a in agents if is_chat_capable(a.type)]
    
    # Prefer agents that don't require API key
    for agent in candidates:
        if not agent.requires_api_key:
            return agent
    
    # Fall back to any agent in candidates
    return candidates[0] if candidates else None


def get_chat_capable_agents(agents: list[Agent]) -> list[Agent]:
    """Filter to only chat-capable agents."""
    return [a for a in agents if is_chat_capable(a.type)]


def get_ide_agents(agents: list[Agent]) -> list[Agent]:
    """Filter to only IDE agents (have MCP but no CLI chat)."""
    return [a for a in agents if is_ide_agent(a.type)]


async def run_agent_prompt(agent: Agent, prompt: str, context: str = "") -> str:
    """Run a prompt through an AI agent.
    
    Args:
        agent: The agent to use
        prompt: The user's prompt
        context: Additional context to provide
        
    Returns:
        The agent's response
    """
    full_prompt = f"{context}\n\n{prompt}" if context else prompt
    
    if agent.type == AgentType.GEMINI_CLI:
        return await _run_gemini(agent, full_prompt)
    elif agent.type == AgentType.CODEX_CLI:
        return await _run_codex(agent, full_prompt)
    elif agent.type == AgentType.CLAUDE_CLI:
        return await _run_claude(agent, full_prompt)
    elif agent.type == AgentType.AIDER:
        return await _run_aider(agent, full_prompt)
    elif agent.type == AgentType.OLLAMA:
        return await _run_ollama(agent, full_prompt)
    else:
        raise ValueError(f"Unsupported agent type: {agent.type}")


async def _run_gemini(agent: Agent, prompt: str) -> str:
    """Run prompt through Gemini CLI."""
    try:
        # Gemini CLI typically uses: gemini "prompt"
        result = await asyncio.create_subprocess_exec(
            agent.command,
            prompt,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await asyncio.wait_for(result.communicate(), timeout=120)
        
        if result.returncode == 0:
            return stdout.decode().strip()
        else:
            return f"Error: {stderr.decode().strip()}"
    except asyncio.TimeoutError:
        return "Error: Request timed out"
    except Exception as e:
        return f"Error: {str(e)}"


async def _run_codex(agent: Agent, prompt: str) -> str:
    """Run prompt through Codex CLI."""
    try:
        # Codex CLI: codex "prompt"
        result = await asyncio.create_subprocess_exec(
            agent.command,
            prompt,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await asyncio.wait_for(result.communicate(), timeout=120)
        
        if result.returncode == 0:
            return stdout.decode().strip()
        else:
            return f"Error: {stderr.decode().strip()}"
    except asyncio.TimeoutError:
        return "Error: Request timed out"
    except Exception as e:
        return f"Error: {str(e)}"


async def _run_claude(agent: Agent, prompt: str) -> str:
    """Run prompt through Claude CLI."""
    try:
        # Claude CLI: claude "prompt"
        result = await asyncio.create_subprocess_exec(
            agent.command,
            prompt,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await asyncio.wait_for(result.communicate(), timeout=120)
        
        if result.returncode == 0:
            return stdout.decode().strip()
        else:
            return f"Error: {stderr.decode().strip()}"
    except asyncio.TimeoutError:
        return "Error: Request timed out"
    except Exception as e:
        return f"Error: {str(e)}"


async def _run_aider(agent: Agent, prompt: str) -> str:
    """Run prompt through Aider."""
    try:
        # Aider: aider --message "prompt" --yes
        result = await asyncio.create_subprocess_exec(
            agent.command,
            "--message", prompt,
            "--yes",
            "--no-git",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await asyncio.wait_for(result.communicate(), timeout=120)
        
        if result.returncode == 0:
            return stdout.decode().strip()
        else:
            return f"Error: {stderr.decode().strip()}"
    except asyncio.TimeoutError:
        return "Error: Request timed out"
    except Exception as e:
        return f"Error: {str(e)}"


async def _run_ollama(agent: Agent, prompt: str, model: str = "llama3.2") -> str:
    """Run prompt through Ollama."""
    try:
        # Ollama: ollama run model "prompt"
        result = await asyncio.create_subprocess_exec(
            agent.command,
            "run", model,
            prompt,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await asyncio.wait_for(result.communicate(), timeout=120)
        
        if result.returncode == 0:
            return stdout.decode().strip()
        else:
            return f"Error: {stderr.decode().strip()}"
    except asyncio.TimeoutError:
        return "Error: Request timed out"
    except Exception as e:
        return f"Error: {str(e)}"


# System prompt for Context Mesh Hub
CONTEXT_MESH_SYSTEM_PROMPT = """You are the Context Mesh Hub assistant. Your job is to help users manage their context-driven development workflow.

When the user gives a command, determine which MCP tool to call and return a JSON response:

Available tools:
- cm_help: Show available workflows
- cm_status: Get project status
- cm_list_features: List all features
- cm_list_decisions: List all decisions
- cm_add_feature: Add a new feature (needs: name, what, why, acceptance_criteria)
- cm_fix_bug: Document a bug (needs: title, description, impact)
- cm_create_decision: Create a decision (needs: number, title, context, decision, rationale)

Respond with JSON only:
{"tool_name": "tool_name", "arguments": {...}}

Or if you need more info:
{"tool_name": "ask_user", "arguments": {"questions": ["question1", "question2"]}}
"""


def build_agent_prompt(user_message: str) -> str:
    """Build the full prompt for the agent."""
    return f"""{CONTEXT_MESH_SYSTEM_PROMPT}

User command: {user_message}

Respond with JSON only:"""


def parse_agent_response(response: str) -> Optional[dict]:
    """Parse the agent's JSON response."""
    try:
        # Try to find JSON in the response
        # Sometimes agents add extra text
        import re
        
        # Look for JSON object
        json_match = re.search(r'\{[^{}]*"tool_name"[^{}]*\}', response, re.DOTALL)
        if json_match:
            return json.loads(json_match.group())
        
        # Try parsing the whole response
        return json.loads(response)
    except (json.JSONDecodeError, AttributeError):
        return None
