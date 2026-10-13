-- =====================================================================
-- 03 | Status dos pedidos
-- Documentado: 96.478 pedidos delivered (97,02%);
--              461 pedidos cancelados possuem itens.
-- Decisão: universo comercial = apenas 'delivered'.
-- =====================================================================
SELECT
    order_status,
    COUNT(*)                                           AS pedidos,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 2) AS pct
FROM raw.orders
GROUP BY order_status
ORDER BY pedidos DESC;

-- Pedidos NÃO entregues que mesmo assim têm itens registrados
SELECT
    o.order_status,
    COUNT(DISTINCT o.order_id) AS pedidos_com_itens
FROM raw.orders o
JOIN raw.order_items i ON i.order_id = o.order_id
WHERE o.order_status <> 'delivered'
GROUP BY o.order_status
ORDER BY pedidos_com_itens DESC;
