-- =============================================================================
-- Script 02: Data Exploration & Quality Checks
-- Target Table: staging_churn
-- Author: Hedi Jarraya
-- =============================================================================

-------------------------------------------------------------------------------
-- 1. APERÇU GÉNÉRAL ET STRUCTURE DE LA TABLE
-------------------------------------------------------------------------------

-- Visualisation des 10 premières lignes
SELECT * 
FROM staging_churn 
LIMIT 10;

-- Inspection des métadonnées des colonnes et types de données actuels
SELECT 
    column_name, 
    data_type, 
    is_nullable
FROM information_schema.columns
WHERE table_name = 'staging_churn';

-- Distribution par genre (Validation de l'unicité des IDs)
SELECT 
    gender,
    COUNT(customer_id) AS total_customers
FROM staging_churn
GROUP BY gender;

-------------------------------------------------------------------------------
-- 2. EXPLORATION DES MODALITÉS (SERVICES ET ABONNEMENTS)
-------------------------------------------------------------------------------

-- Distribution des contrats
SELECT 
    contract, 
    COUNT(customer_id) AS total_customers 
FROM staging_churn 
GROUP BY contract;

-- Distribution des types de services Internet
SELECT 
    internet_service, 
    COUNT(customer_id) AS total_customers 
FROM staging_churn 
GROUP BY internet_service;

-- Distribution des modes de paiement
SELECT 
    payment_method, 
    COUNT(customer_id) AS total_customers 
FROM staging_churn 
GROUP BY payment_method;

-- Distribution de la variable cible (Churn)
SELECT 
    churn, 
    COUNT(customer_id) AS total_customers 
FROM staging_churn 
GROUP BY churn;

-------------------------------------------------------------------------------
-- 3. STATISTIQUES DESCRIPTIVES (TENURE & MONTHLY CHARGES)
-------------------------------------------------------------------------------

SELECT 
    MIN(tenure) AS min_tenure,
    MAX(tenure) AS max_tenure,
    ROUND(AVG(tenure), 2) AS avg_tenure,
    MIN(monthly_charges) AS min_monthly,
    MAX(monthly_charges) AS max_monthly,
    ROUND(AVG(monthly_charges), 2) AS avg_monthly
FROM staging_churn;

-------------------------------------------------------------------------------
-- 4. VALIDATION ET AUDIT DES ANOMALIES (DATA QUALITY)
-------------------------------------------------------------------------------

-- A. Contrôle d'unicité sur la clé primaire (Détection de doublons)
SELECT 
    customer_id,
    COUNT(*) AS occurrence_count
FROM staging_churn
GROUP BY customer_id 
HAVING COUNT(*) > 1;

-- B. Vérification du typage de la variable senior_citizen (Attendu: 0 et 1)
SELECT DISTINCT 
    senior_citizen,
    senior_citizen::boolean AS is_senior_citizen
FROM staging_churn;

-- C. Identification des lignes contenant des valeurs vides/NULL dans total_charges
SELECT 
    customer_id,
    tenure,
    monthly_charges,
    total_charges
FROM staging_churn
WHERE total_charges IS NULL 
   OR total_charges = ' ' 
   OR total_charges = '';

-- D. Vérification de cohérence financière (total_charges < monthly_charges)
-- Exclusions : clients sans facture (tenure = 0) et espaces vides
SELECT 
    customer_id,
    tenure,
    monthly_charges,
    total_charges::numeric AS total_charges_clean
FROM staging_churn
WHERE total_charges IS NOT NULL 
  AND total_charges <> ' ' 
  AND total_charges <> ''
  AND total_charges::numeric < monthly_charges
  AND tenure > 0;