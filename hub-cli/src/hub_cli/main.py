"""Main CLI application for Context Mesh Hub."""

import asyncio
import json
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Optional

import typer
from rich.prompt import Prompt, Confirm
from rich.table import Table

from hub_cli import __version__
from hub_cli.ui import (
    console,
    print_banner,
    print_success,
    print_error,
    print_warning,
    print_info,
    print_mcp_config,
    print_status_table,
    print_divider,
)
from hub_cli.mcp_client import MCPClient
from hub_cli.llm_client import LLMClient
from hub_cli.config import (
    get_config,
    set_ai_agent,
    get_ai_agent,
    AI_AGENTS,
    get_agent_details,
    is_agent_installed,
    get_installed_agents,
    register_project,
    unregister_project,
    get_registered_projects,
    is_project_registered,
    CONFIG_DIR,
)
from hub_cli.agents import (
    detect_all_agents,
    detect_agent,
    get_preferred_agent,
    get_chat_capable_agents,
    get_ide_agents,
    get_agent_info,
    is_chat_capable,
    is_ide_agent,
    run_agent_prompt,
    build_agent_prompt,
    parse_agent_response,
    Agent,
    AgentType,
    AGENT_INFO,
    CHAT_CAPABLE_AGENTS,
)

app = typer.Typer(
    name="cm",
    help="Context Mesh Hub - Framework that standardizes Context Engineering processes",
    no_args_is_help=False,
    add_completion=False,
)


def get_repo_root() -> Optional[Path]:
    """Find the repository root by looking for .git or context/ directory."""
    cwd = Path.cwd()
    
    # Check current directory and parents
    for path in [cwd] + list(cwd.parents):
        if (path / ".git").exists() or (path / "context").exists():
            return path
    
    return cwd


def check_python() -> tuple[bool, str]:
    """Check Python version."""
    version = sys.version_info
    if version >= (3, 12):
        return True, f"Python {version.major}.{version.minor}.{version.micro}"
    return False, f"Python {version.major}.{version.minor} (requires 3.12+)"


def check_hub_core() -> tuple[bool, str]:
    """Check if hub_core is available."""
    import os
    
    # Check environment variable first
    hub_core_env = os.environ.get("CONTEXT_MESH_HUB_CORE_PATH")
    if hub_core_env and Path(hub_core_env).exists():
        return True, f"hub_core (env: {hub_core_env})"
    
    # Try import
    try:
        import hub_core
        return True, f"hub_core {hub_core.__version__}"
    except ImportError:
        pass
    
    # Check for local development - multiple possible locations
    repo_root = get_repo_root()
    if repo_root:
        # Same directory level (hub/hub-core)
        hub_core_path = repo_root / "hub-core" / "src"
        if hub_core_path.exists():
            return True, f"hub_core (dev: {hub_core_path})"
        
        # Parent directory (hub-cli/../hub-core)
        hub_core_path = repo_root.parent / "hub-core" / "src"
        if hub_core_path.exists():
            return True, f"hub_core (dev: {hub_core_path})"
    
    # Check common paths
    common_paths = [
        Path.home() / "Jeftar" / "hub" / "hub-core" / "src",
        Path.home() / "projects" / "context-mesh-hub" / "hub-core" / "src",
        Path.home() / "dev" / "context-mesh-hub" / "hub-core" / "src",
    ]
    
    for path in common_paths:
        if path.exists():
            return True, f"hub_core (found: {path})"
    
    return False, "hub_core not found (set CONTEXT_MESH_HUB_CORE_PATH)"


def check_context_dir() -> tuple[bool, str]:
    """Check if context directory exists (optional for greenfield projects)."""
    repo_root = get_repo_root()
    if repo_root and (repo_root / "context").exists():
        return True, str(repo_root / "context")
    return False, "No context/ directory (use 'cm init' to create)"


@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    version: bool = typer.Option(False, "--version", "-v", help="Show version"),
):
    """Context Mesh Hub CLI - Framework that standardizes Context Engineering processes.
    
    Run without arguments to start the interactive setup.
    """
    if version:
        console.print(f"Context Mesh Hub v{__version__}")
        raise typer.Exit()
    
    # If no subcommand, show interactive menu
    if ctx.invoked_subcommand is None:
        interactive_menu()


