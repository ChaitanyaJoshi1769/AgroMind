from fastapi import APIRouter

from src.api.routes import farms, fields, telemetry, vision, robotics, predictions, treatments, marketplace, enterprise

router = APIRouter()

# Include sub-routers
router.include_router(farms.router, prefix="/farms", tags=["farms"])
router.include_router(fields.router, prefix="/fields", tags=["fields"])
router.include_router(telemetry.router, prefix="/telemetry", tags=["telemetry"])
router.include_router(vision.router, prefix="/vision", tags=["vision"])
router.include_router(robotics.router, prefix="/robotics", tags=["robotics"])
router.include_router(predictions.router, prefix="/predictions", tags=["predictions"])
router.include_router(treatments.router, prefix="/treatments", tags=["treatments"])
router.include_router(marketplace.router, prefix="/marketplace", tags=["marketplace"])
router.include_router(enterprise.router, prefix="/enterprise", tags=["enterprise"])
