-- =====================================================================
-- 06 | Produtos sem categoria e categorias sem tradução
-- Documentado: 610 produtos sem categoria; 1.537 itens entregues;
--              R$ 170.726,63.
-- Decisão: manter nos totais como "Não informado", fora dos rankings.
-- =====================================================================
SELECT COUNT(*) AS produtos_sem_categoria
FROM raw.products
WHERE NULLIF(TRIM(product_category_name), '') IS NULL;

SELECT
    COUNT(*)              AS itens_entregues_sem_categoria,
    SUM(i.price::NUMERIC) AS faturamento_sem_categoria
FROM raw.order_items i
JOIN raw.orders   o ON o.order_id   = i.order_id
JOIN raw.products p ON p.product_id = i.product_id
WHERE o.order_status = 'delivered'
  AND NULLIF(TRIM(p.product_category_name), '') IS NULL;

-- Categorias sem correspondência na tabela de tradução
-- (justifica o LEFT OUTER JOIN no Power Query)
SELECT DISTINCT p.product_category_name
FROM raw.products p
LEFT JOIN raw.product_category_name_translation t
       ON t.product_category_name = p.product_category_name
WHERE t.product_category_name IS NULL
  AND NULLIF(TRIM(p.product_category_name), '') IS NOT NULL;
