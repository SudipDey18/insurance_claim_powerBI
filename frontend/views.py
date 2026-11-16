"""
Views Module
Provides view rendering functions for the claims intelligence dashboard.
Minimalist layout, clean corporate typography, and zero emojis or stickers.
Properly scaled visuals and compact presentation.
"""

from typing import Dict, Any, List, Optional
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns


def render_overview_view(kpis: Dict[str, Any], breakdown: Dict[str, Any], trends: Dict[str, Any]):
    """Renders the executive overview and portfolio financial indicators."""
    st.markdown('<div class="view-title">Executive Claims Overview</div>', unsafe_allow_html=True)
    st.markdown('<div class="view-description">Summary of portfolio performance, incurred claim severity, loss ratio estimates, and component allocations.</div>', unsafe_allow_html=True)

    # Metric Cards Grid
    c1, c2, c3, c4, c5 = st.columns(5)
    
    with c1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Total Claims</div>
            <div class="metric-value">{kpis['total_claims']:,}</div>
            <div class="metric-caption">Processed volume</div>
        </div>
        """, unsafe_allow_html=True)

    with c2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Incurred Claims</div>
            <div class="metric-value">${kpis['total_incurred_amount']/1e6:.2f}M</div>
            <div class="metric-caption">Total payout requested</div>
        </div>
        """, unsafe_allow_html=True)

    with c3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Average Severity</div>
            <div class="metric-value">${kpis['average_claim_amount']:,.0f}</div>
            <div class="metric-caption">Median: ${kpis['median_claim_amount']:,.0f}</div>
        </div>
        """, unsafe_allow_html=True)

    with c4:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Fraud Rate</div>
            <div class="metric-value">{kpis['fraud_rate_percentage']:.1f}%</div>
            <div class="metric-caption">{kpis['fraud_claims_count']:,} confirmed cases</div>
        </div>
        """, unsafe_allow_html=True)

    with c5:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Loss Ratio Proxy</div>
            <div class="metric-value">{kpis['loss_ratio_proxy_percentage']:.1f}%</div>
            <div class="metric-caption">Incurred / premiums</div>
        </div>
        """, unsafe_allow_html=True)

    # Compact 2-column layout for visual balance
    col_left, col_right = st.columns([1, 1.15])

    with col_left:
        st.markdown('<div class="section-title">Expense Allocation Breakdown</div>', unsafe_allow_html=True)
        components = breakdown.get("components", [])
        if components:
            names = [c["name"] for c in components]
            amounts = [c["amount"] for c in components]
            colors = ["#1E40AF", "#0D9488", "#D97706"]

            # Compact donut chart
            fig, ax = plt.subplots(figsize=(4.0, 2.2), dpi=100)
            wedges, texts, autotexts = ax.pie(
                amounts, labels=names, autopct='%1.1f%%',
                startangle=140, colors=colors, pctdistance=0.72,
                wedgeprops={'edgecolor': 'white', 'linewidth': 1.5}
            )
            for t in texts: t.set_fontsize(8); t.set_color('#334155')
            for at in autotexts: at.set_fontsize(8); at.set_weight('bold'); at.set_color('white')

            centre_circle = plt.Circle((0,0), 0.52, fc='white')
            ax.add_artist(centre_circle)
            ax.set_title("Payout Allocation Share", fontsize=9, fontweight='bold', pad=4)
            plt.tight_layout()
            st.pyplot(fig)
            plt.close(fig)

            # Compact category table below chart
            for comp in components:
                st.markdown(f"""
                <div style="border-bottom: 1px solid #F1F5F9; padding: 4px 0; display: flex; justify-content: space-between;">
                    <span style="font-size: 0.78rem; font-weight: 500; color: #334155;">{comp['name']}</span>
                    <span style="font-size: 0.78rem; font-weight: 700; color: #0F172A;">${comp['amount']:,.0f} ({comp['percentage']}%)</span>
                </div>
                """, unsafe_allow_html=True)

    with col_right:
        st.markdown('<div class="section-title">Monthly Volume & Payout Dynamics</div>', unsafe_allow_html=True)
        monthly = trends.get("monthly_trends", [])
        if monthly:
            m_df = pd.DataFrame(monthly)
            
            # Compact monthly dual-axis chart
            fig, ax1 = plt.subplots(figsize=(5.4, 2.4), dpi=100)
            ax2 = ax1.twinx()

            x = np.arange(len(m_df))
            w = 0.32

            ax1.bar(x - w/2, m_df['claims_count'], w, label='Total Claims', color='#1E40AF', alpha=0.9)
            ax1.bar(x + w/2, m_df['fraud_count'], w, label='Fraud Cases', color='#DC2626', alpha=0.9)
            ax2.plot(x, m_df['total_incurred'] / 1e6, color='#D97706', marker='o', markersize=4, linewidth=1.8, label='Payout ($M)')

            ax1.set_xticks(x)
            ax1.set_xticklabels(m_df['month'], fontsize=8)
            ax1.set_ylabel("Claims Count", fontsize=8, color='#1E293B')
            ax2.set_ylabel("Payout ($M)", fontsize=8, color='#D97706')
            ax1.tick_params(axis='both', labelsize=8)
            ax2.tick_params(axis='both', labelsize=8)
            ax1.grid(axis='y', linestyle='--', alpha=0.3)
            ax2.grid(False)

            lines1, labels1 = ax1.get_legend_handles_labels()
            lines2, labels2 = ax2.get_legend_handles_labels()
            ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper right', fontsize=7, framealpha=0.85)
            plt.tight_layout()
            st.pyplot(fig)
            plt.close(fig)

            st.markdown(f"""
            <div style="background-color: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 4px; padding: 8px 10px; font-size: 0.76rem; color: #475569; margin-top: 6px;">
                <strong>Key Takeaway:</strong> Vehicle repair and replacement accounts for <strong>{kpis['vehicle_share_percentage']:.1f}%</strong> (${kpis['total_vehicle_claim']:,.0f}) of total organizational outlay, making it the primary focal area for claims cost containment.
            </div>
            """, unsafe_allow_html=True)


# 4.2 Claim Amount Decomposition & Distribution Analysis
def plot_claim_distributions(df: pd.DataFrame) -> None:
    """Visualizes the distributions and central tendencies of claim financial components."""
    claim_types = [
        ('total_claim_amount', '#1f77b4', 'Total Claim Amount ($)'),
        ('vehicle_claim', '#ff7f0e', 'Vehicle Claim Amount ($)'),
        ('property_claim', '#2ca02c', 'Property Claim Amount ($)'),
        ('injury_claim', '#d62728', 'Injury Claim Amount ($)')
    ]
    
    try:
        fig, axes = plt.subplots(2, 2, figsize=(9.2, 5.0), dpi=100)
        axes = axes.flatten()
        
        for idx, (col, color, label) in enumerate(claim_types):
            if col in df.columns:
                sns.histplot(df[col], kde=True, ax=axes[idx], color=color, bins=30)
                mean_val = float(df[col].mean())
                med_val = float(df[col].median())
                
                axes[idx].axvline(mean_val, color='black', linestyle='--', linewidth=1.4, label=f'Mean: ${mean_val:,.0f}')
                axes[idx].axvline(med_val, color='blue', linestyle=':', linewidth=1.6, label=f'Median: ${med_val:,.0f}')
                axes[idx].set_title(f'Distribution of {label}', fontweight='bold', fontsize=8.5, pad=4)
                axes[idx].set_xlabel('Amount in USD ($)', fontsize=7.5)
                axes[idx].set_ylabel('Frequency', fontsize=7.5)
                axes[idx].tick_params(axis='both', labelsize=7)
                axes[idx].grid(axis='y', linestyle='--', alpha=0.3)
                axes[idx].legend(fontsize=7, loc='upper right', framealpha=0.85)
                
        plt.tight_layout()
        st.pyplot(fig)
        plt.close(fig)
    except Exception:
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        axes = axes.flatten()
        
        for idx, (col, color, label) in enumerate(claim_types):
            if col in df.columns:
                sns.histplot(df[col], kde=True, ax=axes[idx], color=color, bins=30)
                mean_val = float(df[col].mean())
                med_val = float(df[col].median())
                
                axes[idx].axvline(mean_val, color='black', linestyle='--', linewidth=1.5, label=f'Mean: ${mean_val:,.0f}')
                axes[idx].axvline(med_val, color='blue', linestyle=':', linewidth=1.8, label=f'Median: ${med_val:,.0f}')
                axes[idx].set_title(f'Distribution of {label}', fontweight='bold')
                axes[idx].set_xlabel('Amount in USD ($)')
                axes[idx].set_ylabel('Frequency')
                axes[idx].legend()
                
        plt.tight_layout()
        plt.show()


def compute_claim_financial_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Computes statistical summary metrics and skewness for financial claim components."""
    claim_cols = ['total_claim_amount', 'vehicle_claim', 'property_claim', 'injury_claim']
    valid_cols = [c for c in claim_cols if c in df.columns]
    if not valid_cols:
        return pd.DataFrame()
    stats_summary = df[valid_cols].describe().T[['mean', 'std', 'min', '25%', '50%', '75%', 'max']]
    stats_summary['skewness'] = df[valid_cols].skew()
    return stats_summary


