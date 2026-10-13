-- =====================================================================
-- 02 | Reconciliação das fatos de avaliação
-- ft_avaliacoes_seller:    1 linha = 1 pedido-seller avaliado
-- ft_avaliacoes_categoria: 1 linha = 1 pedido-categoria avaliada
-- Dashboard: 95.832 pedidos avaliados | nota média geral 4,16
-- =====================================================================
WITH nota_pedido AS (
    SELECT order_id, AVG(review_score::NUMERIC) AS nota
    FROM raw.order_reviews
    GROUP BY order_id
),
itens_entregues AS (
    SELECT
        i.order_id,
        i.seller_id,
        COALESCE(NULLIF(TRIM(p.product_category_name), ''), 'nao_informado') AS categoria
    FROM raw.order_items i
    JOIN raw.orders o        ON o.order_id   = i.order_id
    LEFT JOIN raw.products p ON p.product_id = i.product_id
    WHERE o.order_status = 'delivered'
),
ft_avaliacoes_seller AS (
    SELECT DISTINCT ie.order_id, ie.seller_id, n.nota
    FROM itens_entregues ie
    JOIN nota_pedido n ON n.order_id = ie.order_id   -- inner: pedido sem review não tem nota
),
ft_avaliacoes_categoria AS (
    SELECT DISTINCT ie.order_id, ie.categoria, n.nota
    FROM itens_entregues ie
    JOIN nota_pedido n ON n.order_id = ie.order_id
)
SELECT 'ft_avaliacoes_seller' AS fato,
       COUNT(*)                                         AS linhas,
       COUNT(DISTINCT order_id)                         AS pedidos_distintos,
       COUNT(*) - COUNT(DISTINCT (order_id, seller_id)) AS duplicados_na_granularidade
FROM ft_avaliacoes_seller
UNION ALL
SELECT 'ft_avaliacoes_categoria',
       COUNT(*),
       COUNT(DISTINCT order_id),
       COUNT(*) - COUNT(DISTINCT (order_id, categoria))
FROM ft_avaliacoes_categoria;

-- Resumo das notas no nível do pedido (seção 06 do dashboard)
WITH nota_pedido AS (
    SELECT r.order_id, AVG(r.review_score::NUMERIC) AS nota
    FROM raw.order_reviews r
    JOIN raw.orders o ON o.order_id = r.order_id
    WHERE o.order_status = 'delivered'
    GROUP BY r.order_id
)
SELECT
    COUNT(*)                                                       AS pedidos_avaliados,
    ROUND(AVG(nota), 2)                                            AS nota_media,
    ROUND(100.0 * COUNT(*) FILTER (WHERE nota >= 4) / COUNT(*), 2) AS pct_notas_4_a_5,
    ROUND(100.0 * COUNT(*) FILTER (WHERE nota = 1)  / COUNT(*), 2) AS pct_nota_1
FROM nota_pedido;
