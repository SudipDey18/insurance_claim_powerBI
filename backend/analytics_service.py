"""
Analytics Service Module
Computes executive insurance KPIs, financial component allocations,
loss ratio estimates, temporal dynamics, and demographic risk cross-flows.
"""

from typing import Dict, Any, List
import pandas as pd
import numpy as np


def compute_executive_kpis(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Computes key performance indicators aligned with Section 6 of the internship scope.
    """
    total_claims = int(len(df))
    if total_claims == 0:
        return {
            "total_claims": 0,
            "total_incurred_amount": 0.0,
            "average_claim_amount": 0.0,
            "median_claim_amount": 0.0,
            "fraud_claims_count": 0,
            "fraud_rate_percentage": 0.0,
            "fraud_financial_exposure": 0.0,
            "loss_ratio_proxy_percentage": 0.0,
            "average_annual_premium": 0.0,
            "total_vehicle_claim": 0.0,
            "vehicle_share_percentage": 0.0,
            "total_injury_claim": 0.0,
            "injury_share_percentage": 0.0,
            "total_property_claim": 0.0,
            "property_share_percentage": 0.0
        }

    total_incurred = float(df['total_claim_amount'].sum())
    avg_claim = float(df['total_claim_amount'].mean())
    median_claim = float(df['total_claim_amount'].median())

    fraud_claims = int(df['fraud_reported_flag'].sum())
    fraud_rate = float((fraud_claims / total_claims) * 100.0)
    fraud_exposure = float(df[df['fraud_reported'] == 'Y']['total_claim_amount'].sum())

    total_vehicle = float(df['vehicle_claim'].sum())
    total_injury = float(df['injury_claim'].sum())
    total_property = float(df['property_claim'].sum())

    vehicle_share = (total_vehicle / total_incurred * 100.0) if total_incurred > 0 else 0.0
    injury_share = (total_injury / total_incurred * 100.0) if total_incurred > 0 else 0.0
    property_share = (total_property / total_incurred * 100.0) if total_incurred > 0 else 0.0

    avg_premium = float(df['policy_annual_premium'].mean())
    estimated_collected_premiums = float((df['policy_annual_premium'] * df['customer_tenure_years']).sum())
    loss_ratio_proxy = (total_incurred / estimated_collected_premiums * 100.0) if estimated_collected_premiums > 0 else 0.0

    return {
        "total_claims": total_claims,
        "total_incurred_amount": round(total_incurred, 2),
        "average_claim_amount": round(avg_claim, 2),
        "median_claim_amount": round(median_claim, 2),
        "fraud_claims_count": fraud_claims,
        "fraud_rate_percentage": round(fraud_rate, 2),
        "fraud_financial_exposure": round(fraud_exposure, 2),
        "loss_ratio_proxy_percentage": round(loss_ratio_proxy, 2),
        "average_annual_premium": round(avg_premium, 2),
        "total_vehicle_claim": round(total_vehicle, 2),
        "vehicle_share_percentage": round(vehicle_share, 2),
        "total_injury_claim": round(total_injury, 2),
        "injury_share_percentage": round(injury_share, 2),
        "total_property_claim": round(total_property, 2),
        "property_share_percentage": round(property_share, 2)
    }


def compute_component_breakdown(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Returns aggregated figures for claim components.
    """
    total = float(df['total_claim_amount'].sum())
    vehicle = float(df['vehicle_claim'].sum())
    injury = float(df['injury_claim'].sum())
    property_claim = float(df['property_claim'].sum())

    return {
        "total_claim_amount": round(total, 2),
        "components": [
            {
                "name": "Vehicle Claim",
                "amount": round(vehicle, 2),
                "percentage": round((vehicle / total * 100.0), 2) if total > 0 else 0.0
            },
            {
                "name": "Injury Claim",
                "amount": round(injury, 2),
                "percentage": round((injury / total * 100.0), 2) if total > 0 else 0.0
            },
            {
                "name": "Property Claim",
                "amount": round(property_claim, 2),
                "percentage": round((property_claim / total * 100.0), 2) if total > 0 else 0.0
            }
        ]
    }


def compute_temporal_trends(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Returns monthly and hourly distribution metrics.
    """
    # Monthly aggregation
    month_order = ["January", "February", "March"]
    monthly_data = []
    
    if 'incident_month' in df.columns:
        grp = df.groupby('incident_month').agg(
            claim_count=('total_claim_amount', 'count'),
            total_amount=('total_claim_amount', 'sum'),
            fraud_count=('fraud_reported_flag', 'sum')
        ).reset_index()

        grp['sort_order'] = grp['incident_month'].apply(lambda m: month_order.index(m) if m in month_order else 99)
        grp = grp.sort_values(by='sort_order')

        for _, row in grp.iterrows():
            monthly_data.append({
                "month": str(row['incident_month']),
                "claims_count": int(row['claim_count']),
                "total_incurred": round(float(row['total_amount']), 2),
                "fraud_count": int(row['fraud_count'])
            })

    # Hourly 24-hour timeline
    hourly_data = []
    if 'incident_hour_of_the_day' in df.columns:
        hourly_grp = df.groupby(['incident_hour_of_the_day', 'fraud_reported']).size().unstack(fill_value=0)
        for hour in range(24):
            legit = int(hourly_grp.loc[hour, 'N']) if (hour in hourly_grp.index and 'N' in hourly_grp.columns) else 0
            fraud = int(hourly_grp.loc[hour, 'Y']) if (hour in hourly_grp.index and 'Y' in hourly_grp.columns) else 0
            hourly_data.append({
                "hour": hour,
                "legitimate_count": legit,
                "fraud_count": fraud,
                "total_count": legit + fraud
            })

    return {
        "monthly_trends": monthly_data,
        "hourly_distribution": hourly_data
    }


def compute_severity_metrics(df: pd.DataFrame) -> List[Dict[str, Any]]:
    """
    Returns metrics segmented by incident severity tier.
    """
    if 'incident_severity' not in df.columns:
        return []

    agg = df.groupby('incident_severity').agg(
        volume=('total_claim_amount', 'count'),
        total_payout=('total_claim_amount', 'sum'),
        average_payout=('total_claim_amount', 'mean'),
        fraud_count=('fraud_reported_flag', 'sum')
    ).reset_index()

    records = []
    for _, row in agg.iterrows():
        vol = int(row['volume'])
        fraud_cnt = int(row['fraud_count'])
        rate = (fraud_cnt / vol * 100.0) if vol > 0 else 0.0
        records.append({
            "severity_tier": str(row['incident_severity']),
            "claim_count": vol,
            "total_payout": round(float(row['total_payout']), 2),
            "average_payout": round(float(row['average_payout']), 2),
            "fraud_count": fraud_cnt,
            "fraud_rate_percentage": round(rate, 2)
        })

    return sorted(records, key=lambda x: x['fraud_rate_percentage'], reverse=True)


def compute_correlation_matrix(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Calculates pairwise Pearson correlation for continuous numerical fields.
    """
    features = [
        'age', 'months_as_customer', 'customer_tenure_years',
        'policy_annual_premium', 'umbrella_limit', 'policy_age_days',
        'vehicle_age', 'total_claim_amount', 'injury_claim',
        'property_claim', 'vehicle_claim', 'fraud_reported_flag'
    ]
    valid_cols = [c for c in features if c in df.columns]
    corr_df = df[valid_cols].corr().round(3)

    return {
        "columns": valid_cols,
        "matrix": corr_df.values.tolist()
    }
