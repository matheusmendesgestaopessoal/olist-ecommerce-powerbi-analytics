-- =====================================================================
-- 09 | Preços extremos
-- Documentado: máximo R$ 6.735; P99 R$ 890.
-- Decisão: preservar. Extremo estatístico não significa erro.
-- =====================================================================
WITH itens_entregues AS (
    SELECT i.price::NUMERIC AS preco
    FROM raw.order_items i
    JOIN raw.orders o ON o.order_id = i.order_id
    WHERE o.order_status = 'delivered'
)
SELECT
    MIN(preco)                                          AS minimo,
    PERCENTILE_CONT(0.50) WITHIN GROUP (ORDER BY preco) AS mediana,
    PERCENTILE_CONT(0.99) WITHIN GROUP (ORDER BY preco) AS p99,
    MAX(preco)                                          AS maximo
FROM itens_entregues;

-- Os 10 itens mais caros e suas categorias: são plausíveis?
SELECT i.order_id, i.price::NUMERIC AS preco, p.product_category_name
FROM raw.order_items i
JOIN raw.orders   o ON o.order_id   = i.order_id
JOIN raw.products p ON p.product_id = i.product_id
WHERE o.order_status = 'delivered'
ORDER BY preco DESC
LIMIT 10;
