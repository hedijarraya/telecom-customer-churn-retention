-- 1. Vue des KPIs Globaux
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

SELECT * FROM v_churn_kpis;


-- 2. Vue d'Analyse par Contrat
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

SELECT * FROM v_churn_by_contract;

-- 3. Vue d'Analyse par service d'internet

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

select * from v_churn_by_internet_service;


-- 4. Vue d'Analyse par tenure

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

SELECT * FROM v_churn_by_tenure ORDER BY churn_rate_perc DESC;

-- 4. Vue d'Analyse par methode de paiement

select * from cleaned_churn limit 10;

drop view if exists v_churn_by_payment_method;

create or replace view v_churn_by_payment_method as
	select payment_method, 
	count(*) as total_clients,
	count(*) filter (where churn='Yes') as clients_perdus,
	round( (count(*) filter (where churn='Yes')::numeric / count(*))*100 ,
		2) as churn_rate_perc,
	round(avg(monthly_charges),2) as avg_monthly_charges
from cleaned_churn
group by payment_method;

select * from v_churn_by_payment_method;