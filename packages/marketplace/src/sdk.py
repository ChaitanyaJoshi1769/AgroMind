"""Plugin SDK for third-party developers"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List
from enum import Enum


class PluginCapability(str, Enum):
    VISION_INFERENCE = "vision_inference"
    PEST_DETECTION = "pest_detection"
    DISEASE_DETECTION = "disease_detection"
    YIELD_PREDICTION = "yield_prediction"
    IRRIGATION_OPTIMIZATION = "irrigation_optimization"
    DRONE_CONTROL = "drone_control"
    SENSOR_INTEGRATION = "sensor_integration"
    DATA_ANALYTICS = "data_analytics"


class AgroMindPlugin(ABC):
    """Base class for all AgroMind marketplace plugins"""

    def __init__(self, plugin_id: str, version: str):
        self.plugin_id = plugin_id
        self.version = version
        self.capabilities = []
        self.config = {}

    @abstractmethod
    async def initialize(self, config: Dict[str, Any]) -> bool:
        """Initialize plugin with farm-specific config"""
        pass

    @abstractmethod
    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute plugin logic"""
        pass

    async def validate_compatibility(self, system_version: str) -> bool:
        """Validate plugin compatibility with AgroMind version"""
        return True

    async def get_plugin_metadata(self) -> Dict[str, Any]:
        return {
            "id": self.plugin_id,
            "version": self.version,
            "capabilities": self.capabilities,
            "required_dependencies": [],
        }


class SensorPluginInterface(AgroMindPlugin):
    """Interface for sensor driver plugins"""

    @abstractmethod
    async def read_sensor_data(self) -> Dict[str, Any]:
        pass

    @abstractmethod
    async def calibrate(self) -> bool:
        pass


class VisionPluginInterface(AgroMindPlugin):
    """Interface for vision model plugins"""

    @abstractmethod
    async def infer(self, image_path: str) -> Dict[str, Any]:
        pass

    @abstractmethod
    async def get_model_info(self) -> Dict[str, Any]:
        pass


class AgentPluginInterface(AgroMindPlugin):
    """Interface for autonomous agent plugins"""

    @abstractmethod
    async def make_decision(self, farm_state: Dict[str, Any]) -> Dict[str, Any]:
        pass
