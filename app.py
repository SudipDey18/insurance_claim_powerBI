"""
Claims Intelligence Analytics System
Root Streamlit Entrypoint for Cloud Deployment (Streamlit Community Cloud).
"""

import os
import sys

# Ensure root directory is on Python path
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

# Configure Matplotlib writable cache for headless/cloud environments
os.environ.setdefault("MPLCONFIGDIR", os.path.join(CURRENT_DIR, ".matplotlib_cache"))
os.makedirs(os.environ["MPLCONFIGDIR"], exist_ok=True)

from frontend.app import main

if __name__ == "__main__":
    main()
