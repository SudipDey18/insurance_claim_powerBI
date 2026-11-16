import os

# Base directory paths
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, ".."))

# Data file paths
CLEANED_DATA_FILE = os.path.join(PROJECT_ROOT, "dataset", "insurance_claims_cleaned.csv")
RAW_DATA_FILE = os.path.join(PROJECT_ROOT, "dataset", "insurance_claims.csv")
VIEWERS_DATA_FILE = os.path.join(PROJECT_ROOT, "dataset", "viewers.json")
SAMPLE_CSV_FILE = os.path.join(PROJECT_ROOT, "dataset", "sample_template.csv")
SAMPLE_EXCEL_FILE = os.path.join(PROJECT_ROOT, "dataset", "sample_template.xlsx")
UPLOADED_DATA_FILE = os.path.join(PROJECT_ROOT, "dataset", "uploaded_dataset.csv")

# Logging directory and file paths
LOGS_DIR = os.path.join(CURRENT_DIR, "logs")
VIEWER_LOG_FILE = os.path.join(LOGS_DIR, "viewer_audit.log")
SERVER_LOG_FILE = os.path.join(LOGS_DIR, "server.log")

# Server configuration (Streamlit Standalone)
SERVER_HOST = "0.0.0.0"
SERVER_PORT = 8501
