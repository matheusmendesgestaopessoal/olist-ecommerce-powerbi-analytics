let
  Origem = src_orders,
  #"As outras colunas foram removidas" = Table.SelectColumns(Origem, {"order_id", "customer_id", "order_status", "order_purchase_timestamp", "order_delivered_carrier_date", "order_delivered_customer_date", "order_estimated_delivery_date"}),
  #"Vazios como nulo" = Table.ReplaceValue(#"As outras colunas foram removidas", "", null, Replacer.ReplaceValue, {"order_delivered_carrier_date", "order_delivered_customer_date", "order_estimated_delivery_date"}),
  #"Tipo de coluna alterado" = Table.TransformColumnTypes(#"Vazios como nulo", {{"order_purchase_timestamp", type datetime}, {"order_delivered_carrier_date", type datetime}, {"order_delivered_customer_date", type datetime}, {"order_estimated_delivery_date", type datetime}}),
  #"Coluna duplicada" = Table.DuplicateColumn(#"Tipo de coluna alterado", "order_purchase_timestamp", "order_purchase_timestamp – Cópia"),
  #"Tipo de coluna alterado 1" = Table.TransformColumnTypes(#"Coluna duplicada", {{"order_purchase_timestamp – Cópia", type date}}),
  #"Colunas renomeadas" = Table.RenameColumns(#"Tipo de coluna alterado 1", {{"order_purchase_timestamp – Cópia", "order_purchase_date"}})
in
  #"Colunas renomeadas"
