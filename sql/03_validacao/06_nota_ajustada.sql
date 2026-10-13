-- =====================================================================
-- 06 | Nota ajustada (Empirical Bayes) por seller e ano
--   nota_ajustada = n/(n+m) * nota_media + m/(n+m) * media_do_ano
-- m usado no projeto: 13,88 (sellers) | 16,36 (categorias)
-- media_do_ano = média de todas as linhas pedido-seller avaliadas no ano
-- =====================================================================
WITH params AS (SELECT 13.88::NUMERIC AS m),
nota_pedido AS (
    SELECT order_id, AVG(review_score::NUMERIC) AS nota
    FROM raw.order_reviews
    GROUP BY order_id
),
pedido_seller AS (
    SELECT DISTINCT
        i.order_id,
        i.seller_id,
        EXTRACT(YEAR FROM o.order_purchase_timestamp::TIMESTAMP) AS ano
    FROM raw.order_items i
    JOIN raw.orders o ON o.order_id = i.order_id
    WHERE o.order_status = 'delivered'
),
avaliacoes AS (
    SELECT ps.ano, ps.seller_id, n.nota
    FROM pedido_seller ps
    JOIN nota_pedido n ON n.order_id = ps.order_id
),
media_ano AS (
    SELECT ano, AVG(nota) AS media_ano FROM avaliacoes GROUP BY ano
),
por_seller AS (
    SELECT ano, seller_id, COUNT(*) AS n, AVG(nota) AS nota_media
    FROM avaliacoes
    GROUP BY ano, seller_id
)
SELECT
    s.ano,
    s.seller_id,
    s.n                                       AS n_avaliacoes,
    ROUND(s.nota_media, 2)                    AS nota_media,
    ROUND(  (s.n / (s.n + p.m)) * s.nota_media
          + (p.m / (s.n + p.m)) * a.media_ano, 2) AS nota_ajustada
FROM por_seller s
JOIN media_ano a ON a.ano = s.ano
CROSS JOIN params p
ORDER BY s.ano, nota_ajustada DESC;
