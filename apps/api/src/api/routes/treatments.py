from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from typing import List, Optional
from uuid import UUID
from datetime import datetime

from src.database import get_db
from src.services.biological import BiologicalIntelligence
from src.models.treatment import Treatment, BiologicalAgent, ChemicalProduct

router = APIRouter()
biological_intel = BiologicalIntelligence()


class TreatmentRecommendationRequest(BaseModel):
    field_id: UUID
    crop_id: UUID
    detected_pest: str
    severity: str = "moderate"


class TreatmentApplicationRequest(BaseModel):
    field_id: UUID
    farm_id: UUID
    treatment_type: str
    product_id: Optional[UUID] = None
    agent_id: Optional[UUID] = None
    target_pest: Optional[str] = None
    application_method: str
    application_rate: float
    application_date: datetime
    notes: Optional[str] = None


@router.post("/recommend")
async def get_treatment_recommendations(
    request: TreatmentRecommendationRequest,
    db: AsyncSession = Depends(get_db),
):
    """Get treatment recommendations for detected pest/disease"""
    recommendations = await biological_intel.get_treatment_recommendations(
        field_id=request.field_id,
        crop_id=request.crop_id,
        detected_pest=request.detected_pest,
        severity=request.severity,
    )

    return {
        "pest": request.detected_pest,
        "severity": request.severity,
        "recommendations": [rec.to_dict() for rec in recommendations],
        "count": len(recommendations),
    }


@router.post("/apply")
async def apply_treatment(
    request: TreatmentApplicationRequest,
    db: AsyncSession = Depends(get_db),
):
    """Record treatment application"""
    try:
        treatment = Treatment(
            farm_id=request.farm_id,
            field_id=request.field_id,
            treatment_type=request.treatment_type,
            product_id=request.product_id,
            agent_id=request.agent_id,
            target_pest=request.target_pest,
            application_method=request.application_method,
            application_rate_per_acre=request.application_rate,
            application_date=request.application_date,
            status="applied",
        )

        db.add(treatment)
        await db.commit()

        return {
            "treatment_id": str(treatment.id),
            "status": "applied",
            "field_id": str(treatment.field_id),
            "application_date": treatment.application_date.isoformat(),
        }

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to apply treatment: {str(e)}")


@router.get("/history/{field_id}")
async def get_treatment_history(
    field_id: UUID,
    days: int = 365,
    db: AsyncSession = Depends(get_db),
):
    """Get treatment history for a field"""
    history = await biological_intel.get_treatment_history(field_id, days)

    return {
        "field_id": str(field_id),
        "period_days": days,
        "total_treatments": len(history),
        "treatments": history,
    }


@router.get("/resistance-risk/{pest_name}")
async def predict_resistance(
    pest_name: str,
    field_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """Predict herbicide/pesticide resistance for a pest"""
    history = await biological_intel.get_treatment_history(field_id, 365)
    resistance_analysis = await biological_intel.predict_resistance(
        pest_name, history
    )

    return resistance_analysis


@router.get("/agents")
async def list_biological_agents(
    skip: int = 0,
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
):
    """List available biological agents"""
    from sqlalchemy import select

    query = select(BiologicalAgent).offset(skip).limit(limit)
    agents = (await db.execute(query)).scalars().all()

    return {
        "count": len(agents),
        "agents": [
            {
                "id": str(a.id),
                "name": a.agent_name,
                "type": a.agent_type,
                "target_pest": a.target_pest,
                "efficacy": a.average_efficacy,
            }
            for a in agents
        ],
    }


@router.get("/chemicals")
async def list_chemical_products(
    skip: int = 0,
    limit: int = 50,
    product_type: str = None,
    db: AsyncSession = Depends(get_db),
):
    """List available chemical products"""
    from sqlalchemy import select

    query = select(ChemicalProduct)

    if product_type:
        query = query.where(ChemicalProduct.product_type == product_type)

    query = query.offset(skip).limit(limit)
    chemicals = (await db.execute(query)).scalars().all()

    return {
        "count": len(chemicals),
        "chemicals": [
            {
                "id": str(c.id),
                "name": c.product_name,
                "type": c.product_type,
                "active_ingredient": c.active_ingredient,
                "toxicity_class": c.toxicity_class,
            }
            for c in chemicals
        ],
    }


@router.get("/treatment/{treatment_id}")
async def get_treatment_details(
    treatment_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """Get details of a specific treatment"""
    treatment = await db.get(Treatment, treatment_id)

    if not treatment:
        raise HTTPException(status_code=404, detail="Treatment not found")

    return {
        "id": str(treatment.id),
        "type": treatment.treatment_type,
        "target": treatment.target_pest or treatment.target_disease,
        "application_date": treatment.application_date.isoformat(),
        "application_method": treatment.application_method,
        "status": treatment.status,
        "efficacy": treatment.final_efficacy,
        "cost": treatment.total_cost,
    }


@router.patch("/treatment/{treatment_id}")
async def update_treatment_efficacy(
    treatment_id: UUID,
    efficacy_percent: float,
    db: AsyncSession = Depends(get_db),
):
    """Update treatment efficacy after evaluation"""
    treatment = await db.get(Treatment, treatment_id)

    if not treatment:
        raise HTTPException(status_code=404, detail="Treatment not found")

    treatment.final_efficacy = efficacy_percent
    treatment.status = "evaluated"

    await db.commit()

    return {
        "treatment_id": str(treatment.id),
        "efficacy": treatment.final_efficacy,
        "status": treatment.status,
    }
