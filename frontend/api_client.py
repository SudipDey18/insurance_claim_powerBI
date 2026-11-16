"""
Service Controller Module
Directly connects Streamlit frontend components to backend operational,
analytics, and audit domain services in-process.
Streamlit-native architecture: zero HTTP overhead and zero external server dependencies.
"""

import os
from typing import Dict, Any, Tuple, Optional, List
import pandas as pd

from backend.data_service import (
    load_dataset,
    filter_dataset,
    process_uploaded_bytes,
    reset_custom_dataset,
    get_sample_dataset_bytes,
    validate_dataset_columns,
    REQUIRED_COLUMNS
)
from backend.analytics_service import (
    compute_executive_kpis,
    compute_component_breakdown,
    compute_temporal_trends,
    compute_severity_metrics,
    compute_correlation_matrix
)
from backend.audit_service import run_full_anomaly_audit
from backend.viewer_service import record_viewer_visit, get_viewer_stats
from backend.config import UPLOADED_DATA_FILE

# In-memory local cache reference
_local_df = None


def _get_local_df(force_reload: bool = False) -> pd.DataFrame:
    """Retrieves or refreshes the cached master DataFrame."""
    global _local_df
    if _local_df is None or force_reload:
        _local_df = load_dataset()
    return _local_df


def check_backend_status() -> Tuple[bool, Dict[str, Any]]:
    """Returns engine health and dataset status for the Streamlit application."""
    df = _get_local_df()
    return True, {
        "status": "healthy",
        "engine": "Streamlit Core",
        "records_loaded": len(df) if df is not None else 0
    }


def fetch_filter_options() -> Dict[str, Any]:
    """Retrieves unique filter options directly from the active dataset."""
    df = _get_local_df()
    return {
        "policy_states": ["All"] + sorted(df['policy_state'].dropna().unique().tolist()),
        "incident_severities": ["All"] + sorted(df['incident_severity'].dropna().unique().tolist()),
        "incident_months": ["All"] + sorted(df['incident_month'].dropna().unique().tolist()),
        "fraud_statuses": ["All", "Legitimate", "Fraudulent"]
    }


def fetch_kpis(
    policy_state: Optional[str] = None,
    incident_severity: Optional[str] = None,
    fraud_status: Optional[str] = None,
    incident_month: Optional[str] = None
) -> Dict[str, Any]:
    """Calculates executive KPIs based on active filter parameters."""
    df = _get_local_df()
    filtered = filter_dataset(df, policy_state, incident_severity, fraud_status, incident_month)
    return compute_executive_kpis(filtered)


def fetch_breakdown(
    policy_state: Optional[str] = None,
    incident_severity: Optional[str] = None,
    fraud_status: Optional[str] = None,
    incident_month: Optional[str] = None
) -> Dict[str, Any]:
    """Calculates financial payout allocation across vehicle, injury, and property shares."""
    df = _get_local_df()
    filtered = filter_dataset(df, policy_state, incident_severity, fraud_status, incident_month)
    return compute_component_breakdown(filtered)


def fetch_trends(
    policy_state: Optional[str] = None,
    incident_severity: Optional[str] = None,
    fraud_status: Optional[str] = None
) -> Dict[str, Any]:
    """Calculates monthly volume and 24-hour incident occurrence dynamics."""
    df = _get_local_df()
    filtered = filter_dataset(df, policy_state, incident_severity, fraud_status)
    return compute_temporal_trends(filtered)


def fetch_severities(
    policy_state: Optional[str] = None,
    incident_month: Optional[str] = None
) -> Dict[str, Any]:
    """Calculates claim volume, total outlay, and fraud rate per incident severity tier."""
    df = _get_local_df()
    filtered = filter_dataset(df, policy_state=policy_state, incident_month=incident_month)
    return compute_severity_metrics(filtered)


def fetch_correlation() -> Dict[str, Any]:
    """Calculates Pearson correlation matrix for numerical attributes."""
    df = _get_local_df()
    return compute_correlation_matrix(df)


def fetch_audits() -> Dict[str, Any]:
    """Calculates Module 6 operational anomaly and data quality audits."""
    df = _get_local_df()
    return run_full_anomaly_audit(df)


