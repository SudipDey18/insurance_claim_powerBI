"""
Data Service Module
Handles dataset ingestion, schema validation, data quality auditing,
hygiene transformation, domain feature derivation, and custom dataset uploads.
No machine learning dependencies.
"""

import io
import os
from typing import Optional, Tuple, List, Dict, Any
import numpy as np
import pandas as pd

from .config import (
    CLEANED_DATA_FILE,
    RAW_DATA_FILE,
    UPLOADED_DATA_FILE,
    SAMPLE_CSV_FILE,
    SAMPLE_EXCEL_FILE
)

# Canonical schema: 39 required raw insurance claims attributes
REQUIRED_COLUMNS: List[str] = [
    'months_as_customer', 'age', 'policy_number', 'policy_bind_date',
    'policy_state', 'policy_csl', 'policy_deductable', 'policy_annual_premium',
    'umbrella_limit', 'insured_zip', 'insured_sex', 'insured_education_level',
    'insured_occupation', 'insured_hobbies', 'insured_relationship',
    'capital-gains', 'capital-loss', 'incident_date', 'incident_type',
    'collision_type', 'incident_severity', 'authorities_contacted',
    'incident_state', 'incident_city', 'incident_location',
    'incident_hour_of_the_day', 'number_of_vehicles_involved',
    'property_damage', 'bodily_injuries', 'witnesses',
    'police_report_available', 'total_claim_amount', 'injury_claim',
    'property_claim', 'vehicle_claim', 'auto_make', 'auto_model',
    'auto_year', 'fraud_reported'
]


def validate_dataset_columns(df: pd.DataFrame) -> Tuple[bool, List[str]]:
    """
    Validates that the provided dataframe contains all expected standard columns.
    Returns (is_valid, missing_columns_list).
    """
    df_cols = set(c.strip() for c in df.columns)
    missing = [col for col in REQUIRED_COLUMNS if col not in df_cols]
    return (len(missing) == 0, missing)


