-- =====================================================================
-- Vues d'analyse du churn client — schéma "Gold" (telecom_db)
-- Source : table cleaned_churn (dataset Telco Customer Churn)
-- Objectif : alimenter le dashboard Power BI "Telecom Customer Churn
-- Analytics" avec des indicateurs prêts à consommer, sans recalcul
-- côté BI.
-- =====================================================================

-- 1. KPIs globaux
-- Sert de base aux 4 cartes KPI en haut du dashboard (total clients,
-- clients perdus, taux de churn, MRR). Le "perdu_perc" mesure le
-- revenu mensuel exposé au churn, pas juste le nombre de clients.
CREATE OR REPLACE VIEW v_churn_kpis AS
SELECT 
    COUNT(*) AS total_clients,
    COUNT(*) FILTER (WHERE churn = 'Yes') AS clients_perdus,
    ROUND(
        (COUNT(*) FILTER (WHERE churn = 'Yes')::numeric / COUNT(*)) * 100, 
        2
    ) AS churn_rate_perc,
    SUM(monthly_charges) AS mrr_total,
    SUM(monthly_charges) FILTER (WHERE churn = 'Yes') AS mrr_perdu,
    ROUND(
        (SUM(monthly_charges) FILTER (WHERE churn = 'Yes')::numeric / SUM(monthly_charges)) * 100, 
        2
    ) AS perdu_perc
FROM cleaned_churn;


-- 2. Churn par type de contrat
-- Insight clé du projet : les contrats "month-to-month" ont un taux
-- de churn largement supérieur aux contrats engagés (1 an / 2 ans),
-- car ils n'ont pas de coût de sortie.
DROP VIEW IF EXISTS v_churn_by_contract;
CREATE OR REPLACE VIEW v_churn_by_contract AS
SELECT 
    contract,
    COUNT(*) AS total_clients,
    COUNT(*) FILTER (WHERE churn = 'Yes') AS clients_perdus,
    ROUND(
        (COUNT(*) FILTER (WHERE churn = 'Yes')::numeric / COUNT(*)) * 100, 
        2
    ) AS churn_rate_perc,
    ROUND(AVG(monthly_charges), 2) AS avg_monthly_charges
FROM cleaned_churn
GROUP BY contract
ORDER BY churn_rate_perc DESC;


-- 3. Churn par type de service internet
-- Permet de vérifier si un type de service (fibre, DSL, aucun) est
-- associé à plus d'insatisfaction / résiliation.
DROP VIEW IF EXISTS v_churn_by_internet_service;
CREATE OR REPLACE VIEW v_churn_by_internet_service AS
SELECT 
    internet_service,
    COUNT(*) AS total_clients,
    COUNT(*) FILTER (WHERE churn = 'Yes') AS clients_perdus,
    ROUND(
        (COUNT(*) FILTER (WHERE churn = 'Yes')::numeric / COUNT(*)) * 100, 
        2
    ) AS churn_rate_perc,
    ROUND(AVG(monthly_charges), 2) AS avg_monthly_charges
FROM cleaned_churn
GROUP BY internet_service
ORDER BY churn_rate_perc DESC;


-- 4. Churn par ancienneté client (tenure)
-- Regroupement en 4 tranches business (0-12, 13-24, 25-48, 49+ mois)
-- plutôt que le tenure brut en mois : plus lisible pour un dashboard
-- exécutif, et confirme l'hypothèse que le churn est concentré sur
-- les clients récents (0-12 mois = risque d'attrition le plus élevé).
DROP VIEW IF EXISTS v_churn_by_tenure;
CREATE OR REPLACE VIEW v_churn_by_tenure AS
SELECT 
    CASE 
        WHEN tenure >= 0 AND tenure <= 12 THEN '0-12 mois'
        WHEN tenure >= 13 AND tenure <= 24 THEN '13-24 mois'
        WHEN tenure >= 25 AND tenure <= 48 THEN '25-48 mois'
        ELSE '49+ mois' 
    END AS tenure_group,
    COUNT(*) AS total_clients,
    COUNT(*) FILTER (WHERE churn = 'Yes') AS clients_perdus,
    ROUND(
        (COUNT(*) FILTER (WHERE churn = 'Yes')::numeric / COUNT(*)) * 100, 
        2
    ) AS churn_rate_perc,
    ROUND(AVG(monthly_charges), 2) AS avg_monthly_charges
FROM cleaned_churn
GROUP BY tenure_group;


-- 5. Churn par méthode de paiement
-- Le paiement par "electronic check" (vs prélèvement automatique ou
-- carte) est historiquement associé à un churn plus élevé — souvent
-- un signal de clients moins engagés/moins automatisés.
DROP VIEW IF EXISTS v_churn_by_payment_method;
CREATE OR REPLACE VIEW v_churn_by_payment_method AS
SELECT 
    payment_method,
    COUNT(*) AS total_clients,
    COUNT(*) FILTER (WHERE churn = 'Yes') AS clients_perdus,
    ROUND(
        (COUNT(*) FILTER (WHERE churn = 'Yes')::numeric / COUNT(*)) * 100, 
        2
    ) AS churn_rate_perc,
    ROUND(AVG(monthly_charges), 2) AS avg_monthly_charges
FROM cleaned_churn
GROUP BY payment_method;