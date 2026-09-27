import os
from pathlib import Path
import pandas as pd
import numpy as np
import joblib
from dotenv import load_dotenv
from sqlalchemy import create_engine

# --- 1. Chargement des variables d'environnement ---
load_dotenv()

ROOT = Path(__file__).resolve().parents[1]
MODELS_DIR = ROOT / "models"
OUTPUTS_DIR = ROOT / "outputs"
OUTPUTS_DIR.mkdir(exist_ok=True)

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL non trouvée dans le fichier .env")

# --- 2. Chargement du modèle & Données ---
print("Chargement du modèle sauvegardé...")
pipeline = joblib.load(MODELS_DIR / "xgb_churn_pipeline.joblib")

print("Connexion à PostgreSQL et lecture des données...")
engine = create_engine(DATABASE_URL)
df = pd.read_sql("SELECT * FROM cleaned_churn", engine)

# On conserve customer_id et les variables financières
customer_ids = df["customer_id"]
monthly_charges = df["monthly_charges"]
X = df.drop(columns=["customer_id", "churn"])

# --- 3. Prédiction des probabilités & Risk Scoring ---
print("Calcul des probabilités de churn...")
churn_probs = pipeline.predict_proba(X)[:, 1]

# Définition des règles de segmentation métier
# Low: < 25% | Medium: 25-50% | High: 50-75% | Critical: >= 75%
conditions = [
    (churn_probs < 0.25),
    (churn_probs >= 0.25) & (churn_probs < 0.50),
    (churn_probs >= 0.50) & (churn_probs < 0.75),
    (churn_probs >= 0.75)
]
risk_levels = ["Low Risk", "Medium Risk", "High Risk", "Critical Risk"]

risk_segments = np.select(conditions, risk_levels, default="Low Risk")

# Création du DataFrame de scoring (toute la population, avec actual_churn)
df_scoring = pd.DataFrame({
    "customer_id": customer_ids,
    "monthly_charges": monthly_charges,
    "churn_probability": churn_probs.round(4),
    "risk_segment": risk_segments,
    "actual_churn": df["churn"]
})

# --- 3bis. Séparer validation (tous) et actionnable (clients actifs uniquement) ---
# Table de validation : sert à vérifier que le modèle a bien vu venir les départs réels
df_scoring_all = df_scoring.copy()

# Table actionnable : seulement les clients encore actifs (churn = 'No')
# -> c'est CETTE table qui a du sens pour une équipe CVM : on ne peut pas
#    "retenir" un client déjà parti.
df_scoring_active = df_scoring[df_scoring["actual_churn"] == "No"].drop(
    columns=["actual_churn"]
)

# --- 4. Analyse financière & MRR à risque (sur les clients ACTIFS uniquement) ---
print("\n=== AGRÉGATION FINANCIÈRE PAR SEGMENT DE RISQUE (clients actifs) ===")
summary_mrr = df_scoring_active.groupby("risk_segment").agg(
    total_customers=("customer_id", "count"),
    total_mrr_at_risk=("monthly_charges", "sum"),
    avg_mrr=("monthly_charges", "mean"),
    avg_churn_prob=("churn_probability", "mean")
).reset_index()

# Tri logique des segments
risk_order = {"Critical Risk": 1, "High Risk": 2, "Medium Risk": 3, "Low Risk": 4}
summary_mrr["sort_key"] = summary_mrr["risk_segment"].map(risk_order)
summary_mrr = summary_mrr.sort_values("sort_key").drop(columns=["sort_key"])

# Calcul du % du MRR total (actif) à risque
total_mrr = summary_mrr["total_mrr_at_risk"].sum()
summary_mrr["pct_mrr_at_risk"] = (summary_mrr["total_mrr_at_risk"] / total_mrr * 100).round(2)

print(summary_mrr.to_string(index=False))

# --- 4bis. Petit contrôle de validation (informatif, pas exporté) ---
# Vérifie que les clients ayant réellement churné étaient bien scorés "à risque"
validation = df_scoring_all[df_scoring_all["actual_churn"] == "Yes"]["risk_segment"].value_counts()
print("\n=== VALIDATION : répartition des segments chez les clients ayant réellement churné ===")
print(validation.to_string())

# --- 5. Exportation des résultats (PostgreSQL & CSV) ---
print("\nExportation vers PostgreSQL...")
df_scoring_all.to_sql("churn_risk_scoring_all", engine, if_exists="replace", index=False)
df_scoring_active.to_sql("churn_risk_scoring_active", engine, if_exists="replace", index=False)

summary_csv_path = OUTPUTS_DIR / "risk_segmentation_summary.csv"
summary_mrr.to_csv(summary_csv_path, index=False)
print(f"Résumé business (clients actifs) sauvegardé dans : {summary_csv_path}")