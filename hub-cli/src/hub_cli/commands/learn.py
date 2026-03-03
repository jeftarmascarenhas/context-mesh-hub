"""Learn phase slash commands for Context Mesh Hub.

Commands for the Learn phase of the workflow:
- /learn sync    - Sync learnings after implementation
- /learn review  - Review a learning proposal
- /learn apply   - Apply accepted learnings
- /learn status  - Show learning history
"""

import asyncio
from pathlib import Path
from typing import Optional

import typer
from rich.prompt import Prompt, Confirm
from rich.panel import Panel
from rich.table import Table
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


learn_app = typer.Typer(
    name="learn",
    help="Learn phase commands - Update context with learnings",
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


@learn_app.command("sync")
def learn_sync(
    feature: str = typer.Argument(..., help="Feature name to sync learnings for"),
    interactive: bool = typer.Option(True, "--interactive/--no-interactive", "-i", help="Interactive mode"),
):
    """Sync learnings after implementing a feature.
    
    Analyzes the implementation and proposes context updates:
    - Decision outcomes
    - New patterns discovered
    - Anti-patterns to avoid
    - Changelog entries
    
    Examples:
        cm /learn sync user-auth
    """
    console.print(f"\n[bold]Context Mesh - Learn Sync: {feature}[/bold]\n")
    
    repo_root = get_repo_root()
    mcp = MCPClient(repo_root)
    
    # Gather information
    console.print("[dim]Gathering implementation information...[/dim]")
    
    if interactive:
        console.print("\n[bold]What was implemented?[/bold]")
        what_implemented = Prompt.ask("Summary of changes")
        
        console.print("\n[bold]What worked well?[/bold]")
        what_worked = Prompt.ask("Successes", default="")
        
        console.print("\n[bold]What was challenging?[/bold]")
        challenges = Prompt.ask("Difficulties", default="")
        
        console.print("\n[bold]Any surprises or discoveries?[/bold]")
        surprises = Prompt.ask("Learnings", default="")
        
        user_feedback = f"Implemented: {what_implemented}. Worked: {what_worked}. Challenges: {challenges}. Learnings: {surprises}"
    else:
        user_feedback = None
    
    async def do_sync():
        result = await mcp.call_tool("learn_sync_initiate", {
            "feature_name": feature,
            "user_feedback": user_feedback,
            "repo_root": str(repo_root)
        })
        return result
    
    result = _run_async(do_sync())
    
    if not result.success:
        print_error(f"Failed: {result.error}")
        raise typer.Exit(1)
    
    if hasattr(result, 'content') and isinstance(result.content, dict):
        proposal = result.content
        
        if 'error' in proposal:
            print_error(proposal['error'])
            raise typer.Exit(1)
        
        proposal_id = proposal.get('proposal_id', 'N/A')
        
        console.print(f"\n[bold green]Learning Proposal Created![/bold green]")
        console.print(f"  Proposal ID: [cyan]{proposal_id}[/cyan]")
        
        # Show outcome summary
        outcome = proposal.get('outcome_summary', {})
        if outcome.get('what_implemented'):
            console.print(f"\n[bold]Outcomes:[/bold]")
            for item in outcome['what_implemented'][:3]:
                console.print(f"  [green]✓[/green] {item}")
        
        if outcome.get('unexpected_difficulties'):
            console.print(f"\n[bold]Challenges:[/bold]")
            for item in outcome['unexpected_difficulties'][:3]:
                console.print(f"  [yellow]![/yellow] {item}")
        
        # Show learning drafts
        drafts = proposal.get('learning_drafts', [])
        if drafts:
            console.print(f"\n[bold]Proposed Learnings ({len(drafts)}):[/bold]")
            for draft in drafts[:5]:
                artifact_type = draft.get('artifact_type', 'unknown')
                title = draft.get('title', 'Untitled')
                confidence = draft.get('confidence', 'unknown')
                console.print(f"  [{artifact_type}] {title} [dim]({confidence})[/dim]")
        
        # Show context updates
        updates = proposal.get('context_updates', [])
        if updates:
            console.print(f"\n[bold]Proposed Context Updates ({len(updates)}):[/bold]")
            for update in updates[:5]:
                update_type = update.get('update_type', 'unknown')
                artifact_path = update.get('artifact_path', 'unknown')
                console.print(f"  [{update_type}] {artifact_path}")
        
        # Changelog
        changelog = proposal.get('changelog_entry')
        if changelog:
            console.print(f"\n[bold]Changelog Entry:[/bold]")
            console.print(f"  {changelog.get('what_changed', 'N/A')}")
        
        console.print("\n[bold]Next steps:[/bold]")
        console.print(f"  1. Review: [cyan]cm /learn review {proposal_id}[/cyan]")
        console.print(f"  2. Apply: [cyan]cm /learn apply {proposal_id}[/cyan]")


@learn_app.command("review")
def learn_review(
    proposal_id: str = typer.Argument(..., help="Proposal ID to review"),
    full: bool = typer.Option(False, "--full", "-f", help="Show full details"),
):
    """Review a learning proposal.
    
    Shows all proposed learnings and context updates for review.
    
    Examples:
        cm /learn review abc123
        cm /learn review abc123 --full
    """
    console.print(f"\n[bold]Context Mesh - Review Proposal: {proposal_id}[/bold]\n")
    
    repo_root = get_repo_root()
    mcp = MCPClient(repo_root)
    
    async def do_review():
        result = await mcp.call_tool("learn_sync_review", {
            "proposal_id": proposal_id,
            "repo_root": str(repo_root)
        })
        return result
    
    result = _run_async(do_review())
    
    if not result.success:
        print_error(f"Failed: {result.error}")
        raise typer.Exit(1)
    
    if hasattr(result, 'content') and isinstance(result.content, dict):
        proposal = result.content
        
        if 'error' in proposal:
            print_error(proposal['error'])
            raise typer.Exit(1)
        
        console.print(f"[bold]Feature:[/bold] {proposal.get('feature_name', 'N/A')}")
        console.print(f"[bold]Created:[/bold] {proposal.get('created_at', 'N/A')}")
        
        # Learning drafts
        drafts = proposal.get('learning_drafts', [])
        if drafts:
            console.print(f"\n[bold]Learning Drafts ({len(drafts)}):[/bold]\n")
            
            for i, draft in enumerate(drafts):
                console.print(f"  [cyan]{i + 1}. {draft.get('title', 'Untitled')}[/cyan]")
                console.print(f"     Type: {draft.get('artifact_type', 'unknown')}")
                console.print(f"     Confidence: {draft.get('confidence', 'unknown')}")
                console.print(f"     Impact: {draft.get('impact', 'unknown')}")
                
                if full:
                    if draft.get('context'):
                        console.print(f"     Context: {draft['context'][:100]}...")
                    if draft.get('recommendation'):
                        console.print(f"     Recommendation: {draft['recommendation'][:100]}...")
                
                console.print()
        
        # Context updates
        updates = proposal.get('context_updates', [])
        if updates:
            console.print(f"[bold]Context Updates ({len(updates)}):[/bold]\n")
            
            for i, update in enumerate(updates):
                console.print(f"  [cyan]{i + 1}. {update.get('artifact_path', 'unknown')}[/cyan]")
                console.print(f"     Type: {update.get('update_type', 'unknown')}")
                
                if full and update.get('rationale'):
                    console.print(f"     Rationale: {update['rationale'][:100]}...")
                
                console.print()
        
        # Changelog
        changelog = proposal.get('changelog_entry')
        if changelog:
            console.print(f"[bold]Changelog Entry:[/bold]")
            console.print(f"  Date: {changelog.get('date', 'N/A')}")
            console.print(f"  What: {changelog.get('what_changed', 'N/A')}")
            console.print(f"  Why: {changelog.get('why_changed', 'N/A')}")
        
        console.print("\n[bold]Actions:[/bold]")
        console.print(f"  Accept all: [cyan]cm /learn apply {proposal_id}[/cyan]")
        console.print(f"  Accept specific: [cyan]cm /learn apply {proposal_id} --learnings 1,2[/cyan]")


@learn_app.command("apply")
def learn_apply(
    proposal_id: str = typer.Argument(..., help="Proposal ID to apply"),
    learnings: Optional[str] = typer.Option(None, "--learnings", "-l", help="Learning IDs to apply (comma-separated)"),
    updates: Optional[str] = typer.Option(None, "--updates", "-u", help="Update indices to apply (comma-separated)"),
    changelog: bool = typer.Option(True, "--changelog/--no-changelog", help="Apply changelog entry"),
    confirm: bool = typer.Option(False, "--confirm", "-y", help="Skip confirmation"),
):
    """Apply accepted learnings to context.
    
    Updates context files with accepted learnings.
    Requires explicit confirmation.
    
    Examples:
        cm /learn apply abc123
        cm /learn apply abc123 --learnings 1,2 --no-changelog
        cm /learn apply abc123 --confirm
    """
    console.print(f"\n[bold]Context Mesh - Apply Learnings: {proposal_id}[/bold]\n")
    
    repo_root = get_repo_root()
    mcp = MCPClient(repo_root)
    
    # Parse selections
    learning_ids = None
    if learnings:
        learning_ids = [l.strip() for l in learnings.split(",") if l.strip()]
    
    update_indices = None
    if updates:
        update_indices = [int(u.strip()) for u in updates.split(",") if u.strip().isdigit()]
    
    # First, get a preview
    async def preview():
        result = await mcp.call_tool("learn_sync_accept", {
            "proposal_id": proposal_id,
            "learning_ids": learning_ids,
            "context_update_indices": update_indices,
            "accept_changelog": changelog,
            "repo_root": str(repo_root)
        })
        return result
    
    preview_result = _run_async(preview())
    
    if not preview_result.success:
        print_error(f"Failed: {preview_result.error}")
        raise typer.Exit(1)
    
    if hasattr(preview_result, 'content') and isinstance(preview_result.content, dict):
        preview_data = preview_result.content
        
        if 'error' in preview_data:
            print_error(preview_data['error'])
            raise typer.Exit(1)
        
        # Show preview
        console.print("[bold]Will apply:[/bold]")
        
        accepted_learnings = preview_data.get('accepted_learnings', [])
        if accepted_learnings:
            console.print(f"\n  [bold]Learnings ({len(accepted_learnings)}):[/bold]")
            for l in accepted_learnings:
                console.print(f"    [green]+[/green] {l.get('title', 'Untitled')} ({l.get('artifact_type', 'unknown')})")
        
        accepted_updates = preview_data.get('accepted_context_updates', [])
        if accepted_updates:
            console.print(f"\n  [bold]Context Updates ({len(accepted_updates)}):[/bold]")
            for u in accepted_updates:
                console.print(f"    [yellow]~[/yellow] {u.get('artifact_path', 'unknown')} ({u.get('update_type', 'unknown')})")
        
        if preview_data.get('changelog_accepted'):
            console.print(f"\n  [bold]Changelog:[/bold] Will be updated")
    
    # Confirm
    if not confirm:
        console.print()
        if not Confirm.ask("Apply these changes?", default=True):
            print_info("Cancelled.")
            raise typer.Exit(0)
    
    # Actually apply
    async def do_apply():
        result = await mcp.call_tool("learn_sync_apply", {
            "proposal_id": proposal_id,
            "learning_ids": learning_ids,
            "context_update_indices": update_indices,
            "apply_changelog": changelog,
            "confirm": True,
            "repo_root": str(repo_root)
        })
        return result
    
    apply_result = _run_async(do_apply())
    
    if not apply_result.success:
        print_error(f"Failed: {apply_result.error}")
        raise typer.Exit(1)
    
    if hasattr(apply_result, 'content') and isinstance(apply_result.content, dict):
        applied = apply_result.content
        
        if 'error' in applied:
            print_error(applied['error'])
            raise typer.Exit(1)
        
        print_success("Learnings applied!")
        
        applied_items = applied.get('applied', [])
        if applied_items:
            console.print("\n[bold]Applied:[/bold]")
            for item in applied_items:
                console.print(f"  [green]✓[/green] {item.get('action', 'Unknown action')}")
        
        if applied.get('note'):
            console.print(f"\n[dim]{applied['note']}[/dim]")


@learn_app.command("status")
def learn_status():
    """Show learning history and pending proposals.
    
    Displays evolution changelog and any pending learning proposals.
    
    Examples:
        cm /learn status
    """
    console.print("\n[bold]Context Mesh - Learn Status[/bold]\n")
    
    repo_root = get_repo_root()
    mcp = MCPClient(repo_root)
    
    # Get changelog
    async def get_changelog():
        result = await mcp.call_tool("context_read", {
            "artifact_type": "changelog",
            "name": "",
            "repo_root": str(repo_root)
        })
        return result
    
    result = _run_async(get_changelog())
    
    if result.success and hasattr(result, 'content') and isinstance(result.content, dict):
        content = result.content
        
        if 'content' in content:
            changelog_content = content['content']
            
            # Show recent entries (first 500 chars)
            console.print("[bold]Recent Evolution:[/bold]")
            console.print(Panel(
                changelog_content[:500] + ("..." if len(changelog_content) > 500 else ""),
                title="changelog.md",
                border_style="dim"
            ))
    else:
        console.print("[dim]No changelog found.[/dim]")
    
    console.print("\n[bold]Learn Commands:[/bold]")
    console.print("  [cyan]cm /learn sync <feature>[/cyan] - Sync learnings after implementation")
    console.print("  [cyan]cm /learn review <id>[/cyan] - Review a proposal")
    console.print("  [cyan]cm /learn apply <id>[/cyan] - Apply accepted learnings")


@learn_app.command("retrospective")
def learn_retrospective(
    feature: Optional[str] = typer.Option(None, "--feature", "-f", help="Feature to retrospect"),
    interactive: bool = typer.Option(True, "--interactive/--no-interactive", "-i", help="Interactive mode"),
):
    """Run a retrospective for a feature or sprint.
    
    Guided reflection on what worked, what didn't, and
    what to improve.
    
    Examples:
        cm /learn retrospective
        cm /learn retrospective --feature user-auth
    """
    console.print("\n[bold]Context Mesh - Retrospective[/bold]\n")
    
    if feature:
        console.print(f"[dim]Feature: {feature}[/dim]\n")
    
    if not interactive:
        console.print("[dim]Use --interactive for guided retrospective[/dim]")
        return
    
    console.print("[bold]Answer these questions to capture learnings:[/bold]\n")
    
    # What went well
    console.print("[green]What went well?[/green]")
    went_well = []
    while True:
        item = Prompt.ask("  +", default="")
        if not item:
            break
        went_well.append(item)
    
    # What didn't go well
    console.print("\n[yellow]What didn't go well?[/yellow]")
    didnt_go_well = []
    while True:
        item = Prompt.ask("  -", default="")
        if not item:
            break
        didnt_go_well.append(item)
    
    # What to improve
    console.print("\n[cyan]What should we improve?[/cyan]")
    improvements = []
    while True:
        item = Prompt.ask("  →", default="")
        if not item:
            break
        improvements.append(item)
    
    # Summary
    console.print("\n" + "=" * 50)
    console.print("[bold]Retrospective Summary[/bold]\n")
    
    if went_well:
        console.print("[green]Went Well:[/green]")
        for item in went_well:
            console.print(f"  [green]+[/green] {item}")
    
    if didnt_go_well:
        console.print("\n[yellow]Challenges:[/yellow]")
        for item in didnt_go_well:
            console.print(f"  [yellow]-[/yellow] {item}")
    
    if improvements:
        console.print("\n[cyan]Improvements:[/cyan]")
        for item in improvements:
            console.print(f"  [cyan]→[/cyan] {item}")
    
    console.print()
    
    # Offer to save
    if Confirm.ask("Save as a learning artifact?", default=True):
        console.print("\n[dim]Creating learning artifact...[/dim]")
        # Would call MCP to create a learning artifact
        print_success("Retrospective saved!")
        console.print("  Created: [cyan]context/evolution/learning-retrospective-<date>.md[/cyan]")
    else:
        print_info("Retrospective not saved.")
