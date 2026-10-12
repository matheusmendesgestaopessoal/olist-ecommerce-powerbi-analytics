let
  Origem = stg_order_items,
  #"As outras colunas foram removidas" = Table.SelectColumns(Origem, {"order_id", "product_id"}),
  #"Consultas mescladas" = Table.NestedJoin(#"As outras colunas foram removidas", {"product_id"}, stg_products, {"product_id"}, "stg_products", JoinKind.LeftOuter),
  #"Expandido stg_products" = Table.ExpandTableColumn(#"Consultas mescladas", "stg_products", {"product_category_name"}, {"product_category_name"}),
  #"Valor substituído" = Table.ReplaceValue(#"Expandido stg_products", null, "nao_informado", Replacer.ReplaceValue, {"product_category_name"}),
  #"Colunas renomeadas" = Table.RenameColumns(#"Valor substituído", {{"product_category_name", "category_key"}}),
  #"Colunas removidas" = Table.RemoveColumns(#"Colunas renomeadas", {"product_id"}),
  #"Duplicatas removidas" = Table.Distinct(#"Colunas removidas", {"order_id", "category_key"}),
  #"Consultas mescladas 1" = Table.NestedJoin(#"Duplicatas removidas", {"order_id"}, stg_orders, {"order_id"}, "stg_orders", JoinKind.LeftOuter),
  #"Expandido stg_orders" = Table.ExpandTableColumn(#"Consultas mescladas 1", "stg_orders", {"order_status", "order_purchase_date"}, {"order_status", "order_purchase_date"}),
  #"Linhas filtradas" = Table.SelectRows(#"Expandido stg_orders", each ([order_status] = "delivered")),
  #"Colunas removidas 1" = Table.RemoveColumns(#"Linhas filtradas", {"order_status"}),
  #"Consultas mescladas 2" = Table.NestedJoin(#"Colunas removidas 1", {"order_id"}, stg_review_order, {"order_id"}, "stg_review_order", JoinKind.Inner),
  #"Expandido stg_review_order" = Table.ExpandTableColumn(#"Consultas mescladas 2", "stg_review_order", {"review_score_order"}, {"review_score_order"}),
  #"Personalização adicionada" = Table.TransformColumnTypes(Table.AddColumn(#"Expandido stg_review_order", "category_display_pt", each Text.Proper(
    Text.Replace(
        [category_key],
        "_",
        " "
    )
)), {{"category_display_pt", type text}})
in
  #"Personalização adicionada"
