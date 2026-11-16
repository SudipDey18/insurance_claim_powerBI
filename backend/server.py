"""
Claims Intelligence Analytics Backend Service Layer
Provides backend metric computations, operational anomaly audits,
dataset management, and IP-based viewer tracking.
Runs 100% natively in Streamlit with zero FastAPI or Uvicorn dependencies.
"""

from typing import Optional, Dict, Any, List, Tuple
import os

from .config import SERVER_HOST, SERVER_PORT, UPLOADED_DATA_FILE
from .data_service import (
    load_dataset,
    filter_dataset,
    process_uploaded_bytes,
    reset_custom_dataset,
    get_sample_dataset_bytes,
    validate_dataset_columns,
    REQUIRED_COLUMNS
)
from .analytics_service import (
    compute_executive_kpis,
    compute_component_breakdown,
    compute_temporal_trends,
    compute_severity_metrics,
    compute_correlation_matrix
)
from .audit_service import run_full_anomaly_audit
from .viewer_service import record_viewer_visit, get_viewer_stats
from .logger import get_backend_logger

logger = get_backend_logger()

# In-memory cached dataset reference
df_master = None


def get_master_df(force_reload: bool = False):
    """Initializes or retrieves the active master DataFrame."""
    global df_master
    if df_master is None or force_reload:
        try:
            df_master = load_dataset()
            logger.info(f"Data ingestion successful: {len(df_master)} observations loaded.")
        except Exception as e:
            logger.error(f"Failed to load dataset: {e}")
    return df_master


def health_check() -> Dict[str, Any]:
    """Health check for service status verification."""
    df = get_master_df()
    return {
        "status": "healthy",
        "engine": "Streamlit Core",
        "dataset_ready": df is not None,
        "record_count": len(df) if df is not None else 0
    }


def get_filter_options() -> Dict[str, Any]:
    """Returns unique categorical dimensions available for user filtering."""
    df = get_master_df()
    if df is None:
        return {
            "policy_states": ["All"],
            "incident_severities": ["All"],
            "incident_months": ["All"],
            "fraud_statuses": ["All"]
        }

    states = ["All"] + sorted(df['policy_state'].dropna().unique().tolist())
    severities = ["All"] + sorted(df['incident_severity'].dropna().unique().tolist())
    months = ["All"] + sorted(df['incident_month'].dropna().unique().tolist())
    fraud_options = ["All", "Legitimate", "Fraudulent"]

    return {
        "policy_states": states,
        "incident_severities": severities,
        "incident_months": months,
        "fraud_statuses": fraud_options
    }


def get_kpis(
    policy_state: Optional[str] = None,
    incident_severity: Optional[str] = None,
    fraud_status: Optional[str] = None,
    incident_month: Optional[str] = None
) -> Dict[str, Any]:
    """Calculates executive KPIs based on active filter parameters."""
    df = get_master_df()
    filtered_df = filter_dataset(
        df,
        policy_state=policy_state,
        incident_severity=incident_severity,
        fraud_status=fraud_status,
        incident_month=incident_month
    )
    return compute_executive_kpis(filtered_df)


def get_component_breakdown(
    policy_state: Optional[str] = None,
    incident_severity: Optional[str] = None,
    fraud_status: Optional[str] = None,
    incident_month: Optional[str] = None
) -> Dict[str, Any]:
    """Returns financial payout distribution across vehicle, injury, and property shares."""
    df = get_master_df()
    filtered_df = filter_dataset(
        df,
        policy_state=policy_state,
        incident_severity=incident_severity,
        fraud_status=fraud_status,
        incident_month=incident_month
    )
    return compute_component_breakdown(filtered_df)


def get_trends(
    policy_state: Optional[str] = None,
    incident_severity: Optional[str] = None,
    fraud_status: Optional[str] = None
) -> Dict[str, Any]:
    """Returns monthly volume and 24-hour incident occurrence dynamics."""
    df = get_master_df()
    filtered_df = filter_dataset(
        df,
        policy_state=policy_state,
        incident_severity=incident_severity,
        fraud_status=fraud_status
    )
    return compute_temporal_trends(filtered_df)


def get_severities(
    policy_state: Optional[str] = None,
    incident_month: Optional[str] = None
) -> List[Dict[str, Any]]:
    """Returns claim volume, total outlay, and fraud rate per incident severity tier."""
    df = get_master_df()
    filtered_df = filter_dataset(
        df,
        policy_state=policy_state,
        incident_month=incident_month
    )
    return compute_severity_metrics(filtered_df)


def get_correlation() -> Dict[str, Any]:
    """Returns Pearson correlation matrix for numerical attributes."""
    df = get_master_df()
    return compute_correlation_matrix(df)


def get_audits() -> Dict[str, Any]:
    """Returns complete Module 6 operational anomaly and data quality audits."""
    df = get_master_df()
    return run_full_anomaly_audit(df)


def record_viewer(client_ip: Optional[str] = None) -> Dict[str, Any]:
    """Records a viewer visit by client IP and returns updated visitor statistics."""
    return record_viewer_visit(client_ip or "127.0.0.1")


def get_viewers() -> Dict[str, Any]:
    """Returns total viewers (unique IP count) and total visits."""
    return get_viewer_stats()


def get_dataset_status() -> Dict[str, Any]:
    """Returns the status and record count of the currently active dataset."""
    df = get_master_df()
    is_custom = os.path.exists(UPLOADED_DATA_FILE) and os.path.getsize(UPLOADED_DATA_FILE) > 0
    return {
        "status": "ready",
        "is_custom": is_custom,
        "dataset_name": "Custom Uploaded Dataset" if is_custom else "Standard Production Portfolio",
        "record_count": len(df) if df is not None else 0,
        "column_count": len(df.columns) if df is not None else 0
    }


def get_dataset_schema() -> Dict[str, Any]:
    """Returns the list of required column fields and their descriptions for validation."""
    return {
        "required_columns_count": len(REQUIRED_COLUMNS),
        "required_columns": REQUIRED_COLUMNS,
        "expected_format": ["csv", "xlsx", "xls"]
    }


def download_sample_dataset(file_format: Optional[str] = "csv") -> Tuple[bytes, str, str]:
    """Returns downloadable sample format of the dataset (CSV or Excel)."""
    return get_sample_dataset_bytes(format_type=file_format or "csv")


def upload_dataset(file_bytes: bytes, filename: str) -> Dict[str, Any]:
    """Validates and activates an uploaded custom dataset file."""
    global df_master
    processed_df = process_uploaded_bytes(file_bytes, filename)
    df_master = processed_df
    logger.info(f"Custom dataset uploaded: '{filename}' with {len(df_master)} records.")
    return {
        "status": "success",
        "message": f"Dataset '{filename}' successfully validated and activated.",
        "filename": filename,
        "records_loaded": len(df_master),
        "columns_count": len(df_master.columns)
    }


def reset_dataset() -> Dict[str, Any]:
    """Resets active dataset back to the standard default portfolio dataset."""
    global df_master
    df_master = reset_custom_dataset()
    logger.info("Dataset reset to default master portfolio.")
    return {
        "status": "success",
        "message": "Reset to default claims dataset successfully.",
        "records_loaded": len(df_master)
    }


def run_server():
    """Launches the Streamlit application."""
    import subprocess
    import sys
    from .config import PROJECT_ROOT
    frontend_path = os.path.join(PROJECT_ROOT, "frontend", "app.py")
    subprocess.run([sys.executable, "-m", "streamlit", "run", frontend_path, "--server.port", "8501"], cwd=PROJECT_ROOT)


if __name__ == "__main__":
    run_server()
