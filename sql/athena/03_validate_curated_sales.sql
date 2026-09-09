-- Validate the curated sales dataset

SELECT 
    COUNT(*) AS line_item_count,
    COUNT(DISTINCT order_id) AS order_count,
    ROUND(SUM(net_amount), 2) AS total_revenue
FROM ecommerce_curated.sales;