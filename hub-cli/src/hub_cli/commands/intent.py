"""Intent phase slash commands for Context Mesh Hub.

Commands for the Intent phase of the workflow:
- /intent new-project  - Initialize a new project
- /intent add-feature  - Add a new feature
- /intent fix-bug      - Document a bug fix
- /intent update       - Update an existing feature
- /intent create-agent - Create a reusable agent
"""

import asyncio
from pathlib import Path
from typing import Optional

import typer
from rich.prompt import Prompt, Confirm
from rich.panel import Panel
from rich.markdown import Markdown

from hub_cli.ui import (
    console,
    print_success,
    print_error,
    print_warning,
    print_info,
    print_divider,
)
from hub_cli.mcp_client import MCPClient


intent_app = typer.Typer(
    name="intent",
    help="Intent phase commands - Define WHAT and WHY before building",
    no_args_is_help=True,
)


def get_repo_root() -> Optional[Path]:
    """Find the repository root."""
    cwd = Path.cwd()
    for path in [cwd] + list(cwd.parents):
        if (path / ".git").exists() or (path / "context").exists():
            return path
    return cwd


def _run_async(coro):
    """Run async function synchronously."""
    return asyncio.get_event_loop().run_until_complete(coro)


@intent_app.command("new-project")
def new_project(
    name: Optional[str] = typer.Option(None, "--name", "-n", help="Project name"),
    interactive: bool = typer.Option(True, "--interactive/--no-interactive", "-i", help="Interactive mode"),
):
    """Initialize Context Mesh for a new project.
    
    Creates the full context/ structure with project intent,
    initial decisions, and changelog.
    
    Examples:
        cm /intent new-project
        cm /intent new-project --name "My App"
    """
    console.print("\n[bold]Context Mesh - New Project Setup[/bold]\n")
    
    repo_root = get_repo_root()
    mcp = MCPClient(repo_root)
    
    # Check if context already exists
    if repo_root and (repo_root / "context").exists():
        print_warning("Context Mesh already initialized in this project.")
        if not Confirm.ask("Reinitialize?", default=False):
            raise typer.Exit(0)
    
    # Get project info
    if interactive:
        if not name:
            name = Prompt.ask("Project name", default=repo_root.name if repo_root else "my-project")
        
        description = Prompt.ask("What does this project do?")
        why = Prompt.ask("Why is this project important?")
        
        console.print("\n[dim]Optional: Press Enter to skip[/dim]")
        tech_stack = Prompt.ask("Tech stack", default="")
        
        console.print("\n[bold]Features to add (comma-separated, or press Enter to skip):[/bold]")
        features_input = Prompt.ask("Features", default="")
        features = [f.strip() for f in features_input.split(",") if f.strip()]
    else:
        if not name:
            name = repo_root.name if repo_root else "my-project"
        description = ""
        why = ""
        tech_stack = ""
        features = []
    
    # Call MCP to get template and create files
    async def setup():
        result = await mcp.call_tool("cm_new_project", {"repo_root": str(repo_root)})
        return result
    
    result = _run_async(setup())
    
    if not result.success:
        print_error(f"Failed to get template: {result.error}")
        raise typer.Exit(1)
    
    # Show what will be created
    console.print("\n[bold]Files to create:[/bold]")
    if hasattr(result, 'content') and isinstance(result.content, dict):
        content = result.content
        if 'files_to_create' in content:
            for path in content['files_to_create'].keys():
                console.print(f"  [green]+[/green] {path}")
    
    # Create the files
    if interactive:
        if not Confirm.ask("\nCreate these files?", default=True):
            print_info("Cancelled.")
            raise typer.Exit(0)
    
    print_success(f"Context Mesh initialized for '{name}'!")
    console.print("\n[bold]Next steps:[/bold]")
    console.print("  1. Edit [cyan]context/intent/project-intent.md[/cyan] with your details")
    console.print("  2. Run [cyan]cm /intent add-feature[/cyan] to add features")
    console.print("  3. Use your AI agent to start building!\n")