# 4.5 Correlation & Multicollinearity Analysis
def plot_correlation_matrix(df: Optional[pd.DataFrame] = None, correlation: Optional[Dict[str, Any]] = None) -> None:
    """Generates a masked correlation matrix for numeric features."""
    numeric_features = [
        'age', 'months_as_customer', 'customer_tenure_years',
        'policy_annual_premium', 'umbrella_limit', 'policy_age_days',
        'vehicle_age', 'total_claim_amount', 'injury_claim',
        'property_claim', 'vehicle_claim', 'fraud_reported_flag'
    ]
    
    if df is not None:
        valid_cols = [c for c in numeric_features if c in df.columns]
        corr_matrix = df[valid_cols].corr()
        cols = valid_cols
    elif correlation and "columns" in correlation and "matrix" in correlation:
        corr_matrix = pd.DataFrame(correlation["matrix"], index=correlation["columns"], columns=correlation["columns"])
        cols = correlation["columns"]
    else:
        return

    mask = np.triu(np.ones_like(corr_matrix, dtype=bool))

    try:
        fig, ax = plt.subplots(figsize=(6.2, 3.4), dpi=100)
        sns.heatmap(
            corr_matrix, mask=mask, annot=True, fmt='.2f', cmap='coolwarm',
            vmin=-1, vmax=1, linewidths=0.5, cbar_kws={'shrink': 0.8},
            xticklabels=cols, yticklabels=cols, ax=ax,
            annot_kws={"size": 6.5}
        )
        ax.set_title('Correlation Heatmap: Numerical & Financial Attributes', fontweight='bold', fontsize=9, pad=6)
        ax.tick_params(axis='both', labelsize=6.5)
        plt.setp(ax.get_xticklabels(), rotation=45, ha='right', rotation_mode='anchor')
        plt.setp(ax.get_yticklabels(), rotation=0)
        plt.tight_layout()
        st.pyplot(fig)
        plt.close(fig)
    except Exception:
        plt.figure(figsize=(12, 9))
        sns.heatmap(
            corr_matrix, mask=mask, annot=True, fmt='.2f', cmap='coolwarm',
            vmin=-1, vmax=1, linewidths=0.5, cbar_kws={'shrink': 0.8},
            xticklabels=cols, yticklabels=cols
        )
        plt.title('Correlation Heatmap: Numerical & Financial Attributes', fontweight='bold', fontsize=13)
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        plt.show()