def interactive_menu():
    """Show interactive menu."""
    print_banner()
    print_divider()
    
    # Check configured AI
    configured_ai = get_ai_agent()
    
    # Run checks
    checks = [
        ("Python version", *check_python()),
        ("Hub Core", *check_hub_core()),
        ("Context directory", *check_context_dir()),
    ]
    
    # Check configured AI agent
    if configured_ai:
        details = AI_AGENTS.get(configured_ai, {})
        installed = is_agent_installed(configured_ai)
        if installed:
            checks.append(("AI Agent", True, f"{details.get('name', configured_ai)} ★"))
        else:
            checks.append(("AI Agent", False, f"{details.get('name', configured_ai)} (not installed)"))
    else:
        checks.append(("AI Agent", False, "Not configured - run cm init"))
    
    print_status_table(checks)
    print_divider()
    
    # If no AI configured, prompt to init
    if not configured_ai:
        console.print("[yellow]First time? Run [bold]cm init --ai <agent>[/bold] to choose your AI.[/yellow]\n")
        console.print("Supported: [bold]cursor[/bold], [bold]copilot[/bold], [bold]gemini[/bold], [bold]claude[/bold]\n")
        print_divider()
    
    # Show MCP config
    client = MCPClient(get_repo_root())
    mcp_config = client.get_mcp_config()
    
    # Show where to paste based on configured AI
    if configured_ai:
        details = AI_AGENTS.get(configured_ai, {})
        if details.get("mcp_location"):
            console.print(f"[dim]Paste MCP config in: {details['mcp_location']}[/dim]\n")
    
    print_mcp_config(mcp_config)
    
    print_divider()
    
    # Menu options
    console.print("[bold]What would you like to do?[/bold]\n")
    console.print("  [bold cyan]1.[/bold cyan] Done (config copied)")
    console.print("  [bold cyan]2.[/bold cyan] Start UI Dashboard")
    console.print("  [bold cyan]3.[/bold cyan] Run diagnostics")
    console.print("  [bold cyan]4.[/bold cyan] List AI agents")
    console.print("  [bold cyan]5.[/bold cyan] Exit")
    console.print()
    
    choice = Prompt.ask("Select option", choices=["1", "2", "3", "4", "5"], default="1")
    
    if choice == "1":
        print_success("MCP configuration ready! Paste it in your AI editor settings.")
    elif choice == "2":
        ui_command(port=3000, open_browser=True, dev_mode=False)
    elif choice == "3":
        doctor_command()
    elif choice == "4":
        agents()
    elif choice == "5":
        raise typer.Exit()


