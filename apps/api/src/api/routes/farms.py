from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from typing import list
import uuid

from src.database import get_db

router = APIRouter()


class FarmCreate(BaseModel):
    name: str
    location: str
    area_acres: float
    crop_type: str


class FarmResponse(BaseModel):
    id: str
    name: str
    location: str
    area_acres: float
    crop_type: str

    class Config:
        from_attributes = True


@router.get("/", response_model=list[FarmResponse])
async def list_farms(db: AsyncSession = Depends(get_db)) -> list[FarmResponse]:
    """List all farms"""
    # Placeholder - actual implementation will use database
    return []


@router.get("/{farm_id}", response_model=FarmResponse)
async def get_farm(farm_id: str, db: AsyncSession = Depends(get_db)) -> FarmResponse:
    """Get farm by ID"""
    raise HTTPException(status_code=404, detail="Farm not found")


@router.post("/", response_model=FarmResponse)
async def create_farm(
    farm: FarmCreate, db: AsyncSession = Depends(get_db)
) -> FarmResponse:
    """Create a new farm"""
    # Placeholder - actual implementation will use database
    return FarmResponse(
        id=str(uuid.uuid4()),
        name=farm.name,
        location=farm.location,
        area_acres=farm.area_acres,
        crop_type=farm.crop_type,
    )
