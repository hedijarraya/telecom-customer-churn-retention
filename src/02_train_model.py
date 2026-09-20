"""
Entraînement du modèle de prédiction du churn — lit directement depuis
la table cleaned_churn de telecom_db (PostgreSQL).
"""
import os
import json
from pathlib import Path

import joblib
import matplotlib.pyplot as plt
import pandas as pd
import shap
from dotenv import load_dotenv
from sklearn.compose import ColumnTransformer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score, average_precision_score, classification_report
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sqlalchemy import create_engine
from xgboost import XGBClassifier

load_dotenv()  # lit ton fichier .env  

ROOT = Path(__file__).resolve().parents[1]
MODELS_DIR = ROOT / "models"
OUTPUTS_DIR = ROOT / "outputs"
MODELS_DIR.mkdir(exist_ok=True)
OUTPUTS_DIR.mkdir(exist_ok=True)

# --- 1. Charger les données depuis Postgres (pas le CSV) ---
engine = create_engine(os.getenv("DATABASE_URL"))
df = pd.read_sql("SELECT * FROM cleaned_churn", engine)

# --- 2. Préparer la cible ---
df["churn"] = (df["churn"] == "Yes").astype(int)
y = df["churn"]

# on exclut la cible et un éventuel identifiant client  
id_cols = [c for c in df.columns if "id" in c.lower()]
X = df.drop(columns=["churn"] + id_cols)

# détection automatique des types de colonnes (pas besoin de tout lister à la main)
numeric_cols = X.select_dtypes(include="number").columns.tolist()
categorical_cols = X.select_dtypes(exclude="number").columns.tolist()
print("Numériques :", numeric_cols)
print("Catégorielles :", categorical_cols)

# --- 3. Split train/test ---
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, stratify=y, random_state=42
)

# --- 4. Preprocessing + modèle, dans un seul pipeline ---
preprocessor = ColumnTransformer([
    ("num", StandardScaler(), numeric_cols),
    ("cat", OneHotEncoder(handle_unknown="ignore"), categorical_cols),
])

xgb_pipe = Pipeline([
    ("preprocess", preprocessor),
    ("model", XGBClassifier(
        n_estimators=300, max_depth=4, learning_rate=0.05,
        eval_metric="logloss", random_state=42,
        scale_pos_weight=(y_train == 0).sum() / (y_train == 1).sum(),
    )),
])
xgb_pipe.fit(X_train, y_train)

# --- 5. Évaluation ---
proba = xgb_pipe.predict_proba(X_test)[:, 1]
metrics = {
    "roc_auc": round(roc_auc_score(y_test, proba), 4),
    "avg_precision": round(average_precision_score(y_test, proba), 4),
}
print(json.dumps(metrics, indent=2))
print(classification_report(y_test, xgb_pipe.predict(X_test)))

# --- 6. Sauvegarder le modèle entraîné (réutilisable, sans réentraîner) ---
joblib.dump(xgb_pipe, MODELS_DIR / "xgb_churn_pipeline.joblib")

with open(OUTPUTS_DIR / "metrics.json", "w") as f:
    json.dump(metrics, f, indent=2)

print(f"\nModèle sauvegardé dans {MODELS_DIR}")