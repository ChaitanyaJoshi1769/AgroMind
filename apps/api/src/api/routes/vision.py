from fastapi import APIRouter, File, UploadFile, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from uuid import UUID
import tempfile
import os

from src.database import get_db
from src.services.vision import VisionService
from src.models.detection import Detection

router = APIRouter()
vision_service = VisionService()


# Load model on startup
@router.on_event("startup")
async def load_vision_model():
    vision_service.load_model()


@router.post("/detect")
async def detect_objects(
    field_id: UUID,
    file: UploadFile = File(...),
    latitude: float = Query(...),
    longitude: float = Query(...),
    db: AsyncSession = Depends(get_db),
):
    """Detect objects in uploaded image using YOLOv11"""
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")

    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
            contents = await file.read()
            tmp.write(contents)
            tmp_path = tmp.name

        detections = await vision_service.process_field_image(
            field_id=str(field_id),
            image_path=tmp_path,
            lat=latitude,
            lon=longitude,
        )

        os.unlink(tmp_path)

        return {
            "field_id": str(field_id),
            "num_detections": len(detections),
            "detections": [
                {
                    "id": str(d.id),
                    "type": d.detection_type,
                    "class": d.class_name,
                    "confidence": float(d.confidence),
                    "severity": d.severity,
                    "bbox": {
                        "x_min": d.bbox_x_min,
                        "y_min": d.bbox_y_min,
                        "x_max": d.bbox_x_max,
                        "y_max": d.bbox_y_max,
                    },
                }
                for d in detections
            ],
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Detection failed: {str(e)}")


@router.get("/models")
async def list_models():
    """Get available vision models and specs"""
    return vision_service.get_model_info()


@router.get("/detections/{field_id}")
async def get_field_detections(
    field_id: UUID,
    skip: int = 0,
    limit: int = 100,
    status: str = None,
    db: AsyncSession = Depends(get_db),
):
    """Get all detections for a field"""
    from sqlalchemy import select

    query = select(Detection).where(Detection.field_id == field_id)
    if status:
        query = query.where(Detection.status == status)

    query = query.offset(skip).limit(limit)
    results = (await db.execute(query)).scalars().all()

    return {
        "field_id": str(field_id),
        "count": len(results),
        "detections": [
            {
                "id": str(d.id),
                "type": d.detection_type,
                "class": d.class_name,
                "confidence": float(d.confidence),
                "status": d.status,
                "created_at": d.created_at.isoformat(),
            }
            for d in results
        ],
    }
