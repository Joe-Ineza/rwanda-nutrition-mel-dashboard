SELECT COUNT(*) AS primary_rows FROM nutrition.raw_primary_data;
SELECT COUNT(*) AS adjusted_rows FROM nutrition.raw_age_adjusted;
SELECT COUNT(*) AS notes_rows FROM nutrition.raw_notes;

SELECT
    COUNT(*) AS null_country_rows
FROM nutrition.raw_primary_data
WHERE country_and_areas IS NULL;

SELECT
    MIN(year) AS min_year,
    MAX(year) AS max_year
FROM nutrition.raw_primary_data;

SELECT
    country_and_areas,
    year,
    stunting,
    wasting,
    severe_wasting,
    overweight,
    underweight
FROM nutrition.raw_primary_data
WHERE country_and_areas ILIKE 'Rwanda'
ORDER BY year DESC NULLS LAST
LIMIT 25;