@app.command()
def init(
    ai: Optional[str] = typer.Option(None, "--ai", "-a", help="AI agent to use (cursor, copilot, gemini, claude)"),
):
    """Initialize Context Mesh Hub with your preferred AI agent.
    
    Examples:
        cm init --ai cursor
        cm init --ai copilot
        cm init --ai gemini
        cm init --ai claude
    """
    print_banner()
    
    # If no AI specified, prompt for selection
    if not ai:
        console.print("\n[bold]Choose your AI agent:[/bold]\n")
        
        for key, details in AI_AGENTS.items():
            installed = is_agent_installed(key)
            status = "[green]✓[/green]" if installed else "[dim]○[/dim]"
            agent_type = "[cyan]IDE[/cyan]" if details["type"] == "ide" else "[yellow]CLI[/yellow]"
            console.print(f"  {status} [bold]{key}[/bold] - {details['name']} ({agent_type})")
            console.print(f"      [dim]{details['description']}[/dim]")
        
        console.print()
        ai = Prompt.ask(
            "Select AI agent",
            choices=list(AI_AGENTS.keys()),
            default="cursor"
        )
    
    # Validate
    ai = ai.lower()
    if ai not in AI_AGENTS:
        print_error(f"Unknown AI agent: {ai}")
        console.print(f"\nSupported: {', '.join(AI_AGENTS.keys())}")
        raise typer.Exit(1)
    
    details = AI_AGENTS[ai]
    
    # Check if installed
    if not is_agent_installed(ai):
        console.print(f"\n[yellow]⚠ {details['name']} not found[/yellow]\n")
        console.print(f"[bold]To install:[/bold]")
        console.print(f"  [cyan]{details['install']}[/cyan]\n")
        console.print(f"[bold]Documentation:[/bold]")
        console.print(f"  [blue underline]{details['install_url']}[/blue underline]\n")
        
        if not Confirm.ask("Continue anyway?", default=False):
            raise typer.Exit(0)
    
    # Save preference
    set_ai_agent(ai)
    print_success(f"AI agent set to: {details['name']}")
    
    # Auto-register project if context/ exists
    repo_root = get_repo_root()
    if repo_root:
        if register_project(str(repo_root)):
            print_success(f"Project registered: {repo_root.name}")
        else:
            console.print(f"[dim]Project already registered: {repo_root.name}[/dim]")
    
    # Show next steps based on type
    console.print("\n[bold]Next steps:[/bold]\n")
    
    if details["type"] == "ide":
        console.print(f"  1. Run [cyan]cm config[/cyan] to get MCP configuration")
        console.print(f"  2. Add it to [bold]{details['name']}[/bold]: {details['mcp_location']}")
        console.print(f"  3. Use Context Mesh directly in {details['name']}!\n")
    else:
        console.print(f"  1. Run [cyan]cm chat \"your message\"[/cyan] to use {details['name']}")
        console.print(f"  2. Or run [cyan]cm config[/cyan] to configure MCP in an IDE\n")
    
    console.print("[dim]Run [bold]cm doctor[/bold] to verify your setup.[/dim]\n")


@app.command()
def config():
    """Show MCP configuration for AI editors."""
    client = MCPClient(get_repo_root())
    mcp_config = client.get_mcp_config()
    
    # Show configured AI if any
    configured_ai = get_ai_agent()
    if configured_ai:
        details = AI_AGENTS.get(configured_ai, {})
        console.print(f"\n[dim]Configured AI: [bold]{details.get('name', configured_ai)}[/bold][/dim]")
        if details.get("mcp_location"):
            console.print(f"[dim]MCP location: {details['mcp_location']}[/dim]\n")
    
    print_mcp_config(mcp_config)


@app.command()
def doctor():
    """Run diagnostics and check environment."""
    doctor_command()


# Projects subcommand group
projects_app = typer.Typer(help="Manage registered Context Mesh projects")
app.add_typer(projects_app, name="projects")


@projects_app.command("list")
def projects_list():
    """List all registered projects."""
    projects = get_registered_projects()
    
    if not projects:
        console.print("\n[yellow]No projects registered.[/yellow]")
        console.print("Projects are registered automatically when you run [cyan]cm init[/cyan]\n")
        console.print("Or register manually: [cyan]cm projects add .[/cyan]\n")
        return
    
    console.print("\n[bold]Registered Projects[/bold]\n")
    
    table = Table(show_header=True, header_style="bold", box=None)
    table.add_column("", width=3)
    table.add_column("Name")
    table.add_column("Path", style="dim")
    table.add_column("Status")
    
    for proj in projects:
        path = Path(proj["path"])
        name = proj.get("name", path.name)
        
        # Check if context/ exists
        has_context = (path / "context").exists()
        status = "[green]✓ Active[/green]" if has_context else "[yellow]○ No context/[/yellow]"
        
        # Check if current directory
        is_current = path == Path.cwd().resolve()
        icon = "[cyan]►[/cyan]" if is_current else " "
        
        table.add_row(icon, name, str(path), status)
    
    console.print(table)
    console.print(f"\n[dim]Total: {len(projects)} project(s)[/dim]")
    console.print("[dim]Run [bold]cm ui[/bold] to view all projects in the dashboard[/dim]\n")


