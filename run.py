"""
🚀 CloudWalk Technical Assessment — Quick Launcher
"""

import os
import sys
import subprocess

def main():
    root_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(root_dir)
    sys.path.insert(0, os.path.join(root_dir, "src"))

    print("\n" + "=" * 80)
    print("🛡️ CLOUDWALK ANTI-FRAUD INTELLIGENCE — AUTOMATED LAUNCHER")
    print("=" * 80)

    # 1. Database Ingestion and Integrity Verification
    print("\n[1/2] Checking database integrity and transaction ingestion...")
    try:
        from ingest_data import run_ingestion
        run_ingestion(verbose=True)
    except Exception as e:
        print(f"⚠️ Error verifying database: {e}")
        print("Attempting to proceed with the dashboard...")

    # 2. Launching Streamlit Dashboard
    print("\n[2/2] Launching Streamlit Dashboard...")
    dashboard_path = os.path.join("src", "dashboard.py")
    
    cmd = [sys.executable, "-m", "streamlit", "run", dashboard_path]
    print(f"Executing command: {' '.join(cmd)}\n")
    
    try:
        subprocess.run(cmd, check=True)
    except KeyboardInterrupt:
        print("\n👋 Application closed by user.")
    except Exception as e:
        print(f"\n❌ Error launching Streamlit: {e}")
        print("\nManual execution alternative:")
        print("  streamlit run src/dashboard.py")
        print("or with uv:")
        print("  uv run streamlit run src/dashboard.py")

if __name__ == "__main__":
    main()