def preprocess_and_engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Applies data hygiene, standardized token normalization, and domain feature engineering.
    """
    df = df.copy()

    # Drop delimiter artifact column if present
    if '_c39' in df.columns:
        df = df.drop(columns=['_c39'])

    # Standardize missing/placeholder tokens
    if 'collision_type' in df.columns:
        df['collision_type'] = df['collision_type'].replace('?', 'Not Applicable')
    if 'authorities_contacted' in df.columns:
        df['authorities_contacted'] = df['authorities_contacted'].fillna('None')
    if 'property_damage' in df.columns:
        df['property_damage'] = df['property_damage'].replace('?', 'Unknown')
    if 'police_report_available' in df.columns:
        df['police_report_available'] = df['police_report_available'].replace('?', 'Unknown')

    # Parse temporal dates
    if 'policy_bind_date' in df.columns:
        df['policy_bind_date'] = pd.to_datetime(df['policy_bind_date'], errors='coerce')
    if 'incident_date' in df.columns:
        df['incident_date'] = pd.to_datetime(df['incident_date'], errors='coerce')

    # Derived domain attributes
    if 'customer_tenure_years' not in df.columns and 'months_as_customer' in df.columns:
        df['customer_tenure_years'] = (pd.to_numeric(df['months_as_customer'], errors='coerce') / 12.0).round(2)

    if 'policy_age_days' not in df.columns and 'policy_bind_date' in df.columns and 'incident_date' in df.columns:
        df['policy_age_days'] = (df['incident_date'] - df['policy_bind_date']).dt.days

    if 'vehicle_age' not in df.columns and 'incident_date' in df.columns and 'auto_year' in df.columns:
        df['vehicle_age'] = df['incident_date'].dt.year - pd.to_numeric(df['auto_year'], errors='coerce')

    if 'incident_month' not in df.columns and 'incident_date' in df.columns:
        df['incident_month'] = df['incident_date'].dt.strftime('%B')

    if 'incident_day_of_week' not in df.columns and 'incident_date' in df.columns:
        df['incident_day_of_week'] = df['incident_date'].dt.day_name()

    if 'incident_period_of_day' not in df.columns and 'incident_hour_of_the_day' in df.columns:
        def categorize_period(h) -> str:
            try:
                hour = int(h)
                if 5 <= hour < 12:
                    return 'Morning (05-11)'
                elif 12 <= hour < 17:
                    return 'Afternoon (12-16)'
                elif 17 <= hour < 21:
                    return 'Evening (17-20)'
                else:
                    return 'Night (21-04)'
            except Exception:
                return 'Unknown'
        df['incident_period_of_day'] = df['incident_hour_of_the_day'].apply(categorize_period)

    for amt_col in ['total_claim_amount', 'injury_claim', 'property_claim', 'vehicle_claim']:
        if amt_col in df.columns:
            df[amt_col] = pd.to_numeric(df[amt_col], errors='coerce').fillna(0.0)

    if 'injury_claim_ratio' not in df.columns:
        safe_tot = df['total_claim_amount'].replace(0, np.nan)
        df['injury_claim_ratio'] = (df['injury_claim'] / safe_tot).fillna(0.0).round(4)
        df['property_claim_ratio'] = (df['property_claim'] / safe_tot).fillna(0.0).round(4)
        df['vehicle_claim_ratio'] = (df['vehicle_claim'] / safe_tot).fillna(0.0).round(4)

    if 'net_capital_gains' not in df.columns and 'capital-gains' in df.columns and 'capital-loss' in df.columns:
        cg = pd.to_numeric(df['capital-gains'], errors='coerce').fillna(0)
        cl = pd.to_numeric(df['capital-loss'], errors='coerce').fillna(0)
        df['net_capital_gains'] = cg - cl

    if 'fraud_reported_flag' not in df.columns and 'fraud_reported' in df.columns:
        df['fraud_reported_flag'] = (df['fraud_reported'].astype(str).str.upper().str.strip() == 'Y').astype(int)

    return df


def load_dataset() -> pd.DataFrame:
    """
    Loads active historical insurance claims dataset.
    Prioritizes an uploaded custom dataset if active, then cleaned master, then raw.
    """
    if os.path.exists(UPLOADED_DATA_FILE) and os.path.getsize(UPLOADED_DATA_FILE) > 0:
        try:
            df = pd.read_csv(UPLOADED_DATA_FILE)
            return preprocess_and_engineer_features(df)
        except Exception:
            pass

    cleaned_ready = os.path.exists(CLEANED_DATA_FILE) and os.path.getsize(CLEANED_DATA_FILE) > 0
    if cleaned_ready:
        df = pd.read_csv(CLEANED_DATA_FILE)
    elif os.path.exists(RAW_DATA_FILE):
        df = pd.read_csv(RAW_DATA_FILE)
    else:
        raise FileNotFoundError(f"Neither a valid '{CLEANED_DATA_FILE}' nor '{RAW_DATA_FILE}' could be found.")

    return preprocess_and_engineer_features(df)


def process_uploaded_bytes(file_bytes: bytes, filename: str) -> pd.DataFrame:
    """
    Parses uploaded CSV or Excel binary contents, validates schema against required columns,
    engineers features, and caches to UPLOADED_DATA_FILE.
    """
    filename_lower = filename.lower()
    if filename_lower.endswith(('.xlsx', '.xls')):
        df_raw = pd.read_excel(io.BytesIO(file_bytes), engine='openpyxl')
    else:
        try:
            df_raw = pd.read_csv(io.BytesIO(file_bytes), encoding='utf-8')
        except UnicodeDecodeError:
            df_raw = pd.read_csv(io.BytesIO(file_bytes), encoding='latin1')

    if '_c39' in df_raw.columns:
        df_raw = df_raw.drop(columns=['_c39'])

    is_valid, missing_cols = validate_dataset_columns(df_raw)
    if not is_valid:
        raise ValueError(
            f"Uploaded dataset is missing {len(missing_cols)} required columns: {', '.join(missing_cols)}"
        )

    processed_df = preprocess_and_engineer_features(df_raw)

    # Cache uploaded file locally for persistence across server requests
    try:
        os.makedirs(os.path.dirname(UPLOADED_DATA_FILE), exist_ok=True)
        processed_df.to_csv(UPLOADED_DATA_FILE, index=False)
    except Exception as e:
        print(f"Warning: Could not save uploaded dataset cache: {e}")

    return processed_df


def reset_custom_dataset() -> pd.DataFrame:
    """
    Removes the custom uploaded dataset cache and restores the default dataset.
    """
    if os.path.exists(UPLOADED_DATA_FILE):
        try:
            os.remove(UPLOADED_DATA_FILE)
        except Exception as e:
            print(f"Warning: Failed to delete custom dataset cache: {e}")

    return load_dataset()


def get_sample_dataset_bytes(format_type: str = "csv") -> Tuple[bytes, str, str]:
    """
    Returns bytes for the sample template dataset.
    format_type: 'csv' or 'excel'
    Returns (bytes, mime_type, filename)
    """
    format_lower = format_type.lower()
    if format_lower in ("excel", "xlsx"):
        if os.path.exists(SAMPLE_EXCEL_FILE):
            with open(SAMPLE_EXCEL_FILE, "rb") as f:
                content = f.read()
        else:
            df = pd.read_csv(RAW_DATA_FILE)
            if '_c39' in df.columns: df = df.drop(columns=['_c39'])
            buf = io.BytesIO()
            df.head(10).to_excel(buf, index=False, engine='openpyxl')
            content = buf.getvalue()
        return (
            content,
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            "sample_insurance_claims.xlsx"
        )
    else:
        if os.path.exists(SAMPLE_CSV_FILE):
            with open(SAMPLE_CSV_FILE, "rb") as f:
                content = f.read()
        else:
            df = pd.read_csv(RAW_DATA_FILE)
            if '_c39' in df.columns: df = df.drop(columns=['_c39'])
            buf = io.StringIO()
            df.head(10).to_csv(buf, index=False)
            content = buf.getvalue().encode('utf-8')
        return (
            content,
            "text/csv",
            "sample_insurance_claims.csv"
        )


def filter_dataset(
    df: pd.DataFrame,
    policy_state: Optional[str] = None,
    incident_severity: Optional[str] = None,
    fraud_status: Optional[str] = None,
    incident_month: Optional[str] = None
) -> pd.DataFrame:
    """
    Filters the dataset based on state, severity, fraud status, and month.
    """
    filtered = df.copy()

    if policy_state and policy_state != "All" and 'policy_state' in filtered.columns:
        filtered = filtered[filtered['policy_state'] == policy_state]

    if incident_severity and incident_severity != "All" and 'incident_severity' in filtered.columns:
        filtered = filtered[filtered['incident_severity'] == incident_severity]

    if fraud_status and fraud_status != "All" and 'fraud_reported' in filtered.columns:
        if fraud_status in ["Y", "Fraudulent"]:
            filtered = filtered[filtered['fraud_reported'] == 'Y']
        elif fraud_status in ["N", "Legitimate"]:
            filtered = filtered[filtered['fraud_reported'] == 'N']

    if incident_month and incident_month != "All" and 'incident_month' in filtered.columns:
        filtered = filtered[filtered['incident_month'] == incident_month]

    return filtered
