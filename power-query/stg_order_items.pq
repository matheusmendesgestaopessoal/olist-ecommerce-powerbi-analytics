let
  Origem = src_order_items,
  #"As outras colunas foram removidas" = Table.SelectColumns(Origem, {"order_id", "order_item_id", "product_id", "seller_id", "price", "freight_value"}),
  #"Tipo de coluna alterado" = Table.TransformColumnTypes(#"As outras colunas foram removidas", {{"order_item_id", Int64.Type}}),
  #"O tipo de coluna foi alterado com a localidade" = Table.TransformColumnTypes(#"Tipo de coluna alterado", {{"price", type number}}, "en-US"),
  #"O tipo de coluna foi alterado com a localidade 1" = Table.TransformColumnTypes(#"O tipo de coluna foi alterado com a localidade", {{"freight_value", type number}}, "en-US")
in
  #"O tipo de coluna foi alterado com a localidade 1"
