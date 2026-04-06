-- Question:
-- Merge two tables (Orders and Customers) to get customer name and order amount.

SELECT c.name, o.amount
FROM Customers c
JOIN Orders o ON c.id = o.customer_id;