from fastapi import APIRouter

router = APIRouter()

@router.get("/fleet")
async def get_fleet_status() -> dict:
    """Get fleet status"""
    return {"robots": [], "available": 0, "active": 0}

@router.post("/mission")
async def create_mission(mission_data: dict) -> dict:
    """Create robot mission"""
    return {"mission_id": "mission_001", "status": "queued"}

@router.get("/mission/{mission_id}")
async def get_mission_status(mission_id: str) -> dict:
    """Get mission status"""
    return {"mission_id": mission_id, "status": "in_progress", "progress": 45}
