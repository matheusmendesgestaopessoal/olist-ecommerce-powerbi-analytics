-- =====================================================================
-- 02 | Integridade referencial
-- Documentado: nenhum órfão nas relações principais.
-- =====================================================================
SELECT 'order_items -> orders' AS relacao, COUNT(*) AS orfaos
FROM raw.order_items i LEFT JOIN raw.orders o ON o.order_id = i.order_id
WHERE o.order_id IS NULL
UNION ALL
SELECT 'order_items -> products', COUNT(*)
FROM raw.order_items i LEFT JOIN raw.products p ON p.product_id = i.product_id
WHERE p.product_id IS NULL
UNION ALL
SELECT 'order_items -> sellers', COUNT(*)
FROM raw.order_items i LEFT JOIN raw.sellers s ON s.seller_id = i.seller_id
WHERE s.seller_id IS NULL
UNION ALL
SELECT 'order_reviews -> orders', COUNT(*)
FROM raw.order_reviews r LEFT JOIN raw.orders o ON o.order_id = r.order_id
WHERE o.order_id IS NULL
UNION ALL
SELECT 'order_payments -> orders', COUNT(*)
FROM raw.order_payments pg LEFT JOIN raw.orders o ON o.order_id = pg.order_id
WHERE o.order_id IS NULL
UNION ALL
SELECT 'orders -> customers', COUNT(*)
FROM raw.orders o LEFT JOIN raw.customers c ON c.customer_id = o.customer_id
WHERE c.customer_id IS NULL;
