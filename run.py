"""
Launcher Script for Claims Intelligence System
Launches the standalone Streamlit analytics platform.
The backend domain services (analytics, audits, ingestion, and tracking)
run directly and natively in Streamlit.
"""

import sys
import subprocess
import os

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = CURRENT_DIR


def start_app():
    print(">> Starting Claims Intelligence Analytics System on Streamlit (port 8501)...")
    app_path = os.path.join(CURRENT_DIR, "app.py")
    subprocess.run([sys.executable, "-m", "streamlit", "run", app_path, "--server.port", "8501"], cwd=PROJECT_ROOT)


if __name__ == "__main__":
    start_app()