@projects_app.command("add")
def projects_add(
    path: str = typer.Argument(".", help="Path to project (default: current directory)")
):
    """Register a project with Context Mesh Hub."""
    project_path = Path(path).resolve()
    
    if not project_path.exists():
        print_error(f"Path does not exist: {project_path}")
        raise typer.Exit(1)
    
    if register_project(str(project_path)):
        print_success(f"Project registered: {project_path.name}")
        console.print(f"[dim]Path: {project_path}[/dim]\n")
    else:
        print_info(f"Project already registered: {project_path.name}")


@projects_app.command("remove")
def projects_remove(
    path: str = typer.Argument(".", help="Path to project (default: current directory)")
):
    """Remove a project from the registry."""
    project_path = Path(path).resolve()
    
    if unregister_project(str(project_path)):
        print_success(f"Project removed: {project_path.name}")
    else:
        print_warning(f"Project not found in registry: {project_path.name}")


@app.command()
def agents():
    """List supported AI agents and their status."""
    # Get configured agent
    configured_ai = get_ai_agent()
    
    console.print("\n[bold]Supported AI Agents[/bold]\n")
    
    table = Table(show_header=True, header_style="bold", box=None)
    table.add_column("", width=3)
    table.add_column("Agent")
    table.add_column("Type", style="dim")
    table.add_column("Status")
    table.add_column("MCP Location", style="dim")
    
    for key, details in AI_AGENTS.items():
        installed = is_agent_installed(key)
        is_configured = configured_ai == key
        
        # Status indicator
        if is_configured:
            status_icon = "[green bold]★[/green bold]"
        elif installed:
            status_icon = "[green]✓[/green]"
        else:
            status_icon = "[dim]○[/dim]"
        
        # Status text
        if is_configured:
            status_text = "[green bold]Active[/green bold]"
        elif installed:
            status_text = "[green]Installed[/green]"
        else:
            status_text = f"[dim]{details['install']}[/dim]"
        
        # Type
        agent_type = "[cyan]IDE[/cyan]" if details["type"] == "ide" else "[yellow]CLI[/yellow]"
        
        # MCP location
        mcp_loc = details.get("mcp_location") or "[dim]-[/dim]"
        
        table.add_row(
            status_icon,
            details["name"],
            agent_type,
            status_text,
            mcp_loc,
        )
    
    console.print(table)
    
    # Summary
    if configured_ai:
        details = AI_AGENTS.get(configured_ai, {})
        console.print(f"\n[green]★[/green] Active: [bold]{details.get('name', configured_ai)}[/bold]")
        console.print(f"  Change with: [cyan]cm init --ai <agent>[/cyan]\n")
    else:
        console.print("\n[yellow]No agent configured.[/yellow]")
        console.print("  Run [cyan]cm init --ai <agent>[/cyan] to choose one.\n")


def check_hub_ui() -> tuple[bool, str]:
    """Check if hub-ui is available."""
    repo_root = get_repo_root()
    
    # Check in various locations
    locations = []
    if repo_root:
        locations.append(repo_root / "hub-ui")
        locations.append(repo_root.parent / "hub-ui")
    
    locations.extend([
        Path.home() / "Jeftar" / "hub" / "hub-ui",
        Path.home() / "projects" / "context-mesh-hub" / "hub-ui",
    ])
    
    for loc in locations:
        if loc.exists() and (loc / "package.json").exists():
            return True, str(loc)
    
    return False, "Not found (run 'cm ui' will show install instructions)"


