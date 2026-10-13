-- =====================================================================
-- 04 | Top 5 sellers por ano: faturamento, volume e nota média SIMPLES
-- n_avaliacoes aparece ao lado para evidenciar o efeito de amostras
-- pequenas: com média simples, sellers com 1 avaliação nota 5 lideram.
-- Use para conferir qual nota o ranking do dashboard está usando.
-- =====================================================================
WITH itens AS (
    SELECT
        i.order_id,
        i.seller_id,
        EXTRACT(YEAR FROM o.order_purchase_timestamp::TIMESTAMP) AS ano,
        i.price::NUMERIC                                         AS price
    FROM raw.order_items i
    JOIN raw.orders o ON o.order_id = i.order_id
    WHERE o.order_status = 'delivered'
),
nota_pedido AS (
    SELECT order_id, AVG(review_score::NUMERIC) AS nota
    FROM raw.order_reviews
    GROUP BY order_id
),
vendas AS (
    SELECT ano, seller_id, SUM(price) AS faturamento, COUNT(*) AS itens
    FROM itens
    GROUP BY ano, seller_id
),
notas AS (
    SELECT ps.ano, ps.seller_id, AVG(n.nota) AS nota_media, COUNT(*) AS n_avaliacoes
    FROM (SELECT DISTINCT order_id, seller_id, ano FROM itens) ps
    JOIN nota_pedido n ON n.order_id = ps.order_id
    GROUP BY ps.ano, ps.seller_id
),
ranqueado AS (
    SELECT
        v.ano, v.seller_id, v.faturamento, v.itens,
        ROUND(nt.nota_media, 2) AS nota_media, nt.n_avaliacoes,
        RANK() OVER (PARTITION BY v.ano ORDER BY v.faturamento DESC)            AS rk_faturamento,
        RANK() OVER (PARTITION BY v.ano ORDER BY v.itens DESC)                  AS rk_volume,
        RANK() OVER (PARTITION BY v.ano ORDER BY nt.nota_media DESC NULLS LAST) AS rk_nota
    FROM vendas v
    LEFT JOIN notas nt ON nt.ano = v.ano AND nt.seller_id = v.seller_id
)
SELECT * FROM ranqueado
WHERE rk_faturamento <= 5 OR rk_volume <= 5 OR rk_nota <= 5
ORDER BY ano, rk_faturamento;
