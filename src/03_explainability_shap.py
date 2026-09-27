"""
Session B — SHAP explainability
Charge le modèle entraîné, génère summary plot (global) + waterfall plot
(explication individuelle) pour le client le plus à risque.
"""
import os
from pathlib import Path

import joblib
import matplotlib.pyplot as plt
import pandas as pd
import shap
from dotenv import load_dotenv
from sqlalchemy import create_engine

# --- 1. Chargement des variables d'environnement & configuration ---
load_dotenv()

ROOT = Path(__file__).resolve().parents[1]
MODELS_DIR = ROOT / "models"
OUTPUTS_DIR = ROOT / "outputs"
OUTPUTS_DIR.mkdir(exist_ok=True)

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL non trouvée dans le fichier .env")

# --- 2. Chargement du Pipeline & Données ---
print("Chargement du modèle sauvegardé...")
pipeline = joblib.load(MODELS_DIR / "xgb_churn_pipeline.joblib")

print("Connexion à PostgreSQL et lecture des données...")
engine = create_engine(DATABASE_URL)
df = pd.read_sql("SELECT * FROM cleaned_churn", engine)

# Séparation Features / Target
X = df.drop(columns=["customer_id", "churn"])

# --- 3. Extraire le préprocesseur et le modèle XGBoost ---
preprocessor = pipeline.named_steps["preprocess"]
model = pipeline.named_steps["model"]

# Transformation des features (OneHot + Scaling)
X_transformed = preprocessor.transform(X)

# Sécurité : selon la version de scikit-learn, OneHotEncoder peut renvoyer
# une matrice "sparse" (creuse) — on la convertit en tableau dense si besoin,
# sinon la conversion en DataFrame peut échouer ou donner un résultat vide.
if hasattr(X_transformed, "toarray"):
    X_transformed = X_transformed.toarray()

# Récupération des noms de colonnes transformées
feature_names = preprocessor.get_feature_names_out()
X_transformed_df = pd.DataFrame(X_transformed, columns=feature_names)

# --- 4. Calcul des SHAP Values ---
print("Calcul des SHAP values avec TreeExplainer...")
explainer = shap.TreeExplainer(model)
shap_values = explainer(X_transformed_df)

# --- 5. Génération & Sauvegarde : Summary Plot (Global) ---
print("Génération du SHAP Summary Plot...")
plt.figure(figsize=(10, 6))
shap.summary_plot(shap_values, X_transformed_df, show=False)
summary_plot_path = OUTPUTS_DIR / "shap_summary.png"
plt.tight_layout()
plt.savefig(summary_plot_path, dpi=300)
plt.close()
print(f"Summary plot sauvegardé dans : {summary_plot_path}")

# --- 6. Génération & Sauvegarde : Waterfall Plot (Local - Client à haut risque) ---
print("Génération du SHAP Waterfall Plot pour un client à risque...")
# On cherche un client avec une probabilité de churn élevée
probs = pipeline.predict_proba(X)[:, 1]
high_risk_idx = probs.argmax()
print(f"Client le plus à risque : index {high_risk_idx}, probabilité = {probs[high_risk_idx]:.2%}")

plt.figure(figsize=(10, 6))
shap.plots.waterfall(shap_values[high_risk_idx], show=False)
waterfall_plot_path = OUTPUTS_DIR / "shap_waterfall_high_risk.png"
plt.tight_layout()
plt.savefig(waterfall_plot_path, dpi=300)
plt.close()
print(f"Waterfall plot sauvegardé dans : {waterfall_plot_path}")
 