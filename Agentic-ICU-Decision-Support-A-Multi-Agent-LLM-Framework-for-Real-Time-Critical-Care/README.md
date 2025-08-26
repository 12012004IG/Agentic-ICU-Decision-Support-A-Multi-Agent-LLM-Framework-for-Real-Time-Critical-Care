# Agentic ICU Decision Support - Quick Start

**Multi-Agent AI System for ICU Decision Support**

## What This Is

A complete simulation of an ICU with AI agents making clinical decisions:
- **Virtual patients** with realistic medical conditions
- **AI agents** (Physician, Nurse, Pharmacist) working together
- **Real-time monitoring** and clinical alerts
- **No external dependencies** - runs completely offline

## ⚡ Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run Demo
```bash
python run.py demo
```

### 3. View Results
After running, check:
- `./data/patients/` - Generated patient data
- `./data/final_report.json` - Simulation summary

## Commands

```bash
# Run 5-minute demo (default)
python run.py demo

# Run longer demo
python run.py demo --duration 10

# Start web API
python run.py api

# Run tests
python run.py test

# Alternative simple demo
python examples/demo.py
```

## What You'll See

```
1. Starting Agentic ICU Decision Support Demo...
2. Generated data for 10 patients
3. Initialized 3 agents
4. Starting ICU simulation for 5 minutes...

System Status: 23 decisions, 156 messages, 10 patients
High urgency decision: critical_vital for PATIENT_003
Decision made by physician for PATIENT_007: clinical_assessment

ICU SIMULATION COMPLETED!
Duration: 5 minutes
Decisions Made: 23
Messages Processed: 156
Performance: 4.6 decisions/min
```

## Architecture

```
📁 agentic-icu-fixed/
├──  run.py                    # Main entry point
├──  requirements.txt          # Dependencies
├──   .env                     # Configuration
├──  agentic_icu/             # Main framework
│   ├──  agent_framework/     # AI agents
│   ├──  data_layer/          # Data simulation  
│   ├──  orchestration/       # System coordination
│   ├──  api/                 # REST API
│   └──   config/             # Settings
├──  examples/demo.py         # Simple demo
└──  data/                    # Generated data (created on run)
```

##  AI Agents

- ** Physician Agent**: Makes clinical decisions and diagnoses
- ** Nurse Agent**: Monitors patients and coordinates care
- ** Pharmacist Agent**: Manages medications and checks interactions

##  Simulated Features

- **Virtual Patients**: Demographics, medical history, conditions
- **Vital Signs**: Heart rate, blood pressure, oxygen, temperature
- **Lab Results**: Blood tests with normal/abnormal values  
- **Medications**: ICU drugs with realistic dosing
- **Clinical Alerts**: Automated warnings for critical values
- **Agent Decisions**: AI recommendations with confidence scores

##  Configuration

Edit `.env` to customize:
```
SYNTHETIC_PATIENTS=10          # Number of patients
SIMULATION_DURATION_HOURS=1    # Default simulation length
API_PORT=8000                  # Web API port
LOG_LEVEL=INFO                 # Logging detail
```

##  API Endpoints

If you run `python run.py api`:
```bash
# System health
curl http://localhost:8000/health

# All patients
curl http://localhost:8000/patients

# Specific patient  
curl http://localhost:8000/patients/PATIENT_001

# All agents
curl http://localhost:8000/agents

# Start simulation
curl -X POST http://localhost:8000/simulation/start
```

##  Features Demonstrated

-  **Real-time data processing** - Continuous monitoring
-  **Multi-agent coordination** - Agents work together  
-  **Clinical decision support** - Evidence-based recommendations
-  **Alert management** - Automated critical value detection
-  **Performance monitoring** - System metrics and reporting
-  **Realistic simulation** - Healthcare scenarios without real hardware

##  Perfect For Research

Study these topics:
- Multi-agent AI systems in healthcare
- Real-time clinical decision support
- Healthcare process automation
- AI safety in medical applications  
- Human-AI collaboration patterns

##  Troubleshooting

**Import errors**: Make sure you're in project directory and ran `pip install -r requirements.txt`

**No data**: Check that `./data/` directory gets created during run

**Permission errors**: Make sure you can write to the project directory

**Port conflicts**: Change `API_PORT` in `.env` file

##  Next Steps

1. **Run the demo** to see the system in action
2. **Explore generated data** in `./data/patients/`  
3. **Try the API** with `python run.py api`
4. **Modify settings** in `.env` for different scenarios
5. **Extend agents** by editing files in `agent_framework/`

---

