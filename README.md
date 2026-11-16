# Claims Intelligence Analytics System

A comprehensive insurance claims intelligence, fraud analytics, and operational anomaly detection platform built with **Python** and **Streamlit**, featuring enterprise **Power BI / DAX** reporting readiness.

The platform provides end-to-end analytical visibility into claims cost structures, fraud behavioral patterns, chronological and financial anomalies, and portfolio loss performance to empower data-driven underwriting and executive decision-making.

---

## Key Highlights

- **Streamlit-Native Standalone Architecture**: No external FastAPI or microservice server required. Domain computations, analytics, data ingestion, and audits execute directly in-process.
- **One-Click Streamlit Cloud Deployment**: Pre-configured with root entrypoints (`app.py`, `streamlit_app.py`) and `.streamlit/config.toml` for seamless hosting on [Streamlit Community Cloud](https://share.streamlit.io).
- **Custom Dataset Ingestion & Validation**: Drag-and-drop CSV/Excel (`.xlsx`) upload with automated 39-field schema validation, real-time feature engineering, and one-click reset to default data.
- **Sample Template Downloads**: Built-in download buttons for pre-formatted sample datasets in both CSV and Microsoft Excel formats.
- **Privacy-Preserving IP Viewer Tracking**: Automatic client IP-based unique visitor counting displayed discreetly in the top navigation bar with dedicated backend audit logging (`backend/logs/viewer_audit.log`).
- **Power BI & DAX Readiness**: Production-ready DAX measure formulas, star-schema data modeling guidance, and analytical dataset exports.

---

## Analytics Modules & Capabilities

### 1. Executive Claims Overview
- **Key Financial Indicators**: Real-time KPI metric cards for Total Claims Processed, Total Incurred Losses ($M), Average Severity ($), Median Severity ($), Confirmed Fraud Rate (%), and Loss Ratio Proxy (%).
- **Component Cost Allocation**: Donut visualization and financial breakdown of claim payouts across **Vehicle Repair/Replacement** (71.9%), **Injury Compensation** (16.7%), and **Property Damage** (11.4%).
- **Monthly Trajectory & Fraud Incidence**: Dual-axis visualization correlating monthly claims volume, confirmed fraud cases, and aggregate financial liability.

### 2. Claims & Severity Analysis
- **Incident Severity Distribution**: Multi-bar comparison across severity tiers (*Minor Damage*, *Major Damage*, *Total Loss*, *Trivial Damage*) highlighting that Major Damage claims exhibit fraud rates exceeding 60%.
- **24-Hour Temporal Dynamics**: Temporal trend analysis evaluating incident frequency across 24 hours and categorized periods of day (Morning, Afternoon, Evening, Night).
- **Correlation Matrix**: Pearson correlation heatmap assessing multicollinearity across financial, policy, and demographic features.
- **Claim Amount Distribution Decomposition**: Histogram and KDE density plots evaluating skewness and distribution across total, vehicle, injury, and property claims.

### 3. Operational Anomaly Audits (Data Quality)
- **Component Additivity Audit**: Verifies financial integrity (`total_claim_amount == vehicle_claim + injury_claim + property_claim`).
- **Chronological Sequence Audit**: Identifies chronological timeline inversions (e.g., incidents recorded prior to policy bind dates).
- **Rapid Claim Inception Audit**: Detects high-risk policies where claims occurred within 30 days of coverage inception.
- **Statistical Outlier Detection**: Identifies statistical anomalies and high-severity outliers using the Interquartile Range (IQR) method.

### 4. Power BI & DAX Reporting Readiness
- **Core Schema Dictionary**: Standardized definitions for policy dimensions, incident dimensions, and financial measures.
- **Enterprise DAX Measures**: Ready-to-use DAX formulas for Total Incurred, Loss Ratio Proxy, Confirmed Fraud Rate, Severe Incident Fraud Rate, and Component Share Percentages.
- **Data Modeling Guidance**: Star-schema architecture recommendations for enterprise reporting pipelines.

### 5. Strategic Business Insights
- **Underwriting Controls**: Date-sequence validation rules to block retrospective policy binding.
- **SIU Fraud Triage Routing**: Automated referral protocols for Major Damage incidents to Special Investigation Units.
- **Repair Cost Containment**: Recommended preferred partner networks and standardized parts-pricing schedules to control vehicle loss inflation.

### 6. Interactive Dataset Ingestion
- **Schema Validation**: Checks uploaded CSV/Excel files against all 39 canonical raw attributes and provides specific missing-column diagnostic messages.
- **Automated Feature Engineering**: Automatically expands 39 raw fields into 50 enriched attributes upon upload.
- **Downloadable Sample Templates**: Instant downloads of sample files in `.csv` and `.xlsx` formats.
- **One-Click Reset**: Instant restoration of the default 1,000-observation master portfolio.

---

## Technologies Used

| Technology | Purpose |
|---|---|
| **Python 3.10+** | Core programming language |
| **Streamlit** | Interactive web dashboard, state management, and application engine |
| **Pandas** | High-performance data manipulation, filtering, and hygiene |
| **NumPy** | Numerical computations, ratio derivations, and statistical arrays |
| **Matplotlib** | High-resolution publication-quality visual charting |
| **Seaborn** | Statistical distribution plots, KDE distributions, and correlation heatmaps |
| **OpenPyXL** | Microsoft Excel (`.xlsx`) workbook generation and ingestion |
| **Power BI (DAX)** | Business intelligence data modeling and enterprise measure formulas |

---

## Project Structure

```text
insurance_claim_powerBI/
├── .streamlit/
│   └── config.toml               # Streamlit server, headless, and corporate theme settings
├── backend/
│   ├── __init__.py               # Backend package initializer
│   ├── analytics_service.py      # KPI metrics, component breakdowns, trends, and correlation
│   ├── audit_service.py          # Operational anomaly checks (additivity, timeline, IQR)
│   ├── config.py                 # File paths, project directory definitions, and server settings
│   ├── data_service.py           # Ingestion, schema validation, feature engineering, templates
│   ├── logger.py                 # Rotating file loggers for server and viewer audits
│   ├── server.py                 # Pure-Python domain service entrypoint
│   ├── viewer_service.py         # Thread-safe client IP tracking and viewer counters
│   └── logs/
│       ├── server.log            # Operational server and application events
│       └── viewer_audit.log      # Dedicated client IP access audit trail
├── dataset/
│   ├── insurance_claims.csv      # Raw insurance claims dataset (1,000 records, 39 fields)
│   ├── insurance_claims_cleaned.csv # Cleaned master dataset with engineered features
│   ├── sample_template.csv       # Pre-formatted sample template in CSV format
│   ├── sample_template.xlsx      # Pre-formatted sample template in Excel format
│   └── viewers.json              # Persistent JSON store for viewer counts
├── frontend/
│   ├── __init__.py               # Frontend package initializer
│   ├── api_client.py             # Service controller connecting UI directly to domain services
│   ├── app.py                    # Main dashboard application, navigation routing, and filters
│   ├── styles.py                 # Minimalist executive CSS design system
│   └── views.py                  # View renderers for Overview, Audits, Power BI, and Uploads
├── .gitignore                    # Git ignore file (virtualenvs, bytecode, caches, logs)
├── app.py                        # Root entrypoint for Streamlit Community Cloud
├── README.md                     # Comprehensive project documentation
├── requirements.txt              # Production dependency specifications
├── run.py                        # Convenient local launcher script
└── streamlit_app.py              # Cloud deployment alias entrypoint
```

---

## Dataset Schema & Dictionary

The baseline dataset consists of **1,000 historical insurance claim observations**. The system validates 39 canonical raw attributes and engineers 11 derived features:

### Canonical Raw Columns (39 Fields)

| Category | Field Name | Description |
|---|---|---|
| **Policy Details** | `policy_number` | Unique policy identifier |
| | `policy_bind_date` | Date the policy was underwritten and bound |
| | `policy_state` | State in which the policy was issued |
| | `policy_csl` | Combined Single Limit coverage tiers |
| | `policy_deductable` | Insured deductible amount ($) |
| | `policy_annual_premium` | Annual premium billed to policyholder ($) |
| | `umbrella_limit` | Excess liability umbrella coverage limit ($) |
| | `months_as_customer` | Total duration of policyholder tenure in months |
| **Insured Demographics** | `age` | Policyholder age in years |
| | `insured_sex` | Policyholder gender |
| | `insured_education_level` | Highest educational attainment |
| | `insured_occupation` | Professional occupation |
| | `insured_hobbies` | Recorded hobbies |
| | `insured_relationship` | Insured family / household relationship |
| | `capital-gains` | Annual capital gains ($) |
| | `capital-loss` | Annual capital losses ($) |
| | `insured_zip` | Insured billing postal code |
| **Incident Details** | `incident_date` | Date of incident occurrence |
| | `incident_type` | Type of accident (e.g., Single Vehicle, Multi-vehicle, Theft) |
| | `collision_type` | Collision impact point (Front, Rear, Side, or N/A) |
| | `incident_severity` | Damage classification (Minor, Major, Total Loss, Trivial) |
| | `authorities_contacted` | Emergency services notified (Police, Fire, Ambulance, None) |
| | `incident_state` | State where incident occurred |
| | `incident_city` | City where incident occurred |
| | `incident_location` | Street address of incident |
| | `incident_hour_of_the_day` | Incident hour (0 to 23) |
| | `number_of_vehicles_involved` | Count of vehicles involved |
| | `property_damage` | Property damage sustained (YES, NO, Unknown) |
| | `bodily_injuries` | Number of injuries sustained |
| | `witnesses` | Number of recorded witnesses |
| | `police_report_available` | Police report availability (YES, NO, Unknown) |
| **Claim Financials** | `total_claim_amount` | Total financial settlement claimed ($) |
| | `injury_claim` | Injury settlement component ($) |
| | `property_claim` | Property damage component ($) |
| | `vehicle_claim` | Vehicle repair/replacement component ($) |
| **Vehicle Information** | `auto_make` | Vehicle manufacturer |
| | `auto_model` | Vehicle model |
| | `auto_year` | Vehicle manufacturing year |
| **Fraud Outcome** | `fraud_reported` | Confirmed fraud investigation label (`Y` or `N`) |

### Engineered Features (11 Fields)

1. `customer_tenure_years`: Policyholder tenure in years (`months_as_customer / 12`).
2. `policy_age_days`: Elapsed days between policy bind date and incident date.
3. `vehicle_age`: Age of vehicle at incident occurrence (`incident_year - auto_year`).
4. `incident_month`: Month name extracted from incident date.
5. `incident_day_of_week`: Day of the week extracted from incident date.
6. `incident_period_of_day`: Binned occurrence window (*Morning*, *Afternoon*, *Evening*, *Night*).
7. `injury_claim_ratio`: Payout share allocated to bodily injuries.
8. `property_claim_ratio`: Payout share allocated to property damage.
9. `vehicle_claim_ratio`: Payout share allocated to vehicle repairs.
10. `net_capital_gains`: Capital gains minus capital losses (`capital-gains - capital-loss`).
11. `fraud_reported_flag`: Binary integer flag for analytics (`1` for Fraud, `0` for Legitimate).

---

## Installation & How to Run

### Option 1: Run Locally

1. **Clone the repository**:
   ```bash
   git clone https://github.com/SudipDey18/insurance_claim_powerBI.git
   cd insurance_claim_powerBI
   ```

2. **Create and activate a virtual environment (recommended)**:
   ```bash
   # Windows PowerShell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1

   # macOS / Linux
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Launch the platform**:
   ```bash
   streamlit run app.py
   ```
   > *Alternatively, use the launcher script*:
   > ```bash
   > python run.py
   > ```

5. **Access the application**: Open your web browser at `http://localhost:8501`.

---

### Option 2: Deploy to Streamlit Community Cloud (One-Click)

The repository is fully configured for zero-configuration cloud hosting:

1. Sign in to [Streamlit Community Cloud](https://share.streamlit.io/) with your GitHub account.
2. Click **"New app"** (or **"Create app"**).
3. Fill in the deployment form:
   - **Repository**: `SudipDey18/insurance_claim_powerBI`
   - **Branch**: `backend-converted-streamlit` *(or `main`)*
   - **Main file path**: `app.py` *(or `streamlit_app.py`)*
4. Click **"Deploy!"**
5. Streamlit Cloud will install dependencies and launch the platform in a single run.

---

## Audience & Viewer Tracking (Backend Logged)

To monitor user traffic while maintaining clean executive presentation and data privacy:
- **Discreet UI Counter**: The total count of unique viewers (determined by client IP address) is displayed in the top navigation bar badge:
  ```text
  Total Viewers: <count>
  ```
- **Privacy First**: Client IP addresses and access logs are strictly hidden from the frontend user interface and API payloads.
- **Dedicated Audit Logging**: Detailed access events (client IP, status, visit frequency, timestamps) are recorded directly into `backend/logs/viewer_audit.log`:
  ```text
  2026-11-16 17:15:06 [INFO] [viewer_audit] [AUDIT_NEW_VIEWER] Client IP: 192.168.1.105 | Total Unique Viewers: 2 | Total Visits: 2 | First Seen: 2026-11-16 17:15:06
  ```

---

## Authors & Project Contributors

- **Sudip Dey**
- **Sneha Sadhu**
- **Shreya Pal**
- **Dipayan Sardar**

---

## License

This project is developed for educational and academic research purposes under the standard MIT/Academic License.
