-- =====================================================================
-- 03 | Top 5 categorias por ano: faturamento, volume e nota média
-- "Não informado" fica fora do ranking.
-- Compare com "Campeãs por ano" e "Top 5 categorias por ano".
-- =====================================================================
WITH itens AS (
    SELECT
        i.order_id,
        p.product_category_name                                  AS categoria,
        EXTRACT(YEAR FROM o.order_purchase_timestamp::TIMESTAMP) AS ano,
        i.price::NUMERIC                                         AS price
    FROM raw.order_items i
    JOIN raw.orders   o ON o.order_id   = i.order_id
    JOIN raw.products p ON p.product_id = i.product_id
    WHERE o.order_status = 'delivered'
      AND NULLIF(TRIM(p.product_category_name), '') IS NOT NULL
),
nota_pedido AS (
    SELECT order_id, AVG(review_score::NUMERIC) AS nota
    FROM raw.order_reviews
    GROUP BY order_id
),
vendas AS (
    SELECT ano, categoria, SUM(price) AS faturamento, COUNT(*) AS itens
    FROM itens
    GROUP BY ano, categoria
),
notas AS (
    SELECT pc.ano, pc.categoria, AVG(n.nota) AS nota_media, COUNT(*) AS n_avaliacoes
    FROM (SELECT DISTINCT order_id, categoria, ano FROM itens) pc
    JOIN nota_pedido n ON n.order_id = pc.order_id
    GROUP BY pc.ano, pc.categoria
),
ranqueado AS (
    SELECT
        v.ano, v.categoria, v.faturamento, v.itens,
        ROUND(nt.nota_media, 2) AS nota_media, nt.n_avaliacoes,
        RANK() OVER (PARTITION BY v.ano ORDER BY v.faturamento DESC)            AS rk_faturamento,
        RANK() OVER (PARTITION BY v.ano ORDER BY v.itens DESC)                  AS rk_volume,
        RANK() OVER (PARTITION BY v.ano ORDER BY nt.nota_media DESC NULLS LAST) AS rk_nota
    FROM vendas v
    LEFT JOIN notas nt ON nt.ano = v.ano AND nt.categoria = v.categoria
)
SELECT * FROM ranqueado
WHERE rk_faturamento <= 5 OR rk_volume <= 5 OR rk_nota <= 5
ORDER BY ano, rk_faturamento;
