"""
Claims Intelligence Analytics Backend REST API
FastAPI microservice serving executive metrics, temporal trends,
component allocations, and data quality audits.
No machine learning components.
"""

from typing import Optional, Dict, Any
from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from .config import SERVER_HOST, SERVER_PORT
from .data_service import load_dataset, filter_dataset
from .analytics_service import (
    compute_executive_kpis,
    compute_component_breakdown,
    compute_temporal_trends,
    compute_severity_metrics,
    compute_correlation_matrix
)
from .audit_service import run_full_anomaly_audit

# Initialize FastAPI instance
app = FastAPI(
    title="Claims Intelligence Analytics API",
    description="Backend service providing insurance claims performance metrics, operational audits, and KPI analytics.",
    version="2.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory cached dataset reference
df_master = None


@app.on_event("startup")
def startup_event():
    """Initializes and preloads dataset on server launch."""
    global df_master
    try:
        df_master = load_dataset()
        print(f"Data ingestion successful: {len(df_master)} observations loaded.")
    except Exception as e:
        print(f"Failed to load dataset on startup: {e}")


@app.get("/")
def get_root():
    """Root route detailing API status, capabilities, and documentation path."""
    return {
        "service": "Claims Intelligence Analytics API",
        "status": "online",
        "version": "2.0.0",
        "records_loaded": len(df_master) if df_master is not None else 0,
        "documentation": "/docs",
        "endpoints": [
            "/health",
            "/api/filter-options",
            "/api/kpis",
            "/api/breakdown",
            "/api/trends",
            "/api/severities",
            "/api/correlation",
            "/api/audits"
        ]
    }


@app.get("/health")
def health_check():
    """Health check endpoint for service status verification."""
    return {
        "status": "healthy",
        "dataset_ready": df_master is not None,
        "record_count": len(df_master) if df_master is not None else 0
    }


@app.get("/api/filter-options")
def get_filter_options():
    """Returns unique categorical dimensions available for user filtering."""
    if df_master is None:
        raise HTTPException(status_code=503, detail="Dataset not initialized.")

    states = ["All"] + sorted(df_master['policy_state'].dropna().unique().tolist())
    severities = ["All"] + sorted(df_master['incident_severity'].dropna().unique().tolist())
    months = ["All"] + sorted(df_master['incident_month'].dropna().unique().tolist())
    fraud_options = ["All", "Legitimate", "Fraudulent"]

    return {
        "policy_states": states,
        "incident_severities": severities,
        "incident_months": months,
        "fraud_statuses": fraud_options
    }


@app.get("/api/kpis")
def get_kpis(
    policy_state: Optional[str] = Query(None),
    incident_severity: Optional[str] = Query(None),
    fraud_status: Optional[str] = Query(None),
    incident_month: Optional[str] = Query(None)
):
    """Calculates executive KPIs based on active filter parameters."""
    if df_master is None:
        raise HTTPException(status_code=503, detail="Dataset not initialized.")

    filtered_df = filter_dataset(
        df_master,
        policy_state=policy_state,
        incident_severity=incident_severity,
        fraud_status=fraud_status,
        incident_month=incident_month
    )
    return compute_executive_kpis(filtered_df)


@app.get("/api/breakdown")
def get_component_breakdown(
    policy_state: Optional[str] = Query(None),
    incident_severity: Optional[str] = Query(None),
    fraud_status: Optional[str] = Query(None),
    incident_month: Optional[str] = Query(None)
):
    """Returns financial payout distribution across vehicle, injury, and property shares."""
    if df_master is None:
        raise HTTPException(status_code=503, detail="Dataset not initialized.")

    filtered_df = filter_dataset(
        df_master,
        policy_state=policy_state,
        incident_severity=incident_severity,
        fraud_status=fraud_status,
        incident_month=incident_month
    )
    return compute_component_breakdown(filtered_df)


@app.get("/api/trends")
def get_trends(
    policy_state: Optional[str] = Query(None),
    incident_severity: Optional[str] = Query(None),
    fraud_status: Optional[str] = Query(None)
):
    """Returns monthly volume and 24-hour incident occurrence dynamics."""
    if df_master is None:
        raise HTTPException(status_code=503, detail="Dataset not initialized.")

    filtered_df = filter_dataset(
        df_master,
        policy_state=policy_state,
        incident_severity=incident_severity,
        fraud_status=fraud_status
    )
    return compute_temporal_trends(filtered_df)


@app.get("/api/severities")
def get_severities(
    policy_state: Optional[str] = Query(None),
    incident_month: Optional[str] = Query(None)
):
    """Returns claim volume, total outlay, and fraud rate per incident severity tier."""
    if df_master is None:
        raise HTTPException(status_code=503, detail="Dataset not initialized.")

    filtered_df = filter_dataset(
        df_master,
        policy_state=policy_state,
        incident_month=incident_month
    )
    return compute_severity_metrics(filtered_df)


@app.get("/api/correlation")
def get_correlation():
    """Returns Pearson correlation matrix for numerical attributes."""
    if df_master is None:
        raise HTTPException(status_code=503, detail="Dataset not initialized.")

    return compute_correlation_matrix(df_master)


@app.get("/api/audits")
def get_audits():
    """Returns complete Module 6 operational anomaly and data quality audits."""
    if df_master is None:
        raise HTTPException(status_code=503, detail="Dataset not initialized.")

    return run_full_anomaly_audit(df_master)


def run_server():
    """Starts the Uvicorn application server."""
    uvicorn.run("backend.server:app", host=SERVER_HOST, port=SERVER_PORT, reload=False)


if __name__ == "__main__":
    run_server()
