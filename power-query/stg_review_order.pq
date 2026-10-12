let
  Origem = stg_reviews,
  #"Linhas agrupadas" = Table.Group(Origem, {"order_id"}, {{"review_score_order", each List.Average([review_score]), type nullable number}})
in
  #"Linhas agrupadas"
