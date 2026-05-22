from fastapi import APIRouter, File, UploadFile
from typing import list

router = APIRouter()

@router.post("/detect")
async def detect_objects(file: UploadFile = File(...)) -> dict:
    """Detect objects in image"""
    return {"detections": [], "confidence": 0.85}

@router.get("/models")
async def list_models() -> dict:
    """List available vision models"""
    return {"models": ["yolov11m", "sam-base"]}
