-- Question:
-- Find the second highest salary from Employee table.
-- Employee(id, salary)

SELECT MAX(salary) AS SecondHighestSalary
FROM Employee
WHERE salary < (SELECT MAX(salary) FROM Employee);