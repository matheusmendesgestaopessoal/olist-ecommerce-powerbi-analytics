-- =====================================================================
-- 10 | Tamanho das amostras e escala dos sellers
-- Documentado: 572 sellers com apenas 1 pedido avaliado;
--              mediana de 7 pedidos entregues por seller; máximo 1.819.
-- Decisão: nota ajustada (Empirical Bayes) como camada complementar.
-- =====================================================================
WITH pedido_seller AS (
    SELECT DISTINCT i.order_id, i.seller_id
    FROM raw.order_items i
    JOIN raw.orders o ON o.order_id = i.order_id
    WHERE o.order_status = 'delivered'
),
avaliados_por_seller AS (
    SELECT ps.seller_id, COUNT(*) AS pedidos_avaliados
    FROM pedido_seller ps
    WHERE EXISTS (SELECT 1 FROM raw.order_reviews r WHERE r.order_id = ps.order_id)
    GROUP BY ps.seller_id
)
SELECT
    COUNT(*) FILTER (WHERE pedidos_avaliados = 1)  AS sellers_com_1_pedido_avaliado,
    COUNT(*) FILTER (WHERE pedidos_avaliados < 30) AS sellers_com_menos_de_30
FROM avaliados_por_seller;

-- Distribuição de pedidos entregues por seller
WITH pedidos_por_seller AS (
    SELECT i.seller_id, COUNT(DISTINCT i.order_id) AS pedidos
    FROM raw.order_items i
    JOIN raw.orders o ON o.order_id = i.order_id
    WHERE o.order_status = 'delivered'
    GROUP BY i.seller_id
)
SELECT
    COUNT(*)                                             AS sellers_com_vendas,
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY pedidos) AS mediana_pedidos,
    PERCENTILE_CONT(0.9) WITHIN GROUP (ORDER BY pedidos) AS p90_pedidos,
    MAX(pedidos)                                         AS max_pedidos
FROM pedidos_por_seller;
