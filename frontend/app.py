"""
Claims Analytics Frontend Application
Streamlit user interface with minimalist design, clean top navbar,
and direct integration with Streamlit domain services.
Zero emojis, zero stickers, and zero machine learning dependencies.
"""

import os
import sys
import pandas as pd
import streamlit as st

# Ensure the project root is on the path so `backend` and `frontend` packages resolve
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Configure Matplotlib writable cache for headless/cloud environments
os.environ.setdefault("MPLCONFIGDIR", os.path.join(project_root, ".matplotlib_cache"))
os.makedirs(os.environ["MPLCONFIGDIR"], exist_ok=True)

from frontend.styles import get_minimal_css
from frontend.api_client import (
    check_backend_status,
    fetch_filter_options,
    fetch_kpis,
    fetch_breakdown,
    fetch_trends,
    fetch_severities,
    fetch_correlation,
    fetch_audits,
    get_client_ip,
    record_viewer,
    fetch_viewer_stats,
    get_dataset_info,
    _get_local_df
)
from frontend.views import (
    render_overview_view,
    render_claims_analysis_view,
    render_audits_view,
    render_powerbi_view,
    render_strategy_view,
    render_upload_dataset_view,
    plot_correlation_matrix,
    plot_claim_distributions,
    compute_claim_financial_summary
)


def main():
    """Main application loop and view controller."""
    # Page Configuration
    st.set_page_config(
        page_title="Claims Analytics & Intelligence System",
        layout="wide",
        initial_sidebar_state="collapsed"
    )

    # Apply Minimalist Stylesheet
    st.markdown(get_minimal_css(), unsafe_allow_html=True)

    # Check Engine Status
    is_backend_online, backend_meta = check_backend_status()

    # Resolve Client IP and track viewer
    client_ip = get_client_ip()

    # Record once per session; update if client IP changes
    if "session_viewer_logged" not in st.session_state or st.session_state.get("client_ip") != client_ip:
        viewer_stats = record_viewer(client_ip)
        st.session_state["session_viewer_logged"] = True
        st.session_state["client_ip"] = client_ip
        st.session_state["viewer_stats"] = viewer_stats
    else:
        viewer_stats = fetch_viewer_stats()
        st.session_state["viewer_stats"] = viewer_stats

    total_viewers = viewer_stats.get("total_viewers", 1)

    # Active Dataset Information
    dataset_info = get_dataset_info()
    ds_badge_text = f"{dataset_info['dataset_name']} ({dataset_info['record_count']:,} records)"

    # Top Navbar Header
    status_badge_html = '<span class="status-badge badge-online">Engine: Streamlit Core</span>'

    st.markdown(f"""
    <div class="navbar-container">
        <div>
            <div class="navbar-brand">Claims Intelligence Analytics System</div>
            <div class="navbar-subtitle">B.Tech Internship Project: End-to-End Analytics, Audits & Power BI Readiness</div>
        </div>
        <div style="display: flex; gap: 8px; align-items: center;">
            <span class="status-badge badge-dataset" title="Currently active dataset">{ds_badge_text}</span>
            <span class="status-badge badge-viewers" title="Total unique dashboard viewers">Total Viewers: {total_viewers}</span>
            {status_badge_html}
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Top Navigation Bar Menu
    nav_tabs = [
        "Overview",
        "Claims Analysis",
        "Operational Audits",
        "Power BI & DAX",
        "Strategic Insights",
        "Upload Dataset"
    ]

    selected_view = st.radio(
        "Navigation Menu",
        nav_tabs,
        index=0,
        horizontal=True,
        label_visibility="collapsed"
    )

    st.markdown("<hr style='margin-top: 4px; margin-bottom: 16px; border: 0; border-top: 1px solid #E2E8F0;'>", unsafe_allow_html=True)

    # Minimal Inline Filter Bar (Active for Overview and Claims Analysis)
    if selected_view in ["Overview", "Claims Analysis"]:
        filters_data = fetch_filter_options()

        with st.expander("Filter Portfolio Dimensions", expanded=False):
            f_col1, f_col2, f_col3, f_col4 = st.columns(4)
            with f_col1:
                sel_state = st.selectbox("Policy Issuance State", filters_data["policy_states"], index=0)
            with f_col2:
                sel_severity = st.selectbox("Incident Severity Tier", filters_data["incident_severities"], index=0)
            with f_col3:
                sel_fraud = st.selectbox("Claim Outcome / Status", filters_data["fraud_statuses"], index=0)
            with f_col4:
                sel_month = st.selectbox("Incident Month", filters_data["incident_months"], index=0)
    else:
        sel_state = "All"
        sel_severity = "All"
        sel_fraud = "All"
        sel_month = "All"

    # Route to active view
    if selected_view == "Overview":
        kpi_res = fetch_kpis(sel_state, sel_severity, sel_fraud, sel_month)
        breakdown_res = fetch_breakdown(sel_state, sel_severity, sel_fraud, sel_month)
        trends_res = fetch_trends(sel_state, sel_severity, sel_fraud)
        render_overview_view(kpi_res, breakdown_res, trends_res)

    elif selected_view == "Claims Analysis":
        severities_res = fetch_severities(sel_state, sel_month)
        trends_res = fetch_trends(sel_state, sel_severity, sel_fraud)
        corr_res = fetch_correlation()
        df_sample = _get_local_df()
        render_claims_analysis_view(severities_res, trends_res, corr_res, df=df_sample)

    elif selected_view == "Operational Audits":
        audits_res = fetch_audits()
        render_audits_view(audits_res)

    elif selected_view == "Power BI & DAX":
        df_sample = _get_local_df()
        render_powerbi_view(df_sample)

    elif selected_view == "Strategic Insights":
        render_strategy_view()

    elif selected_view == "Upload Dataset":
        render_upload_dataset_view(dataset_info)


if __name__ == "__main__":
    main()
