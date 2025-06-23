import os
import logging
import typer

from lmcp.core.logger import logger

def initialize(help: bool = False, directory: str = ".") -> None:
    """
    Initialize the LMCP workspace.
    This function sets up the necessary environment for LMCP to run.
    """
    if help:
        print("Usage: lmcp init [OPTIONS]")
        print("Initialize the LMCP workspace.")
        print("\nOptions:")
        print("  --help, -h  Show this message and exit.")
        print("  --directory, -d  Directory to initialize the LMCP workspace (default: current directory).")
        typer.Exit()
        raise typer.Exit()
    
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
    config_file = os.path.join(directory, '.lmcp', 'config.yaml')
    if os.path.exists(config_file):
        logger.warning(f"Configuration file already exists at {config_file}. Skipping creation.")
    else:
        logger.step(f"Creating configuration file at {config_file}.")
        try:
            _create_config_file(config_file)
        except Exception as e:
            logger.error(f"Failed to create configuration file: {e}")
            raise typer.Exit(code=1) from e
    
    logger.success("LMCP workspace initialized successfully.")

def _create_config_file(file: str) -> bool:
    """
    Create a default configuration file at the specified path.
    """
    with open(file, 'w') as f:
        f.write("# TEST\n")
    logger.debug(f"Configuration file created at: {file}")
    
    return True

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