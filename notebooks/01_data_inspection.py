import pandas as pd

# 1. Load data
df = pd.read_csv('../data/raw/WA_Fn-UseC_-Telco-Customer-Churn.csv')

# 2. Shape
print("=== SHAPE ===")
print(f"Lignes : {df.shape[0]}, Colonnes : {df.shape[1]}\n")

# 3. Head
print("=== HEAD ===")
print(df.head(3))
print("\n")

# 4. Info
print("=== INFO ===")
df.info()
print("\n")

# 5. Missing values
print("=== MISSING VALUES ===")
missing = df.isnull().sum()
print(missing[missing > 0])
if missing.sum() == 0:
    print("Aucune valeur manquante explicite (NaN/NULL).")
print("\n")

# 6. Duplicates
print("=== DUPLICATES ===")
print(f"Doublons stricts : {df.duplicated().sum()}\n")

# 7. Churn distribution
print("=== CHURN DISTRIBUTION ===")
if 'Churn' in df.columns:
    print(df['Churn'].value_counts(normalize=True) * 100)
else:
    print("Colonnes disponibles :", df.columns.tolist())