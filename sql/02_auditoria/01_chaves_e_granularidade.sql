-- =====================================================================
-- 01 | Chaves e granularidade
-- Pergunta: o que cada linha representa? Existem chaves duplicadas?
-- Esperado: 0 duplicados nas chaves candidatas.
-- Atenção: review_id NÃO é único sozinho no Olist.
-- =====================================================================
SELECT 'orders.order_id' AS chave, COUNT(*) - COUNT(DISTINCT order_id) AS duplicados FROM raw.orders
UNION ALL
SELECT 'order_items (order_id, order_item_id)',         COUNT(*) - COUNT(DISTINCT (order_id, order_item_id))      FROM raw.order_items
UNION ALL
SELECT 'order_payments (order_id, payment_sequential)', COUNT(*) - COUNT(DISTINCT (order_id, payment_sequential)) FROM raw.order_payments
UNION ALL
SELECT 'order_reviews.review_id',                       COUNT(*) - COUNT(DISTINCT review_id)                      FROM raw.order_reviews
UNION ALL
SELECT 'order_reviews (review_id, order_id)',           COUNT(*) - COUNT(DISTINCT (review_id, order_id))          FROM raw.order_reviews
UNION ALL
SELECT 'products.product_id',                           COUNT(*) - COUNT(DISTINCT product_id)                     FROM raw.products
UNION ALL
SELECT 'sellers.seller_id',                             COUNT(*) - COUNT(DISTINCT seller_id)                      FROM raw.sellers
UNION ALL
SELECT 'customers.customer_id',                         COUNT(*) - COUNT(DISTINCT customer_id)                    FROM raw.customers;

-- Volume de linhas por tabela
SELECT 'orders' AS tabela, COUNT(*) AS linhas FROM raw.orders
UNION ALL SELECT 'order_items',    COUNT(*) FROM raw.order_items
UNION ALL SELECT 'order_payments', COUNT(*) FROM raw.order_payments
UNION ALL SELECT 'order_reviews',  COUNT(*) FROM raw.order_reviews
UNION ALL SELECT 'products',       COUNT(*) FROM raw.products
UNION ALL SELECT 'sellers',        COUNT(*) FROM raw.sellers
UNION ALL SELECT 'customers',      COUNT(*) FROM raw.customers;
