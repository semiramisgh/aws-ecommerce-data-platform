SELECT
    c.customer_id,
    CONCAT(c.firstname, ' ', c.lastname) AS customer_name,
    COUNT(*) AS order_count,
    ROUND(SUM(o.discountedtotal), 2) AS total_revenue
FROM ecommerce_clean.orders AS o
JOIN ecommerce_clean.customers AS c
    ON o.userid = c.customer_id
GROUP BY
    c.customer_id,
    c.firstname,
    c.lastname
ORDER BY total_revenue DESC
LIMIT 10;