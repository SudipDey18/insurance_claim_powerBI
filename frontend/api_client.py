"""
API Client Module
Communicates with the FastAPI backend service via HTTP requests.
Implements graceful local fallbacks if the server is offline.
"""

import os
from typing import Dict, Any, Tuple, Optional
import requests

from backend.config import BACKEND_URL
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

# Local cache reference for fallback mode
_local_df = None


def _get_local_df(force_reload: bool = False):
    global _local_df
    if _local_df is None or force_reload:
        _local_df = load_dataset()
    return _local_df


def check_backend_status() -> Tuple[bool, Optional[Dict[str, Any]]]:
    """Tests connectivity to the FastAPI backend service."""
    try:
        response = requests.get(f"{BACKEND_URL}/health", timeout=0.8)
        if response.status_code == 200:
            return True, response.json()
    except Exception:
        pass
    return False, None


def fetch_filter_options() -> Dict[str, Any]:
    """Retrieves unique filter options from backend API or local dataset."""
    try:
        response = requests.get(f"{BACKEND_URL}/api/filter-options", timeout=1.0)
        if response.status_code == 200:
            return response.json()
    except Exception:
        pass

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
    """Retrieves calculated KPIs from backend API or local fallback."""
    params = {}
    if policy_state and policy_state != "All": params['policy_state'] = policy_state
    if incident_severity and incident_severity != "All": params['incident_severity'] = incident_severity
    if fraud_status and fraud_status != "All": params['fraud_status'] = fraud_status
    if incident_month and incident_month != "All": params['incident_month'] = incident_month

    try:
        response = requests.get(f"{BACKEND_URL}/api/kpis", params=params, timeout=1.5)
        if response.status_code == 200:
            return response.json()
    except Exception:
        pass

    df = _get_local_df()
    filtered = filter_dataset(df, policy_state, incident_severity, fraud_status, incident_month)
    return compute_executive_kpis(filtered)


def fetch_breakdown(
    policy_state: Optional[str] = None,
    incident_severity: Optional[str] = None,
    fraud_status: Optional[str] = None,
    incident_month: Optional[str] = None
) -> Dict[str, Any]:
    """Retrieves component breakdown from backend API or local fallback."""
    params = {}
    if policy_state and policy_state != "All": params['policy_state'] = policy_state
    if incident_severity and incident_severity != "All": params['incident_severity'] = incident_severity
    if fraud_status and fraud_status != "All": params['fraud_status'] = fraud_status
    if incident_month and incident_month != "All": params['incident_month'] = incident_month

    try:
        response = requests.get(f"{BACKEND_URL}/api/breakdown", params=params, timeout=1.5)
        if response.status_code == 200:
            return response.json()
    except Exception:
        pass

    df = _get_local_df()
    filtered = filter_dataset(df, policy_state, incident_severity, fraud_status, incident_month)
    return compute_component_breakdown(filtered)


def fetch_trends(
    policy_state: Optional[str] = None,
    incident_severity: Optional[str] = None,
    fraud_status: Optional[str] = None
) -> Dict[str, Any]:
    """Retrieves temporal dynamics from backend API or local fallback."""
    params = {}
    if policy_state and policy_state != "All": params['policy_state'] = policy_state
    if incident_severity and incident_severity != "All": params['incident_severity'] = incident_severity
    if fraud_status and fraud_status != "All": params['fraud_status'] = fraud_status

    try:
        response = requests.get(f"{BACKEND_URL}/api/trends", params=params, timeout=1.5)
        if response.status_code == 200:
            return response.json()
    except Exception:
        pass

    df = _get_local_df()
    filtered = filter_dataset(df, policy_state, incident_severity, fraud_status)
    return compute_temporal_trends(filtered)


def fetch_severities(
    policy_state: Optional[str] = None,
    incident_month: Optional[str] = None
):
    """Retrieves severity tier distributions from backend API or local fallback."""
    params = {}
    if policy_state and policy_state != "All": params['policy_state'] = policy_state
    if incident_month and incident_month != "All": params['incident_month'] = incident_month

    try:
        response = requests.get(f"{BACKEND_URL}/api/severities", params=params, timeout=1.5)
        if response.status_code == 200:
            return response.json()
    except Exception:
        pass

    df = _get_local_df()
    filtered = filter_dataset(df, policy_state=policy_state, incident_month=incident_month)
    return compute_severity_metrics(filtered)


