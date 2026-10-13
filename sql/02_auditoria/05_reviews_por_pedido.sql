-- =====================================================================
-- 05 | Pedidos com várias reviews
-- Documentado: 547 pedidos com mais de uma review; 202 com notas diferentes.
-- Decisão: consolidar UMA nota por pedido (média) antes de ligar a
--          sellers e categorias.
-- =====================================================================
WITH reviews_por_pedido AS (
    SELECT
        order_id,
        COUNT(*)                     AS n_reviews,
        COUNT(DISTINCT review_score) AS n_notas_distintas
    FROM raw.order_reviews
    GROUP BY order_id
)
SELECT
    COUNT(*) FILTER (WHERE n_reviews > 1)         AS pedidos_com_varias_reviews,
    COUNT(*) FILTER (WHERE n_notas_distintas > 1) AS pedidos_com_notas_diferentes,
    MAX(n_reviews)                                AS max_reviews_por_pedido
FROM reviews_por_pedido;

-- Demonstração do risco: join direto itens x reviews infla as linhas
SELECT
    (SELECT COUNT(*) FROM raw.order_items)                  AS linhas_itens,
    (SELECT COUNT(*) FROM raw.order_items i
       JOIN raw.order_reviews r ON r.order_id = i.order_id) AS linhas_apos_join_direto;
