-- Question:
-- Find employees who earn more than the average salary.

-- Table:
-- Employee(id, name, salary)

-- Solution:
SELECT name, salary
FROM Employee
WHERE salary > (SELECT AVG(salary) FROM Employee);