CREATE SCHEMA IF NOT EXISTS nutrition;

CREATE OR REPLACE VIEW nutrition.vw_rwanda_latest_nutrition_snapshot AS
WITH ranked AS (
    SELECT
        country_and_areas,
        stratifier,
        type_of_estimate,
        year,
        survey_year,
        stunting,
        wasting,
        severe_wasting,
        overweight,
        underweight,
        u5_population_thousands,
        ROW_NUMBER() OVER (
            PARTITION BY country_and_areas, COALESCE(stratifier, 'National')
            ORDER BY year DESC NULLS LAST
        ) AS row_rank
    FROM nutrition.raw_primary_data
    WHERE country_and_areas ILIKE 'Rwanda'
)
SELECT
    country_and_areas,
    stratifier,
    type_of_estimate,
    year,
    survey_year,
    stunting,
    wasting,
    severe_wasting,
    overweight,
    underweight,
    u5_population_thousands,
    CASE WHEN stunting IS NOT NULL THEN (stunting / 100.0) * u5_population_thousands END AS est_stunted_thousands,
    CASE WHEN wasting IS NOT NULL THEN (wasting / 100.0) * u5_population_thousands END AS est_wasted_thousands,
    CASE WHEN overweight IS NOT NULL THEN (overweight / 100.0) * u5_population_thousands END AS est_overweight_thousands
FROM ranked
WHERE row_rank = 1;


CREATE OR REPLACE VIEW nutrition.vw_rwanda_trends_primary AS
SELECT
    country_and_areas,
    stratifier,
    year,
    survey_year,
    stunting,
    wasting,
    severe_wasting,
    overweight,
    underweight,
    u5_population_thousands
FROM nutrition.raw_primary_data
WHERE country_and_areas ILIKE 'Rwanda'
    AND stratifier ILIKE 'Total'
ORDER BY year;


CREATE OR REPLACE VIEW nutrition.vw_rwanda_trends_adjusted_vs_primary AS
SELECT
    p.country_and_areas,
    p.year,
    p.survey_year,
    p.stratifier,
    p.wasting AS primary_wasting,
    a.wasting AS adjusted_wasting,
    p.severe_wasting AS primary_severe_wasting,
    a.severe_wasting AS adjusted_severe_wasting,
    p.underweight AS primary_underweight,
    a.underweight AS adjusted_underweight
FROM nutrition.raw_primary_data p
LEFT JOIN nutrition.raw_age_adjusted a
    ON p.country_and_areas = a.country_and_areas
   AND p.year = a.year
   AND COALESCE(p.stratifier, 'National') = COALESCE(a.stratifier, 'National')
WHERE p.country_and_areas ILIKE 'Rwanda'
ORDER BY p.year;


CREATE OR REPLACE VIEW nutrition.vw_rwanda_latest_by_stratifier AS
WITH ranked AS (
    SELECT
        country_and_areas,
        stratifier,
        type_of_estimate,
        year,
        survey_year,
        stunting,
        wasting,
        severe_wasting,
        overweight,
        underweight,
        ROW_NUMBER() OVER (
            PARTITION BY country_and_areas, stratifier
            ORDER BY year DESC NULLS LAST
        ) AS row_rank
    FROM nutrition.raw_primary_data
    WHERE country_and_areas ILIKE 'Rwanda'
)
SELECT
    country_and_areas,
    stratifier,
    type_of_estimate,
    year,
    survey_year,
    stunting,
    wasting,
    severe_wasting,
    overweight,
    underweight
FROM ranked
WHERE row_rank = 1;
