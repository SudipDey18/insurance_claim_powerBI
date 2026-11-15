# Claims Intelligence Analytics System

## Project Overview
This project analyzes insurance claims data using Python, FastAPI,
and Streamlit, with Power BI readiness.

The objective is to understand claims cost patterns, fraud behaviour,
operational anomalies, and overall portfolio performance to support
executive decision-making.

## Objectives
- Analyze claims payout and severity patterns.
- Identify fraud rates across incident severity tiers.
- Break down claim costs into vehicle, injury, and property components.
- Understand monthly and 24-hour incident trends.
- Run data-quality and anomaly audits (additivity, timeline, IQR).
- Provide Power BI / DAX readiness and strategic business insights.

## Technologies Used
- Python
- Pandas
- NumPy
- Matplotlib
- Seaborn
- FastAPI
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

1. Clone the repository.
2. Open the project folder.
3. Start the backend server:

```bash
python -m uvicorn backend.server:app --host 0.0.0.0 --port 8000
```

4. Start the frontend dashboard:

```bash
streamlit run frontend\app.py --server.port 8501
```

5. Open the dashboard in your browser at `http://localhost:8501`.

> Alternatively, use the launcher: `python run.py backend` and `python run.py frontend`.

## Project Outcome
The project provides insights into claims cost distribution, fraud
patterns, operational anomalies, and portfolio performance, along with
a Power BI / DAX readiness guide for further reporting.

## Author
Your Name

## License
This project is for educational purposes.