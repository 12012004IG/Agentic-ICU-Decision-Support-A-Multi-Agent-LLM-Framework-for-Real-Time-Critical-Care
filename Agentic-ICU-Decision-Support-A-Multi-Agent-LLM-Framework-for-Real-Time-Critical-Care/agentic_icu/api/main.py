"""
FastAPI server for the ICU system
"""

from fastapi import FastAPI, HTTPException
from typing import Dict, Any
import asyncio
from datetime import datetime

from ..orchestration.workflow_coordinator import coordinator
from ..config.settings import settings

app = FastAPI(
    title="Agentic ICU Decision Support API",
    description="Real-time ICU decision support with multi-agent AI system",
    version="1.0.0"
)

@app.on_event("startup")
async def startup_event():
    """Initialize system on startup"""
    if not coordinator.is_running:
        await coordinator.initialize()

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Agentic ICU Decision Support API",
        "version": "1.0.0",
        "status": "active",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    status = coordinator.get_system_status()
    return {
        "status": "healthy" if status["is_running"] else "stopped",
        "system": status,
        "timestamp": datetime.now().isoformat()
    }

@app.get("/patients")
async def get_patients():
    """Get all patients"""
    return {
        "patients": list(coordinator.patients.values()),
        "count": len(coordinator.patients)
    }

@app.get("/patients/{patient_id}")
async def get_patient(patient_id: str):
    """Get specific patient data"""
    if patient_id not in coordinator.patients:
        raise HTTPException(status_code=404, detail="Patient not found")

    return {
        "patient": coordinator.patients[patient_id],
        "timestamp": datetime.now().isoformat()
    }

@app.get("/agents")
async def get_agents():
    """Get all agents status"""
    agent_statuses = {}
    for agent_id, agent in coordinator.agents.items():
        agent_statuses[agent_id] = agent.get_status()

    return {
        "agents": agent_statuses,
        "count": len(coordinator.agents)
    }

@app.post("/simulation/start")
async def start_simulation(duration_minutes: int = 10):
    """Start ICU simulation"""
    if coordinator.is_running:
        return {"message": "Simulation already running"}

    # Start simulation in background
    asyncio.create_task(coordinator.start_simulation(duration_minutes))

    return {
        "message": f"Simulation started for {duration_minutes} minutes",
        "timestamp": datetime.now().isoformat()
    }

@app.post("/simulation/stop")
async def stop_simulation():
    """Stop ICU simulation"""
    if not coordinator.is_running:
        return {"message": "Simulation not running"}

    await coordinator.stop_simulation()

    return {
        "message": "Simulation stopped",
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=settings.api_host, port=settings.api_port)
