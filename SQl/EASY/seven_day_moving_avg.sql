SELECT   OrderDate,
         SUM(TotalAmount) AS DailySales,
         AVG(SUM(TotalAmount)) OVER (
             ORDER BY OrderDate
             ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
             ) AS MovingAvg7Days
FROM     Orders
GROUP BY OrderDate
ORDER BY OrderDate;