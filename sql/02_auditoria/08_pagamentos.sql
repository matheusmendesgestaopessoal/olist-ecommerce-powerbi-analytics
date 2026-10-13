-- =====================================================================
-- 08 | Pagamentos em várias linhas
-- Documentado: até 29 ocorrências de pagamento por pedido.
-- Decisão: payment_value NÃO é usado como faturamento de seller
--          (pertence ao pedido inteiro e inclui frete).
-- =====================================================================
WITH pagamentos_por_pedido AS (
    SELECT order_id, COUNT(*) AS n_pagamentos
    FROM raw.order_payments
    GROUP BY order_id
)
SELECT
    MAX(n_pagamentos)                        AS max_pagamentos_por_pedido,
    COUNT(*) FILTER (WHERE n_pagamentos > 1) AS pedidos_com_mais_de_um_pagamento
FROM pagamentos_por_pedido;

-- Quanto payment_value diverge de price + frete por pedido
WITH itens AS (
    SELECT order_id, SUM(price::NUMERIC + freight_value::NUMERIC) AS total_itens
    FROM raw.order_items
    GROUP BY order_id
),
pagamentos AS (
    SELECT order_id, SUM(payment_value::NUMERIC) AS total_pago
    FROM raw.order_payments
    GROUP BY order_id
)
SELECT
    COUNT(*)                                                      AS pedidos_comparados,
    COUNT(*) FILTER (WHERE ABS(p.total_pago - i.total_itens) > 1) AS pedidos_com_divergencia_acima_de_1_real
FROM itens i
JOIN pagamentos p ON p.order_id = i.order_id;