def fetch_correlation():
    """Retrieves numerical correlation matrix."""
    try:
        response = requests.get(f"{BACKEND_URL}/api/correlation", timeout=1.5)
        if response.status_code == 200:
            return response.json()
    except Exception:
        pass

    df = _get_local_df()
    return compute_correlation_matrix(df)


def fetch_audits() -> Dict[str, Any]:
    """Retrieves anomaly audit reports from backend API or local fallback."""
    try:
        response = requests.get(f"{BACKEND_URL}/api/audits", timeout=1.5)
        if response.status_code == 200:
            return response.json()
    except Exception:
        pass

    df = _get_local_df()
    return run_full_anomaly_audit(df)


def get_client_ip() -> str:
    """
    Detects the client's IP address from Streamlit headers, context, or runtime session.
    Falls back to '127.0.0.1' for local access.
    """
    try:
        import streamlit as st
        # 1. Query parameters override (useful for testing or simulation e.g. ?client_ip=192.168.1.10)
        if hasattr(st, "query_params") and "client_ip" in st.query_params:
            param_ip = st.query_params.get("client_ip")
            if param_ip:
                return str(param_ip).strip()

        # 2. Check Streamlit context headers (e.g. reverse proxy, ngrok, cloud deploy)
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
    """Records a viewer visit by IP via backend API or local fallback."""
    if not ip:
        ip = get_client_ip()

    try:
        response = requests.post(f"{BACKEND_URL}/api/viewers/record", json={"ip": ip}, timeout=1.5)
        if response.status_code == 200:
            return response.json()
    except Exception:
        pass

    return record_viewer_visit(ip)


def fetch_viewer_stats() -> Dict[str, Any]:
    """Retrieves viewer statistics via backend API or local fallback."""
    try:
        response = requests.get(f"{BACKEND_URL}/api/viewers", timeout=1.5)
        if response.status_code == 200:
            return response.json()
    except Exception:
        pass

    return get_viewer_stats()


def upload_dataset_file(file_bytes: bytes, filename: str) -> Dict[str, Any]:
    """Uploads and activates a custom dataset via backend API or local fallback."""
    global _local_df
    try:
        files = {"file": (filename, file_bytes)}
        response = requests.post(f"{BACKEND_URL}/api/dataset/upload", files=files, timeout=6.0)
        if response.status_code == 200:
            _local_df = _get_local_df(force_reload=True)
            return response.json()
        elif response.status_code in (400, 422):
            detail = response.json().get("detail", "Validation failed.")
            return {"status": "error", "message": detail}
    except Exception:
        pass

    # Local fallback
    try:
        processed = process_uploaded_bytes(file_bytes, filename)
        _local_df = processed
        return {
            "status": "success",
            "message": f"Dataset '{filename}' successfully validated and loaded locally.",
            "records_loaded": len(processed),
            "columns_count": len(processed.columns)
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


def reset_active_dataset() -> Dict[str, Any]:
    """Resets to default dataset via backend API or local fallback."""
    global _local_df
    try:
        response = requests.post(f"{BACKEND_URL}/api/dataset/reset", timeout=3.0)
        if response.status_code == 200:
            _local_df = _get_local_df(force_reload=True)
            return response.json()
    except Exception:
        pass

    # Local fallback
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
    """Retrieves metadata on active dataset."""
    try:
        response = requests.get(f"{BACKEND_URL}/api/dataset/status", timeout=1.5)
        if response.status_code == 200:
            return response.json()
    except Exception:
        pass

    df = _get_local_df()
    from backend.config import UPLOADED_DATA_FILE
    is_custom = os.path.exists(UPLOADED_DATA_FILE) and os.path.getsize(UPLOADED_DATA_FILE) > 0
    return {
        "status": "ready",
        "is_custom": is_custom,
        "dataset_name": "Custom Uploaded Dataset" if is_custom else "Standard Production Portfolio",
        "record_count": len(df),
        "column_count": len(df.columns)
    }


def fetch_sample_template(format_type: str = "csv") -> Tuple[bytes, str, str]:
    """Returns downloadable sample dataset template (bytes, mime, filename)."""
    return get_sample_dataset_bytes(format_type=format_type)


def get_required_columns() -> List[str]:
    """Returns list of required columns."""
    return REQUIRED_COLUMNS


