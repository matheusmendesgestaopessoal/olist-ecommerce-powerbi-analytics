let
  Origem = src_sellers,
  #"As outras colunas foram removidas" = Table.SelectColumns(Origem, {"seller_id", "seller_city", "seller_state"}),
  #"Texto limpo" = Table.TransformColumns(#"As outras colunas foram removidas", {{"seller_id", each Text.Clean(_), type nullable text}, {"seller_city", each Text.Clean(_), type nullable text}, {"seller_state", each Text.Clean(_), type nullable text}})
in
  #"Texto limpo"
