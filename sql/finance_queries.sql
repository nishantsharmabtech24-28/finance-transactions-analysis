-- Finance project: corrected SQL queries (SQLite)
-- Step 0: clean view. Fixes inconsistent case, extra spaces, and 15 duplicate rows.
DROP VIEW IF EXISTS clean_transactions;
CREATE VIEW clean_transactions AS
SELECT DISTINCT
    transaction_id,
    date,
    CASE UPPER(TRIM(department))
        WHEN 'HR' THEN 'HR' WHEN 'IT' THEN 'IT' WHEN 'R&D' THEN 'R&D'
        ELSE UPPER(SUBSTR(TRIM(department),1,1)) || LOWER(SUBSTR(TRIM(department),2))
    END AS department,
    UPPER(SUBSTR(TRIM(region),1,1)) || LOWER(SUBSTR(TRIM(region),2)) AS region,
    TRIM(type) AS type,
    TRIM(category) AS category,
    amount
FROM company_finance_transactions;

-- Q0: sanity check (expect 1175 rows)
SELECT COUNT(*) AS rows_after_cleaning FROM clean_transactions;

-- Q1: total expense by department
SELECT department, ROUND(SUM(amount),2) AS total_expense
FROM clean_transactions WHERE type='Expense'
GROUP BY department ORDER BY total_expense DESC;

-- Q2: monthly revenue, expense and net
SELECT SUBSTR(date,1,7) AS month,
       ROUND(SUM(CASE WHEN type='Revenue' THEN amount ELSE 0 END),2) AS total_revenue,
       ROUND(SUM(CASE WHEN type='Expense' THEN amount ELSE 0 END),2) AS total_expense,
       ROUND(SUM(CASE WHEN type='Revenue' THEN amount ELSE -amount END),2) AS net
FROM clean_transactions GROUP BY month ORDER BY month;

-- Q3: revenue, expense, net and margin by region
SELECT region,
       ROUND(SUM(CASE WHEN type='Revenue' THEN amount ELSE 0 END),2) AS revenue,
       ROUND(SUM(CASE WHEN type='Expense' THEN amount ELSE 0 END),2) AS expense,
       ROUND(SUM(CASE WHEN type='Revenue' THEN amount ELSE -amount END),2) AS net,
       ROUND(100.0*SUM(CASE WHEN type='Revenue' THEN amount ELSE -amount END)
             /SUM(CASE WHEN type='Revenue' THEN amount END),1) AS margin_pct
FROM clean_transactions GROUP BY region ORDER BY net DESC;

-- Q4: expense categories (count and average)
SELECT category, COUNT(*) AS num_transactions, ROUND(AVG(amount),2) AS avg_amount,
       ROUND(SUM(amount),2) AS total
FROM clean_transactions WHERE type='Expense'
GROUP BY category ORDER BY total DESC;

-- Q5 (FIXED): top department-region combinations by net = revenue MINUS expense
-- The old query added expense instead of subtracting it.
SELECT department, region,
       ROUND(SUM(CASE WHEN type='Revenue' THEN amount ELSE -amount END),2) AS net
FROM clean_transactions
GROUP BY department, region ORDER BY net DESC LIMIT 10;

-- Q6: revenue by category
SELECT category, COUNT(*) AS num_transactions, ROUND(SUM(amount),2) AS total_revenue
FROM clean_transactions WHERE type='Revenue'
GROUP BY category ORDER BY total_revenue DESC;

-- Q7: year-over-year comparison
SELECT SUBSTR(date,1,4) AS year,
       ROUND(SUM(CASE WHEN type='Revenue' THEN amount ELSE 0 END),2) AS revenue,
       ROUND(SUM(CASE WHEN type='Expense' THEN amount ELSE 0 END),2) AS expense,
       ROUND(SUM(CASE WHEN type='Revenue' THEN amount ELSE -amount END),2) AS net
FROM clean_transactions GROUP BY year ORDER BY year;

-- Q8: department profitability (revenue, expense, net, margin)
SELECT department,
       ROUND(SUM(CASE WHEN type='Revenue' THEN amount ELSE 0 END),2) AS revenue,
       ROUND(SUM(CASE WHEN type='Expense' THEN amount ELSE 0 END),2) AS expense,
       ROUND(SUM(CASE WHEN type='Revenue' THEN amount ELSE -amount END),2) AS net,
       ROUND(100.0*SUM(CASE WHEN type='Revenue' THEN amount ELSE -amount END)
             /SUM(CASE WHEN type='Revenue' THEN amount END),1) AS margin_pct
FROM clean_transactions GROUP BY department ORDER BY net DESC;

-- Q9: loss-making months
SELECT month, net FROM (
  SELECT SUBSTR(date,1,7) AS month,
         ROUND(SUM(CASE WHEN type='Revenue' THEN amount ELSE -amount END),2) AS net
  FROM clean_transactions GROUP BY month)
WHERE net < 0;

-- Q10: the 10 largest transactions (a quick check for outliers)
SELECT transaction_id, date, department, region, type, category, amount
FROM clean_transactions ORDER BY amount DESC LIMIT 10;
