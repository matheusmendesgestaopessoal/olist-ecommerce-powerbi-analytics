let
  Origem = stg_products,
  #"As outras colunas foram removidas" = Table.SelectColumns(Origem, {"product_category_name"}),
  #"Duplicatas removidas" = Table.Distinct(#"As outras colunas foram removidas", {"product_category_name"}),
  #"Valor substituído" = Table.ReplaceValue(#"Duplicatas removidas", null, "nao_informado", Replacer.ReplaceValue, {"product_category_name"}),
  #"Colunas renomeadas" = Table.RenameColumns(#"Valor substituído", {{"product_category_name", "category_key"}}),
  #"Consultas mescladas" = Table.NestedJoin(#"Colunas renomeadas", {"category_key"}, src_category_translation, {"product_category_name"}, "src_category_translation", JoinKind.LeftOuter),
  #"Expandido src_category_translation" = Table.ExpandTableColumn(#"Consultas mescladas", "src_category_translation", {"product_category_name_english"}, {"product_category_name_english"}),
  #"Colunas renomeadas 1" = Table.RenameColumns(#"Expandido src_category_translation", {{"product_category_name_english", "category_name_english"}}),
  #"Personalização adicionada" = Table.AddColumn(#"Colunas renomeadas 1", "category_display", each if [category_key] = "pc_gamer" then "PC Gamer"
else if [category_key] = "portateis_cozinha_e_preparadores_de_alimentos" then "Portable Kitchen and Food Preparation Appliances"
else if [category_key] = "nao_informado" then "Não informado"
else [category_name_english]),
  #"Personalização adicionada 1" = Table.AddColumn(#"Personalização adicionada", "ranking_eligible", each if [category_key] = "nao_informado" then false else true),
  #"Tipo de coluna alterado" = Table.TransformColumnTypes(#"Personalização adicionada 1", {{"ranking_eligible", type logical}}),
  #"Personalização adicionada 2" = Table.TransformColumnTypes(Table.AddColumn(#"Tipo de coluna alterado", "category_display_pt", each Text.Proper(
    Text.Replace(
        [category_key],
        "_",
        " "
    )
)), {{"category_display_pt", type text}})
in
  #"Personalização adicionada 2"
