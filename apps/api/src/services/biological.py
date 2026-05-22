import logging
from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import datetime

from src.models.treatment import BiologicalAgent, ChemicalProduct, Treatment
from src.models.crop import Crop, CropVariety
from src.database import AsyncSessionLocal
from sqlalchemy import select

logger = logging.getLogger(__name__)


class TreatmentRecommendation:
    """Treatment recommendation for a detected pest/disease"""

    def __init__(
        self,
        target_organism: str,
        treatment_type: str,
        product_name: str,
        confidence: float,
        efficacy_estimate: float,
        application_rate: str,
        safety_rating: str,
        environmental_impact: str,
        cost: float,
        notes: str = "",
    ):
        self.target_organism = target_organism
        self.treatment_type = treatment_type
        self.product_name = product_name
        self.confidence = confidence
        self.efficacy_estimate = efficacy_estimate
        self.application_rate = application_rate
        self.safety_rating = safety_rating
        self.environmental_impact = environmental_impact
        self.cost = cost
        self.notes = notes

    def to_dict(self) -> Dict[str, Any]:
        return {
            "target_organism": self.target_organism,
            "treatment_type": self.treatment_type,
            "product_name": self.product_name,
            "confidence": self.confidence,
            "efficacy_estimate": self.efficacy_estimate,
            "application_rate": self.application_rate,
            "safety_rating": self.safety_rating,
            "environmental_impact": self.environmental_impact,
            "cost": self.cost,
            "notes": self.notes,
        }


