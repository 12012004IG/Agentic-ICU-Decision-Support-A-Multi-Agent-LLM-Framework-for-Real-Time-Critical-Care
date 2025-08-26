#!/usr/bin/env python3
"""
Simple entry point for the Agentic ICU Decision Support System
No command arguments required - just runs the demo directly!
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

async def main():
    """Main function - directly runs the ICU demo"""

    print("🏥 Agentic ICU Decision Support System")
    print("="*50)
    print("Starting ICU simulation demo...")
    print("(This will run for 5 minutes by default)")
    print("Press Ctrl+C to stop early\n")

    try:
        # Import and run the demo
        from agentic_icu.orchestration.workflow_coordinator import run_demo_simulation
        await run_demo_simulation(5)  # 5 minute demo

    except KeyboardInterrupt:
        print("\n⏹️  Demo stopped by user")
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("\n🔧 Make sure you installed dependencies:")
        print("pip install -r requirements.txt")
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\n🔧 Troubleshooting:")
        print("1. Make sure you ran: pip install -r requirements.txt")
        print("2. Check that you're in the project directory")
        print("3. Verify all files were extracted properly")

if __name__ == "__main__":
    print("🚀 Starting Agentic ICU System...")
    asyncio.run(main())

