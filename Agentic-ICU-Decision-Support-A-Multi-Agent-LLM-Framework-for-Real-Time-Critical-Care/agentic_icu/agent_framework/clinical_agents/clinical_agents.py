"""
Clinical agents for ICU decision support
"""

from typing import Dict, Any
from ..base_agent import BaseAgent, MockLLMInterface


class PhysicianAgent(BaseAgent):
    """Primary physician agent for clinical decisions"""

    def __init__(self, agent_id: str = "PHYSICIAN_001"):
        super().__init__(agent_id, "physician", "critical_care")

    async def _setup_subscriptions(self):
        """Subscribe to relevant data streams"""
        from ...orchestration.mock_message_bus import message_bus
        message_bus.subscribe("vitals", self._handle_vitals)
        message_bus.subscribe("alerts", self._handle_alerts)

    async def _handle_vitals(self, topic: str, message: Dict[str, Any]):
        """Handle incoming vital signs"""
        patient_id = message.get("patient_id")
        if patient_id in self.patients_assigned:
            parameter = message.get("parameter")
            value = message.get("value")

            # Check for critical values
            critical_thresholds = {
                "heart_rate": {"low": 50, "high": 120},
                "systolic_bp": {"low": 90, "high": 180},
                "spo2": {"low": 92, "high": 100}
            }

            if parameter in critical_thresholds:
                thresholds = critical_thresholds[parameter]
                if value < thresholds["low"] or value > thresholds["high"]:
                    await self._make_urgent_decision(patient_id, {
                        "trigger": "critical_vital",
                        "parameter": parameter,
                        "value": value
                    })

    async def _handle_alerts(self, topic: str, message: Dict[str, Any]):
        """Handle clinical alerts"""
        patient_id = message.get("patient_id")
        if patient_id in self.patients_assigned and message.get("severity") in ["high", "critical"]:
            await self._make_urgent_decision(patient_id, {
                "trigger": "clinical_alert",
                "alert_type": message.get("alert_type")
            })

    async def _make_urgent_decision(self, patient_id: str, context: Dict[str, Any]):
        """Make urgent clinical decision"""
        prompt = f"URGENT: Patient {patient_id} - {context.get('trigger')} - Provide immediate recommendations"
        llm_response = await MockLLMInterface.generate_response(prompt, context)

        decision = {
            "patient_id": patient_id,
            "recommendation_type": "urgent_clinical_decision",
            "trigger": context.get("trigger"),
            "recommendation": llm_response["recommendation"],
            "confidence_score": llm_response["confidence"],
            "reasoning": llm_response["reasoning"],
            "urgency": "high"
        }

        await self.make_decision(patient_id, decision)

    async def process_patient_data(self, patient_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process patient data and make clinical decisions"""
        prompt = f"Clinical Assessment for Patient {patient_id}: {data}"
        llm_response = await MockLLMInterface.generate_response(prompt, data)

        decision = {
            "patient_id": patient_id,
            "recommendation_type": "clinical_assessment",
            "assessment": llm_response["recommendation"],
            "confidence_score": llm_response["confidence"],
            "reasoning": llm_response["reasoning"],
            "urgency": "low"
        }

        self.confidence_scores.append(llm_response["confidence"])
        return decision


class NurseAgent(BaseAgent):
    """Nursing agent for patient monitoring and care coordination"""

    def __init__(self, agent_id: str = "NURSE_001"):
        super().__init__(agent_id, "nurse", "icu_nursing")

    async def _setup_subscriptions(self):
        """Subscribe to patient monitoring data"""
        from ...orchestration.mock_message_bus import message_bus
        message_bus.subscribe("vitals", self._handle_vitals_monitoring)

    async def _handle_vitals_monitoring(self, topic: str, message: Dict[str, Any]):
        """Monitor vital signs for nursing interventions"""
        patient_id = message.get("patient_id")
        if patient_id in self.patients_assigned:
            parameter = message.get("parameter")
            value = message.get("value")

            # Nursing intervention thresholds
            if parameter == "temperature" and value > 38.0:
                await self._recommend_nursing_intervention(patient_id, {
                    "intervention": "fever_management",
                    "details": "Administer antipyretic, cooling measures"
                })

    async def _recommend_nursing_intervention(self, patient_id: str, intervention: Dict[str, Any]):
        """Recommend nursing intervention"""
        decision = {
            "patient_id": patient_id,
            "recommendation_type": "nursing_intervention",
            "intervention": intervention["intervention"],
            "details": intervention["details"],
            "confidence_score": 0.90,
            "reasoning": "Standard nursing protocol"
        }
        await self.make_decision(patient_id, decision)

    async def process_patient_data(self, patient_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process nursing assessments and care plans"""
        prompt = f"Nursing Assessment for Patient {patient_id}: {data}"
        llm_response = await MockLLMInterface.generate_response(prompt, data)

        decision = {
            "patient_id": patient_id,
            "recommendation_type": "nursing_care_plan",
            "care_plan": llm_response["recommendation"],
            "confidence_score": llm_response["confidence"],
            "reasoning": llm_response["reasoning"]
        }

        self.confidence_scores.append(llm_response["confidence"])
        return decision


class PharmacistAgent(BaseAgent):
    """Pharmacist agent for medication management"""

    def __init__(self, agent_id: str = "PHARMACIST_001"):
        super().__init__(agent_id, "pharmacist", "clinical_pharmacy")
        self.drug_interactions = {
            "warfarin": ["aspirin", "heparin"],
            "digoxin": ["furosemide"]
        }

    async def _setup_subscriptions(self):
        """Subscribe to medication-related data"""
        from ...orchestration.mock_message_bus import message_bus
        message_bus.subscribe("medications", self._handle_medication_review)

    async def _handle_medication_review(self, topic: str, message: Dict[str, Any]):
        """Review medication orders"""
        patient_id = message.get("patient_id")
        if patient_id in self.patients_assigned:
            drug_name = message.get("drug_name", "").lower()

            # Check for drug interactions
            if drug_name in self.drug_interactions:
                await self._check_drug_interactions(patient_id, message)

    async def _check_drug_interactions(self, patient_id: str, medication: Dict[str, Any]):
        """Check for drug interactions"""
        decision = {
            "patient_id": patient_id,
            "recommendation_type": "drug_interaction_alert",
            "medication": medication.get("drug_name"),
            "alert": "Potential drug interaction detected",
            "confidence_score": 0.95,
            "reasoning": "Drug interaction database match"
        }
        await self.make_decision(patient_id, decision)

    async def process_patient_data(self, patient_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process pharmaceutical care decisions"""
        prompt = f"Pharmaceutical Care Review for Patient {patient_id}: {data}"
        llm_response = await MockLLMInterface.generate_response(prompt, data)

        decision = {
            "patient_id": patient_id,
            "recommendation_type": "pharmaceutical_care",
            "recommendations": llm_response["recommendation"],
            "confidence_score": llm_response["confidence"],
            "reasoning": llm_response["reasoning"]
        }

        self.confidence_scores.append(llm_response["confidence"])
        return decision
