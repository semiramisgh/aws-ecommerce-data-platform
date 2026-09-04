SELECT 'products' AS entity, COUNT(*) AS record_count
FROM ecommerce_clean.products

UNION ALL

SELECT 'customers' AS entity, COUNT(*) AS record_count
FROM ecommerce_clean.customers

UNION ALL

SELECT 'orders' AS entity, COUNT(*) AS record_count
FROM ecommerce_clean.orders;