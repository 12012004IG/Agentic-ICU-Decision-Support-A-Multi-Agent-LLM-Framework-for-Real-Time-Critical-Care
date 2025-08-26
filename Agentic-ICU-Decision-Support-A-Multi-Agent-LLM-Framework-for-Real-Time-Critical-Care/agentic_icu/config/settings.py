"""
Simple configuration settings for Agentic ICU Decision Support
"""

import os
from typing import Dict, Any

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

class Settings:
    """Simple application settings"""

    def __init__(self):
        # Basic settings
        self.debug = os.getenv("DEBUG", "true").lower() == "true"
        self.environment = os.getenv("ENVIRONMENT", "development")
        self.log_level = os.getenv("LOG_LEVEL", "INFO")

        # Mock/Demo mode settings
        self.mock_mode = os.getenv("MOCK_MODE", "true").lower() == "true"
        self.synthetic_patients = int(os.getenv("SYNTHETIC_PATIENTS", "10"))
        self.simulation_duration_hours = int(os.getenv("SIMULATION_DURATION_HOURS", "1"))

        # Processing settings
        self.processing_interval_seconds = int(os.getenv("PROCESSING_INTERVAL_SECONDS", "5"))
        self.batch_size = int(os.getenv("BATCH_SIZE", "100"))

        # API settings
        self.api_host = os.getenv("API_HOST", "0.0.0.0")
        self.api_port = int(os.getenv("API_PORT", "8000"))

        # Data settings
        self.data_path = os.getenv("DATA_PATH", "./data")

        # Feature flags
        self.enable_synthetic_data = os.getenv("ENABLE_SYNTHETIC_DATA", "true").lower() == "true"
        self.enable_real_time_processing = os.getenv("ENABLE_REAL_TIME_PROCESSING", "true").lower() == "true"
        self.enable_ai_agents = os.getenv("ENABLE_AI_AGENTS", "true").lower() == "true"
        self.enable_mock_devices = os.getenv("ENABLE_MOCK_DEVICES", "true").lower() == "true"

# Vital sign normal ranges for simulation
VITAL_RANGES = {
    "heart_rate": {"min": 60, "max": 100, "unit": "bpm"},
    "systolic_bp": {"min": 90, "max": 140, "unit": "mmHg"},
    "diastolic_bp": {"min": 60, "max": 90, "unit": "mmHg"},
    "respiratory_rate": {"min": 12, "max": 20, "unit": "/min"},
    "spo2": {"min": 95, "max": 100, "unit": "%"},
    "temperature": {"min": 36.1, "max": 37.2, "unit": "°C"},
}

# Common medications for ICU simulation
COMMON_ICU_MEDICATIONS = [
    {"name": "Norepinephrine", "type": "vasopressor", "dose_range": (0.1, 2.0), "unit": "mcg/kg/min"},
    {"name": "Propofol", "type": "sedative", "dose_range": (10, 50), "unit": "mcg/kg/min"},
    {"name": "Fentanyl", "type": "analgesic", "dose_range": (0.5, 5.0), "unit": "mcg/kg/hr"},
    {"name": "Midazolam", "type": "sedative", "dose_range": (0.02, 0.1), "unit": "mg/kg/hr"},
    {"name": "Furosemide", "type": "diuretic", "dose_range": (20, 80), "unit": "mg"},
]

# Lab test normal ranges
LAB_RANGES = {
    "glucose": {"min": 70, "max": 140, "unit": "mg/dL"},
    "sodium": {"min": 135, "max": 145, "unit": "mEq/L"},
    "potassium": {"min": 3.5, "max": 5.0, "unit": "mEq/L"},
    "creatinine": {"min": 0.6, "max": 1.3, "unit": "mg/dL"},
    "hemoglobin": {"min": 12.0, "max": 16.0, "unit": "g/dL"},
}

# Global settings instance
settings = Settings()
