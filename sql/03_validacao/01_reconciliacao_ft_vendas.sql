-- =====================================================================
-- 01 | Reconciliação da ft_vendas (1 linha = 1 item entregue)
-- Compare cada número com o cartão/medida equivalente no Power BI.
-- Dashboard: R$ 13,22 Mi | 110 mil itens | 96 mil pedidos | ticket R$ 137
-- =====================================================================
WITH ft_vendas AS (
    SELECT
        i.order_id,
        i.seller_id,
        COALESCE(NULLIF(TRIM(p.product_category_name), ''), 'nao_informado') AS categoria,
        EXTRACT(YEAR FROM o.order_purchase_timestamp::TIMESTAMP)             AS ano,
        i.price::NUMERIC                                                     AS price
    FROM raw.order_items i
    JOIN raw.orders o        ON o.order_id   = i.order_id
    LEFT JOIN raw.products p ON p.product_id = i.product_id
    WHERE o.order_status = 'delivered'
)
SELECT
    COALESCE(ano::TEXT, 'TOTAL')                    AS ano,
    COUNT(*)                                        AS itens,
    COUNT(DISTINCT order_id)                        AS pedidos,
    SUM(price)                                      AS faturamento,
    ROUND(SUM(price) / COUNT(DISTINCT order_id), 2) AS ticket_medio_geral,
    COUNT(DISTINCT seller_id)                       AS sellers,
    COUNT(DISTINCT categoria)                       AS categorias
FROM ft_vendas
GROUP BY ROLLUP (ano)
ORDER BY ano;
