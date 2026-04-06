-- Question:
-- Calculate the running total of sales by date.

-- Table:
-- Sales(date, amount)

-- Solution:
SELECT 
    date,
    amount,
    SUM(amount) OVER (ORDER BY date) AS running_total
FROM Sales;