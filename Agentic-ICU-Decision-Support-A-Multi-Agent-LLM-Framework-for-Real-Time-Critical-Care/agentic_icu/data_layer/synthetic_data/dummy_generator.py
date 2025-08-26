"""
Dummy data generator for ICU simulation (no external hardware needed)
"""

import random
import uuid
from datetime import datetime, timedelta
from typing import Dict, Any, List
import json
from pathlib import Path

try:
    from faker import Faker
except ImportError:
    print("Faker not installed. Using basic data generation.")
    class Faker:
        def first_name(self): return random.choice(["John", "Jane", "Alice", "Bob", "Carol"])
        def last_name(self): return random.choice(["Smith", "Johnson", "Williams", "Brown", "Jones"])

# Import settings from correct path
from ...config.settings import VITAL_RANGES, LAB_RANGES, COMMON_ICU_MEDICATIONS

# Simple logger without external dependencies
class SimpleLogger:
    def info(self, msg): print(f"INFO: {msg}")
    def warning(self, msg): print(f"WARNING: {msg}")
    def error(self, msg): print(f"ERROR: {msg}")

fake = Faker()
logger = SimpleLogger()


class DummyPatientGenerator:
    """Generate realistic dummy patient data"""

    def __init__(self):
        self.conditions = [
            "Sepsis", "Pneumonia", "ARDS", "Heart Failure", "Diabetic Ketoacidosis",
            "Post-operative monitoring", "Trauma", "Stroke", "Myocardial Infarction"
        ]

    def generate_patient(self) -> Dict[str, Any]:
        """Generate a complete dummy patient"""
        patient_id = f"PATIENT_{str(uuid.uuid4())[:8].upper()}"

        return {
            "patient_id": patient_id,
            "mrn": f"MRN{random.randint(100000, 999999)}",
            "first_name": fake.first_name(),
            "last_name": fake.last_name(),
            "age": random.randint(18, 90),
            "gender": random.choice(["male", "female"]),
            "weight_kg": round(random.uniform(50, 120), 1),
            "height_cm": random.randint(150, 200),
            "admission_time": (datetime.now() - timedelta(hours=random.randint(1, 72))).isoformat(),
            "diagnosis": random.choice(self.conditions),
            "severity": random.choice(["stable", "moderate", "critical"]),
            "allergies": random.choice([[], ["Penicillin"], ["Latex"], ["Contrast"]]),
            "medical_history": random.choice([
                ["Hypertension"], 
                ["Diabetes", "Hypertension"], 
                ["COPD"], 
                []
            ])
        }

    def generate_multiple_patients(self, count: int = 10) -> List[Dict[str, Any]]:
        """Generate multiple patients"""
        return [self.generate_patient() for _ in range(count)]


class DummyVitalSignsGenerator:
    """Generate realistic vital signs data"""

    def __init__(self):
        self.last_values = {}

    def generate_vitals(self, patient_id: str, condition: str = "stable") -> Dict[str, Any]:
        """Generate vital signs for a patient"""

        vitals = {}

        for param, range_info in VITAL_RANGES.items():
            min_val, max_val = range_info["min"], range_info["max"]

            # Add some variance based on condition
            if condition == "critical":
                if param == "heart_rate":
                    value = random.uniform(50, 150)
                elif param == "systolic_bp":
                    value = random.uniform(70, 180)
                elif param == "spo2":
                    value = random.uniform(88, 98)
                else:
                    value = random.uniform(min_val * 0.8, max_val * 1.2)
            else:
                # Add realistic drift from previous values
                if patient_id in self.last_values and param in self.last_values[patient_id]:
                    last_val = self.last_values[patient_id][param]
                    change = random.uniform(-0.1, 0.1) * (max_val - min_val)
                    value = last_val + change
                    value = max(min_val * 0.7, min(max_val * 1.3, value))
                else:
                    value = random.uniform(min_val, max_val)

            # Round appropriately
            if param == "temperature":
                value = round(value, 1)
            else:
                value = round(value, 0)

            vitals[param] = {
                "value": value,
                "unit": range_info["unit"],
                "timestamp": datetime.now().isoformat(),
                "quality_score": random.uniform(0.85, 1.0)
            }

        # Store for next iteration
        if patient_id not in self.last_values:
            self.last_values[patient_id] = {}

        for param, data in vitals.items():
            self.last_values[patient_id][param] = data["value"]

        return vitals


class DummyLabResultsGenerator:
    """Generate lab results"""

    def generate_lab_results(self, patient_id: str, test_count: int = 3) -> List[Dict[str, Any]]:
        """Generate lab results for a patient"""

        selected_tests = random.sample(list(LAB_RANGES.keys()), min(test_count, len(LAB_RANGES)))
        results = []

        for test_name in selected_tests:
            range_info = LAB_RANGES[test_name]

            # 80% chance of normal, 20% chance of abnormal
            if random.random() < 0.8:
                value = random.uniform(range_info["min"], range_info["max"])
                abnormal_flag = ""
            else:
                # Generate abnormal value
                if random.random() < 0.5:
                    value = random.uniform(range_info["min"] * 0.5, range_info["min"] * 0.9)
                    abnormal_flag = "L"
                else:
                    value = random.uniform(range_info["max"] * 1.1, range_info["max"] * 1.5)
                    abnormal_flag = "H"

            # Round appropriately
            if test_name in ["glucose", "creatinine"]:
                value = round(value, 1)
            else:
                value = round(value, 0)

            results.append({
                "patient_id": patient_id,
                "test_name": test_name,
                "value": value,
                "unit": range_info["unit"],
                "reference_range": f"{range_info['min']}-{range_info['max']}",
                "abnormal_flag": abnormal_flag,
                "timestamp": datetime.now().isoformat()
            })

        return results


class DummyMedicationGenerator:
    """Generate medication administration data"""

    def generate_medications(self, patient_id: str, med_count: int = 2) -> List[Dict[str, Any]]:
        """Generate medications for a patient"""

        selected_meds = random.sample(COMMON_ICU_MEDICATIONS, min(med_count, len(COMMON_ICU_MEDICATIONS)))
        medications = []

        for med_info in selected_meds:
            dose = round(random.uniform(*med_info["dose_range"]), 2)

            medications.append({
                "patient_id": patient_id,
                "medication_id": f"MED_{uuid.uuid4().hex[:8].upper()}",
                "drug_name": med_info["name"],
                "dose": dose,
                "dose_unit": med_info["unit"],
                "route": random.choice(["IV", "PO"]),
                "frequency": random.choice(["continuous", "q4h", "q6h"]),
                "start_time": (datetime.now() - timedelta(hours=random.randint(1, 24))).isoformat(),
                "prescriber_id": f"DR_{random.randint(1000, 9999)}"
            })

        return medications


# Global instances
patient_generator = DummyPatientGenerator()
vitals_generator = DummyVitalSignsGenerator()
lab_generator = DummyLabResultsGenerator()
medication_generator = DummyMedicationGenerator()


def save_dummy_data_to_files(data_dir: str = "./data"):
    """Save generated dummy data to files"""

    Path(data_dir).mkdir(exist_ok=True)
    Path(f"{data_dir}/patients").mkdir(exist_ok=True)

    # Generate and save patients
    patients = patient_generator.generate_multiple_patients(10)

    with open(f"{data_dir}/patients/patients.json", 'w') as f:
        json.dump(patients, f, indent=2, default=str)

    logger.info(f"Generated dummy data for {len(patients)} patients in {data_dir}")
    return patients


if __name__ == "__main__":
    save_dummy_data_to_files()
