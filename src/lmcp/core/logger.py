from typing import Optional
from rich.console import Console
from rich.logging import RichHandler
from rich.text import Text
import logging
import sys

# Create a Rich console instance for logging
console = Console(stderr=True)

class LMCPLogger:
    """
    A custom logger for LMCP using Rich for better console output.
    """
    
    def __init__(self, name: str = "LMCP"):
        self.name = name
        self.console = console
        self._level = logging.INFO
        
        #  Set up the logger with RichHandler
        self._setup_logging()
    
    def _setup_logging(self):
        """Set up the logging configuration using RichHandler."""
        # Create a logger
        self._logger = logging.getLogger(self.name)
        self._logger.setLevel(self._level)
        
        # Clear existing handlers to avoid duplicates
        self._logger.handlers.clear()
        
        #  Create a RichHandler for logging
        rich_handler = RichHandler(
            console=self.console,
            show_time=True,
            show_path=False,
            markup=True,
            rich_tracebacks=True,
            tracebacks_show_locals=True
        )
        
        # Set formatter for the RichHandler
        rich_handler.setFormatter(
            logging.Formatter(
                fmt="%(message)s",
                datefmt="[%X]"
            )
        )
        
        self._logger.addHandler(rich_handler)
    
    def setLevel(self, level: str):
        """Set the logging level"""
        level_map = {
            "DEBUG": logging.DEBUG,
            "INFO": logging.INFO,
            "WARNING": logging.WARNING,
            "ERROR": logging.ERROR,
            "CRITICAL": logging.CRITICAL
        }
        
        if level.upper() in level_map:
            self._level = level_map[level.upper()]
            self._logger.setLevel(self._level)
            
            # Clear existing handlers and re-setup logging
            self._setup_logging()
    
    def debug(self, message: str, **kwargs):
        """Debug - Gray"""
        self._logger.debug(f"[dim]{message}[/dim]", **kwargs)
    
    def info(self, message: str, **kwargs):
        """Info - Blue"""
        self._logger.info(f"[blue]{message}[/blue]", **kwargs)
    
    def success(self, message: str, **kwargs):
        """Success - Green"""
        self._logger.info(f"[green]✓[/green] {message}", **kwargs)
    
    def warning(self, message: str, **kwargs):
        """Warning - Yellow"""
        self._logger.warning(f"[yellow]⚠[/yellow] {message}", **kwargs)
    
    def error(self, message: str, **kwargs):
        """Error - Red"""
        self._logger.error(f"[red]✗[/red] {message}", **kwargs)
    
    def critical(self, message: str, **kwargs):
        """Critical - Bold Red"""
        self._logger.critical(f"[bold red]💥 {message}[/bold red]", **kwargs)
    
    def step(self, message: str, **kwargs):
        """Step - Cyan"""
        self._logger.info(f"[cyan]→[/cyan] {message}", **kwargs)
    
    def print(self, *args, **kwargs):
        """ Print messages to the console using Rich's print method."""
        self.console.print(*args, **kwargs)
    
    def print_panel(self, content: str, title: Optional[str] = None, **kwargs):
        """Print a panel with content and an optional title."""
        from rich.panel import Panel
        self.console.print(Panel(content, title=title, **kwargs))
    
    def print_table(self, table, **kwargs):
        """Print a Rich table."""
        self.console.print(table, **kwargs)
    
    def separator(self, text: Optional[str] = None):
        """Print a separator line with optional text."""
        from rich.rule import Rule
        if text:
            self.console.print(Rule(f"[bold blue]{text}[/bold blue]"))
        else:
            self.console.print(Rule())

# Initialize the global logger instance
logger = LMCPLogger()