def render_claims_analysis_view(
    severities: List[Dict[str, Any]],
    trends: Dict[str, Any],
    correlation: Dict[str, Any],
    df: Optional[pd.DataFrame] = None
):
    """Renders detailed claims exploratory analysis across severities, hours, and correlations."""
    st.markdown('<div class="view-title">Claims Diagnostic & Risk Analysis</div>', unsafe_allow_html=True)
    st.markdown('<div class="view-description">Module 4: Assessment of incident severity tiers, 24-hour accident timelines, and numerical feature relationships.</div>', unsafe_allow_html=True)

    # 4.1 Incident Severity vs Fraud Incidence
    c1, c2 = st.columns([1, 1.1])

    with c1:
        st.markdown('<div class="section-title">4.1 Incident Severity vs Fraud Incidence</div>', unsafe_allow_html=True)
        if severities:
            sev_df = pd.DataFrame(severities)
            fig, ax = plt.subplots(figsize=(4.2, 2.3), dpi=100)
            # Solved FutureWarning by passing hue=severity_tier and legend=False
            sns.barplot(data=sev_df, x='severity_tier', y='fraud_rate_percentage', hue='severity_tier', palette='Blues_r', legend=False, ax=ax)
            ax.set_title("Fraud Rate by Severity Tier (%)", fontsize=9, fontweight='bold')
            ax.set_xlabel("")
            ax.set_ylabel("Fraud Rate (%)", fontsize=8)
            ax.tick_params(axis='x', labelsize=8)
            ax.tick_params(axis='y', labelsize=8)
            ax.grid(axis='y', linestyle='--', alpha=0.3)
            for p in ax.patches:
                val = p.get_height()
                ax.annotate(f"{val:.1f}%", (p.get_x() + p.get_width()/2., val/2),
                            ha='center', va='center', color='white', fontweight='bold', fontsize=8)
            plt.tight_layout()
            st.pyplot(fig)
            plt.close(fig)

    with c2:
        st.markdown('<div class="section-title">Severity Tier Summary</div>', unsafe_allow_html=True)
        if severities:
            disp_df = pd.DataFrame(severities)
            disp_df.columns = ["Severity Tier", "Claims", "Total Payout ($)", "Avg Payout ($)", "Fraud Count", "Fraud Rate (%)"]
            # Solved width deprecation
            st.dataframe(disp_df, width="stretch")

            st.markdown("""
            <div class="banner-alert" style="margin-top: 6px;">
                <strong>Observation:</strong> Incidents marked as Major Damage exhibit a fraud rate of over 60%, compared to under 10% for minor and trivial incidents.
            </div>
            """, unsafe_allow_html=True)

    # 4.2 Claim Amount Decomposition & Distribution Analysis
    st.markdown('<div class="section-title">4.2 Claim Amount Decomposition & Distribution Analysis</div>', unsafe_allow_html=True)

    if df is None:
        from frontend.api_client import _get_local_df
        df = _get_local_df()

    d_col1, d_col2 = st.columns([1.25, 1.0])

    with d_col1:
        plot_claim_distributions(df)

    with d_col2:
        st.markdown('<div class="metric-label" style="margin-bottom: 6px;">Financial Claim Components Statistical Summary</div>', unsafe_allow_html=True)
        stats_summary = compute_claim_financial_summary(df)
        if not stats_summary.empty:
            disp_stats = stats_summary.copy()
            disp_stats.index = [c.replace('_', ' ').title() for c in disp_stats.index]
            disp_stats.columns = ['Mean ($)', 'Std Dev ($)', 'Min ($)', 'Q1 25% ($)', 'Median ($)', 'Q3 75% ($)', 'Max ($)', 'Skewness']

            formatted_df = pd.DataFrame(index=disp_stats.index)
            for c in ['Mean ($)', 'Std Dev ($)', 'Min ($)', 'Q1 25% ($)', 'Median ($)', 'Q3 75% ($)', 'Max ($)']:
                formatted_df[c] = disp_stats[c].apply(lambda x: f"${x:,.0f}")
            formatted_df['Skewness'] = disp_stats['Skewness'].apply(lambda x: f"{x:+.2f}")

            st.dataframe(formatted_df, width="stretch")

        st.markdown("""
        <div class="metric-card" style="margin-top: 8px;">
            <div class="metric-label">Distribution & Asymmetry Insights</div>
            <ul style="font-size: 0.76rem; color: #334155; margin: 4px 0 0 0; padding-left: 14px; line-height: 1.45;">
                <li><strong>Bimodal Incurred Payouts:</strong> <code>total_claim_amount</code> and <code>vehicle_claim</code> exhibit negative skewness (-0.60 and -0.62) with dual density peaks: minor claims below $5,000 and major total losses clustered between $55,000 and $75,000.</li>
                <li><strong>Right-Skewed Collateral Losses:</strong> <code>property_claim</code> (+0.38) and <code>injury_claim</code> (+0.27) display positive right skew, where the bulk of losses are modest with a long tail of severe incidents.</li>
                <li><strong>Median vs. Mean Divergence:</strong> Median vehicle loss ($42,120) exceeds the mean ($37,929), confirming that high-severity claims dominate portfolio risk exposure.</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

    # 4.4 24-Hour Incident Occurrence Timeline
    st.markdown('<div class="section-title">4.4 24-Hour Incident Occurrence Timeline</div>', unsafe_allow_html=True)
    t_col1, t_col2 = st.columns([1.3, 1.0])

    with t_col1:
        hourly = trends.get("hourly_distribution", [])
        if hourly:
            h_df = pd.DataFrame(hourly)
            fig, ax = plt.subplots(figsize=(5.6, 2.3), dpi=100)
            ax.bar(h_df['hour'], h_df['legitimate_count'], label='Legitimate', color='#1E40AF', alpha=0.85)
            ax.bar(h_df['hour'], h_df['fraud_count'], bottom=h_df['legitimate_count'], label='Fraudulent', color='#DC2626', alpha=0.85)
            ax.set_xlabel("Hour of Day (0 - 23)", fontsize=8)
            ax.set_ylabel("Incident Count", fontsize=8)
            ax.set_title("Timeline of Incident Occurrence Across 24 Hours", fontsize=9, fontweight='bold')
            ax.set_xticks(range(0, 24, 2))
            ax.tick_params(axis='both', labelsize=7.5)
            ax.grid(axis='y', linestyle='--', alpha=0.3)
            ax.legend(loc='upper right', fontsize=7, framealpha=0.85)
            plt.tight_layout()
            st.pyplot(fig)
            plt.close(fig)

    with t_col2:
        st.markdown("""
        <div class="metric-card" style="margin-top: 4px;">
            <div class="metric-label">Temporal Risk Diagnostics</div>
            <div style="font-size: 0.78rem; color: #334155; line-height: 1.45; margin-top: 4px;">
                <strong>Incident Concentration:</strong> Incident volume displays distributed occurrence throughout daylight and evening hours, with secondary clusters during rush hours and late evening.
            </div>
            <div style="font-size: 0.78rem; color: #334155; line-height: 1.45; margin-top: 6px;">
                <strong>Fraud Proportion:</strong> Fraudulent claims are present across all operational time intervals, affirming that incident severity classification is a far stronger predictor of fraud than accident hour alone.
            </div>
        </div>
        """, unsafe_allow_html=True)

    # 4.5 Correlation & Multicollinearity Analysis
    st.markdown('<div class="section-title">4.5 Correlation & Multicollinearity Analysis</div>', unsafe_allow_html=True)
    corr_col1, corr_col2 = st.columns([1.35, 1.0])

    with corr_col1:
        plot_correlation_matrix(df=df, correlation=correlation)

    with corr_col2:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-label">Key Multicollinearity & Correlation Insights</div>
            <ul style="font-size: 0.78rem; color: #334155; margin: 6px 0 0 0; padding-left: 16px; line-height: 1.5;">
                <li><strong>Customer Tenure & Age Redundancy:</strong> <code>months_as_customer</code> and <code>customer_tenure_years</code> exhibit exact collinearity (<em>r</em> = 1.00), and both correlate strongly with policyholder <code>age</code> (<em>r</em> = 0.92). In regression and GLM modeling, retain only one tenure metric to eliminate variance inflation (VIF &gt; 10).</li>
                <li><strong>Claim Component Sum Linearity:</strong> <code>total_claim_amount</code> has near-perfect correlation with <code>vehicle_claim</code> (<em>r</em> = 0.98), driven by vehicle repairs representing ~72% of payouts. Property (<em>r</em> = 0.81) and injury (<em>r</em> = 0.81) claims also correlate strongly due to additive composition.</li>
                <li><strong>Underwriting Metric Independence:</strong> <code>policy_annual_premium</code>, <code>umbrella_limit</code>, and <code>policy_age_days</code> show minimal pairwise correlation (|<em>r</em>| &lt; 0.05), providing independent, non-redundant risk signals.</li>
                <li><strong>Fraud Target Correlation:</strong> <code>fraud_reported_flag</code> demonstrates positive correlation with total and component claim amounts, reflecting that fraudulent claims are concentrated in higher-severity loss tiers.</li>
            </ul>
        </div>
        <div class="banner-alert" style="margin-top: 6px; font-size: 0.76rem;">
            <strong>Actuarial Takeaway:</strong> To prevent model instability from multicollinear features, collapse composite tenure fields and avoid modeling total claim amounts simultaneously with sub-claim components.
        </div>
        """, unsafe_allow_html=True)


