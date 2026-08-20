-- ==========================================
-- SCRIPT: 02_data_quality_checks.sql
-- DESCRIPTION: Contrôle de qualité et d'intégrité des données sur staging_churn
-- ==========================================

-- 1. Détection des espaces vides ou valeurs NULL dans total_charges
SELECT 
    customer_id, 
    tenure, 
    monthly_charges, 
    total_charges
FROM staging_churn
WHERE total_charges = ' ' OR total_charges IS NULL;

-- 2. Vérification de l'unicité de la clé primaire (0 doublon attendu)
SELECT 
    customer_id, 
    COUNT(*) AS occurences
FROM staging_churn 
GROUP BY customer_id 
HAVING COUNT(*) > 1;

-- 3. Validation des valeurs uniques pour les variables catégorielles
SELECT DISTINCT contract FROM staging_churn;
SELECT DISTINCT payment_method FROM staging_churn;
SELECT DISTINCT internet_service FROM staging_churn;