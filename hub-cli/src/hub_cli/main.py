"""Main CLI application for Context Mesh Hub."""

import json
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Optional

import typer
from rich.prompt import Prompt, Confirm
from rich.table import Table
import questionary

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
from hub_cli.config import (
    get_config,
    AI_AGENTS,
    MCP_EDITORS,
    AGENT_COMMAND_DIRS,
    get_agent_details,
    is_agent_installed,
    get_installed_agents,
    register_project,
    unregister_project,
    get_registered_projects,
    is_project_registered,
    CONFIG_DIR,
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

    Run [bold]cm init[/bold] (or [bold]cm[/bold] with no arguments) to start the interactive setup.
    """
    if version:
        console.print(f"Context Mesh Hub v{__version__}")
        raise typer.Exit()

    # No subcommand: run same flow as cm init
    if ctx.invoked_subcommand is None:
        run_init_flow()


def run_init_flow():
    """Interactive setup flow: checks + unified menu (used by cm and cm init)."""
    print_banner()
    print_divider()

    checks = [
        ("Python version", *check_python()),
        ("Hub Core", *check_hub_core()),
        ("Context directory", *check_context_dir()),
    ]
    print_status_table(checks)
    print_divider()

    init_choices = [
        "Register project (cm projects add [path])",
        "Get MCP config (cm config)",
        "Install slash commands (cm setup-commands)",
        "Run diagnostics",
        "List AI agents",
        "Exit",
    ]
    choice = questionary.select(
        "What would you like to do?",
        choices=init_choices,
        use_shortcuts=False,
        use_indicator=True,
    ).ask()

    if choice is None:
        raise typer.Exit()

    root = get_repo_root() or Path.cwd()
    root = Path(root).resolve()

    if choice == "Register project (cm projects add [path])":
        path = Prompt.ask("Project path to register", default=".")
        project_path = (root / path).resolve() if path != "." else root
        if not project_path.exists():
            print_error(f"Path does not exist: {project_path}")
            raise typer.Exit(1)
        if register_project(str(project_path)):
            print_success(f"Project registered: {project_path.name}")
        else:
            print_info(f"Project already registered: {project_path.name}")
        console.print("\n[dim]Next: run [bold]cm config[/bold] or [bold]cm setup-commands[/bold].[/dim]\n")

    elif choice == "Get MCP config (cm config)":
        editor_choices = [MCP_EDITORS[k]["name"] for k in MCP_EDITORS]
        editor_display = questionary.select(
            "Which editor?",
            choices=editor_choices,
            use_shortcuts=False,
            use_indicator=True,
        ).ask()
        if editor_display is None:
            raise typer.Exit()
        editor = next((k for k, v in MCP_EDITORS.items() if v["name"] == editor_display), "cursor")
        _do_config(editor, raw=False)

    elif choice == "Install slash commands (cm setup-commands)":
        agent_choices = [f"{MCP_EDITORS.get(k, {}).get('name', k)}" for k in AGENT_COMMAND_DIRS]
        agent_display = questionary.select(
            "Which agent?",
            choices=agent_choices,
            use_shortcuts=False,
            use_indicator=True,
        ).ask()
        if agent_display is None:
            raise typer.Exit()
        agent = next(
            (k for k in AGENT_COMMAND_DIRS if MCP_EDITORS.get(k, {}).get("name", k) == agent_display),
            "cursor",
        )
        _do_setup_commands(agent, root)

    elif choice == "Run diagnostics":
        doctor_command()
    elif choice == "List AI agents":
        agents()
    elif choice == "Exit":
        raise typer.Exit()


@app.command()
def init():
    """Initialize Context Mesh Hub — interactive setup (register project, MCP config, slash commands, UI, diagnostics).

    Run [bold]cm init[/bold] to open the setup menu. Same as running [bold]cm[/bold] with no arguments.
    """
    run_init_flow()


def _get_slash_commands_templates_dir() -> Path:
    """Return the path to slash command templates (e.g. for .cursor/commands)."""
    return Path(__file__).parent / "templates" / "commands"


def _do_config(editor: str, raw: bool = False) -> None:
    """Show MCP config for the given editor (cursor, copilot, claude, gemini)."""
    client = MCPClient(get_repo_root())
    mcp_config = client.get_mcp_config_for_editor(editor)
    if raw:
        print_mcp_config(mcp_config, raw=True)
        return
    editor_info = MCP_EDITORS[editor]
    console.print(f"\n[dim]MCP configuration for [bold]{editor_info['name']}[/bold]. Paste in: {editor_info['paste']}[/dim]\n")
    print_mcp_config(mcp_config, raw=False, editor=editor)


def _md_to_gemini_toml(md_path: Path) -> tuple[str, str]:
    """Parse a command .md file: extract description from frontmatter and body for prompt. Returns (description, prompt_body)."""
    text = md_path.read_text(encoding="utf-8")
    description = "Context Mesh command"
    body = text
    if text.startswith("---"):
        # Find closing --- (after first newline)
        close = text.find("\n---", 4)
        if close >= 0:
            fm = text[4:close]
            body = text[close + 4:].lstrip()
            for line in fm.splitlines():
                line = line.strip()
                if line.startswith("description:"):
                    description = line.split(":", 1)[1].strip().strip('"\'')
                    break
    return description, body


def _do_setup_commands(agent: str, root: Path) -> None:
    """Install slash commands for the given agent (cursor, copilot, claude, gemini) into root."""
    templates_dir = _get_slash_commands_templates_dir()
    if not templates_dir.exists():
        print_error(f"Templates directory not found: {templates_dir}")
        raise typer.Exit(1)

    rel_parts = AGENT_COMMAND_DIRS[agent].strip("./").split("/")
    commands_dir = root.joinpath(*rel_parts)
    commands_dir.mkdir(parents=True, exist_ok=True)

    count = 0
    if agent == "gemini":
        # Gemini CLI uses .toml: prompt = """...""", description = "..."
        for md in sorted(templates_dir.glob("*.md")):
            description, body = _md_to_gemini_toml(md)
            toml_name = md.stem + ".toml"
            dest = commands_dir / toml_name
            # TOML: description one-line (escape "), prompt multi-line (escape \ and """)
            desc_escaped = description.replace("\\", "\\\\").replace('"', '\\"')
            body_escaped = body.replace("\\", "\\\\").replace('"""', '\\"\\"\\"')
            content = f'description = "{desc_escaped}"\n\nprompt = """\n{body_escaped}\n"""\n'
            dest.write_text(content, encoding="utf-8")
            count += 1
            console.print(f"  [green]+[/green] {commands_dir.relative_to(root)}/{toml_name}")
    else:
        # Cursor, Copilot, Claude: copy .md
        for md in sorted(templates_dir.glob("*.md")):
            dest = commands_dir / md.name
            shutil.copy2(md, dest)
            count += 1
            console.print(f"  [green]+[/green] {commands_dir.relative_to(root)}/{md.name}")

    editor_name = MCP_EDITORS.get(agent, {}).get("name", agent)
    print_success(f"Installed {count} slash commands for [bold]{editor_name}[/bold] in [bold]{commands_dir}[/bold]")
    console.print()
    console.print(f"[bold]How to use in {editor_name}:[/bold]")
    console.print("  1. Open chat / REPL")
    console.print("  2. Type [cyan]/[/cyan] to see commands (e.g. [cyan]/cm-add-feature[/cyan], [cyan]/cm-build[/cyan])")
    console.print("  3. Add your message after the command (e.g. [cyan]/cm-add-feature user login[/cyan])")
    console.print()
    console.print("[dim]Ensure Context Mesh Hub MCP is configured (cm config --editor ...) so tools are available.[/dim]")


