"""
Audit Service Module
Implements discrepancy auditing, chronological consistency validation,
rapid inception monitoring, and IQR statistical outlier detection (Module 6).
"""

from typing import Dict, Any, List
import pandas as pd
import numpy as np


def run_full_anomaly_audit(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Executes all data quality, timeline, and risk anomaly checks.
    """
    total_records = len(df)

    # 1. Component Additivity Check
    component_diff = (df['total_claim_amount'] - (df['injury_claim'] + df['property_claim'] + df['vehicle_claim'])).abs()
    mismatches = df[component_diff > 0]
    additivity_pass = (len(mismatches) == 0)

    # 2. Chronological Timeline Inversion Check
    timeline_inversions = df[df['policy_age_days'] < 0]
    inversion_records = []
    for _, row in timeline_inversions.iterrows():
        inversion_records.append({
            "policy_number": int(row['policy_number']),
            "policy_bind_date": str(pd.to_datetime(row['policy_bind_date']).date()),
            "incident_date": str(pd.to_datetime(row['incident_date']).date()),
            "policy_age_days": int(row['policy_age_days']),
            "total_claim_amount": float(row['total_claim_amount']),
            "fraud_reported": str(row['fraud_reported'])
        })

    # 3. Rapid Claim Inception (0 - 30 days from policy binding)
    rapid_claims = df[(df['policy_age_days'] >= 0) & (df['policy_age_days'] <= 30)]
    rapid_count = len(rapid_claims)
    rapid_fraud_count = int(rapid_claims['fraud_reported_flag'].sum()) if rapid_count > 0 else 0
    rapid_fraud_rate = (rapid_fraud_count / rapid_count * 100.0) if rapid_count > 0 else 0.0
    portfolio_baseline_fraud_rate = (df['fraud_reported_flag'].mean() * 100.0) if total_records > 0 else 0.0

    # 4. Statistical Outliers via IQR Method
    outlier_metrics = {}
    for col_name, label in [('total_claim_amount', 'Total Claim Amount'), ('policy_annual_premium', 'Annual Premium')]:
        q1 = float(df[col_name].quantile(0.25))
        q3 = float(df[col_name].quantile(0.75))
        iqr = q3 - q1
        lower_bound = q1 - 1.5 * iqr
        upper_bound = q3 + 1.5 * iqr
        outlier_rows = df[(df[col_name] < lower_bound) | (df[col_name] > upper_bound)]

        outlier_metrics[col_name] = {
            "label": label,
            "q1": round(q1, 2),
            "median": round(float(df[col_name].median()), 2),
            "q3": round(q3, 2),
            "iqr": round(iqr, 2),
            "lower_bound": round(lower_bound, 2),
            "upper_bound": round(upper_bound, 2),
            "outlier_count": int(len(outlier_rows)),
            "outlier_percentage": round((len(outlier_rows) / total_records * 100.0), 2) if total_records > 0 else 0.0
        }

    return {
        "summary": {
            "total_claims_audited": total_records,
            "additivity_audit_passed": additivity_pass,
            "chronological_inversions_found": len(timeline_inversions),
            "rapid_claims_count": rapid_count
        },
        "component_additivity": {
            "status": "PASS" if additivity_pass else "FAIL",
            "mismatches_count": len(mismatches),
            "rule": "total_claim_amount == injury_claim + property_claim + vehicle_claim"
        },
        "chronological_consistency": {
            "status": "ALERT" if len(timeline_inversions) > 0 else "PASS",
            "inversion_count": len(timeline_inversions),
            "rule": "incident_date >= policy_bind_date (policy_age_days >= 0)",
            "anomalous_records": inversion_records
        },
        "rapid_claim_inception": {
            "window_days": 30,
            "rapid_claims_count": rapid_count,
            "rapid_claim_fraud_rate_percentage": round(rapid_fraud_rate, 2),
            "portfolio_baseline_fraud_rate_percentage": round(portfolio_baseline_fraud_rate, 2),
            "total_rapid_exposure_amount": round(float(rapid_claims['total_claim_amount'].sum()), 2)
        },
        "statistical_outliers_iqr": outlier_metrics
    }
