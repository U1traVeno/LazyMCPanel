import os
import logging
import typer

logger = logging.getLogger(__name__)

def initialize(help: bool = False):
    """
    Initialize the LMCP workspace.
    This function sets up the necessary environment for LMCP to run.
    """
    if help:
        print("Usage: lmcp init [OPTIONS]")
        print("Initialize the LMCP workspace.")
        print("\nOptions:")
        print("  --help, -h  Show this message and exit.")
        raise typer.Exit()
    
    # get the current working directory
    try:
        current_dir = os.getcwd()
    except FileNotFoundError as e:
        print("Error: Current working directory not found.")
        raise typer.Exit(code=1) from e
    logger.debug(f"Current working directory: {current_dir}")
    
    # not empty check, just create the directory if it doesn't exist
    if os.listdir(current_dir):
        logger.warning(f"Current directory is not empty: {current_dir}")
        print(f"Warning: Current directory '{current_dir}' is not empty. Proceeding with initialization.")

    try:
        _create_directories(current_dir)
        _create_config_file(os.path.join(current_dir, 'lmcp.yaml'))
    except Exception as e:
        print(f"Error creating directories: {e}")
        raise typer.Exit(code=1) from e
    

    

def _create_config_file(file: str) -> bool:
    """
    Create a default configuration file at the specified path.
    """
    with open(file, 'w') as f:
        f.write("version: 1.0\n")
        f.write("description: LMCP configuration file\n")
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