import os

# Base directory paths
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, ".."))
print(PROJECT_ROOT)
print(r"G:\claims_dashboard\claims_dashboard\claims_dashboard\dataset\insurance_claims_cleaned.csv")
# Data file paths
CLEANED_DATA_FILE = os.path.join(PROJECT_ROOT, r"dataset\insurance_claims_cleaned.csv")
RAW_DATA_FILE = os.path.join(PROJECT_ROOT, r"dataset\insurance_claims.csv")
print(CLEANED_DATA_FILE,"\n",RAW_DATA_FILE)

# Server configuration
SERVER_HOST = "0.0.0.0"
SERVER_PORT = 8000
BACKEND_URL = f"http://127.0.0.1:{SERVER_PORT}"
