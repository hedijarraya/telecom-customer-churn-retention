import os
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine

# --- 1. Connexion : lue dans le fichier .env, jamais écrite dans le code ---
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL non trouvée dans le fichier .env")

engine = create_engine(DATABASE_URL)

# --- 2. Lecture du CSV (chemin construit depuis la racine du projet) ---
ROOT = Path(__file__).resolve().parents[1]
csv_path = ROOT / "data" / "raw" / "WA_Fn-UseC_-Telco-Customer-Churn.csv"

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

# --- 3. Chargement idempotent : relancer le script remplace la table au lieu de dupliquer les lignes ---
print("Insertion dans PostgreSQL...")
df.to_sql('staging_churn', con=engine, if_exists='replace', index=False)

print(f"✅ Ingestion réussie ! {len(df)} lignes insérées dans staging_churn.")
