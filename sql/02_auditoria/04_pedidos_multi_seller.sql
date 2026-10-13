-- =====================================================================
-- 04 | Pedidos com mais de um seller
-- Documentado: 1.278 pedidos multi-seller.
-- Decisão: faturamento atribuído por item, nunca pelo total do pedido.
-- =====================================================================
WITH sellers_por_pedido AS (
    SELECT order_id, COUNT(DISTINCT seller_id) AS n_sellers
    FROM raw.order_items
    GROUP BY order_id
)
SELECT
    COUNT(*) FILTER (WHERE n_sellers > 1) AS pedidos_multi_seller,
    MAX(n_sellers)                        AS max_sellers_no_pedido
FROM sellers_por_pedido;
