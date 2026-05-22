import asyncio
import logging
from typing import List, Optional, Dict, Any
from datetime import datetime
import numpy as np
from pathlib import Path

import cv2
from ultralytics import YOLO

from src.models.detection import Detection, DetectionEvent
from src.database import AsyncSessionLocal

logger = logging.getLogger(__name__)


class BoundingBox:
    def __init__(self, x_min: float, y_min: float, x_max: float, y_max: float):
        self.x_min = x_min
        self.y_min = y_min
        self.x_max = x_max
        self.y_max = y_max
        self.width = x_max - x_min
        self.height = y_max - y_min
        self.area = self.width * self.height

    def to_dict(self) -> Dict[str, float]:
        return {
            "x_min": self.x_min,
            "y_min": self.y_min,
            "x_max": self.x_max,
            "y_max": self.y_max,
            "width": self.width,
            "height": self.height,
            "area": self.area,
        }


class DetectionResult:
    """Single detection from vision model"""

    def __init__(
        self,
        detection_type: str,
        class_name: str,
        confidence: float,
        bbox: BoundingBox,
        image_height: int,
        image_width: int,
        model_name: str = "yolov11m",
        inference_time_ms: float = 0,
    ):
        self.detection_type = detection_type
        self.class_name = class_name
        self.confidence = confidence
        self.bbox = bbox
        self.image_height = image_height
        self.image_width = image_width
        self.model_name = model_name
        self.inference_time_ms = inference_time_ms

    def to_dict(self) -> Dict[str, Any]:
        return {
            "detection_type": self.detection_type,
            "class_name": self.class_name,
            "confidence": float(self.confidence),
            "bbox": self.bbox.to_dict(),
            "image_height": self.image_height,
            "image_width": self.image_width,
            "model_name": self.model_name,
            "inference_time_ms": float(self.inference_time_ms),
        }


