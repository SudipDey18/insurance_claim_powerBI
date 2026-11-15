"""
Data Service Module
Handles dataset ingestion, data quality auditing, hygiene transformation,
and domain feature derivation. No machine learning dependencies.
"""

import os
import numpy as np
import pandas as pd
from typing import Optional
from .config import CLEANED_DATA_FILE, RAW_DATA_FILE



def load_dataset() -> pd.DataFrame:
    """
    Loads raw or cleaned historical insurance claims dataset.
    Applies standardization and feature derivation if needed.
    """
    cleaned_ready = os.path.exists(CLEANED_DATA_FILE) and os.path.getsize(CLEANED_DATA_FILE) > 0
    if cleaned_ready:
        df = pd.read_csv(CLEANED_DATA_FILE)
    elif os.path.exists(RAW_DATA_FILE):
        df = pd.read_csv(RAW_DATA_FILE)
    else:
        raise FileNotFoundError(f"Neither a valid '{CLEANED_DATA_FILE}' nor '{RAW_DATA_FILE}' could be found.")

    # Drop delimiter artifact column
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
        df['policy_bind_date'] = pd.to_datetime(df['policy_bind_date'])
    if 'incident_date' in df.columns:
        df['incident_date'] = pd.to_datetime(df['incident_date'])

    # Derived domain attributes
    if 'customer_tenure_years' not in df.columns and 'months_as_customer' in df.columns:
        df['customer_tenure_years'] = (df['months_as_customer'] / 12.0).round(2)

    if 'policy_age_days' not in df.columns and 'policy_bind_date' in df.columns and 'incident_date' in df.columns:
        df['policy_age_days'] = (df['incident_date'] - df['policy_bind_date']).dt.days

    if 'vehicle_age' not in df.columns and 'incident_date' in df.columns and 'auto_year' in df.columns:
        df['vehicle_age'] = df['incident_date'].dt.year - df['auto_year']

    if 'incident_month' not in df.columns and 'incident_date' in df.columns:
        df['incident_month'] = df['incident_date'].dt.strftime('%B')

    if 'incident_day_of_week' not in df.columns and 'incident_date' in df.columns:
        df['incident_day_of_week'] = df['incident_date'].dt.day_name()

    if 'incident_period_of_day' not in df.columns and 'incident_hour_of_the_day' in df.columns:
        def categorize_period(h: int) -> str:
            if 5 <= h < 12:
                return 'Morning (05-11)'
            elif 12 <= h < 17:
                return 'Afternoon (12-16)'
            elif 17 <= h < 21:
                return 'Evening (17-20)'
            else:
                return 'Night (21-04)'
        df['incident_period_of_day'] = df['incident_hour_of_the_day'].apply(categorize_period)

    if 'injury_claim_ratio' not in df.columns:
        safe_tot = df['total_claim_amount'].replace(0, np.nan)
        df['injury_claim_ratio'] = (df['injury_claim'] / safe_tot).fillna(0.0).round(4)
        df['property_claim_ratio'] = (df['property_claim'] / safe_tot).fillna(0.0).round(4)
        df['vehicle_claim_ratio'] = (df['vehicle_claim'] / safe_tot).fillna(0.0).round(4)

    if 'net_capital_gains' not in df.columns:
        df['net_capital_gains'] = df['capital-gains'] - df['capital-loss']

    if 'fraud_reported_flag' not in df.columns and 'fraud_reported' in df.columns:
        df['fraud_reported_flag'] = (df['fraud_reported'] == 'Y').astype(int)

    return df


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

    if policy_state and policy_state != "All":
        filtered = filtered[filtered['policy_state'] == policy_state]

    if incident_severity and incident_severity != "All":
        filtered = filtered[filtered['incident_severity'] == incident_severity]

    if fraud_status and fraud_status != "All":
        if fraud_status in ["Y", "Fraudulent"]:
            filtered = filtered[filtered['fraud_reported'] == 'Y']
        elif fraud_status in ["N", "Legitimate"]:
            filtered = filtered[filtered['fraud_reported'] == 'N']

    if incident_month and incident_month != "All":
        filtered = filtered[filtered['incident_month'] == incident_month]

    return filtered
