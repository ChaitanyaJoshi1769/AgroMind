from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from typing import List
from uuid import UUID

from src.database import get_db
from src.services.robotics import RoboticsService
from src.models.mission import RobotMission
from src.models.asset import Robot

router = APIRouter()
robotics_service = RoboticsService()


class MissionCreate(BaseModel):
    farm_id: UUID
    robot_id: UUID
    mission_type: str
    mission_name: str = None
    waypoints: List[dict] = []


class MissionResponse(BaseModel):
    id: UUID
    robot_id: UUID
    mission_type: str
    status: str
    total_steps: int
    completed_steps: int


@router.get("/fleet/{farm_id}")
async def get_fleet_status(farm_id: UUID, db: AsyncSession = Depends(get_db)):
    """Get status of robot fleet on farm"""
    fleet_status = await robotics_service.get_fleet_status(farm_id)
    return fleet_status


@router.get("/robot/{robot_id}")
async def get_robot_status(robot_id: UUID, db: AsyncSession = Depends(get_db)):
    """Get status of specific robot"""
    status = await robotics_service.get_robot_status(robot_id)
    return status


@router.post("/mission")
async def create_mission(
    mission: MissionCreate,
    db: AsyncSession = Depends(get_db),
):
    """Create new robot mission"""
    created_mission = await robotics_service.create_mission(
        field_id=mission.farm_id,
        robot_id=mission.robot_id,
        mission_type=mission.mission_type,
        waypoints=mission.waypoints,
        mission_name=mission.mission_name,
    )

    if not created_mission:
        raise HTTPException(status_code=400, detail="Failed to create mission")

    return {
        "id": str(created_mission.id),
        "robot_id": str(created_mission.robot_id),
        "mission_type": created_mission.mission_type,
        "status": created_mission.status,
        "total_steps": created_mission.total_steps,
        "estimated_duration_hours": created_mission.estimated_duration_hours,
    }


@router.post("/mission/{mission_id}/start")
async def start_mission(mission_id: UUID, db: AsyncSession = Depends(get_db)):
    """Start executing a mission"""
    success = await robotics_service.start_mission(mission_id)
    if not success:
        raise HTTPException(status_code=404, detail="Mission not found")
    return {"mission_id": str(mission_id), "status": "started"}


@router.post("/mission/{mission_id}/pause")
async def pause_mission(mission_id: UUID, db: AsyncSession = Depends(get_db)):
    """Pause executing mission"""
    success = await robotics_service.pause_mission(mission_id)
    if not success:
        raise HTTPException(status_code=404, detail="Mission not found")
    return {"mission_id": str(mission_id), "status": "paused"}


@router.post("/mission/{mission_id}/resume")
async def resume_mission(mission_id: UUID, db: AsyncSession = Depends(get_db)):
    """Resume paused mission"""
    success = await robotics_service.resume_mission(mission_id)
    if not success:
        raise HTTPException(status_code=404, detail="Mission not found")
    return {"mission_id": str(mission_id), "status": "resumed"}


@router.post("/mission/{mission_id}/cancel")
async def cancel_mission(mission_id: UUID, db: AsyncSession = Depends(get_db)):
    """Cancel mission"""
    success = await robotics_service.cancel_mission(mission_id)
    if not success:
        raise HTTPException(status_code=404, detail="Mission not found")
    return {"mission_id": str(mission_id), "status": "cancelled"}


@router.get("/mission/{mission_id}")
async def get_mission_status(mission_id: UUID, db: AsyncSession = Depends(get_db)):
    """Get mission status and progress"""
    mission = await db.get(RobotMission, mission_id)
    if not mission:
        raise HTTPException(status_code=404, detail="Mission not found")

    progress_percent = 0
    if mission.total_steps > 0:
        progress_percent = (mission.completed_steps / mission.total_steps) * 100

    return {
        "mission_id": str(mission.id),
        "robot_id": str(mission.robot_id),
        "mission_type": mission.mission_type,
        "status": mission.status,
        "total_steps": mission.total_steps,
        "completed_steps": mission.completed_steps,
        "progress_percent": progress_percent,
        "estimated_completion": mission.estimated_completion.isoformat() if mission.estimated_completion else None,
    }


@router.post("/robot/{robot_id}/telemetry")
async def update_robot_telemetry(
    robot_id: UUID,
    latitude: float,
    longitude: float,
    battery_level: float,
    db: AsyncSession = Depends(get_db),
):
    """Update robot location and status"""
    success = await robotics_service.update_robot_location(
        robot_id, latitude, longitude, battery_level
    )

    if not success:
        raise HTTPException(status_code=404, detail="Robot not found")

    return {"robot_id": str(robot_id), "status": "updated"}
