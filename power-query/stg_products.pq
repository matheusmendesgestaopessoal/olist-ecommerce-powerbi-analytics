let
  Origem = src_products,
  #"As outras colunas foram removidas" = Table.SelectColumns(Origem, {"product_id", "product_category_name"}),
  #"Texto limpo" = Table.TransformColumns(#"As outras colunas foram removidas", {{"product_category_name", each Text.Clean(_), type nullable text}})
in
  #"Texto limpo"
