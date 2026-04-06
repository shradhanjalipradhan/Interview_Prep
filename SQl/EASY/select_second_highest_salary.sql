-- Question:
-- Find the second highest salary from the Employee table.

-- Table:
-- Employee(id, salary)

-- Solution:
SELECT MAX(salary) AS SecondHighestSalary
FROM Employee
WHERE salary < (SELECT MAX(salary) FROM Employee);