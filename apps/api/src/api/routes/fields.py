from fastapi import APIRouter
from typing import list

router = APIRouter()


@router.get("/")
async def list_fields() -> dict:
    """List all fields"""
    return {"data": []}


@router.get("/{field_id}")
async def get_field(field_id: str) -> dict:
    """Get field by ID"""
    return {"id": field_id, "name": "Field", "status": "active"}
