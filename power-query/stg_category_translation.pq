let
  Origem = src_category_translation,
  #"Texto limpo" = Table.TransformColumns(Origem, {{"product_category_name", each Text.Clean(_), type nullable text}, {"product_category_name_english", each Text.Clean(_), type nullable text}})
in
  #"Texto limpo"
