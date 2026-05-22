"""Marketplace models for plugins, agents, and data"""

from datetime import datetime
from uuid import UUID
from enum import Enum


class PluginCategory(str, Enum):
    VISION_MODEL = "vision_model"
    BIOLOGICAL_AGENT = "biological_agent"
    SENSOR_DRIVER = "sensor_driver"
    ROBOT_INTEGRATION = "robot_integration"
    AGRONOMY_MODEL = "agronomy_model"
    WEATHER_DATA = "weather_data"
    DISEASE_DETECTION = "disease_detection"


class Plugin:
    """Marketplace plugin entry"""

    def __init__(
        self,
        name: str,
        category: PluginCategory,
        version: str,
        developer: str,
        description: str,
        price_usd: float,
        rating: float = 0.0,
        download_count: int = 0,
    ):
        self.id = str(UUID('12345678-1234-5678-1234-567812345678'))
        self.name = name
        self.category = category
        self.version = version
        self.developer = developer
        self.description = description
        self.price_usd = price_usd
        self.rating = rating
        self.download_count = download_count
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "category": self.category.value,
            "version": self.version,
            "developer": self.developer,
            "description": self.description,
            "price_usd": self.price_usd,
            "rating": self.rating,
            "download_count": self.download_count,
        }


class MarketplaceService:
    """Marketplace operations"""

    def __init__(self):
        self.plugins = {}

    async def list_plugins(
        self,
        category: str = None,
        sort_by: str = "downloads",
    ) -> list:
        """List available plugins"""
        plugins = [
            {
                "name": "YOLOv11 Weed Detector",
                "category": "vision_model",
                "developer": "AgroMind Labs",
                "price_usd": 99.99,
                "rating": 4.8,
                "downloads": 2341,
            },
            {
                "name": "Beneficial Insect Library",
                "category": "biological_agent",
                "developer": "BioControl Inc",
                "price_usd": 49.99,
                "rating": 4.6,
                "downloads": 1203,
            },
        ]
        return plugins

    async def search_plugins(self, query: str) -> list:
        """Search marketplace for plugins"""
        return []

    async def install_plugin(
        self,
        farm_id: str,
        plugin_id: str,
    ) -> bool:
        """Install plugin on farm"""
        return True

    async def get_plugin_details(self, plugin_id: str) -> dict:
        """Get detailed plugin info"""
        return {
            "id": plugin_id,
            "documentation": "https://docs.example.com",
            "source_code": "https://github.com/example",
            "changelog": ["v1.2.1: Fixed edge cases", "v1.2: Added new models"],
        }

    async def rate_plugin(
        self,
        plugin_id: str,
        rating: float,
        review: str = "",
    ) -> bool:
        """Rate and review plugin"""
        return True

    async def publish_plugin(
        self,
        name: str,
        category: str,
        version: str,
        price_usd: float,
    ) -> dict:
        """Publish plugin to marketplace"""
        return {
            "plugin_id": "plugin_123",
            "status": "approved",
            "listing_date": datetime.utcnow().isoformat(),
        }
