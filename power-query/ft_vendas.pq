let
  Origem = stg_order_items,
  #"Consultas mescladas" = Table.NestedJoin(Origem, {"order_id"}, stg_orders, {"order_id"}, "stg_orders", JoinKind.LeftOuter),
  #"Expandido stg_orders" = Table.ExpandTableColumn(#"Consultas mescladas", "stg_orders", {"order_status", "order_purchase_date"}, {"order_status", "order_purchase_date"}),
  #"Linhas filtradas" = Table.SelectRows(#"Expandido stg_orders", each ([order_status] = "delivered")),
  #"Colunas removidas" = Table.RemoveColumns(#"Linhas filtradas", {"order_status"}),
  #"Consultas mescladas 1" = Table.NestedJoin(#"Colunas removidas", {"product_id"}, stg_products, {"product_id"}, "stg_products", JoinKind.LeftOuter),
  #"Expandido stg_products" = Table.ExpandTableColumn(#"Consultas mescladas 1", "stg_products", {"product_category_name"}, {"product_category_name"}),
  #"Valor substituído" = Table.ReplaceValue(#"Expandido stg_products", null, "nao_informado", Replacer.ReplaceValue, {"product_category_name"}),
  #"Colunas renomeadas" = Table.RenameColumns(#"Valor substituído", {{"product_category_name", "category_key"}}),
  #"Personalização adicionada" = Table.TransformColumnTypes(Table.AddColumn(#"Colunas renomeadas", "category_display_pt", each Text.Proper(
    Text.Replace(
        [category_key],
        "_",
        " "
    )
)), {{"category_display_pt", type text}})
in
  #"Personalização adicionada"