@app.command()
def setup_commands(
    agent: Optional[str] = typer.Option(
        None,
        "--agent",
        "-a",
        help="Agent: cursor, copilot, claude, gemini. If omitted, you will be asked.",
    ),
    target_dir: Optional[str] = typer.Option(
        None,
        "--dir",
        "-d",
        help="Target directory (default: repo root or current dir).",
    ),
):
    """Install slash commands for agent chat (Cursor, GitHub Copilot, Claude, Gemini).

    Creates command files so you can type /cm-add-feature, /cm-build, etc.
    Run without --agent to choose: Cursor, GitHub Copilot (VS Code), Claude Desktop, Gemini CLI.

    Examples:
        cm setup-commands
        cm setup-commands --agent cursor
        cm setup-commands --agent copilot --dir /path/to/project
    """
    root = Path(target_dir).resolve() if target_dir else (get_repo_root() or Path.cwd())
    root = root.resolve()

    if agent is None:
        agent_choices = [MCP_EDITORS[k]["name"] for k in AGENT_COMMAND_DIRS]
        agent_display = questionary.select(
            "Which agent?",
            choices=agent_choices,
            use_shortcuts=False,
            use_indicator=True,
        ).ask()
        if agent_display is None:
            raise typer.Exit(0)
        agent = next(
            (k for k in AGENT_COMMAND_DIRS if MCP_EDITORS.get(k, {}).get("name") == agent_display),
            "cursor",
        )
    else:
        agent = agent.lower()
        if agent not in AGENT_COMMAND_DIRS:
            print_error(f"Unknown agent: {agent}")
            console.print(f"Supported: {', '.join(AGENT_COMMAND_DIRS.keys())}")
            raise typer.Exit(1)

    _do_setup_commands(agent, root)


