-- Question:
-- Count number of employees in each department.

SELECT department_id, COUNT(*) AS employee_count
FROM Employee
GROUP BY department_id;