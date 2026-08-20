import pandas as pd
from sqlalchemy import create_engine

DB_USER = "postgres"
DB_PASS = "TelecomData2026!"
DB_HOST = "localhost"
DB_PORT = "5432"
DB_NAME = "telecom_db"

engine = create_engine(f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}")

csv_path = "../data/raw/WA_Fn-UseC_-Telco-Customer-Churn.csv"
print("Chargement du CSV...")
df = pd.read_csv(csv_path)

# Normalisation des noms de colonnes en snake_case
df.columns = [
    'customer_id', 'gender', 'senior_citizen', 'partner', 'dependents',
    'tenure', 'phone_service', 'multiple_lines', 'internet_service',
    'online_security', 'online_backup', 'device_protection', 'tech_support',
    'streaming_tv', 'streaming_movies', 'contract', 'paperless_billing',
    'payment_method', 'monthly_charges', 'total_charges', 'churn'
]

print("Insertion dans PostgreSQL...")
df.to_sql('staging_churn', con=engine, if_exists='append', index=False)

print("✅ Ingestion réussie ! 7 043 lignes insérées dans staging_churn.")