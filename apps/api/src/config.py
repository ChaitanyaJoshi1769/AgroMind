from pydantic_settings import BaseSettings
from typing import list


class Settings(BaseSettings):
    # App
    DEBUG: bool = True
    VERSION: str = "0.0.1"

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://agromind:agromind@localhost:5432/agromind"
    DATABASE_ECHO: bool = False
    DATABASE_POOL_SIZE: int = 20
    DATABASE_MAX_OVERFLOW: int = 20

    # Redis
    REDIS_URL: str = "redis://localhost:6379"

    # CORS
    CORS_ORIGINS: list[str] = [
        "http://localhost:3000",
        "http://localhost:3001",
        "http://localhost:8000",
        "http://localhost:8001",
    ]

    # JWT
    JWT_SECRET_KEY: str = "change-me-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_HOURS: int = 24

    # Kafka
    KAFKA_BROKERS: str = "localhost:9092"
    KAFKA_COMPRESSION_TYPE: str = "snappy"

    # Vision API
    VISION_MODEL_PATH: str = "/models/yolov11m.onnx"
    VISION_CONFIDENCE_THRESHOLD: float = 0.5
    VISION_IOU_THRESHOLD: float = 0.45

    # Robotics
    ROBOTICS_ENABLE_SIMULATION: bool = True
    ROBOTICS_BASE_URL: str = "http://localhost:9000"

    # Geospatial
    POSTGIS_ENABLED: bool = True
    MAPBOX_ACCESS_TOKEN: str = ""

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
