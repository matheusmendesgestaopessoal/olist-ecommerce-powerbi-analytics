-- =====================================================================
-- 07 | Concentração: quanto do faturamento vem dos 10% maiores sellers
-- Documentado: 67% (R$ 8,86 Mi de R$ 13,22 Mi)
-- =====================================================================
WITH fat_seller AS (
    SELECT i.seller_id, SUM(i.price::NUMERIC) AS faturamento
    FROM raw.order_items i
    JOIN raw.orders o ON o.order_id = i.order_id
    WHERE o.order_status = 'delivered'
    GROUP BY i.seller_id
),
ordenado AS (
    SELECT
        faturamento,
        ROW_NUMBER() OVER (ORDER BY faturamento DESC) AS posicao,
        COUNT(*) OVER ()                              AS total_sellers
    FROM fat_seller
)
SELECT
    SUM(faturamento) FILTER (WHERE posicao <= CEIL(total_sellers * 0.10)) AS faturamento_top10pct,
    SUM(faturamento)                                                      AS faturamento_total,
    ROUND(100.0 * SUM(faturamento) FILTER (WHERE posicao <= CEIL(total_sellers * 0.10))
          / SUM(faturamento), 2)                                          AS pct_top10
FROM ordenado;
