-- Question:
-- Get running total of sales by date.

SELECT 
    date,
    amount,
    SUM(amount) OVER (ORDER BY date) AS running_total
FROM Sales;