class VisionService:
    """
    Computer vision service for plant-level detection.
    Uses YOLOv11 for real-time weed/pest/disease detection.
    """

    def __init__(self, model_path: str = "/models/yolov11m.pt"):
        self.model_path = Path(model_path)
        self.model = None
        self.confidence_threshold = 0.5
        self.iou_threshold = 0.45

        # Class mappings
        self.class_mapping = {
            "weed": [
                "dandelion",
                "chickweed",
                "crabgrass",
                "pigweed",
                "foxtail",
                "bindweed",
                "thistles",
                "docks",
            ],
            "pest": [
                "aphids",
                "spider_mites",
                "whiteflies",
                "thrips",
                "beetles",
                "armyworms",
                "caterpillars",
                "grasshoppers",
            ],
            "disease": [
                "early_blight",
                "late_blight",
                "powdery_mildew",
                "rust",
                "leaf_spot",
                "anthracnose",
                "wilt",
                "canker",
            ],
            "crop": ["healthy_plant", "crop_row"],
        }

    def load_model(self) -> bool:
        """Load YOLOv11 model"""
        try:
            logger.info(f"Loading vision model from {self.model_path}")
            self.model = YOLO(str(self.model_path))
            self.model.conf = self.confidence_threshold
            self.model.iou = self.iou_threshold
            logger.info("Vision model loaded successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to load vision model: {e}")
            return False

    async def detect_objects(
        self,
        image_path: str,
        image_array: Optional[np.ndarray] = None,
        confidence_threshold: Optional[float] = None,
    ) -> List[DetectionResult]:
        """
        Run inference on image to detect objects.

        Args:
            image_path: Path to image file
            image_array: Optional numpy array instead of path
            confidence_threshold: Override default threshold

        Returns:
            List of DetectionResult objects
        """
        if self.model is None:
            logger.warning("Model not loaded, loading now")
            if not self.load_model():
                return []

        if confidence_threshold:
            self.model.conf = confidence_threshold
        else:
            self.model.conf = self.confidence_threshold

        try:
            # Load image
            if image_array is not None:
                image = image_array
            else:
                image = cv2.imread(image_path)
                if image is None:
                    raise ValueError(f"Failed to load image: {image_path}")

            image_height, image_width = image.shape[:2]

            # Run inference
            import time

            start_time = time.time()
            results = self.model(image, verbose=False)
            inference_time_ms = (time.time() - start_time) * 1000

            detections = []

            # Process results
            for result in results:
                if result.boxes is None:
                    continue

                for box in result.boxes:
                    confidence = float(box.conf[0])
                    if confidence < self.confidence_threshold:
                        continue

                    # Get class name
                    class_id = int(box.cls[0])
                    class_name = self.model.names[class_id]

                    # Determine detection type
                    detection_type = self._classify_detection(class_name)

                    # Get bounding box
                    coords = box.xyxy[0].cpu().numpy()
                    bbox = BoundingBox(
                        float(coords[0]), float(coords[1]), float(coords[2]), float(coords[3])
                    )

                    detection = DetectionResult(
                        detection_type=detection_type,
                        class_name=class_name,
                        confidence=confidence,
                        bbox=bbox,
                        image_height=image_height,
                        image_width=image_width,
                        model_name="yolov11m",
                        inference_time_ms=inference_time_ms,
                    )
                    detections.append(detection)

            logger.info(f"Detected {len(detections)} objects in {inference_time_ms:.1f}ms")
            return detections

        except Exception as e:
            logger.error(f"Error during inference: {e}")
            return []

    def _classify_detection(self, class_name: str) -> str:
        """Map class name to detection type"""
        for detection_type, classes in self.class_mapping.items():
            if class_name.lower() in [c.lower() for c in classes]:
                return detection_type
        return "unknown"

    async def process_field_image(
        self,
        field_id: str,
        image_path: str,
        lat: float,
        lon: float,
    ) -> List[Detection]:
        """
        Process field image and save detections to database.

        Args:
            field_id: UUID of field
            image_path: Path to image
            lat: Latitude
            lon: Longitude

        Returns:
            List of Detection objects saved to database
        """
        detections = []

        try:
            # Run inference
            results = await self.detect_objects(image_path)

            if not results:
                logger.info(f"No detections in field {field_id}")
                return []

            # Save to database
            async with AsyncSessionLocal() as session:
                for result in results:
                    detection = Detection(
                        field_id=field_id,
                        detection_type=result.detection_type,
                        class_name=result.class_name,
                        confidence=result.confidence,
                        location=f"POINT({lon} {lat})",
                        image_url=image_path,
                        bbox_x_min=result.bbox.x_min,
                        bbox_y_min=result.bbox.y_min,
                        bbox_x_max=result.bbox.x_max,
                        bbox_y_max=result.bbox.y_max,
                        bbox_area_pixels=result.bbox.area,
                        model_name=result.model_name,
                        model_version="1.0",
                        inference_time_ms=result.inference_time_ms,
                        image_size_pixels={
                            "width": result.image_width,
                            "height": result.image_height,
                        },
                    )
                    session.add(detection)
                    detections.append(detection)

                await session.commit()
                logger.info(f"Saved {len(detections)} detections for field {field_id}")

        except Exception as e:
            logger.error(f"Error processing field image: {e}")

        return detections

    async def batch_detect(
        self,
        image_paths: List[str],
        batch_size: int = 32,
    ) -> Dict[str, List[DetectionResult]]:
        """Batch process multiple images"""
        results = {}
        for image_path in image_paths:
            detections = await self.detect_objects(image_path)
            results[image_path] = detections
        return results

    def get_model_info(self) -> Dict[str, Any]:
        """Get information about loaded model"""
        if self.model is None:
            return {"status": "not_loaded"}

        return {
            "status": "loaded",
            "model_name": "YOLOv11m",
            "num_classes": len(self.model.names),
            "classes": list(self.model.names.values()),
            "input_size": 640,
            "confidence_threshold": self.confidence_threshold,
        }
