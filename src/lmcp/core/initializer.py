import os
import typer

from lmcp.core.logger import logger
from lmcp.core.config import generate_default_config

def initialize(help: bool = False, directory: str = ".") -> None:
    """
    Initialize the LMCP workspace with a minimal velocity cluster setup(without any servers).
    This function sets up the necessary environment for LMCP to run.
    """
    if help:
        _show_help()
    
    if not os.path.exists(directory):
        logger.step(f"Directory {directory} does not exist. Creating it.")
        try:
            os.makedirs(directory)
        except Exception as e:
            logger.error(f"Failed to create directory {directory}: {e}")
            raise typer.Exit(code=1) from e
    
    logger.debug(f"Initializing LMCP workspace in directory: {directory}")
    
    # Create necessary directories
    try:
        _create_directories(directory)
    except Exception as e:
        logger.error(f"Failed to create necessary directories: {e}")
        raise typer.Exit(code=1) from e
    
    # Create configuration file
    logger.debug("Creating configuration file for LMCP.")
    config_file = os.path.join(directory, 'lmcp.yaml')
    if not os.path.exists(config_file):
        try:
            _create_config_file(config_file)
        except Exception as e:
            logger.error(f"Failed to create configuration file: {e}")
            raise typer.Exit(code=1) from e
    else:
        logger.warning(f"Configuration file already exists at {config_file}. Skipping creation.")
        
    logger.success("LMCP workspace initialized successfully.")

def _show_help() -> None:
    """
    Show help information for the LMCP initialization command.
    """
    print("Usage: lmcp init [OPTIONS]")
    print("Initialize the LMCP workspace.")
    print("\nOptions:")
    print("  --help, -h  Show this message and exit.")
    print("  --directory, -d  Directory to initialize the LMCP workspace (default: current directory).")
    typer.Exit()
    raise typer.Exit()

def _create_config_file(file: str) -> bool:
    """
    Create a default configuration file at the specified path.
    """
    try:
        # Extract directory name as project name
        directory = os.path.dirname(file)
        project_name = os.path.basename(os.path.abspath(directory)) if directory != '.' else 'my_lazy_cluster'
        
        # Use the config manager to generate default configuration
        generate_default_config(project_name=project_name, config_path=file)
        logger.debug(f"Configuration file created at: {file}")
        return True
    except Exception as e:
        logger.error(f"Failed to generate default configuration: {e}")
        raise

def _create_directories(directory: str) -> bool:
    """
    Create necessary directories for LMCP.
    """
    directories = [
        os.path.join(directory, '.lmcp'),
        os.path.join(directory, 'templates'),
        os.path.join(directory, 'servers'),
    ]
    
    for dir in directories:
        try:
            os.makedirs(dir, exist_ok=True)
            logger.debug(f"Directory created: {dir}")
        except Exception as e:
            logger.error(f"Failed to create directory {dir}: {e}")
            raise typer.Exit(code=1) from e
    
    return True