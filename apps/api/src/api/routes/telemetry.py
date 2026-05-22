from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def get_telemetry() -> dict:
    """Get telemetry data"""
    return {"data": []}

@router.post("/")
async def post_telemetry(data: dict) -> dict:
    """Ingest telemetry data"""
    return {"status": "received"}