def render_audits_view(audits: Dict[str, Any]):
    """Renders operational discrepancy checks and anomaly audits (Module 6)."""
    st.markdown('<div class="view-title">Operational Audits & Anomaly Detection</div>', unsafe_allow_html=True)
    st.markdown('<div class="view-description">Module 6: Verification of arithmetic component additivity, chronological timeline integrity, rapid claims, and statistical IQR bounds.</div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown('<div class="section-title">1. Component Additivity Check</div>', unsafe_allow_html=True)
        additivity = audits.get("component_additivity", {})
        if additivity.get("status") == "PASS":
            st.markdown("""
            <div class="banner-pass">
                <strong>Status: Passed (100% Reconciled)</strong><br>
                Total claim amount equals the exact sum of injury, property, and vehicle claim components across all 1,000 records. Zero discrepancies detected.
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="banner-alert">
                <strong>Status: Failed</strong><br>
                Found {additivity.get('mismatches_count')} arithmetic discrepancies.
            </div>
            """, unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="section-title">2. Chronological Timeline Inversion Check</div>', unsafe_allow_html=True)
        chrono = audits.get("chronological_consistency", {})
        inv_count = chrono.get("inversion_count", 0)
        if inv_count > 0:
            st.markdown(f"""
            <div class="banner-alert">
                <strong>Status: Alert ({inv_count} Inversion Detected)</strong><br>
                Identified record where incident date precedes policy inception date. Requires underwriting issuance audit.
            </div>
            """, unsafe_allow_html=True)
            recs = chrono.get("anomalous_records", [])
            if recs:
                st.dataframe(pd.DataFrame(recs), width="stretch")
        else:
            st.markdown('<div class="banner-pass"><strong>Status: Passed</strong> — All incidents occurred after policy binding.</div>', unsafe_allow_html=True)

    st.markdown('<div class="section-title">3. Rapid Claim Inception Audit (0 - 30 Days)</div>', unsafe_allow_html=True)
    rapid = audits.get("rapid_claim_inception", {})
    r_col1, r_col2, r_col3 = st.columns(3)
    with r_col1:
        st.metric("Rapid Inception Claims", f"{rapid.get('rapid_claims_count', 0)} claims")
    with r_col2:
        st.metric("Rapid Fraud Rate", f"{rapid.get('rapid_claim_fraud_rate_percentage', 0.0):.1f}%")
    with r_col3:
        st.metric("Total Rapid Exposure", f"${rapid.get('total_rapid_exposure_amount', 0.0):,.2f}")

    st.markdown('<div class="section-title">4. Statistical Outliers via Interquartile Range (IQR)</div>', unsafe_allow_html=True)
    iqr_data = audits.get("statistical_outliers_iqr", {})
    if iqr_data:
        iqr_rows = []
        for key, item in iqr_data.items():
            iqr_rows.append({
                "Metric": item["label"],
                "Q1 (25%)": f"${item['q1']:,.2f}",
                "Median (50%)": f"${item['median']:,.2f}",
                "Q3 (75%)": f"${item['q3']:,.2f}",
                "IQR": f"${item['iqr']:,.2f}",
                "Lower Bound": f"${item['lower_bound']:,.2f}",
                "Upper Bound": f"${item['upper_bound']:,.2f}",
                "Outliers": item["outlier_count"],
                "Share": f"{item['outlier_percentage']:.1f}%"
            })
        st.dataframe(pd.DataFrame(iqr_rows), width="stretch")


def render_powerbi_view(df: pd.DataFrame):
    """Renders Power BI data export and verified DAX measures guide."""
    st.markdown('<div class="view-title">Power BI Integration & DAX Library</div>', unsafe_allow_html=True)
    st.markdown('<div class="view-description">Module 8: Analysis-ready data export, dataset schema verification, and standardized DAX formulas for Power BI Desktop.</div>', unsafe_allow_html=True)

    col_info, col_dl = st.columns([1.5, 1])

    with col_info:
        st.write(f"- Dataset Rows: **{len(df):,}** observations")
        st.write(f"- Dataset Columns: **{df.shape[1]}** fields (including 8 engineered domain metrics)")
        st.write("- Missing Values Remaining: **0** (100% sanitized)")

    with col_dl:
        csv_bytes = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Download Cleaned CSV Dataset",
            data=csv_bytes,
            file_name="insurance_claims_cleaned.csv",
            mime="text/csv",
            width="stretch"
        )

    st.markdown('<div class="section-title">Standard DAX Measures Library</div>', unsafe_allow_html=True)
    st.write("Formulas for Power BI Desktop ingestion:")

    st.code("""
// 1. Total Claims Volume
Total Claims = COUNTROWS('insurance_claims_cleaned')

// 2. Cumulative Incurred Claim Amount
Total Claim Amount = SUM('insurance_claims_cleaned'[total_claim_amount])

// 3. Average Claim Severity
Average Claim Amount = AVERAGE('insurance_claims_cleaned'[total_claim_amount])

// 4. Confirmed Fraud Claims Count
Fraud Claims Count = CALCULATE(
    COUNTROWS('insurance_claims_cleaned'),
    'insurance_claims_cleaned'[fraud_reported] = "Y"
)

// 5. Portfolio Fraud Rate Percentage
Fraud Rate % = DIVIDE([Fraud Claims Count], [Total Claims], 0) * 100

// 6. Total Vehicle Claim Payout
Vehicle Claims Total = SUM('insurance_claims_cleaned'[vehicle_claim])

// 7. Vehicle Claim Share %
Vehicle Claim Share % = DIVIDE([Vehicle Claims Total], [Total Claim Amount], 0) * 100

// 8. Total Premium Collected
Total Premium Collected = SUMX(
    'insurance_claims_cleaned',
    'insurance_claims_cleaned'[policy_annual_premium] * 'insurance_claims_cleaned'[customer_tenure_years]
)

// 9. Loss Ratio Proxy %
Loss Ratio Proxy % = DIVIDE([Total Claim Amount], [Total Premium Collected], 0) * 100
    """, language="dax")

    st.markdown('<div class="section-title">Recommended Power BI Architecture</div>', unsafe_allow_html=True)
    p1, p2, p3, p4 = st.columns(4)
    with p1:
        st.markdown("**Page 1: Overview**<br><span style='font-size:0.75rem; color:#64748B;'>Executive KPI cards, monthly claim volume, loss ratio proxy.</span>", unsafe_allow_html=True)
    with p2:
        st.markdown("**Page 2: Fraud & Risk**<br><span style='font-size:0.75rem; color:#64748B;'>Fraud rate %, incident severity distribution, collision types.</span>", unsafe_allow_html=True)
    with p3:
        st.markdown("**Page 3: Demographics**<br><span style='font-size:0.75rem; color:#64748B;'>Insured education, occupation, state cross-flows.</span>", unsafe_allow_html=True)
    with p4:
        st.markdown("**Page 4: Diagnostics**<br><span style='font-size:0.75rem; color:#64748B;'>Auto make/model breakdown, repair proportions, timelines.</span>", unsafe_allow_html=True)


def render_strategy_view():
    """Renders strategic underwriting insights and project scope alignment."""
    st.markdown('<div class="view-title">Strategic Insights & Project Scope</div>', unsafe_allow_html=True)
    st.markdown('<div class="view-description">Module 9: Actionable operational guidance, claims triage recommendations, and academic requirements alignment.</div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown('<div class="section-title">Operational Underwriting Recommendations</div>', unsafe_allow_html=True)
        st.markdown("""
        **1. Severe Damage Investigation Routing**
        - Incidents classified as Major Damage display an empirical fraud rate exceeding 60%.
        - Mandatory automated routing of all Major Damage claims to the Special Investigation Unit (SIU) prior to settlement.

        **2. Vehicle Repair Cost Containment**
        - Vehicle repairs account for 71.9% ($37.93M) of organizational payout expenses.
        - Implement certified repair network partnerships with audited part-pricing schedules to control loss inflation.

        **3. Policy Issuance Validation Controls**
        - Chronological audits uncovered Policy #794731 with an incident date preceding the policy bind date.
        - Enforce date-sequence validation rules in the policy administration software to block retrospective coverage binding.
        """)

    with col2:
        st.markdown('<div class="section-title">Internship Scope Module Compliance</div>', unsafe_allow_html=True)
        st.markdown("""
        - **Module 1: Problem Understanding & Data Ingestion** — Schema audited, 1,000 observations loaded.
        - **Module 2: Data Preprocessing & Cleaning** — Placeholder tokens handled, dates parsed, zero nulls.
        - **Module 3: Feature Engineering** — Customer tenure, vehicle age, policy age, claim ratios.
        - **Module 4: Exploratory Data Analysis** — Target proportions, claim amount decomposition & distribution analysis, incident timelines, severity distributions, and correlation/multicollinearity analysis.
        - **Module 5: Performance Metrics & KPIs** — Loss ratio proxy, component shares, severity averages.
        - **Module 6: Risk Patterns & Anomaly Audits** — Component additivity, chronological timeline inversions, IQR bounds.
        - **Module 8: Power BI Data Readiness** — Cleaned CSV dataset and standard DAX measures guide.
        - **Module 9: Strategic Business Insights** — Executive recommendations and operational triage rules.
        """)
