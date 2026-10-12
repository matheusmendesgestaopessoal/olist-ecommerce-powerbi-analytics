let
  Origem = PostgreSQL.Database("localhost:5432", "olist_db"),
  #"Navegação 1" = Origem{[Schema = "raw", Item = "product_category_translation"]}[Data]
in
  #"Navegação 1"