def doctor_command():
    """Run diagnostic checks."""
    console.print("\n[bold]Context Mesh Hub Diagnostics[/bold]\n")
    
    checks = []
    
    # Python version
    passed, details = check_python()
    checks.append(("Python version", passed, details))
    
    # Hub Core
    passed, details = check_hub_core()
    checks.append(("Hub Core", passed, details))
    
    # Hub UI
    passed, details = check_hub_ui()
    checks.append(("Hub UI", passed, details))
    
    # Context directory
    passed, details = check_context_dir()
    checks.append(("Context directory", passed, details))
    
    # Registered projects
    projects = get_registered_projects()
    if projects:
        checks.append(("Registered projects", True, f"{len(projects)} project(s)"))
    else:
        checks.append(("Registered projects", False, "None (run 'cm init' to register)"))
    
    # Check for uv
    uv_path = shutil.which("uv")
    if uv_path:
        checks.append(("uv (package manager)", True, uv_path))
    else:
        checks.append(("uv (package manager)", False, "Not installed (optional)"))
    
    # Check for Node.js (for hub-ui)
    npm_path = shutil.which("npm")
    if npm_path:
        checks.append(("Node.js/npm", True, npm_path))
    else:
        checks.append(("Node.js/npm", False, "Not installed (needed for UI)"))
    
    # Check for git
    git_path = shutil.which("git")
    if git_path:
        checks.append(("Git", True, git_path))
    else:
        checks.append(("Git", False, "Not installed"))
    
    print_status_table(checks)
    
    # Summary - only Python and Hub Core are required, context/ is optional
    required_checks = [checks[0][1], checks[1][1]]  # Python, Hub Core
    console.print()
    if all(required_checks):
        if not checks[3][1]:  # context/ not found
            print_success("Ready! Use 'cm init' to create Context Mesh structure.")
        else:
            print_success("All checks passed!")
    else:
        print_error("Some checks failed. Please fix the issues above.")


def find_free_port(start_port: int = 3000, max_attempts: int = 10) -> int:
    """Find a free port starting from start_port."""
    import socket
    
    for port in range(start_port, start_port + max_attempts):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(("127.0.0.1", port))
                return port
        except OSError:
            continue
    
    # If no free port found, return start_port and let the server handle it
    return start_port


@app.command()
def ui(
    port: int = typer.Option(3000, "--port", "-p", help="UI server port"),
    open_browser: bool = typer.Option(False, "--open", "-o", help="Open browser automatically"),
    dev: bool = typer.Option(False, "--dev", "-d", help="Run in development mode"),
):
    """Start the UI dashboard to view all registered projects."""
    ui_command(port, open_browser, dev)


