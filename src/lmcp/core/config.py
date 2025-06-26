from ruamel.yaml import YAML, YAMLError
from ruamel.yaml.comments import CommentedMap
import textwrap
from pathlib import Path
from typing import Type, Union, Optional, Any
from pydantic import BaseModel, ValidationError

from lmcp.schemas.config import ClusterConfig, NetworkConfig, ImagesConfig, ContainerEnvConfig, VelocityConfig
from lmcp.core.logger import logger
from lmcp.core.types import SerializableData, CommentedStructure


class ConfigManager:
    """
    LMCP Configuration Manager
    
    Handles reading, writing, validation, and generation of default lmcp.yaml configuration files.
    """
    
    DEFAULT_CONFIG_FILENAME: str = "lmcp.yaml"
    
    def __init__(self) -> None:
        # Use ruamel.yaml to preserve format and comments
        self.yaml: YAML = YAML()
        self.yaml.preserve_quotes = True
        self.yaml.width = 4096  # Avoid folding long lines
        logger.debug("ConfigManager initialized with ruamel.yaml settings")
        
    def load_config(self, config_path: Optional[Union[str, Path]] = None) -> ClusterConfig:
        """
        Load LMCP configuration file
        
        Args:
            config_path: Configuration file path, if None, search for lmcp.yaml in current directory
            
        Returns:
            ClusterConfig: Validated configuration object
            
        Raises:
            FileNotFoundError: Configuration file does not exist
            ValidationError: Configuration file format is incorrect
            ruamel.yaml.YAMLError: YAML parsing error
        """
        if config_path is None:
            config_path = Path.cwd() / self.DEFAULT_CONFIG_FILENAME
            logger.debug(f"Using default config path: {config_path}")
        else:
            config_path = Path(config_path)
            logger.debug(f"Using specified config path: {config_path}")
            
        if not config_path.exists():
            logger.error(f"Configuration file does not exist: {config_path}")
            raise FileNotFoundError(f"Configuration file does not exist: {config_path}")
            
        logger.debug(f"Reading configuration file: {config_path}")
        # Read and parse YAML
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                yaml_data: Any = self.yaml.load(f)  # type: ignore[no-any-return]
                logger.debug(f"Successfully parsed YAML data from {config_path}")
        except Exception as e:
            logger.error(f"Failed to read or parse YAML file {config_path}: {e}")
            raise

        if not isinstance(yaml_data, dict):
            logger.error(f"Configuration file {config_path} does not contain valid YAML dictionary")
            raise ValueError(f"Configuration file {config_path} does not contain valid YAML dictionary")
            
        logger.debug(f"loaded yaml data keys: {list(yaml_data.keys())}") # type: ignore[no-any-return]
         
        # Validate configuration using Pydantic model
        try:
            # Unpack YAML data into ClusterConfig model
            config: ClusterConfig = ClusterConfig(**yaml_data) # type: ignore[call-arg]
            logger.info(f"Successfully loaded and validated configuration from {config_path}")
            logger.debug(f"Project name: {config.project_name}")
            logger.debug(f"Active servers: {config.active_servers}")
            return config
        except ValidationError as e:
            logger.error(f"Configuration file validation failed for {config_path}: {e}")
            raise ValidationError(f"Configuration file validation failed: {e}")
    
    def save_config(self, config: ClusterConfig, config_path: Optional[Union[str, Path]] = None) -> Path:
        """
        Save configuration to file
        
        Args:
            config: Configuration object to save
            config_path: Save path, if None, save to lmcp.yaml in current directory
            
        Returns:
            Path: Path of the saved file
        """
        if config_path is None:
            config_path = Path.cwd() / self.DEFAULT_CONFIG_FILENAME
            logger.debug(f"Using default save path: {config_path}")
        else:
            config_path = Path(config_path)
            logger.debug(f"Using specified save path: {config_path}")
            
        # Ensure parent directory exists
        config_path.parent.mkdir(parents=True, exist_ok=True)
        logger.debug(f"Ensured parent directory exists: {config_path.parent}")
        
        # Convert Pydantic model to dictionary, then save as YAML
        try:
            config_dict: dict[str, Any] = config.model_dump()
            logger.debug(f"Converted config to dictionary with keys: {list(config_dict.keys())}")
            
            with open(config_path, 'w', encoding='utf-8') as f:
                self.yaml.dump(config_dict, f) # type: ignore[no-any-return]
                
            logger.info(f"Successfully saved configuration to {config_path}")
            logger.debug(f"Saved config for project: {config.project_name}")
            return config_path
            
        except Exception as e:
            logger.error(f"Failed to save configuration to {config_path}: {e}")
            raise
    
    def generate_default_config(self, 
                              project_name: str = "my_lazy_cluster",
                              config_path: Optional[Union[str, Path]] = None) -> Path:
        """
        Generate default lmcp.yaml configuration file
        
        Args:
            project_name: Project name
            config_path: Save path, if None, save to lmcp.yaml in current directory
            
        Returns:
            Path: Path of the generated configuration file
        """
        if config_path is None:
            config_path = Path.cwd() / self.DEFAULT_CONFIG_FILENAME
            logger.debug(f"Using default config generation path: {config_path}")
        else:
            config_path = Path(config_path)
            logger.debug(f"Using specified config generation path: {config_path}")
            
        # Ensure parent directory exists
        config_path.parent.mkdir(parents=True, exist_ok=True)
        logger.debug(f"Ensured parent directory exists: {config_path.parent}")
        
        logger.debug(f"Generating default configuration with project name: {project_name}")
        
        # Create default configuration using Pydantic models
        try:
            # Create default configuration object
            default_config = ClusterConfig(
                project_name=project_name,
                lmcp_dir=".lmcp",
                servers_dir="servers", 
                templates_dir="templates",
                container_env=ContainerEnvConfig(
                    network=NetworkConfig(name=f"{project_name}_net"),
                    images=ImagesConfig()  # Uses default values from model
                ),
                velocity=VelocityConfig(),  # Uses default values from model
                active_servers=[]
            )
            
            logger.debug(f"Created default config object for project: {project_name}")
            
            # Use new, simpler method to generate YAML with comments
            self._generate_yaml_with_comments(default_config, config_path)
            
            logger.success(f"Generated default configuration file: {config_path}")
            logger.debug(f"Configuration contains project '{project_name}' with network '{project_name}_net'")
            return config_path
            
        except Exception as e:
            logger.error(f"Failed to generate default configuration at {config_path}: {e}")
            raise
    
    def _generate_yaml_with_comments(self, config_model: BaseModel, config_path: Path) -> None:
        """
        Generate YAML file with comments by directly inspecting Pydantic model fields.
        """
        # 1. Convert Pydantic model instance to pure Python dictionary
        config_dict: dict[str, Any] = config_model.model_dump(mode='python')
        
        # 2. Starting from model class (Type), recursively convert dictionary to commented structure
        yaml_data: CommentedMap = self._add_comments_recursively(config_dict, type(config_model))
        
        # 3. Add file header
        yaml_data.yaml_set_start_comment( # type: ignore[no-any-return]
            "===================================================\n"
            "LMCP Configuration\n"
            "Generated by `lmcp init`\n"
            "==================================================="
        )
        
        # 4. Write to file
        with open(config_path, 'w', encoding='utf-8') as f:
            self.yaml.dump(yaml_data, f) # type: ignore[no-any-return]

    def _add_comments_recursively(self, data: SerializableData, model: Type[BaseModel]) -> CommentedStructure:
        """
        Recursively convert dictionary to CommentedMap and add comments from Pydantic model fields.
        """
        if not isinstance(data, dict):
            # If data is not a dictionary (e.g., list, string, number), return directly
            # Note: This simplified version doesn't handle comments for complex objects within lists
            return data # type: ignore[no-any-return]

        commented_map: CommentedMap = CommentedMap()
        
        # Iterate through each key-value pair in the data dictionary
        for key, value in data.items():
            # Get corresponding field information from Pydantic model
            field_info = model.model_fields.get(key)
            
            if field_info:
                # Check field annotation to see if it's a nested Pydantic model
                # field_info.annotation is the field type, e.g. NetworkConfig, Optional[List[str]]
                nested_model: Optional[Type[BaseModel]] = self._get_nested_model_type(field_info.annotation)
                
                if nested_model:
                    # If value is a dictionary and field type is another Pydantic model, recursively process
                    commented_map[key] = self._add_comments_recursively(value, nested_model)
                else:
                    # Otherwise, assign directly
                    commented_map[key] = value

                # Add comment (if field has description)
                if field_info.description:
                    comment = self._format_comment(field_info.description)
                    commented_map.yaml_set_comment_before_after_key(key, before='\n' + comment) # type: ignore[no-any-return]
            else:
                 # If field not found in model (theoretically shouldn't happen), assign directly
                commented_map[key] = value
                
        return commented_map

    def _get_nested_model_type(self, annotation: Any) -> Optional[Type[BaseModel]]:
        """
        Extract Pydantic model class from field type annotation.
        For example, extract NetworkConfig from Union[NetworkConfig, None].
        """
        # Handle Optional[SomeModel], i.e., Union[SomeModel, None]
        if hasattr(annotation, '__origin__') and annotation.__origin__ is Union:
            for arg in annotation.__args__:
                if isinstance(arg, type) and issubclass(arg, BaseModel):
                    return arg
        # Handle direct model types, like NetworkConfig
        if isinstance(annotation, type) and issubclass(annotation, BaseModel):
            return annotation
        return None

    def _format_comment(self, description: str) -> str:
        """
        Use textwrap to format comments for better appearance.
        """
        # textwrap elegantly handles multi-line and long text
        return '\n'.join(
            textwrap.fill(line, width=80, subsequent_indent='  ', drop_whitespace=True)
            for line in description.strip().split('\n')
        )
    
    def find_config_file(self, start_path: Optional[Union[str, Path]] = None) -> Optional[Path]:
        """
        Search for lmcp.yaml configuration file starting from specified path upwards
        
        Args:
            start_path: Starting search path, if None, start from current directory
            
        Returns:
            Optional[Path]: Found configuration file path, None if not found
        """
        if start_path is None:
            start_path = Path.cwd()
            logger.debug("Starting config file search from current directory")
        else:
            start_path = Path(start_path)
            logger.debug(f"Starting config file search from: {start_path}")
            
        current_path = start_path.resolve()
        logger.debug(f"Resolved start path to: {current_path}")
        
        # Search upwards for configuration file
        search_count = 0
        while current_path != current_path.parent:
            config_file = current_path / self.DEFAULT_CONFIG_FILENAME
            logger.debug(f"Searching for config file at: {config_file}")
            
            if config_file.exists():
                logger.info(f"Found configuration file at: {config_file}")
                return config_file
                
            current_path = current_path.parent
            search_count += 1
            
            # Prevent infinite loops in edge cases
            if search_count > 50:
                logger.warning("Config file search exceeded maximum depth (50 levels)")
                break
                
        logger.debug(f"Configuration file not found after searching {search_count} directories")
        return None
    
    def validate_config_file(self, config_path: Union[str, Path]) -> bool:
        """
        Validate whether configuration file is valid
        
        Args:
            config_path: Configuration file path
            
        Returns:
            bool: Whether configuration file is valid
        """
        logger.debug(f"Validating configuration file: {config_path}")
        try:
            self.load_config(config_path)
            logger.debug(f"Configuration file validation successful: {config_path}")
            return True
        except FileNotFoundError as e:
            logger.error(f"Config file not found during validation: {e}")
            return False
        except ValidationError as e:
            logger.error(f"Config validation failed: {e}")
            return False
        except YAMLError as e:
            logger.error(f"YAML parsing error during validation: {e}")
            return False
        except ValueError as e:
            logger.error(f"Value error during validation: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error during config validation: {e}")
            return False


# Global configuration manager instance
config_manager: ConfigManager = ConfigManager()
logger.debug("Global ConfigManager instance created")


def load_config(config_path: Optional[Union[str, Path]] = None) -> ClusterConfig:
    """
    Convenience function: Load configuration file
    """
    logger.debug(f"load_config called with path: {config_path}")
    return config_manager.load_config(config_path)


def generate_default_config(project_name: str = "my_lazy_cluster", 
                          config_path: Optional[Union[str, Path]] = None) -> Path:
    """
    Convenience function: Generate default configuration file
    """
    logger.debug(f"generate_default_config called with project_name='{project_name}', path={config_path}")
    return config_manager.generate_default_config(project_name, config_path)


def find_config_file(start_path: Optional[Union[str, Path]] = None) -> Optional[Path]:
    """
    Convenience function: Find configuration file
    """
    logger.debug(f"find_config_file called with start_path: {start_path}")
    return config_manager.find_config_file(start_path)

