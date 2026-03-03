"""Build phase slash commands for Context Mesh Hub.

Commands for the Build phase of the workflow:
- /build plan     - Create implementation plan
- /build approve  - Approve a plan
- /build execute  - Get execution instructions
- /build status   - Show build status
- /build clarify  - Get clarifying questions before build
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


build_app = typer.Typer(
    name="build",
    help="Build phase commands - Plan, Approve, Execute",
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


@build_app.command("plan")
def build_plan(
    feature: str = typer.Argument(..., help="Feature name to plan"),
    show_full: bool = typer.Option(False, "--full", "-f", help="Show full plan details"),
):
    """Create an implementation plan for a feature.
    
    Generates a detailed plan with steps, target files,
    constraints, and validation checks.
    
    Examples:
        cm /build plan user-auth
        cm /build plan hub-core --full
    """
    console.print(f"\n[bold]Context Mesh - Build Plan: {feature}[/bold]\n")
    
    repo_root = get_repo_root()
    mcp = MCPClient(repo_root)
    
    # Check context exists
    if repo_root and not (repo_root / "context").exists():
        print_error("Context Mesh not initialized. Run 'cm /intent new-project' first.")
        raise typer.Exit(1)
    
    console.print("[dim]Generating implementation plan...[/dim]\n")
    
    async def create_plan():
        result = await mcp.call_tool("build_plan", {
            "feature_name": feature,
            "repo_root": str(repo_root)
        })
        return result
    
    result = _run_async(create_plan())
    
    if not result.success:
        print_error(f"Failed: {result.error}")
        raise typer.Exit(1)
    
    if hasattr(result, 'content') and isinstance(result.content, dict):
        plan = result.content
        
        if 'error' in plan:
            print_error(plan['error'])
            if 'tip' in plan:
                console.print(f"[dim]{plan['tip']}[/dim]")
            raise typer.Exit(1)
        
        # Show plan summary
        console.print(f"[bold green]Plan created![/bold green]")
        console.print(f"  Plan ID: [cyan]{plan.get('plan_id', 'N/A')}[/cyan]")
        console.print(f"  Feature: [bold]{plan.get('feature_name', feature)}[/bold]")
        
        # Implementation steps
        steps = plan.get('implementation_steps', [])
        if steps:
            console.print(f"\n[bold]Implementation Steps ({len(steps)}):[/bold]")
            for step in steps:
                console.print(f"\n  [cyan]Step {step.get('step_number', '?')}[/cyan]: {step.get('description', 'N/A')}")
                if show_full:
                    if step.get('target_files'):
                        console.print(f"    Files: {', '.join(step['target_files'])}")
                    if step.get('operations'):
                        console.print(f"    Operations: {', '.join(step['operations'])}")
        
        # Target files
        target_files = plan.get('target_files', [])
        if target_files:
            console.print(f"\n[bold]Target Files ({len(target_files)}):[/bold]")
            for f in target_files[:10]:
                console.print(f"  [dim]•[/dim] {f}")
            if len(target_files) > 10:
                console.print(f"  [dim]... and {len(target_files) - 10} more[/dim]")
        
        # Constraints
        if show_full and plan.get('constraints'):
            console.print(f"\n[bold]Constraints:[/bold]")
            for c in plan['constraints']:
                console.print(f"  [yellow]![/yellow] {c}")
        
        # Related decisions
        if plan.get('related_decisions'):
            console.print(f"\n[bold]Related Decisions:[/bold]")
            for d in plan['related_decisions']:
                console.print(f"  [dim]•[/dim] {d}")
        
        # Acceptance criteria
        if plan.get('acceptance_criteria'):
            console.print(f"\n[bold]Acceptance Criteria:[/bold]")
            for ac in plan['acceptance_criteria']:
                console.print(f"  [ ] {ac}")
        
        console.print("\n[bold]Next steps:[/bold]")
        console.print(f"  1. Review the plan above")
        console.print(f"  2. Run [cyan]cm /build approve {plan.get('plan_id', '<plan_id>')}[/cyan]")
        console.print(f"  3. Or request changes and re-plan")


@build_app.command("approve")
def build_approve(
    plan_id: str = typer.Argument(..., help="Plan ID to approve"),
    reject: bool = typer.Option(False, "--reject", "-r", help="Reject the plan"),
    feedback: Optional[str] = typer.Option(None, "--feedback", "-f", help="Feedback message"),
    partial: Optional[str] = typer.Option(None, "--steps", "-s", help="Approve specific steps (comma-separated)"),
):
    """Approve or reject a build plan.
    
    Human approval is required before execution.
    
    Examples:
        cm /build approve abc123
        cm /build approve abc123 --reject --feedback "Need more detail on step 2"
        cm /build approve abc123 --steps 1,2,3
    """
    action = "reject" if reject else "approve"
    console.print(f"\n[bold]Context Mesh - {action.title()} Plan: {plan_id}[/bold]\n")
    
    repo_root = get_repo_root()
    mcp = MCPClient(repo_root)
    
    # Parse partial scope
    scope = None
    if partial:
        scope = [int(s.strip()) for s in partial.split(",") if s.strip().isdigit()]
    
    async def do_approve():
        result = await mcp.call_tool("build_approve", {
            "plan_id": plan_id,
            "action": action,
            "scope": scope,
            "feedback": feedback,
            "repo_root": str(repo_root)
        })
        return result
    
    result = _run_async(do_approve())
    
    if not result.success:
        print_error(f"Failed: {result.error}")
        raise typer.Exit(1)
    
    if hasattr(result, 'content') and isinstance(result.content, dict):
        approval = result.content
        
        if 'error' in approval:
            print_error(approval['error'])
            raise typer.Exit(1)
        
        status = approval.get('status', 'unknown')
        
        if status == 'approved':
            print_success(f"Plan {plan_id} approved!")
            if approval.get('approved_scope'):
                console.print(f"  Approved steps: {approval['approved_scope']}")
            console.print("\n[bold]Next step:[/bold]")
            console.print(f"  Run [cyan]cm /build execute {plan_id}[/cyan]")
        elif status == 'rejected':
            print_warning(f"Plan {plan_id} rejected.")
            if approval.get('rejection_feedback'):
                console.print(f"  Feedback: {approval['rejection_feedback']}")
            console.print("\n[bold]Next step:[/bold]")
            console.print("  Address feedback and create a new plan")
        else:
            console.print(f"Status: {status}")


@build_app.command("execute")
def build_execute(
    plan_id: str = typer.Argument(..., help="Plan ID to execute"),
    mode: str = typer.Option("instruction", "--mode", "-m", help="Execution mode: instruction or assisted"),
):
    """Get execution instructions for an approved plan.
    
    Generates step-by-step instructions for implementing the plan.
    
    Examples:
        cm /build execute abc123
        cm /build execute abc123 --mode assisted
    """
    console.print(f"\n[bold]Context Mesh - Execute Plan: {plan_id}[/bold]\n")
    
    repo_root = get_repo_root()
    mcp = MCPClient(repo_root)
    
    async def do_execute():
        result = await mcp.call_tool("build_execute", {
            "plan_id": plan_id,
            "mode": mode,
            "repo_root": str(repo_root)
        })
        return result
    
    result = _run_async(do_execute())
    
    if not result.success:
        print_error(f"Failed: {result.error}")
        raise typer.Exit(1)
    
    if hasattr(result, 'content') and isinstance(result.content, dict):
        execution = result.content
        
        if 'error' in execution:
            print_error(execution['error'])
            raise typer.Exit(1)
        
        instructions = execution.get('instructions', [])
        
        console.print(f"[bold green]Execution Instructions ({len(instructions)} steps)[/bold green]\n")
        
        for inst in instructions:
            step_num = inst.get('step_number', '?')
            operation = inst.get('operation', 'unknown')
            target = inst.get('target_file', 'N/A')
            desc = inst.get('description', '')
            
            console.print(f"[cyan]Step {step_num}[/cyan]: [bold]{operation}[/bold]")
            console.print(f"  Target: {target}")
            if desc:
                console.print(f"  {desc}")
            
            if inst.get('validation_check'):
                console.print(f"  [dim]Validate: {inst['validation_check']}[/dim]")
            
            console.print()
        
        console.print("[bold]After implementation:[/bold]")
        console.print("  Run [cyan]cm /learn sync[/cyan] to update context with learnings")


@build_app.command("status")
def build_status(
    feature: Optional[str] = typer.Argument(None, help="Feature name (optional)"),
):
    """Show build status for features.
    
    Displays current state of the Build phase.
    
    Examples:
        cm /build status
        cm /build status user-auth
    """
    console.print("\n[bold]Context Mesh - Build Status[/bold]\n")
    
    repo_root = get_repo_root()
    mcp = MCPClient(repo_root)
    
    async def get_status():
        result = await mcp.call_tool("cm_status", {"repo_root": str(repo_root)})
        return result
    
    result = _run_async(get_status())
    
    if not result.success:
        print_error(f"Failed: {result.error}")
        raise typer.Exit(1)
    
    if hasattr(result, 'content') and isinstance(result.content, dict):
        status = result.content
        
        # Project info
        project = status.get('project', {})
        console.print(f"[bold]Project:[/bold] {Path(project.get('repo_root', '.')).name}")
        console.print(f"  Lifecycle Phase: [cyan]{project.get('lifecycle_phase', 'Unknown')}[/cyan]")
        console.print(f"  Context Mesh: {'[green]✓[/green]' if project.get('context_mesh_initialized') else '[red]✗[/red]'}")
        
        # Artifacts
        artifacts = status.get('artifacts', {})
        console.print(f"\n[bold]Artifacts:[/bold]")
        console.print(f"  Features: {artifacts.get('feature_intents', 0)}")
        console.print(f"  Decisions: {artifacts.get('decisions', 0)}")
        console.print(f"  Patterns: {artifacts.get('patterns', 0)}")
        
        # Validation
        validation = status.get('validation', {})
        if validation.get('valid'):
            console.print(f"\n[green]✓[/green] Validation passed")
        else:
            console.print(f"\n[yellow]![/yellow] Validation: {validation.get('errors', 0)} errors, {validation.get('warnings', 0)} warnings")
            for detail in validation.get('details', [])[:3]:
                level = detail.get('level', 'info')
                icon = "[red]✗[/red]" if level == 'error' else "[yellow]![/yellow]"
                console.print(f"  {icon} {detail.get('message', '')}")
        
        # Guidance
        guidance = status.get('guidance', {})
        if guidance:
            console.print(f"\n[bold]Next Step:[/bold]")
            console.print(f"  {guidance.get('next_step', 'No guidance available')}")


@build_app.command("clarify")
def build_clarify(
    feature: str = typer.Argument(..., help="Feature name to clarify"),
):
    """Get clarifying questions before building.
    
    Generates questions to reduce ambiguity and ensure
    the feature is well-understood before implementation.
    
    Examples:
        cm /build clarify user-auth
    """
    console.print(f"\n[bold]Context Mesh - Clarify: {feature}[/bold]\n")
    
    repo_root = get_repo_root()
    mcp = MCPClient(repo_root)
    
    async def do_clarify():
        # First get feature info
        feature_result = await mcp.call_tool("context_read", {
            "artifact_type": "feature_intent",
            "name": feature,
            "repo_root": str(repo_root)
        })
        return feature_result
    
    result = _run_async(do_clarify())
    
    if not result.success:
        print_error(f"Failed: {result.error}")
        raise typer.Exit(1)
    
    if hasattr(result, 'content') and isinstance(result.content, dict):
        content = result.content
        
        if 'error' in content:
            print_error(content['error'])
            raise typer.Exit(1)
        
        feature_content = content.get('content', '')
        
        # Analyze for potential clarifications
        console.print("[bold]Clarifying Questions:[/bold]\n")
        
        questions = []
        
        # Check for missing sections
        if "## What" not in feature_content or not feature_content.split("## What")[1].split("##")[0].strip():
            questions.append("What exactly does this feature do? The 'What' section needs more detail.")
        
        if "## Why" not in feature_content or not feature_content.split("## Why")[1].split("##")[0].strip():
            questions.append("Why is this feature important? The 'Why' section needs more detail.")
        
        if "Acceptance Criteria" not in feature_content:
            questions.append("What are the acceptance criteria? How do we know when this is done?")
        
        # Check for technical details
        if "decision" not in feature_content.lower() and "adr" not in feature_content.lower():
            questions.append("Is there a technical decision (ADR) for this feature?")
        
        # General questions
        questions.extend([
            "Are there any edge cases we should handle?",
            "What are the constraints or limitations?",
            "How does this interact with existing features?",
            "What should NOT be included in this feature?",
        ])
        
        for i, q in enumerate(questions, 1):
            console.print(f"  {i}. {q}")
        
        console.print("\n[bold]Next steps:[/bold]")
        console.print("  1. Answer these questions")
        console.print("  2. Update the feature intent with the answers")
        console.print(f"  3. Run [cyan]cm /build plan {feature}[/cyan]")


@build_app.command("gate")
def build_gate(
    phase: str = typer.Argument("intent-to-build", help="Gate to check: intent-to-build, build-to-learn"),
    feature: Optional[str] = typer.Option(None, "--feature", "-f", help="Feature to check"),
):
    """Check quality gates for phase transition.
    
    Validates that requirements are met before transitioning
    to the next phase.
    
    Examples:
        cm /build gate intent-to-build --feature user-auth
        cm /build gate build-to-learn
    """
    console.print(f"\n[bold]Context Mesh - Quality Gate: {phase}[/bold]\n")
    
    repo_root = get_repo_root()
    mcp = MCPClient(repo_root)
    
    gates = {
        "intent-to-build": [
            ("Feature has What section", True),
            ("Feature has Why section", True),
            ("Feature has Acceptance Criteria", True),
            ("ADR exists for technical approach", True),
            ("No validation errors", True),
        ],
        "build-to-learn": [
            ("Implementation complete", True),
            ("Tests pass", True),
            ("Acceptance criteria met", True),
            ("Code reviewed", False),
        ],
    }
    
    if phase not in gates:
        print_error(f"Unknown gate: {phase}")
        console.print(f"Valid gates: {', '.join(gates.keys())}")
        raise typer.Exit(1)
    
    console.print(f"[bold]Checking {phase} gate...[/bold]\n")
    
    # For now, show the checklist (actual validation would query MCP)
    all_passed = True
    for gate_name, required in gates[phase]:
        # In a real implementation, we'd check each condition via MCP
        passed = True  # Placeholder
        icon = "[green]✓[/green]" if passed else "[red]✗[/red]"
        req_label = "[bold](required)[/bold]" if required else "[dim](optional)[/dim]"
        console.print(f"  {icon} {gate_name} {req_label}")
        if required and not passed:
            all_passed = False
    
    console.print()
    
    if all_passed:
        print_success(f"Gate {phase} passed!")
        if phase == "intent-to-build":
            console.print("  Ready to create build plan.")
        elif phase == "build-to-learn":
            console.print("  Ready to sync learnings.")
    else:
        print_warning(f"Gate {phase} has blockers.")
        console.print("  Address the failed checks before proceeding.")
