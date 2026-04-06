-- Question:
-- Find employees earning above the average salary.

SELECT name, salary
FROM Employee
WHERE salary > (SELECT AVG(salary) FROM Employee);