def ui_command(port: int = 3000, open_browser: bool = False, dev_mode: bool = False):
    """Start the UI dashboard."""
    import os
    import webbrowser
    import time
    import threading
    
    # Current directory where user ran the command
    current_dir = Path.cwd().resolve()
    
    # Find hub-ui directory (NOT in current project - in hub installation)
    hub_ui_path = None
    
    search_paths = [
        Path.home() / "Jeftar" / "hub" / "hub-ui",
        Path.home() / "projects" / "context-mesh-hub" / "hub-ui",
        Path.home() / ".context-mesh-hub" / "hub-ui",
        Path("/usr/local/share/context-mesh-hub/hub-ui"),
    ]
    
    for search_path in search_paths:
        if search_path.exists() and (search_path / "package.json").exists():
            hub_ui_path = search_path
            break
    
    if not hub_ui_path:
        print_error("hub-ui not found.")
        console.print("\n[bold]To install Hub UI:[/bold]")
        console.print("  git clone https://github.com/jeftarmascarenhas/context-mesh-hub")
        console.print("  cd context-mesh-hub/hub-ui")
        console.print("  npm install\n")
        raise typer.Exit(1)
    
    # Check if npm is available (prefer npm over pnpm for consistent port handling)
    npm_path = shutil.which("npm")
    if not npm_path:
        npm_path = shutil.which("pnpm")
    if not npm_path:
        print_error("npm or pnpm not found. Please install Node.js.")
        raise typer.Exit(1)
    
    # Find a free port
    actual_port = find_free_port(port)
    if actual_port != port:
        print_warning(f"Port {port} is in use, using {actual_port} instead")
    
    # Determine project path - where the user ran 'cm ui'
    project_path = current_dir
    project_name = current_dir.name
    has_context = (current_dir / "context").exists()
    
    # Get registered projects
    projects = get_registered_projects()
    
    # Auto-register current project if it has context/
    if has_context and not is_project_registered(str(current_dir)):
        register_project(str(current_dir))
        projects = get_registered_projects()  # Refresh list
    
    # Set environment variables for hub-ui
    env = os.environ.copy()
    env["CONTEXT_MESH_PROJECTS"] = json.dumps(projects)
    env["CONTEXT_MESH_CONFIG_DIR"] = str(CONFIG_DIR)
    env["PORT"] = str(actual_port)  # Next.js respects PORT env var
    
    # Always set the project path to current directory
    env["CONTEXT_MESH_PROJECT_PATH"] = str(project_path)
    
    # Show info
    console.print("\n[bold]Context Mesh Hub UI[/bold]\n")
    
    # Show current project
    if has_context:
        console.print(f"[green]►[/green] Viewing project: [bold]{project_name}[/bold]")
        console.print(f"  [dim]{project_path}[/dim]")
    else:
        console.print(f"[yellow]⚠[/yellow] Directory: [bold]{project_name}[/bold]")
        console.print(f"  [dim]No context/ found - run 'cm init' first[/dim]")
    
    console.print()
    
    # Check if build exists (for production mode)
    next_build_path = hub_ui_path / ".next"
    has_build = next_build_path.exists()
    
    if dev_mode:
        # Development mode
        print_info(f"Starting UI in dev mode at http://localhost:{actual_port}")
        cmd = [npm_path, "run", "dev"]
    else:
        # Production mode - build if needed
        if not has_build:
            console.print("[dim]Building UI for first time (this may take a moment)...[/dim]")
            try:
                subprocess.run(
                    [npm_path, "run", "build"],
                    cwd=str(hub_ui_path),
                    env=env,
                    check=True,
                    capture_output=True,
                )
                print_success("Build complete!")
            except subprocess.CalledProcessError as e:
                print_error("Build failed. Try running with --dev flag for development mode.")
                console.print(f"[dim]{e.stderr.decode() if e.stderr else ''}[/dim]")
                raise typer.Exit(1)
        
        print_info(f"Starting UI at http://localhost:{actual_port}")
        cmd = [npm_path, "run", "start"]
    
    # Open browser after a short delay if requested
    if open_browser:
        def open_browser_delayed():
            time.sleep(2)  # Wait for server to start
            webbrowser.open(f"http://localhost:{actual_port}")
        
        threading.Thread(target=open_browser_delayed, daemon=True).start()
    
    # Start the UI
    try:
        subprocess.run(
            cmd,
            cwd=str(hub_ui_path),
            env=env,
            check=True,
        )
    except subprocess.CalledProcessError as e:
        print_error(f"Failed to start UI: {e}")
        raise typer.Exit(1)
    except KeyboardInterrupt:
        console.print("\n")
        print_info("UI stopped")


@app.command()
def chat(
    message: Optional[str] = typer.Argument(None, help="Natural language command"),
    agent: Optional[str] = typer.Option(None, "--agent", "-a", help="Agent to use (gemini, codex, claude, ollama, aider)"),
    use_api: bool = typer.Option(False, "--api", help="Use direct API instead of agent CLI"),
):
    """Chat with Context Mesh Hub using natural language.
    
    Uses detected AI agents (Gemini CLI, Codex, Claude, etc.) by default.
    No API key needed if you have an agent CLI installed.
    
    Examples:
        cm chat "add a feature for user authentication"
        cm chat "what features do we have?"
        cm chat --agent=gemini "add feature"
        cm chat --api "add feature"  # uses OpenAI API (needs key)
    """
    if message:
        asyncio.run(process_chat_message(message, agent_name=agent, use_api=use_api))
    else:
        asyncio.run(chat_loop(agent_name=agent, use_api=use_api))


AGENT_NAME_MAP = {
    "gemini": AgentType.GEMINI_CLI,
    "codex": AgentType.CODEX_CLI,
    "claude": AgentType.CLAUDE_CLI,
    "cursor": AgentType.CURSOR_CLI,
    "ollama": AgentType.OLLAMA,
    "aider": AgentType.AIDER,
}


