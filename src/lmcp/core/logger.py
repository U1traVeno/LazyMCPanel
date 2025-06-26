from typing import Optional, Union, Dict, Any, Tuple, Type
from types import TracebackType
from rich.console import Console
from rich.logging import RichHandler
from rich.table import Table
import logging

# Type aliases for logging parameters
_ExcInfoType = Union[None, bool, Tuple[Type[BaseException], BaseException, TracebackType], BaseException]
LoggingExtraDict = Dict[str, Any]

# Create a Rich console instance for logging
console: Console = Console(stderr=True)

class LMCPLogger:
    """
    A custom logger for LMCP using Rich for better console output.
    """
    
    def __init__(self, name: str = "LMCP") -> None:
        self.name: str = name
        self.console: Console = console
        self._level: int = logging.INFO
        self._logger: logging.Logger
        
        #  Set up the logger with RichHandler
        self._setup_logging()
    
    def _setup_logging(self) -> None:
        """Set up the logging configuration using RichHandler."""
        # Create a logger
        self._logger = logging.getLogger(self.name)
        self._logger.setLevel(self._level)
        
        # Clear existing handlers to avoid duplicates
        self._logger.handlers.clear()
        
        #  Create a RichHandler for logging
        rich_handler: RichHandler = RichHandler(
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
    
    def setLevel(self, level: str) -> None:
        """Set the logging level"""
        level_map: Dict[str, int] = {
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
    
    def debug(
        self, 
        message: str, 
        *, 
        exc_info: _ExcInfoType = None,
        stack_info: bool = False,
        stacklevel: int = 1,
        extra: Optional[LoggingExtraDict] = None
    ) -> None:
        """Debug - Gray"""
        self._logger.debug(
            f"[dim]{message}[/dim]", 
            exc_info=exc_info,
            stack_info=stack_info,
            stacklevel=stacklevel,
            extra=extra
        )
    
    def info(
        self, 
        message: str, 
        *, 
        exc_info: _ExcInfoType = None,
        stack_info: bool = False,
        stacklevel: int = 1,
        extra: Optional[LoggingExtraDict] = None
    ) -> None:
        """Info - Blue"""
        self._logger.info(
            f"[blue]{message}[/blue]", 
            exc_info=exc_info,
            stack_info=stack_info,
            stacklevel=stacklevel,
            extra=extra
        )
    
    def success(
        self, 
        message: str, 
        *, 
        exc_info: _ExcInfoType = None,
        stack_info: bool = False,
        stacklevel: int = 1,
        extra: Optional[LoggingExtraDict] = None
    ) -> None:
        """Success - Green"""
        self._logger.info(
            f"[green]✓[/green] {message}", 
            exc_info=exc_info,
            stack_info=stack_info,
            stacklevel=stacklevel,
            extra=extra
        )
    
    def warning(
        self, 
        message: str, 
        *, 
        exc_info: _ExcInfoType = None,
        stack_info: bool = False,
        stacklevel: int = 1,
        extra: Optional[LoggingExtraDict] = None
    ) -> None:
        """Warning - Yellow"""
        self._logger.warning(
            f"[yellow]⚠[/yellow] {message}", 
            exc_info=exc_info,
            stack_info=stack_info,
            stacklevel=stacklevel,
            extra=extra
        )
    
    def error(
        self, 
        message: str, 
        *, 
        exc_info: _ExcInfoType = None,
        stack_info: bool = False,
        stacklevel: int = 1,
        extra: Optional[LoggingExtraDict] = None
    ) -> None:
        """Error - Red"""
        self._logger.error(
            f"[red]✗[/red] {message}", 
            exc_info=exc_info,
            stack_info=stack_info,
            stacklevel=stacklevel,
            extra=extra
        )
    
    def critical(
        self, 
        message: str, 
        *, 
        exc_info: _ExcInfoType = None,
        stack_info: bool = False,
        stacklevel: int = 1,
        extra: Optional[LoggingExtraDict] = None
    ) -> None:
        """Critical - Bold Red"""
        self._logger.critical(
            f"[bold red]💥 {message}[/bold red]", 
            exc_info=exc_info,
            stack_info=stack_info,
            stacklevel=stacklevel,
            extra=extra
        )
    
    def step(
        self, 
        message: str, 
        *, 
        exc_info: _ExcInfoType = None,
        stack_info: bool = False,
        stacklevel: int = 1,
        extra: Optional[LoggingExtraDict] = None
    ) -> None:
        """Step - Cyan"""
        self._logger.info(
            f"[cyan]→[/cyan] {message}", 
            exc_info=exc_info,
            stack_info=stack_info,
            stacklevel=stacklevel,
            extra=extra
        )
    
    def print(self, *args: Any, **kwargs: Any) -> None:
        """ Print messages to the console using Rich's print method."""
        self.console.print(*args, **kwargs)
    
    def print_panel(self, content: str, title: Optional[str] = None, **kwargs: Any) -> None:
        """Print a panel with content and an optional title."""
        from rich.panel import Panel
        panel: Panel = Panel(content, title=title, **kwargs)
        self.console.print(panel)
    
    def print_table(self, table: Table, **kwargs: Any) -> None:
        """Print a Rich table."""
        self.console.print(table, **kwargs)
    
    def separator(self, text: Optional[str] = None) -> None:
        """Print a separator line with optional text."""
        from rich.rule import Rule
        if text:
            self.console.print(Rule(f"[bold blue]{text}[/bold blue]"))
        else:
            self.console.print(Rule())

# Initialize the global logger instance
logger: LMCPLogger = LMCPLogger()

