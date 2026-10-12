let
  Origem = src_orders,
  #"As outras colunas foram removidas" = Table.SelectColumns(Origem, {"order_id", "order_status", "order_purchase_timestamp"}),
  #"Tipo de coluna alterado" = Table.TransformColumnTypes(#"As outras colunas foram removidas", {{"order_purchase_timestamp", type datetime}}),
  #"Coluna duplicada" = Table.DuplicateColumn(#"Tipo de coluna alterado", "order_purchase_timestamp", "order_purchase_timestamp – Cópia"),
  #"Tipo de coluna alterado 1" = Table.TransformColumnTypes(#"Coluna duplicada", {{"order_purchase_timestamp – Cópia", type date}}),
  #"Colunas renomeadas" = Table.RenameColumns(#"Tipo de coluna alterado 1", {{"order_purchase_timestamp – Cópia", "order_purchase_date"}})
in
  #"Colunas renomeadas"
