from pydantic import BaseModel
from typing import List, Optional


class NetworkConfig(BaseModel):
    """Network configuration for the cluster."""
    name: str


class ImagesConfig(BaseModel):
    """Docker/Podman images configuration for different Java versions."""
    java8: str
    java21: str


class ContainerEnvConfig(BaseModel):
    """Container environment configuration."""
    network: NetworkConfig
    images: ImagesConfig


class VelocityConfig(BaseModel):
    """Velocity proxy server configuration."""
    service_name: str
    java_version: str
    port: int


class ClusterConfig(BaseModel):
    """
    Configuration for the LMCP cluster.
    """
    project_name: str
    lmcp_dir: str
    servers_dir: str
    templates_dir: str
    container_env: ContainerEnvConfig
    velocity: VelocityConfig
    active_servers: Optional[List[str]] = None
    
