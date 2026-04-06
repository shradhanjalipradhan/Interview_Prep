-- Question:
-- Find duplicate emails in a table.

-- Table:
-- Users(id, email)

-- Solution:
SELECT email, COUNT(*) as count
FROM Users
GROUP BY email
HAVING COUNT(*) > 1;