def _show_agent_install_help(agent_type: AgentType):
    """Show installation instructions for an agent."""
    info = get_agent_info(agent_type)
    if not info:
        print_error(f"Unknown agent type: {agent_type}")
        return
    
    console.print(f"\n[bold red]✗ {info.display_name} not installed[/bold red]\n")
    console.print(f"[dim]{info.description}[/dim]\n")
    
    console.print("[bold]To install:[/bold]")
    if info.install_command:
        console.print(f"  [cyan]{info.install_command}[/cyan]\n")
    
    console.print("[bold]Documentation:[/bold]")
    console.print(f"  [blue underline]{info.install_url}[/blue underline]\n")


def _show_ide_agent_message(ide_agents: list[Agent]):
    """Show message when only IDE agents are detected."""
    console.print("\n[bold green]✓ IDE with MCP support detected![/bold green]\n")
    
    for agent in ide_agents:
        console.print(f"  [green]✓[/green] {agent.display_name} (v{agent.version or 'unknown'})")
    
    console.print("\n[bold]You already have the best experience![/bold]")
    console.print("\nUse Context Mesh Hub directly in your IDE (not CLI):")
    console.print("  1. Run [cyan]cm config[/cyan] to get your MCP configuration")
    console.print("  2. Add it to your IDE's MCP settings")
    console.print("  3. Chat with Context Mesh in your editor!\n")
    
    console.print("[dim]The [bold]cm chat[/bold] command is for terminal-only users.[/dim]")
    console.print("[dim]Since you have an IDE with MCP, use it there instead![/dim]\n")


def _get_chat_agent(agent_name: Optional[str], show_help: bool = True) -> Optional[Agent]:
    """Get a chat-capable agent by name or auto-detect.
    
    Args:
        agent_name: Name of agent to use (gemini, claude, etc.)
        show_help: If True, show installation help when agent not found
        
    Returns:
        Chat-capable Agent or None
    """
    if agent_name:
        agent_type = AGENT_NAME_MAP.get(agent_name.lower())
        
        if not agent_type:
            if show_help:
                print_error(f"Unknown agent: {agent_name}")
                console.print("\nSupported chat CLIs:")
                console.print("  • [bold]gemini[/bold] - Google Gemini CLI")
                console.print("  • [bold]claude[/bold] - Claude Code")
            return None
        
        # Check if agent type is chat-capable
        if not is_chat_capable(agent_type):
            if show_help:
                info = get_agent_info(agent_type)
                name = info.display_name if info else agent_type
                console.print(f"\n[yellow]{name} is an IDE, not a terminal chat CLI.[/yellow]")
                console.print(f"\n[bold]You don't need [cyan]cm chat[/cyan] - use {name} directly![/bold]")
                console.print("\n1. Run [cyan]cm config[/cyan] to get MCP configuration")
                console.print(f"2. Add it to {name}'s MCP settings")
                console.print(f"3. Chat with Context Mesh inside {name}!\n")
            return None
        
        agent = detect_agent(agent_type)
        
        if not agent and show_help:
            _show_agent_install_help(agent_type)
        
        return agent
    
    # Auto-detect chat-capable agents
    detected = detect_all_agents()
    chat_agents = get_chat_capable_agents(detected)
    
    if chat_agents:
        return get_preferred_agent(chat_agents, for_chat=True)
    
    # No chat agents, but maybe IDEs?
    ide_agents = get_ide_agents(detected)
    if ide_agents and show_help:
        _show_ide_agent_message(ide_agents)
    
    return None


def _get_agent(agent_name: Optional[str], show_help: bool = True) -> Optional[Agent]:
    """Get agent by name or detect preferred one (any type).
    
    Args:
        agent_name: Name of agent to use
        show_help: If True, show installation help when agent not found
        
    Returns:
        Detected Agent or None
    """
    if agent_name:
        agent_type = AGENT_NAME_MAP.get(agent_name.lower())
        
        if not agent_type:
            if show_help:
                print_error(f"Unknown agent: {agent_name}")
                console.print("\nAvailable agents:")
                for name in AGENT_NAME_MAP.keys():
                    console.print(f"  • {name}")
            return None
        
        agent = detect_agent(agent_type)
        
        if not agent and show_help:
            _show_agent_install_help(agent_type)
        
        return agent
    
    # Auto-detect
    detected = detect_all_agents()
    return get_preferred_agent(detected)


