-- Question:
-- Rank employees based on salary (highest first).
-- If salaries are the same, give the same rank.

-- Table:
-- Employee(id, name, salary)

-- Solution:
SELECT 
    name,
    salary,
    RANK() OVER (ORDER BY salary DESC) AS rank
FROM Employee;