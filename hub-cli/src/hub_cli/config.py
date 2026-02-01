"""Configuration management for Context Mesh Hub CLI.

Stores user preferences like AI agent choice and registered projects.
"""

import json
from pathlib import Path
from typing import Optional, List
from dataclasses import dataclass, asdict, field


# Config directory and file
CONFIG_DIR = Path.home() / ".context-mesh-hub"
CONFIG_FILE = CONFIG_DIR / "config.json"
PROJECTS_FILE = CONFIG_DIR / "projects.json"


@dataclass
class HubConfig:
    """Hub CLI configuration."""
    
    ai_agent: Optional[str] = None  # cursor, copilot, gemini, claude
    mcp_configured: bool = False
    last_repo: Optional[str] = None
    
    def save(self):
        """Save configuration to disk."""
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        with open(CONFIG_FILE, "w") as f:
            json.dump(asdict(self), f, indent=2)
    
    @classmethod
    def load(cls) -> "HubConfig":
        """Load configuration from disk."""
        if CONFIG_FILE.exists():
            try:
                with open(CONFIG_FILE) as f:
                    data = json.load(f)
                return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})
            except (json.JSONDecodeError, TypeError):
                pass
        return cls()


@dataclass
class ProjectInfo:
    """Information about a registered project."""
    path: str
    name: str
    added_at: str  # ISO format date


@dataclass 
class ProjectsRegistry:
    """Registry of Context Mesh projects."""
    
    projects: List[dict] = field(default_factory=list)
    
    def save(self):
        """Save projects to disk."""
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        with open(PROJECTS_FILE, "w") as f:
            json.dump({"projects": self.projects}, f, indent=2)
    
    @classmethod
    def load(cls) -> "ProjectsRegistry":
        """Load projects from disk."""
        if PROJECTS_FILE.exists():
            try:
                with open(PROJECTS_FILE) as f:
                    data = json.load(f)
                return cls(projects=data.get("projects", []))
            except (json.JSONDecodeError, TypeError):
                pass
        return cls()
    
    def add_project(self, path: str, name: Optional[str] = None) -> bool:
        """Add a project to the registry. Returns True if added, False if already exists."""
        from datetime import datetime
        
        # Resolve to absolute path
        abs_path = str(Path(path).resolve())
        
        # Check if already registered
        for proj in self.projects:
            if proj.get("path") == abs_path:
                return False
        
        # Get name from path if not provided
        if not name:
            name = Path(abs_path).name
        
        self.projects.append({
            "path": abs_path,
            "name": name,
            "added_at": datetime.now().isoformat(),
        })
        self.save()
        return True
    
    def remove_project(self, path: str) -> bool:
        """Remove a project from the registry. Returns True if removed."""
        abs_path = str(Path(path).resolve())
        
        for i, proj in enumerate(self.projects):
            if proj.get("path") == abs_path:
                self.projects.pop(i)
                self.save()
                return True
        return False
    
    def get_projects(self) -> List[dict]:
        """Get all registered projects."""
        return self.projects
    
    def is_registered(self, path: str) -> bool:
        """Check if a project is registered."""
        abs_path = str(Path(path).resolve())
        return any(proj.get("path") == abs_path for proj in self.projects)


def get_config() -> HubConfig:
    """Get current configuration."""
    return HubConfig.load()


def get_projects_registry() -> ProjectsRegistry:
    """Get projects registry."""
    return ProjectsRegistry.load()


def register_project(path: str, name: Optional[str] = None) -> bool:
    """Register a project. Returns True if newly added."""
    registry = get_projects_registry()
    return registry.add_project(path, name)


def unregister_project(path: str) -> bool:
    """Unregister a project. Returns True if removed."""
    registry = get_projects_registry()
    return registry.remove_project(path)


def get_registered_projects() -> List[dict]:
    """Get all registered projects."""
    return get_projects_registry().get_projects()


def is_project_registered(path: str) -> bool:
    """Check if a project is registered."""
    return get_projects_registry().is_registered(path)


def set_ai_agent(agent: str) -> HubConfig:
    """Set the preferred AI agent."""
    config = get_config()
    config.ai_agent = agent
    config.save()
    return config


def get_ai_agent() -> Optional[str]:
    """Get the configured AI agent."""
    return get_config().ai_agent


# Supported AI agents with their details
AI_AGENTS = {
    "cursor": {
        "name": "Cursor",
        "type": "ide",
        "description": "AI code editor with MCP support",
        "check_command": "cursor",
        "install": "curl -fsSL https://cursor.com/install | bash",
        "install_url": "https://www.cursor.com/",
        "mcp_location": "Settings → Features → MCP Servers",
    },
    "copilot": {
        "name": "GitHub Copilot",
        "type": "ide",
        "description": "AI pair programmer in VS Code",
        "check_command": "code",  # VS Code
        "install": "Install VS Code extension: GitHub Copilot",
        "install_url": "https://github.com/features/copilot",
        "mcp_location": "Settings → GitHub Copilot → MCP",
    },
    "gemini": {
        "name": "Gemini CLI",
        "type": "cli",
        "description": "Google's Gemini AI in your terminal",
        "check_command": "gemini",
        "install": "npm install -g @anthropic-ai/gemini-cli",
        "install_url": "https://github.com/google-gemini/gemini-cli",
        "mcp_location": None,
    },
    "claude": {
        "name": "Claude Code",
        "type": "cli",
        "description": "Claude AI coding assistant",
        "check_command": "claude",
        "install": "npm install -g @anthropic-ai/claude-code",
        "install_url": "https://docs.anthropic.com/en/docs/claude-code",
        "mcp_location": None,
    },
}


def get_agent_details(agent: str) -> Optional[dict]:
    """Get details for an AI agent."""
    return AI_AGENTS.get(agent)


def is_agent_installed(agent: str) -> bool:
    """Check if an AI agent is installed."""
    import shutil
    details = AI_AGENTS.get(agent)
    if not details:
        return False
    return shutil.which(details["check_command"]) is not None


def get_installed_agents() -> list[str]:
    """Get list of installed agents."""
    return [agent for agent in AI_AGENTS if is_agent_installed(agent)]
