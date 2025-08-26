"""
Mock message bus for simulation (no external dependencies)
"""

import asyncio
from datetime import datetime
from typing import Dict, Any, List, Callable, Optional
from collections import defaultdict, deque


class MockMessageBus:
    """In-memory message bus that simulates Redis/Kafka functionality"""

    def __init__(self):
        self.topics: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        self.subscribers: Dict[str, List[Callable]] = defaultdict(list)
        self.state: Dict[str, Any] = {}

    async def publish(self, topic: str, message: Dict[str, Any]) -> bool:
        """Publish message to topic"""
        try:
            # Add metadata
            enriched_message = {
                **message,
                "_topic": topic,
                "_timestamp": datetime.now().isoformat(),
                "_id": f"{topic}_{len(self.topics[topic])}"
            }

            # Store message
            self.topics[topic].append(enriched_message)

            # Notify subscribers
            for callback in self.subscribers[topic]:
                try:
                    if asyncio.iscoroutinefunction(callback):
                        await callback(topic, enriched_message)
                    else:
                        callback(topic, enriched_message)
                except Exception as e:
                    print(f"Error in subscriber callback: {e}")

            return True

        except Exception as e:
            print(f"Failed to publish to {topic}: {e}")
            return False

    def subscribe(self, topic: str, callback: Callable):
        """Subscribe to topic messages"""
        self.subscribers[topic].append(callback)

    async def get_messages(self, topic: str, count: int = 10) -> List[Dict[str, Any]]:
        """Get recent messages from topic"""
        messages = list(self.topics[topic])
        return messages[-count:] if messages else []

    async def set_state(self, key: str, value: Any):
        """Set shared state"""
        self.state[key] = {
            "value": value,
            "timestamp": datetime.now().isoformat()
        }

    async def get_state(self, key: str) -> Any:
        """Get shared state"""
        state_data = self.state.get(key)
        return state_data["value"] if state_data else None

    def get_topic_stats(self) -> Dict[str, int]:
        """Get statistics for all topics"""
        return {topic: len(messages) for topic, messages in self.topics.items()}


# Global message bus instance
message_bus = MockMessageBus()


class MockDevice:
    """Simulate an ICU device"""

    def __init__(self, device_id: str, device_type: str, patient_id: str):
        self.device_id = device_id
        self.device_type = device_type
        self.patient_id = patient_id
        self.is_running = False

    async def start_simulation(self, duration_seconds: int = 300):
        """Start device data simulation"""
        if self.is_running:
            return

        self.is_running = True
        print(f"Starting {self.device_type} simulation for {self.patient_id}")

        # Import here to avoid circular imports
        from ..data_layer.synthetic_data.dummy_generator import vitals_generator

        try:
            end_time = datetime.now().timestamp() + duration_seconds

            while self.is_running and datetime.now().timestamp() < end_time:
                # Generate device data
                if self.device_type == "monitor":
                    vitals = vitals_generator.generate_vitals(self.patient_id)

                    for param, data in vitals.items():
                        await message_bus.publish("vitals", {
                            "patient_id": self.patient_id,
                            "device_id": self.device_id,
                            "parameter": param,
                            "value": data["value"],
                            "unit": data["unit"],
                            "quality_score": data["quality_score"]
                        })

                # Wait before next reading
                await asyncio.sleep(5)  # 5 second intervals

        except Exception as e:
            print(f"Error in device simulation: {e}")
        finally:
            self.is_running = False
            print(f"Stopped {self.device_type} simulation for {self.patient_id}")

    def stop_simulation(self):
        """Stop device simulation"""
        self.is_running = False


class MockICUUnit:
    """Simulate an entire ICU unit with multiple devices"""

    def __init__(self, unit_id: str = "ICU_1"):
        self.unit_id = unit_id
        self.devices: List[MockDevice] = []
        self.patients: List[str] = []

    def add_patient(self, patient_id: str):
        """Add patient and create associated devices"""
        if patient_id in self.patients:
            return

        self.patients.append(patient_id)

        # Create devices for this patient
        device = MockDevice(f"{patient_id}_MONITOR", "monitor", patient_id)
        self.devices.append(device)

    async def start_unit_simulation(self, duration_seconds: int = 300):
        """Start simulation for all devices in the unit"""
        tasks = []

        for device in self.devices:
            task = asyncio.create_task(device.start_simulation(duration_seconds))
            tasks.append(task)

        print(f"Started simulation for {len(self.devices)} devices")

        try:
            await asyncio.gather(*tasks, return_exceptions=True)
        except Exception as e:
            print(f"Unit simulation error: {e}")

    def stop_unit_simulation(self):
        """Stop all device simulations"""
        for device in self.devices:
            device.stop_simulation()

        print(f"Stopped simulation for {len(self.devices)} devices")

    def get_unit_status(self) -> Dict[str, Any]:
        """Get status of the ICU unit"""
        return {
            "unit_id": self.unit_id,
            "patient_count": len(self.patients),
            "device_count": len(self.devices),
            "active_devices": sum(1 for device in self.devices if device.is_running),
            "patients": self.patients
        }


# Global ICU unit instance
icu_unit = MockICUUnit()


# Convenience functions
async def publish_message(topic: str, message: Dict[str, Any]) -> bool:
    """Convenience function to publish message"""
    return await message_bus.publish(topic, message)
