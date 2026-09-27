# Telecom Customer Churn & Retention Pipeline

An end-to-end data engineering and analytics solution built to ingest, clean, and model customer churn data in PostgreSQL, providing actionable business metrics to reduce customer loss.


## Executive Summary & Business Insights

In this phase, five PostgreSQL analytics views were implemented in `sql/04_create_analytics_views.sql` to transform clean tabular data into actionable business intelligence.

### Key Business Findings
1. **Contract Type Risk:** Customers on **Month-to-month** contracts present a massive churn rate of **42.71%**, compared to just **2.83%** for two-year contracts.
2. **Fiber Optic Vulnerability:** Despite bringing the highest revenue ($91.50 average monthly charge), **Fiber Optic** service suffers from a high churn rate of **41.89%**.
3. **Critical Tenure Window:** The highest churn risk occurs within the **first 12 months (47.44%)**, dropping drastically to **9.51%** for customers staying beyond 4 years.
4. **Payment Method Retention:** Non-automated payment methods, particularly **Electronic check (45.29% churn)**, drastically increase customer loss compared to automated methods (~15-16%).

---

## Dashboard Preview

Executive Power BI dashboard (`dashboard/telecom_churn.pbix`) — 4 KPI cards (total customers, churned customers, churn rate, MRR) and a 2x2 grid of breakdowns by contract type, tenure, payment method, and internet service. Bar colors are conditionally formatted by risk level (red ≥40% churn, orange 15-40%, green <15%).

![Dashboard Overview](dashboard/dashboard_screenshot.png)

---

## Data Pipeline Architecture

1. **Ingestion & Data Quality (Silver Layer):** Raw CSV loaded to PostgreSQL, schema structured, missing `TotalCharges` handled, binary columns normalized.
2. **Gold Layer Views:**
   - `v_churn_kpis`
   - `v_churn_by_contract`
   - `v_churn_by_internet_service`
   - `v_churn_by_tenure`
   - `v_churn_by_payment_method`

---

## Machine Learning: Churn Prediction & Explainability

A gradient-boosted model (XGBoost) predicts churn probability for each customer, with class imbalance handled via `scale_pos_weight`.

| Metric | Value |
|---|---|
| ROC-AUC | 0.8392 |
| Average Precision | 0.664 |

**Model explainability (SHAP):** to understand *why* the model flags a customer as high-risk — not just *that* it does — SHAP values were computed on the trained pipeline.

![SHAP Summary Plot](outputs/shap_summary.png)
*Global feature importance: which variables push customers toward churn across the whole population (e.g. Month-to-month contract, Fiber optic, Electronic check).*

![SHAP Waterfall — High Risk Customer](outputs/shap_waterfall_high_risk.png)
*Individual explanation for a single high-risk customer: how each feature pushed their churn probability up or down from the baseline.*

---

## Business Risk Scoring

Active customers (excluding those who already churned) are segmented into 4 risk tiers based on predicted churn probability, to prioritize retention actions and quantify financial exposure.

| Risk Tier | Customers | MRR at Risk | Avg. Churn Probability | % of Active MRR |
|---|---|---|---|---|
| Critical | 352 | 27,186 DT | 82.4% | 8.58% |
| High | 812 | 57,009 DT | 61.9% | 17.98% |
| Medium | 1,049 | 73,511 DT | 36.6% | 23.19% |
| Low | 2,961 | 159,280 DT | 8.0% | 50.25% |

**Model validation:** among customers who actually churned historically, 86% (1,607 / 1,869) had been scored Critical or High risk — showing the model would have flagged the large majority of real departures in advance, had it been in production.

---

## Project Structure

```text
telecom-customer-churn-retention/
├── data/
│   └── raw/                             # Raw customer churn dataset
├── sql/
│   ├── 02_data_quality_checks.sql
│   ├── 03_create_cleaned_table.sql
│   └── 04_create_analytics_views.sql
├── src/
│   ├── 01_ingest_to_postgres.py         # Loads raw CSV into PostgreSQL
│   ├── 02_train_model.py                # Trains XGBoost churn model
│   ├── 03_explainability_shap.py        # SHAP summary & waterfall plots
│   └── 04_risk_scoring_business.py      # Risk tiers + MRR at risk
├── notebooks/
│   └── 01_data_inspection.py
├── models/                               # Saved trained model (.joblib)
├── outputs/                              # Metrics, SHAP plots, risk scoring CSVs
├── dashboard/
│   └── telecom_churn.pbix                # Power BI executive dashboard
├── .gitignore
└── README.md
```

---

## Setup & Installation

### Prerequisites
- Python 3.10+
- PostgreSQL (local or remote instance)

### Steps

1. Clone the repo and install dependencies:
   ```
   git clone https://github.com/hedijarraya/telecom-customer-churn-retention.git
   cd telecom-customer-churn-retention
   pip install -r requirements.txt
   ```

2. Create a `.env` file at the project root with your database connection:
   ```
   DATABASE_URL=postgresql://user:password@localhost:5432/telecom_db
   ```

3. Run the SQL scripts in order to build the data layers:
   ```
   sql/02_data_quality_checks.sql
   sql/03_create_cleaned_table.sql
   sql/04_create_analytics_views.sql
   ```

4. Train the churn prediction model:
   ```
   python src/02_train_model.py
   ```

5. Generate SHAP explainability plots:
   ```
   python src/03_explainability_shap.py
   ```

6. Generate business risk scoring:
   ```
   python src/04_risk_scoring_business.py
   ```

7. Open `dashboard/telecom_churn.pbix` in Power BI Desktop and refresh the data connection.