def get_client_ip() -> str:
    """
    Detects the client's IP address from Streamlit headers, context, or runtime session.
    Falls back to '127.0.0.1' for local access.
    """
    try:
        import streamlit as st
        # 1. Query parameters override (useful for testing e.g. ?client_ip=192.168.1.10)
        if hasattr(st, "query_params") and "client_ip" in st.query_params:
            param_ip = st.query_params.get("client_ip")
            if param_ip:
                return str(param_ip).strip()

        # 2. Check Streamlit context headers (e.g. reverse proxy, cloud deployment)
        if hasattr(st, "context") and hasattr(st.context, "headers") and st.context.headers:
            headers = st.context.headers
            for key in ["x-forwarded-for", "x-real-ip", "cf-connecting-ip", "client-ip", "x-client-ip"]:
                val = headers.get(key)
                if val:
                    first_ip = val.split(",")[0].strip()
                    if first_ip and first_ip not in ("::1", "localhost"):
                        return first_ip

        # 3. Check st.context.ip_address
        if hasattr(st, "context") and hasattr(st.context, "ip_address"):
            ip = st.context.ip_address
            if ip and ip not in ("::1", "localhost"):
                return str(ip).strip()

        # 4. Check Streamlit runtime session client context
        from streamlit.runtime.scriptrunner_utils.script_run_context import get_script_run_ctx
        from streamlit import runtime
        ctx = get_script_run_ctx()
        if ctx:
            client = runtime.get_instance().get_client(ctx.session_id)
            if client and hasattr(client, "client_context") and client.client_context:
                remote_ip = getattr(client.client_context, "remote_ip", None)
                if remote_ip and remote_ip not in ("::1", "localhost"):
                    return str(remote_ip).strip()
    except Exception:
        pass

    return "127.0.0.1"


def record_viewer(ip: Optional[str] = None) -> Dict[str, Any]:
    """Records a viewer visit by IP and logs to backend/logs/viewer_audit.log."""
    if not ip:
        ip = get_client_ip()
    return record_viewer_visit(ip)


def fetch_viewer_stats() -> Dict[str, Any]:
    """Retrieves current unique viewer counts."""
    return get_viewer_stats()


def upload_dataset_file(file_bytes: bytes, filename: str) -> Dict[str, Any]:
    """Validates and activates a custom dataset file in-process."""
    global _local_df
    try:
        processed = process_uploaded_bytes(file_bytes, filename)
        _local_df = processed
        return {
            "status": "success",
            "message": f"Dataset '{filename}' successfully validated and activated.",
            "records_loaded": len(processed),
            "columns_count": len(processed.columns)
        }
    except ValueError as ve:
        return {"status": "error", "message": str(ve)}
    except Exception as e:
        return {"status": "error", "message": f"Failed to process dataset: {str(e)}"}


def reset_active_dataset() -> Dict[str, Any]:
    """Resets the active dataset back to the standard master portfolio."""
    global _local_df
    try:
        _local_df = reset_custom_dataset()
        return {
            "status": "success",
            "message": "Reset to default claims portfolio.",
            "records_loaded": len(_local_df)
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


def get_dataset_info() -> Dict[str, Any]:
    """Retrieves metadata on the currently active dataset."""
    df = _get_local_df()
    is_custom = os.path.exists(UPLOADED_DATA_FILE) and os.path.getsize(UPLOADED_DATA_FILE) > 0
    return {
        "status": "ready",
        "is_custom": is_custom,
        "dataset_name": "Custom Uploaded Dataset" if is_custom else "Standard Production Portfolio",
        "record_count": len(df) if df is not None else 0,
        "column_count": len(df.columns) if df is not None else 0
    }


def fetch_sample_template(format_type: str = "csv") -> Tuple[bytes, str, str]:
    """Returns downloadable sample dataset template (bytes, mime, filename)."""
    return get_sample_dataset_bytes(format_type=format_type)


def get_required_columns() -> List[str]:
    """Returns list of required columns."""
    return REQUIRED_COLUMNS
