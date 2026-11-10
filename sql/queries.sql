-- 1. Trips, average fare and average distance by pickup borough
SELECT pickup_borough,
       COUNT(*)                AS trips,
       ROUND(AVG(fare), 2)     AS avg_fare,
       ROUND(AVG(distance), 2) AS avg_miles
FROM trips
GROUP BY pickup_borough
ORDER BY trips DESC;

-- 2. Busiest hours of the day
SELECT pickup_hour, COUNT(*) AS trips
FROM trips
GROUP BY pickup_hour
ORDER BY trips DESC
LIMIT 5;

-- 3. Average tip by payment type (cash trips show a tip of 0)
SELECT payment,
       COUNT(*)                AS trips,
       ROUND(AVG(tip), 2)      AS avg_tip,
       ROUND(AVG(tip_pct), 1)  AS avg_tip_pct
FROM trips
GROUP BY payment
ORDER BY trips DESC;

-- 4. Average total fare by day of the week
SELECT pickup_day,
       COUNT(*)              AS trips,
       ROUND(AVG(total), 2)  AS avg_total
FROM trips
GROUP BY pickup_day
ORDER BY avg_total DESC;

-- 5. Top 10 pickup zones
SELECT pickup_zone, COUNT(*) AS trips
FROM trips
WHERE pickup_zone <> 'Unknown'
GROUP BY pickup_zone
ORDER BY trips DESC
LIMIT 10;

-- 6. Yellow versus green taxis
SELECT color,
       COUNT(*)                    AS trips,
       ROUND(AVG(fare), 2)         AS avg_fare,
       ROUND(AVG(trip_minutes), 1) AS avg_minutes
FROM trips
GROUP BY color;

-- 7. Top 3 pickup zones inside each borough (window function)
SELECT pickup_borough, pickup_zone, trips
FROM (
    SELECT pickup_borough, pickup_zone, COUNT(*) AS trips,
           ROW_NUMBER() OVER (PARTITION BY pickup_borough ORDER BY COUNT(*) DESC) AS rn
    FROM trips
    WHERE pickup_borough <> 'Unknown'
    GROUP BY pickup_borough, pickup_zone
)
WHERE rn <= 3
ORDER BY pickup_borough, trips DESC;

-- 8. Average fare per mile by hour, busiest first (CTE)
WITH hourly AS (
    SELECT pickup_hour,
           COUNT(*)                     AS trips,
           ROUND(AVG(fare / distance), 2) AS fare_per_mile
    FROM trips
    GROUP BY pickup_hour
)
SELECT * FROM hourly
ORDER BY trips DESC
LIMIT 8;

-- 9. Why rows were rejected during cleaning
SELECT reason, COUNT(*) AS rows_rejected
FROM rejected_trips
GROUP BY reason
ORDER BY rows_rejected DESC;
