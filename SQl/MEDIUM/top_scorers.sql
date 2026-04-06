-- Question:
-- Get top 3 scoring students per class.

SELECT *
FROM (
    SELECT *,
           ROW_NUMBER() OVER (PARTITION BY class ORDER BY score DESC) AS rn
    FROM Students
) t
WHERE rn <= 3;