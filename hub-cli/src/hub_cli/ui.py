"""UI components for the CLI with Rich."""

from typing import Optional

from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.table import Table
from rich.box import ROUNDED
from rich.style import Style
from rich import print as rprint

console = Console()

# Brand colors
PURPLE = "#8B5CF6"
BLUE = "#3B82F6"
YELLOW = "#FBBF24"
WHITE = "#FFFFFF"
GRAY = "#6B7280"
GREEN = "#10B981"
RED = "#EF4444"


def gradient_text(text: str) -> Text:
    """Create gradient text from purple to blue to yellow."""
    colors = [PURPLE, PURPLE, BLUE, BLUE, YELLOW, YELLOW, WHITE]
    result = Text()
    
    for i, char in enumerate(text):
        color_idx = int(i / len(text) * (len(colors) - 1))
        result.append(char, style=Style(color=colors[color_idx], bold=True))
    
    return result


def print_banner():
    """Print the Context Mesh Hub banner with gradient."""
    # ASCII art logo
    logo_lines = [
        "   ██████╗ ██████╗ ███╗   ██╗████████╗███████╗██╗  ██╗████████╗",
        "  ██╔════╝██╔═══██╗████╗  ██║╚══██╔══╝██╔════╝╚██╗██╔╝╚══██╔══╝",
        "  ██║     ██║   ██║██╔██╗ ██║   ██║   █████╗   ╚███╔╝    ██║   ",
        "  ██║     ██║   ██║██║╚██╗██║   ██║   ██╔══╝   ██╔██╗    ██║   ",
        "  ╚██████╗╚██████╔╝██║ ╚████║   ██║   ███████╗██╔╝ ██╗   ██║   ",
        "   ╚═════╝ ╚═════╝ ╚═╝  ╚═══╝   ╚═╝   ╚══════╝╚═╝  ╚═╝   ╚═╝   ",
    ]
    
    # Create gradient logo
    logo_text = Text()
    for line in logo_lines:
        logo_text.append_text(gradient_text(line))
        logo_text.append("\n")
    
    # Add MESH HUB subtitle
    mesh_hub = Text()
    mesh_hub.append("                        ", style=Style(color=GRAY))
    mesh_hub.append("MESH", style=Style(color=PURPLE, bold=True))
    mesh_hub.append(" ", style=Style(color=GRAY))
    mesh_hub.append("HUB", style=Style(color=BLUE, bold=True))
    logo_text.append_text(mesh_hub)
    logo_text.append("\n\n")
    
    # Add tagline
    tagline = Text()
    tagline.append("   Framework that standardizes Context Engineering processes", 
                   style=Style(color=GRAY, italic=True))
    logo_text.append_text(tagline)
    
    console.print(Panel(
        logo_text,
        border_style=Style(color=PURPLE),
        box=ROUNDED,
        padding=(1, 2),
    ))


def print_success(message: str):
    """Print a success message."""
    console.print(f"[bold green]✓[/bold green] {message}")


def print_error(message: str):
    """Print an error message."""
    console.print(f"[bold red]✗[/bold red] {message}")


def print_warning(message: str):
    """Print a warning message."""
    console.print(f"[bold yellow]⚠[/bold yellow] {message}")


def print_info(message: str):
    """Print an info message."""
    console.print(f"[bold blue]ℹ[/bold blue] {message}")


def print_mcp_config(config: dict, raw: bool = False, editor: Optional[str] = None):
    """Print MCP configuration. Use raw=True for copy-paste friendly JSON only (no borders).

    When editor is set (cursor, copilot, claude, gemini), shows only that editor's paste location.
    When raw=False, prints a short instruction then plain JSON (no Panel around JSON)
    so selecting and copying gives clean JSON without box-drawing characters (│, ─).
    """
    import json
    from hub_cli.config import MCP_EDITORS

    config_json = json.dumps(config, indent=2)

    if raw:
        console.print(config_json)
        return

    editor_name = MCP_EDITORS.get(editor or "", {}).get("name", "your editor")
    console.print()
    console.print("[bold cyan]MCP Configuration[/bold cyan]")
    console.print(f"[dim]Copy the JSON below (from {{ to }}) and paste it in {editor_name}.[/dim]")
    console.print()
    # Plain JSON only — no Panel/box so copy-paste gives clean JSON (no │ or other border chars)
    console.print(config_json)
    console.print()
    if editor and editor in MCP_EDITORS:
        paste = MCP_EDITORS[editor]["paste"]
        console.print("[dim]Where to paste:[/dim]")
        console.print(f"  [bold]{MCP_EDITORS[editor]['name']}[/bold]  {paste}")
    else:
        console.print("[dim]Where to paste:[/dim]")
        for key, info in MCP_EDITORS.items():
            console.print(f"  [bold]{info['name']}[/bold]  {info['paste']}")


def print_status_table(checks: list[tuple[str, bool, str]]):
    """Print a status table with checks."""
    table = Table(show_header=False, box=None, padding=(0, 1))
    table.add_column("Status", width=3)
    table.add_column("Check")
    table.add_column("Details", style="dim")
    
    for name, passed, details in checks:
        status = "[bold green]✓[/bold green]" if passed else "[bold red]✗[/bold red]"
        table.add_row(status, name, details)
    
    console.print(table)


def print_divider():
    """Print a styled divider."""
    console.print()
    console.rule(style=Style(color=GRAY))
    console.print()
