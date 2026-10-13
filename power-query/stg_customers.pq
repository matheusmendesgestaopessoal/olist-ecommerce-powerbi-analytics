let
  Origem = src_customers,
  #"As outras colunas foram removidas" = Table.SelectColumns(Origem, {"customer_id", "customer_state"}),
  #"Texto limpo" = Table.TransformColumns(#"As outras colunas foram removidas", {{"customer_state", each Text.Upper(Text.Clean(_)), type nullable text}})
in
  #"Texto limpo"
