"""
Simple demo script to run the ICU system
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

async def main():
    """Main demo function"""

    print("🏥 Agentic ICU Decision Support System - Simple Demo")
    print("=" * 60)
    print("This demo will simulate:")
    print("• Virtual ICU patients with different conditions")
    print("• Real-time vital signs monitoring") 
    print("• AI agents making clinical decisions")
    print("• Clinical alerts and recommendations")
    print("=" * 60)

    try:
        duration = input("Enter demo duration in minutes (default 3): ").strip()
        if not duration:
            duration = 3
        else:
            duration = int(duration)

        print(f"\n🚀 Starting {duration}-minute demo...")
        print("Press Ctrl+C to stop early\n")

        from agentic_icu.orchestration.workflow_coordinator import run_demo_simulation
        await run_demo_simulation(duration)

    except KeyboardInterrupt:
        print("\n⏹️  Demo stopped by user")
    except ValueError:
        print("❌ Invalid duration. Using 3 minutes.")
        from agentic_icu.orchestration.workflow_coordinator import run_demo_simulation
        await run_demo_simulation(3)
    except Exception as e:
        print(f"❌ Demo error: {e}")

    print("\n🎉 Demo completed!")
    print("Check these files:")
    print("• ./data/patients/ - Generated patient data")
    print("• ./data/final_report.json - Simulation summary")

if __name__ == "__main__":
    asyncio.run(main())
