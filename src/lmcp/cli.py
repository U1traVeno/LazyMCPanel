import typer
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from pathlib import Path

from lmcp.core.initializer import initialize 
from lmcp.core.logger import logger
from lmcp.__version__ import __version__, __title__, __description__
from lmcp.core.config import config_manager
from lmcp.core.orchestrator import Orchestrator

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
    
@app.command()
def init(
    help: bool = typer.Option(False, "--help", "-h", help="Show this message and exit."),
    directory: str = typer.Option(".", "--directory", "-d", help="Directory to initialize the LMCP workspace.")
):
    """
    Initialize the LMCP workspace.
    """
    initialize(help=help, directory=directory)

@app.command()
def up(
    ctx: typer.Context,
):
    """
    Generates a compose file and starts the server cluster in the background.
    """
    logger.step("Starting 'up' command...")
    
    # The command should be run from within the project directory.
    # We find the config file upwards from the current directory.
    project_root = Path.cwd()
    config_file_path = config_manager.find_config_file(project_root)
    
    if not config_file_path:
        logger.error("No 'lmcp.yaml' found in the current directory or any parent directory.")
        logger.error("Please run 'lmcp init' first or run the command in a valid project directory.")
        raise typer.Exit(code=1)
        
    logger.info(f"Using configuration file: {config_file_path}")
    
    try:
        # The project root is the directory containing the config file.
        project_root_from_config = config_file_path.parent
        logger.debug(f"Project root identified as: {project_root_from_config}")
        
        # Load config
        config = config_manager.load_config(config_file_path)
        
        # Instantiate and run orchestrator
        orchestrator = Orchestrator(config, project_root=project_root_from_config)
        orchestrator.up()
        
    except Exception as e:
        logger.error(f"An error occurred during the 'up' process: {e}")
        if ctx.meta.get("debug"):
            # The orchestrator already logs the traceback for critical errors
            pass
        raise typer.Exit(code=1)

@app.command()
def down(
    ctx: typer.Context,
):
    """
    Stops and removes the containers and networks for the server cluster.
    """
    logger.step("Starting 'down' command...")
    
    project_root = Path.cwd()
    config_file_path = config_manager.find_config_file(project_root)
    
    if not config_file_path:
        logger.error("No 'lmcp.yaml' found in the current directory or any parent directory.")
        logger.error("Please run the command in a valid project directory.")
        raise typer.Exit(code=1)
        
    logger.info(f"Using configuration file: {config_file_path}")
    
    try:
        project_root_from_config = config_file_path.parent
        logger.debug(f"Project root identified as: {project_root_from_config}")
        
        config = config_manager.load_config(config_file_path)
        
        orchestrator = Orchestrator(config, project_root=project_root_from_config)
        orchestrator.down()
        
    except Exception as e:
        logger.error(f"An error occurred during the 'down' process: {e}")
        if ctx.meta.get("debug"):
            pass
        raise typer.Exit(code=1)
    
@app.command()
def build(
    help: bool = typer.Option(False, "--help", "-h", help="Show this message and exit."),
    directory: str = typer.Option(".", "--directory", "-d", help="Directory to build the LMCP workspace."),
    config: str = typer.Option("lmcp.yaml", "--config", "-c", help="Path to the configuration file.")
):
    """
    Build LMCP servers cluster based on server configuration.
    Defaults to the configuration files in templates/ directory.
    """
    # Here you would implement the build logic, e.g., reading the config file
    # and building the servers based on the templates.
    logger.info(f"Building LMCP servers cluster in directory: {directory} with config: {config}")
    # Placeholder for actual build logic
    console.print(f"[bold green]Building LMCP servers cluster...[/bold green]")

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
  [blue]up[/blue]      Generate a compose file and start the server cluster
  [blue]down[/blue]    Stop and remove the containers and networks for the cluster

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

    