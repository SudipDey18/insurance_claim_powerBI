"""
Claims Intelligence Analytics Backend REST API
FastAPI microservice serving executive metrics, temporal trends,
component allocations, and data quality audits.
No machine learning components.
"""

from typing import Optional, Dict, Any, List
from fastapi import FastAPI, Query, HTTPException, Request, UploadFile, File, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

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


@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Logs incoming HTTP requests and response status codes."""
    client_ip = request.headers.get("x-forwarded-for") or (request.client.host if request.client else "unknown")
    if "," in client_ip:
        client_ip = client_ip.split(",")[0].strip()
    logger.info(f"Incoming {request.method} {request.url.path} from {client_ip}")
    response = await call_next(request)
    logger.info(f"Completed {request.method} {request.url.path} with status {response.status_code}")
    return response


# In-memory cached dataset reference
df_master = None


@app.on_event("startup")
def startup_event():
    """Initializes and preloads dataset on server launch."""
    global df_master
    try:
        df_master = load_dataset()
        logger.info(f"Data ingestion successful: {len(df_master)} observations loaded.")
    except Exception as e:
        logger.error(f"Failed to load dataset on startup: {e}")


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
            "/api/audits",
            "/api/viewers",
            "/api/viewers/record",
            "/api/dataset/status",
            "/api/dataset/upload",
            "/api/dataset/reset",
            "/api/dataset/sample",
            "/api/dataset/schema"
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


class ViewerRecordRequest(BaseModel):
    ip: Optional[str] = None


@app.post("/api/viewers/record")
def record_viewer(req: Optional[ViewerRecordRequest] = None, request: Request = None):
    """Records a viewer visit by client IP and returns updated visitor statistics."""
    client_ip = None
    if req and req.ip:
        client_ip = req.ip
    elif request:
        forwarded = request.headers.get("x-forwarded-for")
        if forwarded:
            client_ip = forwarded.split(",")[0].strip()
        elif request.client and request.client.host:
            client_ip = request.client.host

    return record_viewer_visit(client_ip or "127.0.0.1")


@app.get("/api/viewers")
def get_viewers():
    """Returns total viewers (unique IP count), total visits, and IP breakdown."""
    return get_viewer_stats()


@app.get("/api/dataset/status")
def get_dataset_status():
    """Returns the status and record count of the currently active dataset."""
    import os
    is_custom = os.path.exists(UPLOADED_DATA_FILE) and os.path.getsize(UPLOADED_DATA_FILE) > 0
    return {
        "status": "ready",
        "is_custom": is_custom,
        "dataset_name": "Custom Uploaded Dataset" if is_custom else "Standard Production Portfolio",
        "record_count": len(df_master) if df_master is not None else 0,
        "column_count": len(df_master.columns) if df_master is not None else 0
    }


@app.get("/api/dataset/schema")
def get_dataset_schema():
    """Returns the list of required column fields and their descriptions for validation."""
    return {
        "required_columns_count": len(REQUIRED_COLUMNS),
        "required_columns": REQUIRED_COLUMNS,
        "expected_format": ["csv", "xlsx", "xls"]
    }


@app.get("/api/dataset/sample")
def download_sample_dataset(format: Optional[str] = Query("csv")):
    """Returns a downloadable sample format of the dataset (CSV or Excel) with matching columns."""
    content, media_type, filename = get_sample_dataset_bytes(format_type=format or "csv")
    return Response(
        content=content,
        media_type=media_type,
        headers={"Content-Disposition": f'attachment; filename="{filename}"'}
    )


@app.post("/api/dataset/upload")
async def upload_dataset(file: UploadFile = File(...)):
    """
    Accepts an uploaded CSV or Excel file, validates that all required columns match,
    runs domain feature engineering, and updates the active dataset.
    """
    global df_master
    if not file.filename.lower().endswith(('.csv', '.xlsx', '.xls')):
        raise HTTPException(
            status_code=400,
            detail="Unsupported file format. Please upload a CSV (.csv) or Excel (.xlsx, .xls) file."
        )

    try:
        contents = await file.read()
        processed_df = process_uploaded_bytes(contents, file.filename)
        df_master = processed_df
        logger.info(f"Custom dataset uploaded: '{file.filename}' with {len(df_master)} records.")
        return {
            "status": "success",
            "message": f"Dataset '{file.filename}' successfully validated and activated.",
            "filename": file.filename,
            "records_loaded": len(df_master),
            "columns_count": len(df_master.columns)
        }
    except ValueError as ve:
        logger.warning(f"Dataset upload validation failure: {ve}")
        raise HTTPException(status_code=422, detail=str(ve))
    except Exception as e:
        logger.error(f"Failed to process uploaded dataset: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to process dataset: {str(e)}")


@app.post("/api/dataset/reset")
def reset_dataset():
    """Resets active dataset back to the standard default portfolio dataset."""
    global df_master
    try:
        df_master = reset_custom_dataset()
        logger.info("Dataset reset to default master portfolio.")
        return {
            "status": "success",
            "message": "Reset to default claims dataset successfully.",
            "records_loaded": len(df_master)
        }
    except Exception as e:
        logger.error(f"Failed to reset dataset: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to reset dataset: {str(e)}")


def run_server():
    """Starts the Uvicorn application server."""
    uvicorn.run("backend.server:app", host=SERVER_HOST, port=SERVER_PORT, reload=False)


if __name__ == "__main__":
    run_server()
