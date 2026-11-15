"""
API Client Module
Communicates with the FastAPI backend service via HTTP requests.
Implements graceful local fallbacks if the server is offline.
"""

import os
from typing import Dict, Any, Tuple, Optional
import requests

from backend.config import BACKEND_URL
from backend.data_service import load_dataset, filter_dataset
from backend.analytics_service import (
    compute_executive_kpis,
    compute_component_breakdown,
    compute_temporal_trends,
    compute_severity_metrics,
    compute_correlation_matrix
)
from backend.audit_service import run_full_anomaly_audit

# Local cache reference for fallback mode
_local_df = None


def _get_local_df():
    global _local_df
    if _local_df is None:
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