class BiologicalIntelligence:
    """
    Recommends non-chemical interventions based on:
    - Crop genetics
    - Target organism biology
    - Environmental conditions
    - Resistance patterns
    - Efficacy data
    """

    def __init__(self):
        # Knowledge base of treatments
        self.biological_treatments = {
            "aphids": [
                {
                    "agent": "Aphidius colemani",
                    "type": "predator",
                    "efficacy": 0.75,
                    "cost": 45.0,
                }
            ],
            "spider_mites": [
                {
                    "agent": "Phytoseiulus persimilis",
                    "type": "predator",
                    "efficacy": 0.85,
                    "cost": 55.0,
                }
            ],
            "powdery_mildew": [
                {
                    "agent": "Bacillus subtilis",
                    "type": "bacterium",
                    "efficacy": 0.70,
                    "cost": 30.0,
                }
            ],
            "early_blight": [
                {
                    "agent": "Bacillus subtilis QST 713",
                    "type": "bacterium",
                    "efficacy": 0.72,
                    "cost": 32.0,
                }
            ],
            "late_blight": [
                {
                    "agent": "Trichoderma harzianum",
                    "type": "fungus",
                    "efficacy": 0.65,
                    "cost": 28.0,
                }
            ],
        }

    async def get_treatment_recommendations(
        self,
        field_id: UUID,
        crop_id: UUID,
        detected_pest: str,
        severity: str = "moderate",
        environmental_data: Optional[Dict[str, Any]] = None,
    ) -> List[TreatmentRecommendation]:
        """
        Get treatment recommendations for detected pest/disease.

        Args:
            field_id: Target field
            crop_id: Crop being grown
            detected_pest: Name of detected pest/disease
            severity: mild, moderate, severe
            environmental_data: Temperature, humidity, rainfall, etc

        Returns:
            List of TreatmentRecommendation sorted by score
        """
        recommendations = []

        try:
            async with AsyncSessionLocal() as session:
                # Get crop info
                crop = await session.get(Crop, crop_id)
                if not crop:
                    logger.warning(f"Crop {crop_id} not found")
                    return []

                # Get biological agents
                biological_options = self.biological_treatments.get(
                    detected_pest.lower(), []
                )

                for option in biological_options:
                    recommendation = TreatmentRecommendation(
                        target_organism=detected_pest,
                        treatment_type="biological",
                        product_name=option["agent"],
                        confidence=0.82,
                        efficacy_estimate=option["efficacy"],
                        application_rate=self._get_application_rate(
                            option["agent"],
                            severity,
                        ),
                        safety_rating="safe",
                        environmental_impact="minimal",
                        cost=option["cost"],
                        notes=f"Recommended for {severity} infestations of {detected_pest}",
                    )
                    recommendations.append(recommendation)

                # Get chemical alternatives
                chemicals = await self._get_chemical_alternatives(
                    session, detected_pest
                )

                for chemical in chemicals:
                    rec = TreatmentRecommendation(
                        target_organism=detected_pest,
                        treatment_type="chemical",
                        product_name=chemical.get("product_name", "Unknown"),
                        confidence=0.88,
                        efficacy_estimate=chemical.get("efficacy", 0.85),
                        application_rate=chemical.get("application_rate", "TBD"),
                        safety_rating=self._rate_chemical_safety(
                            chemical.get("toxicity_class", "IV")
                        ),
                        environmental_impact=self._rate_environmental_impact(
                            chemical
                        ),
                        cost=chemical.get("cost", 50.0),
                        notes=f"Chemical alternative for rapid control of {detected_pest}",
                    )
                    recommendations.append(rec)

                # Sort by overall score
                recommendations.sort(
                    key=lambda r: self._calculate_recommendation_score(r),
                    reverse=True,
                )

                logger.info(
                    f"Generated {len(recommendations)} recommendations for {detected_pest}"
                )

                return recommendations

        except Exception as e:
            logger.error(f"Error generating recommendations: {e}")
            return []

    async def _get_chemical_alternatives(
        self, session, pest_name: str
    ) -> List[Dict[str, Any]]:
        """Get registered chemical products for pest control"""
        # In production: query against chemical database
        return [
            {
                "product_name": "Neem Oil 70%",
                "toxicity_class": "IV",
                "efficacy": 0.75,
                "cost": 35.0,
                "application_rate": "1-2% solution",
                "half_life_days": 3,
            },
            {
                "product_name": "Insecticidal Soap",
                "toxicity_class": "IV",
                "efficacy": 0.72,
                "cost": 25.0,
                "application_rate": "1-2% solution",
                "half_life_days": 1,
            },
        ]

    def _get_application_rate(self, agent_name: str, severity: str) -> str:
        """Get application rate based on agent and severity"""
        base_rates = {
            "Aphidius colemani": "5 adults/m² for light, 15 adults/m² for heavy",
            "Phytoseiulus persimilis": "10 mites/m² for light, 30 mites/m² for heavy",
            "Bacillus subtilis": "1-5 x10⁸ CFU/ml",
            "Trichoderma harzianum": "1-5 x10⁸ CFU/ml",
        }
        return base_rates.get(agent_name, "As per label instructions")

    def _rate_chemical_safety(self, toxicity_class: str) -> str:
        """Rate chemical safety"""
        ratings = {
            "I": "highly_toxic",
            "II": "moderately_toxic",
            "III": "low_toxicity",
            "IV": "minimal_toxicity",
        }
        return ratings.get(toxicity_class, "unknown")

    def _rate_environmental_impact(self, chemical: Dict[str, Any]) -> str:
        """Rate environmental impact"""
        half_life = chemical.get("half_life_days", 30)
        if half_life < 2:
            return "minimal"
        elif half_life < 7:
            return "low"
        elif half_life < 30:
            return "moderate"
        else:
            return "high"

    def _calculate_recommendation_score(self, recommendation: TreatmentRecommendation) -> float:
        """Calculate overall recommendation score"""
        score = 0.0

        # Efficacy (0-40 points)
        score += recommendation.efficacy_estimate * 40

        # Safety (0-30 points)
        safety_scores = {
            "highly_toxic": 5,
            "moderately_toxic": 15,
            "low_toxicity": 25,
            "minimal_toxicity": 30,
        }
        score += safety_scores.get(recommendation.safety_rating, 0)

        # Environmental impact (0-20 points)
        impact_scores = {
            "minimal": 20,
            "low": 15,
            "moderate": 8,
            "high": 2,
        }
        score += impact_scores.get(recommendation.environmental_impact, 0)

        # Cost efficiency (0-10 points, lower is better)
        score += max(0, 10 - (recommendation.cost / 10))

        return score

    async def get_treatment_history(
        self, field_id: UUID, days: int = 365
    ) -> List[Dict[str, Any]]:
        """Get treatment history for a field"""
        try:
            async with AsyncSessionLocal() as session:
                from datetime import timedelta

                cutoff_date = datetime.utcnow() - timedelta(days=days)

                stmt = select(Treatment).where(
                    (Treatment.field_id == field_id)
                    & (Treatment.application_date >= cutoff_date)
                )
                treatments = (await session.execute(stmt)).scalars().all()

                history = []
                for treatment in treatments:
                    history.append(
                        {
                            "date": treatment.application_date,
                            "type": treatment.treatment_type,
                            "target": treatment.target_pest
                            or treatment.target_disease,
                            "product": treatment.product_id,
                            "efficacy": treatment.final_efficacy,
                            "cost": treatment.total_cost,
                        }
                    )

                return history

        except Exception as e:
            logger.error(f"Error getting treatment history: {e}")
            return []

    async def predict_resistance(
        self, pest_name: str, field_treatment_history: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Predict resistance development based on treatment history.
        Uses simple model - production would use ML.
        """
        # Count treatments over time
        chemical_count = sum(
            1 for t in field_treatment_history if t.get("type") == "chemical"
        )

        # Simple resistance model
        if chemical_count == 0:
            resistance_risk = "low"
            resistance_probability = 0.05
        elif chemical_count < 3:
            resistance_risk = "moderate"
            resistance_probability = 0.25
        else:
            resistance_risk = "high"
            resistance_probability = 0.60

        return {
            "pest": pest_name,
            "resistance_risk": resistance_risk,
            "resistance_probability": resistance_probability,
            "recommendations": self._get_resistance_management_recommendations(
                resistance_risk
            ),
        }

    def _get_resistance_management_recommendations(
        self, risk_level: str
    ) -> List[str]:
        """Get resistance management recommendations"""
        if risk_level == "high":
            return [
                "Rotate chemical classes",
                "Use biological controls",
                "Implement cultural practices",
                "Monitor for resistance",
                "Use combination therapies",
            ]
        elif risk_level == "moderate":
            return [
                "Monitor for resistance",
                "Consider biological alternatives",
                "Rotate products",
            ]
        else:
            return ["Continue monitoring", "No immediate action needed"]

    def get_service_status(self) -> Dict[str, Any]:
        """Get service status"""
        return {
            "service": "BiologicalIntelligence",
            "agents_available": len(self.biological_treatments),
            "status": "operational",
        }
