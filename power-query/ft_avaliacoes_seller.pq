let
  Origem = stg_order_items,
  #"As outras colunas foram removidas" = Table.SelectColumns(Origem, {"seller_id", "order_id"}),
  #"Duplicatas removidas" = Table.Distinct(#"As outras colunas foram removidas", {"seller_id", "order_id"}),
  #"Consultas mescladas" = Table.NestedJoin(#"Duplicatas removidas", {"order_id"}, stg_orders, {"order_id"}, "stg_orders", JoinKind.LeftOuter),
  #"Expandido stg_orders" = Table.ExpandTableColumn(#"Consultas mescladas", "stg_orders", {"order_status", "order_purchase_date"}, {"order_status", "order_purchase_date"}),
  #"Linhas filtradas" = Table.SelectRows(#"Expandido stg_orders", each ([order_status] = "delivered")),
  #"Colunas removidas" = Table.RemoveColumns(#"Linhas filtradas", {"order_status"}),
  #"Consultas mescladas 1" = Table.NestedJoin(#"Colunas removidas", {"order_id"}, stg_review_order, {"order_id"}, "stg_review_order", JoinKind.Inner),
  #"Expandido stg_review_order" = Table.ExpandTableColumn(#"Consultas mescladas 1", "stg_review_order", {"review_score_order"}, {"review_score_order"})
in
  #"Expandido stg_review_order"