async def process_chat_message(message: str, agent_name: Optional[str] = None, use_api: bool = False):
    """Process a single chat message."""
    mcp = MCPClient(get_repo_root())
    
    # Decide which backend to use
    if use_api:
        # Use direct API
        llm = LLMClient()
        if not llm.is_configured:
            print_warning("No LLM API key configured. Set OPENAI_API_KEY or use --agent flag.")
            return
        
        with console.status("[bold blue]Thinking...[/bold blue]"):
            tool_call = await llm.parse_command(message)
        
        await llm.close()
    else:
        # Use external agent CLI (must be chat-capable)
        agent = _get_chat_agent(agent_name)
        
        if not agent:
            # Message already shown by _get_chat_agent
            return
        
        console.print(f"[dim]Using agent: {agent.display_name}[/dim]")
        
        # Build prompt and run through agent
        prompt = build_agent_prompt(message)
        
        with console.status(f"[bold blue]Asking {agent.display_name}...[/bold blue]"):
            response = await run_agent_prompt(agent, prompt)
        
        # Parse the response
        parsed = parse_agent_response(response)
        
        if not parsed:
            # Agent didn't return valid JSON, show raw response
            console.print(f"\n[dim]Agent response:[/dim]\n{response}")
            return
        
        tool_call = type("ToolCall", (), {
            "tool_name": parsed.get("tool_name"),
            "arguments": parsed.get("arguments", {}),
        })()
    
    if not tool_call or not tool_call.tool_name:
        print_error("Could not understand the command. Please try again.")
        return
    
    if tool_call.tool_name == "ask_user":
        # Agent needs more information
        questions = tool_call.arguments.get("questions", [])
        console.print("\n[bold]I need more information:[/bold]")
        for q in questions:
            console.print(f"  • {q}")
        return
    
    # Execute the tool
    console.print(f"\n[dim]Calling: {tool_call.tool_name}[/dim]")
    
    result = await mcp.call_tool(tool_call.tool_name, tool_call.arguments)
    
    if result.success:
        console.print(f"\n{result.content}")
    else:
        print_error(f"Tool failed: {result.error}")


async def chat_loop(agent_name: Optional[str] = None, use_api: bool = False):
    """Interactive chat loop."""
    
    # Check if we have a backend available
    if use_api:
        llm = LLMClient()
        if not llm.is_configured:
            print_warning("No LLM API key configured.")
            console.print("\nOptions:")
            console.print("  • Set [bold]OPENAI_API_KEY[/bold] or [bold]ANTHROPIC_API_KEY[/bold]")
            console.print("  • Use an agent: [bold]cm chat --agent=gemini[/bold]")
            console.print("  • Run [bold]cm agents[/bold] to see available agents")
            return
        backend_name = "API"
    else:
        agent = _get_agent(agent_name)
        if not agent:
            print_warning("No AI agent detected.")
            console.print("\nOptions:")
            console.print("  • Install: [bold]gemini[/bold], [bold]codex[/bold], [bold]claude[/bold], [bold]ollama[/bold]")
            console.print("  • Use API: [bold]cm chat --api[/bold]")
            console.print("  • Run [bold]cm agents[/bold] to see available agents")
            return
        backend_name = agent.display_name
    
    console.print(f"\n[bold]Context Mesh Hub Chat[/bold] [dim](using {backend_name})[/dim]")
    console.print("[dim]Type your commands in natural language. Type 'exit' to quit.[/dim]\n")
    
    while True:
        try:
            message = Prompt.ask("[bold cyan]cm[/bold cyan]")
            
            if message.lower() in ("exit", "quit", "q"):
                break
            
            if not message.strip():
                continue
            
            await process_chat_message(message, agent_name=agent_name, use_api=use_api)
            console.print()
            
        except KeyboardInterrupt:
            break
    
    print_info("Goodbye!")


if __name__ == "__main__":
    app()
