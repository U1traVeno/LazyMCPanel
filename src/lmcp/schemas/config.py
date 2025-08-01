from pydantic import BaseModel, Field
from typing import List, Optional, Dict


class ServerConfig(BaseModel):
    """Configuration for a single Minecraft server."""
    java_version: str = Field(
        default="java21",
        description="Java Version for the server (must be a key in the 'images' mapping, e.g., 'java8', 'java21')."
    )


class NetworkConfig(BaseModel):
    """Network configuration for the cluster."""
    name: str = Field(
        default="MyLMCPNetwork",
        description="Network name for the cluster. \n"
                    "In most cases, you can keep it as is. "
                    "This name will be used in the generated podman-compose.yml. "
                    "It should be unique within the LMCP environment. "
                    "If you have multiple clusters, ensure they use different network names."
    )


class ImagesConfig(BaseModel):
    """Docker/Podman images configuration for different Java versions."""
    java8: str = Field(
        default="localhost/lmcp:jre8-py312",
        description="Docker/Podman image for Java 8 runtime"
    )
    java21: str = Field(
        default="localhost/lmcp:jre21-py312", 
        description="Docker/Podman image for Java 21 runtime"
    )


class ContainerEnvConfig(BaseModel):
    """Container environment configuration."""
    network: NetworkConfig = Field(
        default_factory=NetworkConfig,
        description="Network configuration"
    )
    images: ImagesConfig = Field(
        default_factory=ImagesConfig,
        description="\nPodman/Docker Image Configuration. \n"
                   "In most cases, you can keep the default values. "
                   "This section defines the images used for different Java versions. "
                   "If you need to use a different image, you can change the values here."
    )


class VelocityConfig(BaseModel):
    """Velocity proxy server configuration."""
    service_name: str = Field(
        default="velocity",
        description="Service name in podman-compose.yml"
    )
    java_version: str = Field(
        default="java21",
        description="Java Version for Velocity (will be looked up in the images mapping above)"
    )
    port: int = Field(
        default=25565,
        description="Port exposed to players for connection"
    )


class ClusterConfig(BaseModel):
    """
    Configuration for the LMCP cluster.
    """
    cluster_name: str = Field(
        default="My LMCP Cluster",
        description="\nName of the LMCP cluster"
    )
    lmcp_dir: str = Field(
        default=".lmcp",
        description="\nDirectory for LMCP internal files"
    )
    servers_dir: str = Field(
        default="servers",
        description="\nDirectory containing server configurations"
    )
    templates_dir: str = Field(
        default="templates",
        description="\nDirectory containing server templates"
    )
    container_env: ContainerEnvConfig = Field(
        default_factory=ContainerEnvConfig,
        description="\nCluster Container Environment Configuration"
    )
    velocity: VelocityConfig = Field(
        default_factory=VelocityConfig,
        description="\nVelocity Configuration"
    )
    servers: Dict[str, ServerConfig] = Field(
        default_factory=lambda: {
            "lobby": ServerConfig(java_version="java21"),
            "survival": ServerConfig(java_version="java8")
        },
        description="\nDefines the servers to be included in the cluster. "
                    "The key for each entry (e.g., 'lobby') must correspond to a directory with the same name inside the 'servers_dir'."
    )
    active_servers: Optional[List[str]] = Field(
        default=None,
        description="\nList of active servers. If defined, only servers from this list will be started. "
                    "If not defined, all servers in the 'servers' section will be started."
    )
    
