-- Analyze revenue by product category

SELECT 
    category,
    COUNT(DISTINCT order_id) AS order_count,
    SUM(quantity) AS units_sold,
    ROUND(SUM(net_amount), 2) AS total_revenue
FROM ecommerce_curated.sales
GROUP BY category
ORDER BY total_revenue DESC;