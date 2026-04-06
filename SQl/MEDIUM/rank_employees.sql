-- Question:
-- Rank employees by salary (highest first). Tie gets same rank.

SELECT 
    name,
    salary,
    RANK() OVER (ORDER BY salary DESC) AS rank
FROM Employee;