"""
Workflow Coordinator - Main orchestration system for all agents
"""

import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any, List
import json
from pathlib import Path

from ..agent_framework.clinical_agents.clinical_agents import PhysicianAgent, NurseAgent, PharmacistAgent
from ..data_layer.synthetic_data.dummy_generator import save_dummy_data_to_files
from ..orchestration.mock_message_bus import message_bus, icu_unit, publish_message
from ..config.settings import settings


class WorkflowCoordinator:
    """Main coordinator for the ICU agent system"""

    def __init__(self):
        self.agents: Dict[str, Any] = {}
        self.patients: Dict[str, Dict[str, Any]] = {}
        self.is_running = False
        self.tasks: List[asyncio.Task] = []

        # Performance tracking
        self.start_time: datetime = None
        self.total_decisions = 0
        self.total_messages = 0

    async def initialize(self):
        """Initialize the entire system"""
        print("🏥 Initializing Agentic ICU Decision Support System...")

        # Generate dummy data
        await self._setup_dummy_data()

        # Initialize agents
        await self._initialize_agents()

        # Setup monitoring
        await self._setup_monitoring()

        self.start_time = datetime.now()
        print("✅ System initialization completed")

    async def _setup_dummy_data(self):
        """Generate and load dummy patient data"""
        print("📊 Generating dummy patient data...")

        # Generate patients and save to files
        patients = save_dummy_data_to_files(settings.data_path)

        # Load patients into system
        for patient in patients:
            patient_id = patient["patient_id"]
            self.patients[patient_id] = patient

            # Add to ICU unit simulation
            icu_unit.add_patient(patient_id)

            # Set initial patient state
            await message_bus.set_state(f"patient_{patient_id}", {
                "status": "admitted",
                "severity": patient["severity"],
                "last_update": datetime.now().isoformat()
            })

        print(f"✅ Loaded {len(patients)} patients into system")

    async def _initialize_agents(self):
        """Initialize all agents"""
        print("🤖 Initializing agents...")

        # Create clinical agents
        agents_to_create = [
            ("PHYSICIAN_001", PhysicianAgent),
            ("NURSE_001", NurseAgent), 
            ("PHARMACIST_001", PharmacistAgent)
        ]

        for agent_id, agent_class in agents_to_create:
            agent = agent_class(agent_id)
            await agent.initialize()
            self.agents[agent_id] = agent

        # Assign patients to agents
        await self._assign_patients_to_agents()

        # Subscribe to decision tracking
        message_bus.subscribe("agent_decisions", self._track_decisions)

        print(f"✅ Initialized {len(self.agents)} agents")

    async def _assign_patients_to_agents(self):
        """Assign patients to appropriate agents"""
        patient_list = list(self.patients.keys())

        # Assign all patients to all agents for demo
        for agent in self.agents.values():
            for patient_id in patient_list:
                agent.assign_patient(patient_id)

        print(f"✅ Assigned {len(patient_list)} patients to agents")

    async def _setup_monitoring(self):
        """Setup system monitoring"""
        topics = ["vitals", "labs", "medications", "alerts", "agent_decisions"]
        for topic in topics:
            message_bus.subscribe(topic, self._monitor_messages)

    async def _monitor_messages(self, topic: str, message: Dict[str, Any]):
        """Monitor all system messages"""
        self.total_messages += 1

        # Log important messages
        if topic == "alerts" and message.get("severity") in ["high", "critical"]:
            print(f"🚨 Critical alert: {message}")

    async def _track_decisions(self, topic: str, decision: Dict[str, Any]):
        """Track agent decisions"""
        self.total_decisions += 1

        # Log important decisions
        if decision.get("urgency") == "high":
            print(f"⚠️  High urgency decision: {decision.get('recommendation_type')} for {decision.get('patient_id')}")

    async def start_simulation(self, duration_minutes: int = 10):
        """Start the complete ICU simulation"""
        if self.is_running:
            print("⚠️  Simulation already running")
            return

        self.is_running = True
        print(f"🚀 Starting ICU simulation for {duration_minutes} minutes...")

        # Start device simulations
        device_task = asyncio.create_task(
            icu_unit.start_unit_simulation(duration_minutes * 60)
        )
        self.tasks.append(device_task)

        # Start periodic tasks
        monitoring_task = asyncio.create_task(self._periodic_monitoring())
        self.tasks.append(monitoring_task)

        try:
            # Wait for simulation duration
            await asyncio.sleep(duration_minutes * 60)

        except KeyboardInterrupt:
            print("⏹️  Simulation interrupted by user")

        finally:
            await self.stop_simulation()

    async def _periodic_monitoring(self):
        """Periodic system monitoring and reporting"""
        while self.is_running:
            try:
                await self._generate_status_report() 
                await asyncio.sleep(30)  # Every 30 seconds
            except Exception as e:
                print(f"❌ Error in periodic monitoring: {e}")
                await asyncio.sleep(10)

    async def _generate_status_report(self):
        """Generate and log system status report"""
        uptime = datetime.now() - self.start_time if self.start_time else timedelta(0)

        print(f"📊 System Status: {self.total_decisions} decisions, {self.total_messages} messages, {len(self.patients)} patients")

        # Save status report
        status_report = {
            "timestamp": datetime.now().isoformat(),
            "uptime_minutes": int(uptime.total_seconds() / 60),
            "total_decisions": self.total_decisions,
            "total_messages": self.total_messages,
            "active_patients": len(self.patients),
            "active_agents": len([a for a in self.agents.values() if a.is_active])
        }

        Path(settings.data_path).mkdir(exist_ok=True)
        with open(f"{settings.data_path}/status_report.json", 'w') as f:
            json.dump(status_report, f, indent=2, default=str)

    async def stop_simulation(self):
        """Stop the simulation and cleanup"""
        print("⏹️  Stopping ICU simulation...")
        self.is_running = False

        # Stop ICU unit simulation
        icu_unit.stop_unit_simulation()

        # Cancel all tasks
        for task in self.tasks:
            if not task.done():
                task.cancel()

        # Wait for tasks to complete
        if self.tasks:
            await asyncio.gather(*self.tasks, return_exceptions=True)

        # Shutdown agents
        for agent in self.agents.values():
            await agent.shutdown()

        # Generate final report
        await self._generate_final_report()

        print("✅ ICU simulation stopped")

    async def _generate_final_report(self):
        """Generate final simulation report"""
        duration_minutes = int((datetime.now() - self.start_time).total_seconds() / 60) if self.start_time else 0

        final_report = {
            "simulation_completed": datetime.now().isoformat(),
            "duration_minutes": duration_minutes,
            "total_decisions_made": self.total_decisions,
            "total_messages_processed": self.total_messages,
            "patients_monitored": len(self.patients),
            "agents_deployed": len(self.agents),
            "decisions_per_minute": self.total_decisions / max(1, duration_minutes)
        }

        # Save final report
        Path(settings.data_path).mkdir(exist_ok=True)
        with open(f"{settings.data_path}/final_report.json", 'w') as f:
            json.dump(final_report, f, indent=2, default=str)

        print("\n" + "="*60)
        print("🎉 ICU SIMULATION COMPLETED!")
        print("="*60)
        print(f"Duration: {final_report['duration_minutes']} minutes")
        print(f"Decisions Made: {final_report['total_decisions_made']}")
        print(f"Messages Processed: {final_report['total_messages_processed']}")
        print(f"Patients Monitored: {final_report['patients_monitored']}")
        print(f"Performance: {final_report['decisions_per_minute']:.1f} decisions/min")
        print("="*60)
        print("📄 Reports saved:")
        print(f"  • {settings.data_path}/final_report.json")
        print(f"  • {settings.data_path}/status_report.json")
        print(f"  • {settings.data_path}/patients/")

    def get_system_status(self) -> Dict[str, Any]:
        """Get current system status"""
        return {
            "is_running": self.is_running,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "active_patients": len(self.patients),
            "active_agents": len([a for a in self.agents.values() if a.is_active]),
            "total_decisions": self.total_decisions,
            "total_messages": self.total_messages
        }


# Global coordinator instance
coordinator = WorkflowCoordinator()


async def run_demo_simulation(duration_minutes: int = 5):
    """Run a complete demo simulation"""
    print("🏥 Starting Agentic ICU Decision Support Demo...")
    print("="*60)

    try:
        # Initialize system
        await coordinator.initialize()

        # Run simulation
        await coordinator.start_simulation(duration_minutes)

    except KeyboardInterrupt:
        print("\n⏹️  Demo interrupted by user")

    except Exception as e:
        print(f"❌ Demo error: {e}")

    finally:
        if coordinator.is_running:
            await coordinator.stop_simulation()


if __name__ == "__main__":
    # Run the demo
    asyncio.run(run_demo_simulation(5))