@intent_app.command("add-feature")
def add_feature(
    name: Optional[str] = typer.Option(None, "--name", "-n", help="Feature name"),
    interactive: bool = typer.Option(True, "--interactive/--no-interactive", "-i", help="Interactive mode"),
):
    """Add a new feature intent.
    
    Creates a feature intent file with What, Why, and Acceptance Criteria,
    plus an optional technical decision (ADR).
    
    Examples:
        cm /intent add-feature
        cm /intent add-feature --name "user-auth"
    """
    console.print("\n[bold]Context Mesh - Add Feature[/bold]\n")
    
    repo_root = get_repo_root()
    mcp = MCPClient(repo_root)
    
    # Check context exists
    if repo_root and not (repo_root / "context").exists():
        print_error("Context Mesh not initialized. Run 'cm /intent new-project' first.")
        raise typer.Exit(1)
    
    # Get feature info
    if not name:
        name = Prompt.ask("Feature name (slug format, e.g., user-auth)")
    
    # Normalize name
    name = name.lower().replace(" ", "-").replace("_", "-")
    
    if interactive:
        console.print(f"\n[bold]Feature: {name}[/bold]\n")
        
        what = Prompt.ask("What does this feature do?")
        why = Prompt.ask("Why do we need it?")
        
        console.print("\n[bold]Acceptance Criteria (one per line, empty line to finish):[/bold]")
        criteria = []
        while True:
            criterion = Prompt.ask(f"  {len(criteria) + 1}", default="")
            if not criterion:
                break
            criteria.append(criterion)
        
        # Technical decision
        console.print("\n[bold]Technical Decision (ADR)[/bold]")
        needs_decision = Confirm.ask("Create a technical decision for this feature?", default=True)
        
        decision_context = ""
        decision_approach = ""
        decision_rationale = ""
        
        if needs_decision:
            decision_context = Prompt.ask("Context (situation, constraints)")
            decision_approach = Prompt.ask("Chosen approach")
            decision_rationale = Prompt.ask("Why this approach?")
    else:
        what = ""
        why = ""
        criteria = []
        needs_decision = False
        decision_context = ""
        decision_approach = ""
        decision_rationale = ""
    
    # Call MCP
    async def create():
        result = await mcp.call_tool("cm_add_feature", {"repo_root": str(repo_root)})
        return result
    
    result = _run_async(create())
    
    if not result.success:
        print_error(f"Failed: {result.error}")
        raise typer.Exit(1)
    
    # Show template
    if hasattr(result, 'content') and isinstance(result.content, dict):
        content = result.content
        if 'prompt_template' in content:
            console.print("\n[dim]Template loaded. Creating files...[/dim]")
    
    print_success(f"Feature '{name}' added!")
    console.print(f"\n  Created: [cyan]context/intent/feature-{name}.md[/cyan]")
    if needs_decision:
        console.print(f"  Created: [cyan]context/decisions/XXX-{name}.md[/cyan]")
    
    console.print("\n[bold]Next steps:[/bold]")
    console.print("  1. Review and edit the feature intent")
    console.print("  2. Run [cyan]cm /build plan <feature>[/cyan] to create a build plan")


@intent_app.command("fix-bug")
def fix_bug(
    name: Optional[str] = typer.Option(None, "--name", "-n", help="Bug identifier"),
    interactive: bool = typer.Option(True, "--interactive/--no-interactive", "-i", help="Interactive mode"),
):
    """Document a bug fix intent.
    
    Creates a bug intent file with description, impact, and root cause.
    
    Examples:
        cm /intent fix-bug
        cm /intent fix-bug --name "login-timeout"
    """
    console.print("\n[bold]Context Mesh - Fix Bug[/bold]\n")
    
    repo_root = get_repo_root()
    mcp = MCPClient(repo_root)
    
    # Check context exists
    if repo_root and not (repo_root / "context").exists():
        print_error("Context Mesh not initialized. Run 'cm /intent new-project' first.")
        raise typer.Exit(1)
    
    if not name:
        name = Prompt.ask("Bug identifier (slug format)")
    
    name = name.lower().replace(" ", "-").replace("_", "-")
    
    if interactive:
        console.print(f"\n[bold]Bug: {name}[/bold]\n")
        
        description = Prompt.ask("Bug description")
        expected = Prompt.ask("Expected behavior")
        actual = Prompt.ask("Actual behavior")
        impact = Prompt.ask("Impact (low/medium/high)", default="medium")
        related_feature = Prompt.ask("Related feature (if any)", default="")
    else:
        description = ""
        expected = ""
        actual = ""
        impact = "medium"
        related_feature = ""
    
    # Call MCP
    async def create():
        result = await mcp.call_tool("cm_fix_bug", {"repo_root": str(repo_root)})
        return result
    
    result = _run_async(create())
    
    if not result.success:
        print_error(f"Failed: {result.error}")
        raise typer.Exit(1)
    
    print_success(f"Bug '{name}' documented!")
    console.print(f"\n  Created: [cyan]context/intent/bug-{name}.md[/cyan]")
    
    console.print("\n[bold]Next steps:[/bold]")
    console.print("  1. Review and complete the bug intent")
    console.print("  2. Fix the bug")
    console.print("  3. Run [cyan]cm /learn sync[/cyan] to update context")


