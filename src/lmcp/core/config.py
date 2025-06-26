import ruamel.yaml
from pathlib import Path
from typing import Optional, Union
from pydantic import ValidationError

from lmcp.schemas.config import ClusterConfig, NetworkConfig, ImagesConfig, ContainerEnvConfig, VelocityConfig
from lmcp.core.logger import logger


class ConfigManager:
    """
    LMCP Configuration Manager
    
    Handles reading, writing, validation, and generation of default lmcp.yaml configuration files.
    """
    
    DEFAULT_CONFIG_FILENAME = "lmcp.yaml"
    
    def __init__(self):
        # Use ruamel.yaml to preserve format and comments
        self.yaml = ruamel.yaml.YAML()
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
                yaml_data = self.yaml.load(f)
                logger.debug(f"Successfully parsed YAML data from {config_path}")
        except Exception as e:
            logger.error(f"Failed to read or parse YAML file {config_path}: {e}")
            raise
            
        if yaml_data is None:
            logger.error(f"Configuration file is empty: {config_path}")
            raise ValueError(f"Configuration file is empty: {config_path}")
            
        logger.debug(f"Loaded YAML data keys: {list(yaml_data.keys()) if isinstance(yaml_data, dict) else 'Not a dict'}")
        
        # Validate configuration using Pydantic model
        try:
            config = ClusterConfig(**yaml_data) # Unpack YAML data into ClusterConfig model
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
            config_dict = config.model_dump()
            logger.debug(f"Converted config to dictionary with keys: {list(config_dict.keys())}")
            
            with open(config_path, 'w', encoding='utf-8') as f:
                self.yaml.dump(config_dict, f)
                
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
            
            # Convert to dictionary for YAML generation
            config_dict = default_config.model_dump()
            
            # Generate YAML with comments
            self._generate_yaml_with_comments(config_dict, config_path, project_name)
            
            logger.success(f"Generated default configuration file: {config_path}")
            logger.debug(f"Configuration contains project '{project_name}' with network '{project_name}_net'")
            return config_path
            
        except Exception as e:
            logger.error(f"Failed to generate default configuration at {config_path}: {e}")
            raise
    
    def _generate_yaml_with_comments(self, config_dict: dict, config_path: Path, project_name: str):
        """
        Generate YAML file with comments using ruamel.yaml
        Automatically extracts descriptions from Pydantic model schema
        """
        # Get the schema from ClusterConfig model
        schema = ClusterConfig.model_json_schema()
        
        # Create a CommentedMap for the root with schema-based comments
        yaml_data = self._convert_to_commented_structure(config_dict, schema)
        
        # Add header comments
        self._add_yaml_header_comment(yaml_data)
        
        # Add some spacing for better readability
        self._add_section_spacing(yaml_data)
        
        # Write YAML with comments
        with open(config_path, 'w', encoding='utf-8') as f:
            self.yaml.dump(yaml_data, f)

    def _convert_to_commented_structure(self, data, current_schema=None, parent_key=None):
        """
        Recursively convert dict/list to CommentedMap/CommentedSeq and add schema-based comments
        """
        if isinstance(data, dict):
            return self._process_dict_with_comments(data, current_schema, parent_key)
        elif isinstance(data, list):
            return self._process_list_with_comments(data, current_schema, parent_key)
        else:
            return data

    def _process_dict_with_comments(self, data: dict, current_schema=None, parent_key=None):
        """
        Process dictionary and add comments from schema
        """
        cm = ruamel.yaml.CommentedMap()
        properties_schema = self._extract_properties_schema(current_schema, parent_key)
        
        for key, value in data.items():
            key_schema = self._resolve_key_schema(key, properties_schema, current_schema)
            
            # Recursively process the value
            cm[key] = self._convert_to_commented_structure(value, key_schema, key)
            
            # Add comment if description exists
            self._add_field_comment(cm, key, key_schema)
            
            logger.debug(f"Processed key '{key}' with schema: {bool('description' in key_schema)}")
        
        return cm

    def _process_list_with_comments(self, data: list, current_schema=None, parent_key=None):
        """
        Process list and convert to CommentedSeq
        """
        cl = ruamel.yaml.CommentedSeq()
        items_schema = self._get_items_schema(current_schema)
        
        for item in data:
            cl.append(self._convert_to_commented_structure(item, items_schema, parent_key))
        
        return cl

    def _extract_properties_schema(self, current_schema, parent_key):
        """
        Extract properties schema for current level
        """
        properties_schema = {}
        if not current_schema:
            return properties_schema
            
        if 'properties' in current_schema:
            properties_schema = current_schema['properties']
        elif '$defs' in current_schema and parent_key:
            # Handle nested model references
            for def_name, def_schema in current_schema['$defs'].items():
                if 'properties' in def_schema:
                    properties_schema = def_schema['properties']
                    break
        
        return properties_schema

    def _resolve_key_schema(self, key: str, properties_schema: dict, current_schema):
        """
        Resolve schema for a specific key, handling $ref references
        """
        key_schema = properties_schema.get(key, {})
        
        # If the field has its own description, use it directly and don't resolve $ref
        if 'description' in key_schema:
            # For fields with their own description, we want to use that description
            # but still need the nested structure for recursive processing
            if '$ref' in key_schema and current_schema and '$defs' in current_schema:
                ref_path = key_schema['$ref']
                if ref_path.startswith('#/$defs/'):
                    def_name = ref_path.split('/')[-1]
                    if def_name in current_schema['$defs']:
                        ref_schema = current_schema['$defs'][def_name]
                        # Merge field description with referenced schema structure
                        merged_schema = ref_schema.copy()
                        merged_schema['description'] = key_schema['description']
                        return merged_schema
            return key_schema
        
        # Handle $ref references to nested models only when no field description exists
        if '$ref' in key_schema and current_schema and '$defs' in current_schema:
            ref_path = key_schema['$ref']
            if ref_path.startswith('#/$defs/'):
                def_name = ref_path.split('/')[-1]
                if def_name in current_schema['$defs']:
                    key_schema = current_schema['$defs'][def_name]
        
        return key_schema

    def _get_items_schema(self, current_schema):
        """
        Get items schema for array types
        """
        if current_schema and 'items' in current_schema:
            return current_schema['items']
        return None

    def _add_field_comment(self, commented_map, key: str, key_schema: dict):
        """
        Add comment to a field if description exists in schema
        """
        if 'description' not in key_schema:
            return
            
        description = key_schema['description']
        comment_text = self._format_description_for_comment(description)
        commented_map.yaml_set_comment_before_after_key(key, before=comment_text)

    def _format_description_for_comment(self, description: str) -> str:
        """
        Format description text for YAML comments, handling long lines and multi-line text
        """
        if '\n' not in description and len(description) <= 80:
            return description
            
        lines = []
        for line in description.split('\n'):
            if len(line) <= 80:
                lines.append(line)
            else:
                lines.extend(self._wrap_long_line(line))
        
        return '\n'.join(lines)

    def _wrap_long_line(self, line: str) -> list:
        """
        Word wrap a long line to fit within 80 characters
        """
        words = line.split()
        wrapped_lines = []
        current_line = ""
        
        for word in words:
            test_line = f"{current_line} {word}" if current_line else word
            if len(test_line) <= 80:
                current_line = test_line
            else:
                if current_line:
                    wrapped_lines.append(current_line)
                current_line = word
        
        if current_line:
            wrapped_lines.append(current_line)
        
        return wrapped_lines

    def _add_yaml_header_comment(self, yaml_data):
        """
        Add header comment to YAML file
        """
        yaml_data.yaml_set_start_comment(
            "===================================================\n"
            "LMCP Configuration\n"
            "Generated by `lmcp init`\n"
            "==================================================="
        )
    
    def _add_section_spacing(self, yaml_data):
        """
        Add spacing between major sections for better readability
        """
        # Define major sections that should have extra spacing
        major_sections = ['container_env', 'velocity', 'active_servers']
        
        for section in major_sections:
            if section in yaml_data:
                # Check if there's already a comment for this section
                existing_comment = None
                if hasattr(yaml_data, 'ca') and yaml_data.ca.items and section in yaml_data.ca.items:
                    comment_info = yaml_data.ca.items[section]
                    if comment_info and len(comment_info) > 1 and comment_info[1]:
                        existing_comment = comment_info[1]
                
                if existing_comment:
                    # If there's already a comment, add extra spacing
                    if hasattr(existing_comment, 'value'):
                        if not existing_comment.value.startswith('\n'):
                            existing_comment.value = '\n' + existing_comment.value
                else:
                    # Add a simple spacing comment if no description exists
                    yaml_data.yaml_set_comment_before_after_key(section, before='\n')
    
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
        except ruamel.yaml.YAMLError as e:
            logger.error(f"YAML parsing error during validation: {e}")
            return False
        except ValueError as e:
            logger.error(f"Value error during validation: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error during config validation: {e}")
            return False


# Global configuration manager instance
config_manager = ConfigManager()
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

