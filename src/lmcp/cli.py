import typer

from lmcp.core.initializer import initialize 

app = typer.Typer()

@app.command()
def main(help: bool = typer.Option(False, "--help", "-h", help="Show this message and exit.")):
    """
    Main entry point for the LMCP CLI.
    """
    typer.echo("Welcome to the LMCP CLI!")
    typer.echo("Use 'lmcp --help' to see available commands.")
    if help:
        typer.echo("Help info")
    else:
        typer.echo("Run 'lmcp --help' for more information.")

@app.command()
def init(help: bool = typer.Option(False, "--help", "-h", help="Show this message and exit.")):
    """
    Initialize the LMCP workspace.
    """
    initialize(help=help)
    