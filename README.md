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

## Data Pipeline Architecture

1. **Ingestion & Data Quality (Silver Layer):** Raw CSV loaded to PostgreSQL, schema structured, missing `TotalCharges` handled, binary columns normalized.
2. **Gold Layer Views:**
   - `v_churn_kpis`
   - `v_churn_by_contract`
   - `v_churn_by_internet_service`
   - `v_churn_by_tenure`
   - `v_churn_by_payment_method`

---

## Project Structure

```text
telecom-customer-churn-retention/
├── data/
│   └── raw/                        # Raw customer churn dataset
├── sql/
│   ├── 02_data_quality_checks.sql
│   ├── 03_create_cleaned_table.sql
│   └── 04_create_analytics_views.sql
├── src/
│   ├── 01_ingest_to_postgres.py    # Loads raw CSV into PostgreSQL
│   └── 02_train_model.py           # Trains XGBoost churn model
├── notebooks/
│   └── 01_data_inspection.py
├── models/                         # Saved trained model (.joblib)
├── outputs/                        # Metrics, evaluation artifacts
├── dashboard/
│   └── telecom_churn.pbix          # Power BI executive dashboard
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

5. Open `dashboard/telecom_churn.pbix` in Power BI Desktop and refresh the data connection.
