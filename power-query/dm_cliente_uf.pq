let
  Regioes = [Sudeste = 1, Sul = 2, #"Centro-Oeste" = 3, Nordeste = 4, Norte = 5],
  Estados = #table(type table [uf = text, estado = text, regiao = text], {
      {"SP", "São Paulo", "Sudeste"}, {"RJ", "Rio de Janeiro", "Sudeste"}, {"MG", "Minas Gerais", "Sudeste"}, {"ES", "Espírito Santo", "Sudeste"},
      {"PR", "Paraná", "Sul"}, {"SC", "Santa Catarina", "Sul"}, {"RS", "Rio Grande do Sul", "Sul"},
      {"DF", "Distrito Federal", "Centro-Oeste"}, {"GO", "Goiás", "Centro-Oeste"}, {"MT", "Mato Grosso", "Centro-Oeste"}, {"MS", "Mato Grosso do Sul", "Centro-Oeste"},
      {"BA", "Bahia", "Nordeste"}, {"PE", "Pernambuco", "Nordeste"}, {"CE", "Ceará", "Nordeste"}, {"MA", "Maranhão", "Nordeste"},
      {"PB", "Paraíba", "Nordeste"}, {"RN", "Rio Grande do Norte", "Nordeste"}, {"AL", "Alagoas", "Nordeste"}, {"PI", "Piauí", "Nordeste"}, {"SE", "Sergipe", "Nordeste"},
      {"PA", "Pará", "Norte"}, {"AM", "Amazonas", "Norte"}, {"TO", "Tocantins", "Norte"}, {"RO", "Rondônia", "Norte"},
      {"AC", "Acre", "Norte"}, {"AP", "Amapá", "Norte"}, {"RR", "Roraima", "Norte"}}),
  Ordem = Table.AddColumn(Estados, "regiao_ordem", each Record.Field(Regioes, [regiao]), Int64.Type)
in
  Ordem
