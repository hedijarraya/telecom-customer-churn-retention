-- =============================================================================
-- Script 03: Create Cleaned Table
-- Target Table: cleaned_churn
-- Source Table: staging_churn
-- Author: Hedi Jarraya
-- =============================================================================

-- 1. Suppression de la table si elle existe déjà
DROP TABLE IF EXISTS cleaned_churn;

-- 2. Création de la table nettoyée avec typage et transformations
CREATE TABLE cleaned_churn AS
SELECT 
    customer_id,
    gender,
    senior_citizen::boolean AS is_senior_citizen,
    partner,
    dependents,
    tenure,
    phone_service,
    multiple_lines,
    internet_service,
    online_security,
    online_backup,
    device_protection,
    tech_support,
    streaming_tv,
    streaming_movies,
    contract,
    paperless_billing,
    payment_method,
    monthly_charges,
    CASE 
        WHEN total_charges = '' OR total_charges = ' ' OR total_charges IS NULL THEN 0.00
        ELSE total_charges::numeric 
    END AS total_charges,
    churn
FROM staging_churn;

-- 3. Vérification du nombre de lignes créées
SELECT COUNT(*) AS total_rows FROM cleaned_churn;