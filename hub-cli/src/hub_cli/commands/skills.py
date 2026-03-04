"""Skills management for Context Mesh Hub CLI."""

import shutil
from pathlib import Path
from typing import Optional

import typer
from rich.table import Table

from hub_cli.ui import console, print_success, print_error, print_warning, print_info

skills_app = typer.Typer(
    name="skills",
    help="Manage Context Mesh skills for AI agents",
)

# Skill directories by IDE/agent
SKILL_DIRS = {
    "cursor": ".cursor/skills",
    "copilot": ".github/skills",
    "claude": ".claude/skills",
}

# Human-readable names
AGENT_NAMES = {
    "cursor": "Cursor",
    "copilot": "GitHub Copilot",
    "claude": "Claude",
}


def get_bundled_skill_path() -> Optional[Path]:
    """Get path to bundled context-mesh skill."""
    # First try bundled with package
    bundled = Path(__file__).parent.parent / "templates" / "skills" / "context-mesh"
    if bundled.exists():
        return bundled
    
    # Fallback to development paths
    dev_paths = [
        Path.home() / "Jeftar" / "hub" / ".github" / "skills" / "context-mesh",
        Path(__file__).parent.parent.parent.parent.parent.parent / ".github" / "skills" / "context-mesh",
    ]
    for p in dev_paths:
        if p.exists():
            return p
    return None


def get_skill_install_path(agent: str, target_dir: Optional[Path] = None) -> Path:
    """Get the installation path for a skill."""
    base_dir = target_dir or Path.cwd()
    skill_dir = SKILL_DIRS.get(agent, SKILL_DIRS["copilot"])
    return base_dir / skill_dir / "context-mesh"


def is_skill_installed(agent: str, target_dir: Optional[Path] = None) -> bool:
    """Check if the Context Mesh skill is installed for an agent."""
    install_path = get_skill_install_path(agent, target_dir)
    # Check for SKILL.md as indicator of valid installation
    return (install_path / "SKILL.md").exists()


@skills_app.command("list")
def list_skills(
    directory: Optional[str] = typer.Option(None, "--dir", "-d", help="Target directory (default: current)"),
):
    """List installed Context Mesh skills."""
    target_dir = Path(directory) if directory else Path.cwd()
    
    if not target_dir.exists():
        print_error(f"Directory not found: {target_dir}")
        raise typer.Exit(1)
    
    table = Table(title="Context Mesh Skills", show_header=True)
    table.add_column("Agent", style="cyan")
    table.add_column("Status", style="bold")
    table.add_column("Location", style="dim")
    
    any_installed = False
    
    for agent, skill_dir in SKILL_DIRS.items():
        install_path = get_skill_install_path(agent, target_dir)
        installed = is_skill_installed(agent, target_dir)
        
        if installed:
            any_installed = True
            status = "[green]✓ Installed[/green]"
            location = str(install_path.relative_to(target_dir))
        else:
            status = "[dim]Not installed[/dim]"
            location = f"[dim]{skill_dir}/context-mesh[/dim]"
        
        table.add_row(AGENT_NAMES.get(agent, agent), status, location)
    
    console.print()
    console.print(table)
    console.print()
    
    if not any_installed:
        print_info("No Context Mesh skills installed. Run [bold]cm skills install[/bold] to install.")


