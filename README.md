# Claims Intelligence Analytics System

## Project Overview
This project analyzes insurance claims data using Python and Streamlit,
with Power BI readiness. All data services, operational audits, and KPI
analytics are directly integrated into Streamlit for a fast, standalone experience.

The objective is to understand claims cost patterns, fraud behaviour,
operational anomalies, and overall portfolio performance to support
executive decision-making.

## Objectives
- Analyze claims payout and severity patterns.
- Identify fraud rates across incident severity tiers.
- Break down claim costs into vehicle, injury, and property components.
- Understand monthly and 24-hour incident trends.
- Track and display total dashboard viewers counted by client IP address.
- Run data-quality and anomaly audits (additivity, timeline, IQR).
- Provide Power BI / DAX readiness and strategic business insights.

## Technologies Used
- Python
- Pandas
- NumPy
- Matplotlib
- Seaborn
- Streamlit
- Power BI (DAX)

## Dataset
The dataset contains 1,000 insurance claim records with 40 raw fields,
expanded to 50 after feature engineering.

Key fields include:
- Policy Details (policy number, state, bind date, premium, deductible)
- Insured Details (age, sex, education, occupation, hobbies)
- Incident Details (date, type, severity, hour, location, witnesses)
- Claim Amounts (total, injury, property, vehicle)
- Vehicle Details (make, model, year)
- Fraud Label (fraud_reported: Y / N)

Engineered features include customer tenure, policy age, vehicle age,
incident month, incident period of day, claim ratios, and a fraud flag.

## Project Workflow
1. Data Ingestion
2. Data Cleaning & Preprocessing
3. Feature Engineering
4. Exploratory Data Analysis & KPI Analytics
5. Operational Anomaly Audits
6. Power BI / DAX Readiness
7. Strategic Business Insights

## Installation

Install the required libraries:

```bash
pip install -r requirements.txt
```

## How to Run

1. Clone or open the repository.
2. Install the required libraries:

```bash
pip install -r requirements.txt
```

3. Launch the Streamlit dashboard:

```bash
streamlit run frontend/app.py --server.port 8501
```

> Alternatively, run via the launcher: `python run.py`.

4. Open the dashboard in your browser at `http://localhost:8501`.

## Dataset Upload & Sample Templates
The dashboard features an interactive dataset ingestion pipeline:
- **Download Sample Formats**: Users can download pre-formatted sample datasets in either **CSV (`.csv`)** or **Excel (`.xlsx`)** format directly from the **Upload Dataset** navigation tab.
- **Strict Column Schema Validation**: Uploaded files must match the 39 canonical raw insurance claim attributes. If any fields are missing, the system detects and lists each missing column name.
- **Automatic Domain Feature Engineering**: Successfully validated uploads are automatically processed through the feature engineering pipeline (calculating tenure, vehicle age, policy age, loss ratios, periods of day, etc.).
- **Live Dashboard Updates**: All views (Overview, Claims Analysis, Operational Audits, Power BI readiness) immediately re-compute against the newly loaded dataset.
- **One-Click Reset**: Easily restore the default 1,000-claim production portfolio anytime via the **Reset to Default Dataset** option.

## Viewer Tracking & Backend Logging
The system tracks viewer traffic with backend audit logging:
- **Total Viewers in Front End**: Displays aggregate `Total Viewers: <count>` in the top header navbar and Executive Overview, counted uniquely based on client IP addresses.
- **Privacy-Preserving UI**: Client IP addresses and access audits are strictly hidden from the frontend user interface.
- **Backend Audit Log**: Every connection and IP audit is logged into `backend/logs/viewer_audit.log` (recording client IP, timestamp, visit status, unique viewers count, and IP visit frequency).
- **Application Logging**: General server requests, startup events, and health metrics are logged to `backend/logs/server.log`.
- **Streamlit-Native Services**: Domain services (KPI analytics, breakdown allocations, temporal trends, audits, and dataset processing) execute directly in-process with thread-safe persistence in `dataset/viewers.json`.

## Project Outcome
The project provides insights into claims cost distribution, fraud
patterns, operational anomalies, and portfolio performance, along with
a Power BI / DAX readiness guide for further reporting.

## Author
Sudip Dey
Sneha Sadhu
Shreya Pal
Dipayan Sardar

## License
This project is for educational purposes.
