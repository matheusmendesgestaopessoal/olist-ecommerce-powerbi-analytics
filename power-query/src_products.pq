let
  Origem = PostgreSQL.Database("localhost:5432", "olist"),
  #"Navegação 1" = Origem{[Schema = "raw", Item = "products"]}[Data]
in
  #"Navegação 1"
