import typer
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

from lmcp.core.initializer import initialize 
from lmcp.core.logger import logger
from lmcp.__version__ import __version__, __title__, __description__

console = Console()

app = typer.Typer(
    name="lmcp",
    help="Lazy Minecraft Panel",
    add_completion=False,
    no_args_is_help=True,
    invoke_without_command=True,
)

@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    help: bool = typer.Option(False, "--help", "-h", help="Show this message and exit."),
    debug: bool = typer.Option(False, "--debug", help="Enable debug mode for more verbose output.", is_flag=True),
    version: bool = typer.Option(False, "--version", "-v", help="Show the version of LMCP."),
):
    """
    Lazy Minecraft Panel CLI.
    """
    ctx.meta["debug"] = debug
    if debug:
        logger.setLevel("DEBUG")
        logger.debug("Debug mode enabled")
    
    if version:
        _show_version()
        raise typer.Exit()
    
    if help:
        _show_help()
        raise typer.Exit()
    
    # If no subcommand is invoked, show help
    if ctx.invoked_subcommand is None:
        _show_help()
        raise typer.Exit()

def _show_version():
    """Show the version information of LMCP"""
    version_text = Text()
    version_text.append("LMCP ", style="bold blue")
    version_text.append(f"v{__version__}", style="bold green")
    
    info_panel = Panel(
        version_text,
        title=f"[bold]{__title__}[/bold]",
        subtitle=f"[dim]{__description__}[/dim]",
        border_style="blue",
        padding=(1, 2)
    )
    
    console.print(info_panel)

def _show_help():
    """Show help information"""
    help_text = f"""[bold blue]Usage:[/bold blue] lmcp [OPTIONS] COMMAND [ARGS]...

[bold green]Commands:[/bold green]
  [blue]init[/blue]    Initialize the LMCP workspace

[bold green]Options:[/bold green]
  [blue]--help, -h[/blue]     Show this message and exit
  [blue]--debug[/blue]        Enable debug mode for more verbose output
  [blue]--version, -v[/blue]  Show the version of LMCP
"""
    
    help_panel = Panel(
        help_text,
        title=f"[bold]{__title__} - Help[/bold]",
        border_style="green",
        padding=(1, 2)
    )
    
    console.print(help_panel)

@app.command()
def init(
    help: bool = typer.Option(False, "--help", "-h", help="Show this message and exit."),
    directory: str = typer.Option(".", "--directory", "-d", help="Directory to initialize the LMCP workspace.")
):
    """
    Initialize the LMCP workspace.
    """
    initialize(help=help, directory=directory)
    