@skills_app.command("install")
def install_skill(
    agent: Optional[str] = typer.Option(None, "--agent", "-a", help="Agent: cursor, copilot, claude"),
    target_dir: Optional[str] = typer.Option(None, "--dir", "-d", help="Target directory (default: current)"),
    force: bool = typer.Option(False, "--force", "-f", help="Overwrite existing installation"),
):
    """Install Context Mesh skill for an AI agent."""
    # Validate agent if provided
    if agent and agent not in SKILL_DIRS:
        print_error(f"Unknown agent: {agent}")
        print_info(f"Valid agents: {', '.join(SKILL_DIRS.keys())}")
        raise typer.Exit(1)
    
    # Get source skill path
    source_path = get_bundled_skill_path()
    if not source_path:
        print_error("Context Mesh skill not found in bundle or development paths.")
        print_info("Please ensure the skill exists at .github/skills/context-mesh/")
        raise typer.Exit(1)
    
    # Determine target directory
    target = Path(target_dir) if target_dir else Path.cwd()
    if not target.exists():
        print_error(f"Target directory not found: {target}")
        raise typer.Exit(1)
    
    # If no agent specified, prompt for selection
    if not agent:
        console.print()
        console.print("[bold]Select an agent to install the Context Mesh skill:[/bold]")
        console.print()
        for i, (key, name) in enumerate(AGENT_NAMES.items(), 1):
            installed = is_skill_installed(key, target)
            status = " [dim](already installed)[/dim]" if installed else ""
            console.print(f"  {i}. {name}{status}")
        console.print()
        
        choice = typer.prompt("Enter number (1-3)", default="2")
        try:
            idx = int(choice) - 1
            agent = list(SKILL_DIRS.keys())[idx]
        except (ValueError, IndexError):
            print_error("Invalid selection")
            raise typer.Exit(1)
    
    # Get installation path
    install_path = get_skill_install_path(agent, target)
    
    # Check if already installed
    if install_path.exists() and not force:
        if is_skill_installed(agent, target):
            print_warning(f"Context Mesh skill already installed for {AGENT_NAMES.get(agent, agent)}.")
            print_info("Use --force to overwrite.")
            raise typer.Exit(0)
    
    # Create parent directories
    install_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Remove existing if force
    if install_path.exists() and force:
        shutil.rmtree(install_path)
    
    # Copy skill
    try:
        shutil.copytree(source_path, install_path)
        print_success(f"Context Mesh skill installed for {AGENT_NAMES.get(agent, agent)}!")
        console.print(f"  [dim]Location: {install_path.relative_to(target)}[/dim]")
        console.print()
        print_info("The skill provides Context Mesh workflows to your AI agent.")
    except Exception as e:
        print_error(f"Failed to install skill: {e}")
        raise typer.Exit(1)


@skills_app.command("check")
def check_skill(
    directory: Optional[str] = typer.Option(None, "--dir", "-d", help="Target directory (default: current)"),
):
    """Check if Context Mesh skill is properly installed."""
    target_dir = Path(directory) if directory else Path.cwd()
    
    if not target_dir.exists():
        print_error(f"Directory not found: {target_dir}")
        raise typer.Exit(1)
    
    console.print()
    console.print("[bold]Context Mesh Skill Check[/bold]")
    console.print()
    
    # Check bundled skill source
    source_path = get_bundled_skill_path()
    if source_path:
        print_success(f"Skill source found: {source_path}")
    else:
        print_warning("Skill source not found (bundle or dev path)")
    
    console.print()
    
    # Check each agent
    all_checks = []
    for agent, skill_dir in SKILL_DIRS.items():
        install_path = get_skill_install_path(agent, target_dir)
        installed = is_skill_installed(agent, target_dir)
        
        agent_name = AGENT_NAMES.get(agent, agent)
        
        if installed:
            # Check for expected files
            skill_md = install_path / "SKILL.md"
            references_dir = install_path / "references"
            scripts_dir = install_path / "scripts"
            
            checks = [
                (skill_md.exists(), "SKILL.md"),
                (references_dir.exists(), "references/"),
                (scripts_dir.exists(), "scripts/"),
            ]
            
            all_good = all(c[0] for c in checks)
            
            if all_good:
                print_success(f"{agent_name}: Properly installed")
                all_checks.append(True)
            else:
                print_warning(f"{agent_name}: Partially installed")
                for ok, name in checks:
                    if not ok:
                        console.print(f"    [dim]Missing: {name}[/dim]")
                all_checks.append(False)
        else:
            console.print(f"[dim]  {agent_name}: Not installed[/dim]")
            all_checks.append(None)
    
    console.print()
    
    # Summary
    installed_count = sum(1 for c in all_checks if c is True)
    partial_count = sum(1 for c in all_checks if c is False)
    
    if installed_count > 0:
        print_info(f"{installed_count} agent(s) with Context Mesh skill installed.")
    elif partial_count > 0:
        print_warning("Some installations are incomplete. Run [bold]cm skills install --force[/bold] to reinstall.")
    else:
        print_info("No Context Mesh skills installed. Run [bold]cm skills install[/bold] to get started.")
