import shutil
import subprocess
from pathlib import Path
from typing import Any

from ruamel.yaml import YAML

from lmcp.core.logger import logger
from lmcp.schemas.config import ClusterConfig


class Orchestrator:
    """
    Handles the generation of compose files and starting the cluster.
    """

    def __init__(self, config: ClusterConfig, project_root: Path):
        self.config = config
        self.project_root = project_root
        self.yaml = YAML()
        self.yaml.indent(mapping=2, sequence=4, offset=2)
        logger.debug("Orchestrator initialized.")

    def _get_compose_command(self) -> str:
        """
        Detects which compose command is available on the system.
        """
        for cmd in ["podman-compose", "docker-compose"]:
            if shutil.which(cmd):
                logger.debug(f"Found compose command: {cmd}")
                return cmd
        logger.error("Neither 'podman-compose' nor 'docker-compose' found in PATH.")
        raise FileNotFoundError("Neither 'podman-compose' nor 'docker-compose' found in PATH.")

    def _get_container_runtime(self) -> str:
        """
        Detects which container runtime (podman or docker) is available on the system.
        """
        for cmd in ["podman", "docker"]:
            if shutil.which(cmd):
                logger.debug(f"Found container runtime: {cmd}")
                return cmd
        logger.error("Neither 'podman' nor 'docker' found in PATH.")
        raise FileNotFoundError("Neither 'podman' nor 'docker' found in PATH.")

    def _get_required_images(self) -> set[str]:
        """
        Get the set of all required images for the cluster.
        """
        images: set[str] = set()
        
        # Add velocity image
        velocity_image_key = self.config.velocity.java_version
        try:
            velocity_image = getattr(self.config.container_env.images, velocity_image_key)
            images.add(velocity_image)
            logger.debug(f"Required image for velocity: {velocity_image}")
        except AttributeError:
            logger.error(f"Image key '{velocity_image_key}' for Velocity not found in images config.")
            raise ValueError(f"Image key '{velocity_image_key}' for Velocity not found in images config.")
        
        # Determine active servers
        if self.config.active_servers is None:
            active_server_names = list(self.config.servers.keys())
        else:
            active_server_names = [name for name in self.config.active_servers if name in self.config.servers]
        
        # Add server images
        for server_name in active_server_names:
            server_config = self.config.servers[server_name]
            server_image_key = server_config.java_version
            try:
                server_image = getattr(self.config.container_env.images, server_image_key)
                images.add(server_image)
                logger.debug(f"Required image for server '{server_name}': {server_image}")
            except AttributeError:
                logger.error(f"Image key '{server_image_key}' for server '{server_name}' not found in images config.")
                raise ValueError(f"Image key '{server_image_key}' for server '{server_name}' not found in images config.")
        
        return images

    def _check_image_exists(self, image_name: str, runtime: str) -> bool:
        """
        Check if a Docker/Podman image exists locally.
        """
        try:
            process = subprocess.run(
                [runtime, "images", "-q", image_name],
                capture_output=True,
                text=True,
                check=False
            )
            exists = bool(process.stdout.strip())
            logger.debug(f"Image '{image_name}' exists: {exists}")
            return exists
        except Exception as e:
            logger.warning(f"Failed to check if image '{image_name}' exists: {e}")
            return False

    def _build_image(self, image_name: str, runtime: str) -> bool:
        """
        Build a Docker/Podman image from the assets directory.
        Returns True if successful, False otherwise.
        """
        # Extract the image tag (e.g., "jre21-py312" from "localhost/lmcp:jre21-py312")
        try:
            tag = image_name.split(":")[-1]
            logger.info(f"Building image '{image_name}' from tag '{tag}'...")
            
            # Get the project root (where src/ directory is located)
            # Go up from src/lmcp/core to project root
            project_root = Path(__file__).parent.parent.parent.parent
            dockerfile_dir = project_root / "src" / "lmcp" / "assets" / "containers" / tag
            
            if not dockerfile_dir.exists():
                logger.error(f"Dockerfile directory not found: {dockerfile_dir}")
                return False
            
            dockerfile_path = dockerfile_dir / "Dockerfile"
            if not dockerfile_path.exists():
                logger.error(f"Dockerfile not found: {dockerfile_path}")
                return False
            
            logger.debug(f"Building from: {dockerfile_path}")
            logger.debug(f"Build context: {project_root}")
            
            # Build the image
            cmd_args = [
                runtime, "build",
                "-t", image_name,
                "-f", str(dockerfile_path),
                str(project_root)
            ]
            
            logger.info(f"Executing: {' '.join(cmd_args)}")
            
            process = subprocess.run(
                cmd_args,
                cwd=project_root,
                capture_output=True,
                text=True,
                check=False
            )
            
            if process.returncode == 0:
                logger.success(f"Successfully built image: {image_name}")
                if process.stdout:
                    logger.debug(f"Build output:\n{process.stdout.strip()}")
                return True
            else:
                logger.error(f"Failed to build image: {image_name}")
                logger.error(f"Return Code: {process.returncode}")
                if process.stdout:
                    logger.error(f"Stdout:\n{process.stdout.strip()}")
                if process.stderr:
                    logger.error(f"Stderr:\n{process.stderr.strip()}")
                return False
                
        except Exception as e:
            logger.error(f"Error building image '{image_name}': {e}")
            return False

    def _ensure_images_exist(self):
        """
        Check if all required images exist, and build them if they don't.
        """
        try:
            runtime = self._get_container_runtime()
            required_images = self._get_required_images()
            
            logger.step("Checking required container images...")
            missing_images: list[str] = []
            
            for image in required_images:
                if not self._check_image_exists(image, runtime):
                    logger.warning(f"Image '{image}' not found locally.")
                    missing_images.append(image)
                else:
                    logger.debug(f"Image '{image}' found locally.")
            
            if missing_images:
                logger.info(f"Found {len(missing_images)} missing image(s). Building...")
                for image in missing_images:
                    logger.step(f"Building image: {image}")
                    if not self._build_image(image, runtime):
                        raise RuntimeError(f"Failed to build required image: {image}")
                logger.success("All missing images have been built successfully.")
            else:
                logger.success("All required images are available locally.")
                
        except Exception as e:
            logger.error(f"Error ensuring images exist: {e}")
            raise

    def _generate_compose_dict(self) -> dict[str, Any]:
        """
        Generates the full compose configuration as a Python dictionary.
        """
        logger.debug("Generating compose dictionary.")
        cfg = self.config
        services = {}
        network_name = cfg.container_env.network.name

        # 1. Determine which servers to activate
        if cfg.active_servers is None:
            # If active_servers is not defined, use all servers from the servers dict
            active_server_names = list(cfg.servers.keys())
            logger.debug(f"'active_servers' not defined. Activating all defined servers: {active_server_names}")
        else:
            # Otherwise, filter the servers dict by the active_servers list
            active_server_names = [name for name in cfg.active_servers if name in cfg.servers]
            logger.debug(f"Activating servers based on 'active_servers' list: {active_server_names}")
            
            # Warn about any servers in active_servers that are not in the servers dict
            for name in cfg.active_servers:
                if name not in cfg.servers:
                    logger.warning(f"Server '{name}' from 'active_servers' is not defined in the 'servers' section and will be ignored.")


        # 2. Velocity Service
        logger.debug("Generating 'velocity' service configuration.")
        velocity_image_key = cfg.velocity.java_version
        try:
            velocity_image = getattr(cfg.container_env.images, velocity_image_key)
        except AttributeError:
            logger.error(f"Image key '{velocity_image_key}' for Velocity not found in images config.")
            raise ValueError(f"Image key '{velocity_image_key}' for Velocity not found in images config.")

        velocity_venv_volume = f"{cfg.cluster_name.lower().replace(' ', '-')}-{cfg.velocity.service_name}-venv"
        services[cfg.velocity.service_name] = {
            "image": velocity_image,
            "container_name": f"{cfg.cluster_name.lower().replace(' ', '-')}-{cfg.velocity.service_name}",
            "ports": [f"{cfg.velocity.port}:25565"],  # Standard velocity port is 25565
            "volumes": [
                f"../{cfg.servers_dir}/{cfg.velocity.service_name}:/app:Z",
                f"{velocity_venv_volume}:/app/.venv"
            ],
            "networks": [network_name],
            "restart": "unless-stopped",
            "stdin_open": True,
            "tty": True,
        }

        # 3. Backend Servers
        logger.debug(f"Generating configurations for {len(active_server_names)} active server(s).")
        for server_name in active_server_names:
            server_config = cfg.servers[server_name]
            logger.debug(f"Generating configuration for server: '{server_name}'.")
            server_image_key = server_config.java_version
            try:
                server_image = getattr(cfg.container_env.images, server_image_key)
            except AttributeError:
                logger.error(f"Image key '{server_image_key}' for server '{server_name}' not found in images config.")
                raise ValueError(f"Image key '{server_image_key}' for server '{server_name}' not found in images config.")

            server_venv_volume = f"{cfg.cluster_name.lower().replace(' ', '-')}-{server_name}-venv"
            services[server_name] = {
                "image": server_image,
                "container_name": f"{cfg.cluster_name.lower().replace(' ', '-')}-{server_name}",
                "volumes": [
                    f"../{cfg.servers_dir}/{server_name}:/app:Z",
                    f"{server_venv_volume}:/app/.venv"
                ],
                "networks": [network_name],
                "restart": "unless-stopped",
                "stdin_open": True,
                "tty": True,
            }

        # 4. Network Definition
        logger.debug("Generating network configuration.")
        networks = {
            network_name: {
                "driver": "bridge",
                "name": network_name,
            }
        }

        # 5. Volume Definition
        logger.debug("Generating volume configuration.")
        volumes = {}
        
        # Add velocity venv volume
        velocity_venv_volume = f"{cfg.cluster_name.lower().replace(' ', '-')}-{cfg.velocity.service_name}-venv"
        volumes[velocity_venv_volume] = {"driver": "local"}
        
        # Add server venv volumes
        for server_name in active_server_names:
            server_venv_volume = f"{cfg.cluster_name.lower().replace(' ', '-')}-{server_name}-venv"
            volumes[server_venv_volume] = {"driver": "local"}

        compose_dict = {
            "version": "3.8",
            "services": services,
            "networks": networks,
            "volumes": volumes,
        }
        logger.debug("Finished generating compose dictionary.")
        return compose_dict

    def up(self):
        """
        Generates the compose file and starts the cluster in detached mode.
        """
        try:
            # Step 0: Ensure all required images exist (build if necessary)
            self._ensure_images_exist()
            
            # Step 1: Generate the configuration dictionary
            logger.step("Generating compose configuration...")
            compose_dict = self._generate_compose_dict()

            # Step 2: Save the compose file
            lmcp_dir = self.project_root / self.config.lmcp_dir
            lmcp_dir.mkdir(exist_ok=True)
            compose_file_path = lmcp_dir / "compose.yml"

            logger.debug(f"Saving compose file to {compose_file_path}")
            with open(compose_file_path, 'w', encoding='utf-8') as f:
                self.yaml.dump(compose_dict, f)
            logger.success(f"Compose file generated at {compose_file_path}")

            # Step 3: Detect compose command and execute
            compose_cmd = self._get_compose_command()
            logger.step(f"Starting cluster using {compose_cmd}...")

            cmd_args = [compose_cmd, "-f", str(compose_file_path), "up", "-d"]

            # Run the command from the project root for correct relative path resolution
            process = subprocess.run(
                cmd_args,
                cwd=self.project_root,
                capture_output=True,
                text=True,
                check=False  # We check the return code manually
            )

            # Step 4: Process the result
            if process.returncode == 0:
                logger.success("Cluster command executed successfully.")
                if process.stdout:
                    logger.info(process.stdout.strip())
                if process.stderr:
                    logger.warning(process.stderr.strip())
            else:
                logger.error("Failed to execute cluster command.")
                logger.error(f"Return Code: {process.returncode}")
                if process.stdout:
                    logger.error(f"Stdout:\n{process.stdout.strip()}")
                if process.stderr:
                    logger.error(f"Stderr:\n{process.stderr.strip()}")

        except (FileNotFoundError, ValueError) as e:
            logger.error(str(e))
        except Exception as e:
            logger.critical(f"An unexpected error occurred during the 'up' process: {e}", exc_info=True)

    def down(self):
        """
        Stops and removes the containers and networks for the cluster.
        """
        try:
            # Step 1: Locate the compose file
            lmcp_dir = self.project_root / self.config.lmcp_dir
            compose_file_path = lmcp_dir / "compose.yml"

            if not compose_file_path.exists():
                logger.warning("Compose file not found. The cluster might not have been started with 'up' or is already down.")
                return

            # Step 2: Detect compose command and execute 'down'
            compose_cmd = self._get_compose_command()
            logger.step(f"Stopping cluster using {compose_cmd}...")

            cmd_args = [compose_cmd, "-f", str(compose_file_path), "down"]

            process = subprocess.run(
                cmd_args,
                cwd=self.project_root,
                capture_output=True,
                text=True,
                check=False
            )

            # Step 3: Process the result
            if process.returncode == 0:
                logger.success("Cluster stopped successfully.")
                if process.stdout:
                    logger.info(process.stdout.strip())
                if process.stderr:
                    logger.warning(process.stderr.strip())
            else:
                logger.error("Failed to stop the cluster.")
                logger.error(f"Return Code: {process.returncode}")
                if process.stdout:
                    logger.error(f"Stdout:\n{process.stdout.strip()}")
                if process.stderr:
                    logger.error(f"Stderr:\n{process.stderr.strip()}")

        except FileNotFoundError as e:
            logger.error(str(e))
        except Exception as e:
            logger.critical(f"An unexpected error occurred during the 'down' process: {e}", exc_info=True)