@intent_app.command("update")
def update_feature(
    name: str = typer.Argument(..., help="Feature name to update"),
    interactive: bool = typer.Option(True, "--interactive/--no-interactive", "-i", help="Interactive mode"),
):
    """Update an existing feature intent.
    
    Modifies an existing feature file. Git preserves history.
    
    Examples:
        cm /intent update user-auth
    """
    console.print(f"\n[bold]Context Mesh - Update Feature: {name}[/bold]\n")
    
    repo_root = get_repo_root()
    mcp = MCPClient(repo_root)
    
    # Call MCP
    async def update():
        result = await mcp.call_tool("cm_update_feature", {
            "feature_name": name,
            "repo_root": str(repo_root)
        })
        return result
    
    result = _run_async(update())
    
    if not result.success:
        print_error(f"Failed: {result.error}")
        raise typer.Exit(1)
    
    # Show current content
    if hasattr(result, 'content') and isinstance(result.content, dict):
        content = result.content
        if 'current_content' in content and content['current_content']:
            console.print("[bold]Current content:[/bold]")
            console.print(Panel(content['current_content'][:500] + "...", title=f"feature-{name}.md"))
    
    if interactive:
        console.print("\n[bold]What's changing?[/bold]")
        what_changed = Prompt.ask("Description of changes")
        why_changed = Prompt.ask("Why this change?")
        
        needs_new_decision = Confirm.ask("Does this require a new technical decision?", default=False)
    
    print_success(f"Feature '{name}' update recorded!")
    console.print("\n[dim]Remember: Update the same file - Git preserves history.[/dim]")


@intent_app.command("create-agent")
def create_agent(
    name: Optional[str] = typer.Option(None, "--name", "-n", help="Agent name"),
    interactive: bool = typer.Option(True, "--interactive/--no-interactive", "-i", help="Interactive mode"),
):
    """Create a reusable execution agent.
    
    Creates an agent file with purpose, context files, and execution steps.
    
    Examples:
        cm /intent create-agent
        cm /intent create-agent --name "api-developer"
    """
    console.print("\n[bold]Context Mesh - Create Agent[/bold]\n")
    
    repo_root = get_repo_root()
    mcp = MCPClient(repo_root)
    
    if not name:
        name = Prompt.ask("Agent name (e.g., api-developer)")
    
    name = name.lower().replace(" ", "-").replace("_", "-")
    
    if interactive:
        console.print(f"\n[bold]Agent: {name}[/bold]\n")
        
        purpose = Prompt.ask("What does this agent do?")
        
        console.print("\n[bold]Context files to load (comma-separated):[/bold]")
        context_files = Prompt.ask("Files", default="@context/intent/project-intent.md")
        
        console.print("\n[bold]Execution steps (one per line, empty line to finish):[/bold]")
        steps = []
        while True:
            step = Prompt.ask(f"  Step {len(steps) + 1}", default="")
            if not step:
                break
            steps.append(step)
        
        console.print("\n[bold]Definition of Done (one per line, empty line to finish):[/bold]")
        dod = []
        while True:
            item = Prompt.ask(f"  Criterion {len(dod) + 1}", default="")
            if not item:
                break
            dod.append(item)
    
    # Call MCP
    async def create():
        result = await mcp.call_tool("cm_create_agent", {"repo_root": str(repo_root)})
        return result
    
    result = _run_async(create())
    
    if not result.success:
        print_error(f"Failed: {result.error}")
        raise typer.Exit(1)
    
    print_success(f"Agent '{name}' created!")
    console.print(f"\n  Created: [cyan]context/agents/agent-{name}.md[/cyan]")
    
    console.print("\n[bold]Next steps:[/bold]")
    console.print("  1. Review and refine the agent")
    console.print("  2. Reference it in AGENTS.md")
    console.print("  3. Use it: @context/agents/agent-{name}.md")


@intent_app.command("status")
def intent_status():
    """Show status of all intents (features, bugs, agents).
    
    Lists all intent files with their current status.
    
    Examples:
        cm /intent status
    """
    console.print("\n[bold]Context Mesh - Intent Status[/bold]\n")
    
    repo_root = get_repo_root()
    mcp = MCPClient(repo_root)
    
    async def get_status():
        # Get features
        features_result = await mcp.call_tool("cm_list_features", {"repo_root": str(repo_root)})
        return features_result
    
    result = _run_async(get_status())
    
    if not result.success:
        print_error(f"Failed: {result.error}")
        raise typer.Exit(1)
    
    if hasattr(result, 'content') and isinstance(result.content, dict):
        content = result.content
        features = content.get('features', [])
        
        if features:
            console.print("[bold]Features:[/bold]")
            for f in features:
                status_icon = {
                    "Active": "[yellow]●[/yellow]",
                    "Completed": "[green]✓[/green]",
                    "Draft": "[dim]○[/dim]",
                    "Blocked": "[red]✗[/red]",
                }.get(f.get('status', 'Unknown'), "[dim]?[/dim]")
                
                console.print(f"  {status_icon} [bold]{f['name']}[/bold] - {f.get('status', 'Unknown')}")
                if f.get('summary'):
                    console.print(f"      [dim]{f['summary'][:60]}...[/dim]")
        else:
            console.print("[dim]No features found. Run 'cm /intent add-feature' to add one.[/dim]")
    
    console.print()
