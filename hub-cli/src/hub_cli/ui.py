"""UI components for the CLI with Rich."""

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


def print_mcp_config(config: dict):
    """Print MCP configuration in a styled box."""
    import json
    
    config_json = json.dumps(config, indent=2)
    
    console.print()
    console.print(Panel(
        f"[bold white]{config_json}[/bold white]",
        title="[bold cyan]📋 MCP Configuration[/bold cyan]",
        subtitle="[dim]Copy to your AI editor settings[/dim]",
        border_style=Style(color=BLUE),
        box=ROUNDED,
        padding=(1, 2),
    ))
    
    # Supported editors
    console.print()
    table = Table(show_header=False, box=None, padding=(0, 2))
    table.add_column("Editor", style="bold")
    table.add_column("Location", style="dim")
    
    table.add_row("Cursor", "Settings → Features → MCP Servers")
    table.add_row("VS Code + Copilot", "Settings → GitHub Copilot → MCP")
    table.add_row("Claude Desktop", "~/Library/Application Support/Claude/claude_desktop_config.json")
    table.add_row("Any MCP editor", "Check editor documentation")
    
    console.print(Panel(
        table,
        title="[bold]Supported Editors[/bold]",
        border_style=Style(color=GRAY),
        box=ROUNDED,
    ))


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
