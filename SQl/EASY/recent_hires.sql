-- Question:
-- Find employees hired in the last 30 days.

SELECT *
FROM Employee
WHERE hire_date >= CURRENT_DATE - INTERVAL '30' DAY;