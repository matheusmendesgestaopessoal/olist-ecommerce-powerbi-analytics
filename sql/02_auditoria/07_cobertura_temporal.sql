-- =====================================================================
-- 07 | Cobertura temporal
-- Documentado: 2016 com 329 pedidos; nenhum pedido entregue após ago/2018.
-- Decisão: 2016 e 2018 tratados como parciais; comparar ritmo mensal.
-- =====================================================================
SELECT
    EXTRACT(YEAR FROM order_purchase_timestamp::TIMESTAMP) AS ano,
    COUNT(*)                                               AS pedidos,
    COUNT(*) FILTER (WHERE order_status = 'delivered')     AS pedidos_entregues,
    MIN(order_purchase_timestamp::TIMESTAMP)::DATE         AS primeira_compra,
    MAX(order_purchase_timestamp::TIMESTAMP)::DATE         AS ultima_compra
FROM raw.orders
GROUP BY 1
ORDER BY 1;

-- Pedidos entregues por mês (identifica meses vazios ou residuais)
SELECT
    DATE_TRUNC('month', order_purchase_timestamp::TIMESTAMP)::DATE AS mes,
    COUNT(*)                                                       AS pedidos_entregues
FROM raw.orders
WHERE order_status = 'delivered'
GROUP BY 1
ORDER BY 1;
