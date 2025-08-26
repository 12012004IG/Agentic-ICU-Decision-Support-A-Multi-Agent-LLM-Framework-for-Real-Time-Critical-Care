"""
Base agent class for all ICU agents
"""

import asyncio
import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional
from abc import ABC, abstractmethod


class MockLLMInterface:
    """Mock LLM interface for demonstration"""

    @staticmethod
    async def generate_response(prompt: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Generate mock LLM response"""
        await asyncio.sleep(0.1)  # Simulate processing time

        # Generate contextual responses based on prompt keywords
        if "vital signs" in prompt.lower():
            return {
                "recommendation": "Monitor patient closely. Consider fluid resuscitation if hypotensive.",
                "confidence": 0.85,
                "reasoning": "Based on current vital signs pattern, patient shows signs of hemodynamic instability."
            }
        elif "medication" in prompt.lower():
            return {
                "recommendation": "Continue current medication regimen. Monitor for drug interactions.",
                "confidence": 0.78,
                "reasoning": "Current medications are appropriate for diagnosis. No immediate changes needed."
            }
        elif "lab results" in prompt.lower():
            return {
                "recommendation": "Repeat labs in 6 hours. Consider electrolyte replacement if indicated.",
                "confidence": 0.82,
                "reasoning": "Lab values show mild abnormalities that require monitoring."
            }
        else:
            return {
                "recommendation": "Continue current care plan with regular monitoring.",
                "confidence": 0.75,
                "reasoning": "Patient condition appears stable based on available data."
            }


class BaseAgent(ABC):
    """Base class for all ICU agents"""

    def __init__(self, agent_id: str, agent_type: str, specialization: str = None):
        self.agent_id = agent_id
        self.agent_type = agent_type
        self.specialization = specialization

        # Agent state
        self.is_active = False
        self.patients_assigned: List[str] = []
        self.last_decision_time: Optional[datetime] = None
        self.decision_count = 0

        # Performance metrics
        self.response_times: List[float] = []
        self.confidence_scores: List[float] = []

    async def initialize(self):
        """Initialize the agent"""
        self.is_active = True
        print(f"{self.agent_type} agent {self.agent_id} initialized")

        # Subscribe to relevant topics
        await self._setup_subscriptions()

    @abstractmethod
    async def _setup_subscriptions(self):
        """Setup message subscriptions (implemented by subclasses)"""
        pass

    @abstractmethod
    async def process_patient_data(self, patient_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process patient data and make decisions (implemented by subclasses)"""
        pass

    async def make_decision(self, patient_id: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Make a clinical decision"""
        start_time = datetime.now()

        try:
            # Process the data
            decision = await self.process_patient_data(patient_id, context)

            # Add metadata
            decision.update({
                "agent_id": self.agent_id,
                "agent_type": self.agent_type,
                "timestamp": datetime.now().isoformat(),
                "decision_id": str(uuid.uuid4())
            })

            # Track metrics
            response_time = (datetime.now() - start_time).total_seconds()
            self.response_times.append(response_time)
            self.decision_count += 1
            self.last_decision_time = datetime.now()

            # Publish decision
            from ..orchestration.mock_message_bus import publish_message
            await publish_message("agent_decisions", decision)

            print(f"Decision made by {self.agent_type} for {patient_id}: {decision.get('recommendation_type', 'unknown')}")

            return decision

        except Exception as e:
            print(f"Error making decision for {patient_id}: {e}")
            return {
                "error": str(e),
                "agent_id": self.agent_id,
                "patient_id": patient_id,
                "timestamp": datetime.now().isoformat()
            }

    def assign_patient(self, patient_id: str):
        """Assign a patient to this agent"""
        if patient_id not in self.patients_assigned:
            self.patients_assigned.append(patient_id)
            print(f"Assigned patient {patient_id} to {self.agent_type}")

    def get_status(self) -> Dict[str, Any]:
        """Get agent status"""
        avg_response_time = sum(self.response_times) / len(self.response_times) if self.response_times else 0
        avg_confidence = sum(self.confidence_scores) / len(self.confidence_scores) if self.confidence_scores else 0

        return {
            "agent_id": self.agent_id,
            "agent_type": self.agent_type,
            "specialization": self.specialization,
            "is_active": self.is_active,
            "assigned_patients": len(self.patients_assigned),
            "decision_count": self.decision_count,
            "avg_response_time": avg_response_time,
            "avg_confidence": avg_confidence,
            "last_decision": self.last_decision_time.isoformat() if self.last_decision_time else None
        }

    async def shutdown(self):
        """Shutdown the agent"""
        self.is_active = False
        print(f"{self.agent_type} agent {self.agent_id} shutdown")