@app.command()
def config(
    raw: bool = typer.Option(
        False,
        "--raw",
        "-r",
        help="Print only JSON (no instructions). Use for copy-paste or piping.",
    ),
    editor: Optional[str] = typer.Option(
        None,
        "--editor",
        "-e",
        help="Editor: cursor, copilot, claude, gemini. If omitted, you will be asked.",
    ),
):
    """Show MCP configuration for your editor.
    
    Each editor uses a different JSON format (Cursor/Claude/Gemini: mcpServers;
    VS Code GitHub Copilot: servers). Run without --editor to choose.
    """
    if editor is None:
        editor_choices = [MCP_EDITORS[k]["name"] for k in MCP_EDITORS]
        editor_display = questionary.select(
            "Which editor?",
            choices=editor_choices,
            use_shortcuts=False,
            use_indicator=True,
        ).ask()
        if editor_display is None:
            raise typer.Exit(0)
        editor = next(
            (k for k in MCP_EDITORS if MCP_EDITORS[k]["name"] == editor_display),
            "cursor",
        )
    else:
        editor = (editor or "cursor").lower()
        if editor not in MCP_EDITORS:
            print_error(f"Unknown editor: {editor}")
            console.print(f"Supported: {', '.join(MCP_EDITORS.keys())}")
            raise typer.Exit(1)

    _do_config(editor, raw=raw)


@app.command()
def doctor():
    """Run diagnostics and check environment."""
    doctor_command()


# Projects subcommand group
projects_app = typer.Typer(help="Manage registered Context Mesh projects")
app.add_typer(projects_app, name="projects")

# Slash commands live in agent chat only (Cursor, Copilot, Claude CLI, Gemini CLI).
# Install with: cm setup-commands. Do not expose /intent, /build, /learn in the CLI.

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
    """List supported AI agents and their status.
    
    MCP setup is for Cursor only; other agents (Copilot, Claude CLI, Gemini CLI) will be added later.
    """
    console.print("\n[bold]Supported AI Agents[/bold]\n")

    table = Table(show_header=True, header_style="bold", box=None)
    table.add_column("", width=3)
    table.add_column("Agent")
    table.add_column("Type", style="dim")
    table.add_column("Status")
    table.add_column("MCP setup", style="dim")

    for key, details in AI_AGENTS.items():
        installed = is_agent_installed(key)
        status_icon = "[green]✓[/green]" if installed else "[dim]○[/dim]"
        status_text = "[green]Installed[/green]" if installed else f"[dim]{details['install']}[/dim]"
        agent_type = "[cyan]IDE[/cyan]" if details["type"] == "ide" else "[yellow]CLI[/yellow]"
        mcp_info = MCP_EDITORS.get(key, {})
        mcp_setup = mcp_info.get("paste", "[dim]—[/dim]") if mcp_info else "[dim]—[/dim]"
        table.add_row(status_icon, details["name"], agent_type, status_text, mcp_setup)

    console.print(table)
    console.print("\n[dim]Run [bold]cm config --editor cursor[/bold] (or copilot, claude, gemini) to get the JSON for your editor.[/dim]\n")


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


if __name__ == "__main__":
    app()
