-- =====================================================================
-- 05 | Ticket médio por seller (período completo)
-- Regra: receita própria do seller / pedidos distintos entregues em que
--        participou. Ex.: 4869f7... = R$ 226.987,93 / 1.124 = R$ 201,95
-- =====================================================================
SELECT
    i.seller_id,
    s.seller_state                                               AS uf,
    SUM(i.price::NUMERIC)                                        AS faturamento,
    COUNT(DISTINCT i.order_id)                                   AS pedidos,
    COUNT(*)                                                     AS itens,
    ROUND(SUM(i.price::NUMERIC) / COUNT(DISTINCT i.order_id), 2) AS ticket_medio
FROM raw.order_items i
JOIN raw.orders  o ON o.order_id  = i.order_id
JOIN raw.sellers s ON s.seller_id = i.seller_id
WHERE o.order_status = 'delivered'
GROUP BY i.seller_id, s.seller_state
ORDER BY faturamento DESC
LIMIT 15;
