let
  Origem = src_reviews,
  #"As outras colunas foram removidas" = Table.SelectColumns(Origem, {"order_id", "review_score", "review_comment_message"}),
  #"Tipo de coluna alterado" = Table.TransformColumnTypes(#"As outras colunas foram removidas", {{"review_score", Int64.Type}})
in
  #"Tipo de coluna alterado"
