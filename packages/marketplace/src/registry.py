"""Plugin registry and lifecycle management"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class PluginRegistry:
    """Central registry for plugin discovery, installation, and lifecycle"""

    def __init__(self):
        self.installed_plugins = {}
        self.plugin_instances = {}
        self.plugin_configs = {}
        self.plugin_dependencies = {}
        self.execution_logs = []

    async def register_plugin(
        self,
        plugin_id: str,
        plugin_class: type,
        metadata: Dict[str, Any],
    ) -> bool:
        """Register a plugin in the marketplace"""
        logger.info(f"Registering plugin {plugin_id}")

        self.installed_plugins[plugin_id] = {
            "class": plugin_class,
            "metadata": metadata,
            "install_date": datetime.utcnow().isoformat(),
            "status": "installed",
            "version": metadata.get("version", "1.0.0"),
        }
        return True

    async def instantiate_plugin(
        self,
        plugin_id: str,
        config: Dict[str, Any],
    ) -> Optional[Any]:
        """Create a plugin instance"""
        if plugin_id not in self.installed_plugins:
            logger.error(f"Plugin {plugin_id} not found")
            return None

        plugin_class = self.installed_plugins[plugin_id]["class"]
        try:
            instance = plugin_class(plugin_id, "1.0.0")
            await instance.initialize(config)
            self.plugin_instances[plugin_id] = instance
            self.plugin_configs[plugin_id] = config
            logger.info(f"Plugin {plugin_id} instantiated successfully")
            return instance
        except Exception as e:
            logger.error(f"Failed to instantiate {plugin_id}: {str(e)}")
            return None

    async def execute_plugin(
        self,
        plugin_id: str,
        input_data: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Execute a plugin"""
        if plugin_id not in self.plugin_instances:
            return {"error": f"Plugin {plugin_id} not instantiated"}

        instance = self.plugin_instances[plugin_id]
        try:
            result = await instance.execute(input_data)
            self.execution_logs.append(
                {
                    "plugin_id": plugin_id,
                    "timestamp": datetime.utcnow().isoformat(),
                    "status": "success",
                }
            )
            return result
        except Exception as e:
            logger.error(f"Plugin execution failed: {str(e)}")
            self.execution_logs.append(
                {
                    "plugin_id": plugin_id,
                    "timestamp": datetime.utcnow().isoformat(),
                    "status": "failed",
                    "error": str(e),
                }
            )
            return {"error": str(e)}

    async def uninstall_plugin(self, plugin_id: str) -> bool:
        """Uninstall a plugin"""
        if plugin_id in self.plugin_instances:
            del self.plugin_instances[plugin_id]
        if plugin_id in self.installed_plugins:
            del self.installed_plugins[plugin_id]
        if plugin_id in self.plugin_configs:
            del self.plugin_configs[plugin_id]
        logger.info(f"Plugin {plugin_id} uninstalled")
        return True

    def get_plugin_status(self, plugin_id: str) -> Dict[str, Any]:
        """Get plugin status"""
        if plugin_id not in self.installed_plugins:
            return {"status": "not_found"}

        return {
            "plugin_id": plugin_id,
            "status": self.installed_plugins[plugin_id]["status"],
            "version": self.installed_plugins[plugin_id]["version"],
            "installed_date": self.installed_plugins[plugin_id]["install_date"],
            "instantiated": plugin_id in self.plugin_instances,
        }

    def list_installed_plugins(self) -> List[Dict[str, Any]]:
        """List all installed plugins"""
        return [
            {
                "plugin_id": pid,
                "version": info["version"],
                "status": info["status"],
            }
            for pid, info in self.installed_plugins.items()
        ]
