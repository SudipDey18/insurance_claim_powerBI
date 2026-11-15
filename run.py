"""
Launcher Script for Claims Intelligence System
Provides a convenient CLI entrypoint to launch either the backend, frontend, or both.
"""

import sys
import subprocess
import os

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = CURRENT_DIR


def start_backend():
    print(">> Starting FastAPI Backend Server on port 8000...")
    subprocess.run([sys.executable, "-m", "uvicorn", "backend.server:app", "--host", "0.0.0.0", "--port", "8000"], cwd=PROJECT_ROOT)


def start_frontend():
    print(">> Starting Streamlit Frontend on port 8501...")
    frontend_path = os.path.join(CURRENT_DIR, "frontend", "app.py")
    subprocess.run([sys.executable, "-m", "streamlit", "run", frontend_path, "--server.port", "8501"], cwd=PROJECT_ROOT)


if __name__ == "__main__":
    arg = sys.argv[1] if len(sys.argv) > 1 else "frontend"
    if arg == "backend":
        start_backend()
    elif arg == "frontend":
        start_frontend()
    else:
        print("Usage: python run.py [backend|frontend]")
