-- Find the top 10 products by net revenue

SELECT 
    product_title,
    category,
    SUM(quantity) AS units_sold,
    ROUND(SUM(net_amount), 2) AS total_revenue
FROM ecommerce_curated.sales
GROUP BY product_title, category
ORDER BY total_revenue DESC
LIMIT 10;