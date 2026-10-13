# Requisitos

## Requisitos funcionais

### Métricas do desafio original
- **RF01** Identificar, por ano, a categoria com maior faturamento.
- **RF02** Identificar, por ano, a categoria com maior volume de itens vendidos.
- **RF03** Identificar, por ano, a categoria com maior nota média de avaliação.
- **RF04** Identificar, por ano, o seller com maior faturamento.
- **RF05** Identificar, por ano, o seller com maior volume de itens vendidos.
- **RF06** Identificar, por ano, o seller com maior nota média de avaliação.
- **RF07** Calcular o ticket médio por seller.

### Modelo
- **RF08** Transformar os dados no Power Query antes do Power BI, em camadas `src_` → `stg_` → `ft_`/`dm_`.
- **RF09** Modelo dimensional com tabelas fato (prefixo `ft_`) e dimensão (prefixo `dm_`).
- **RF10** Fato no grão pedido × seller × categoria, com os atributos do pedido (cliente, prazo, atraso, nota); medidas de pedido agregam por `order_id` para não contar o mesmo pedido duas vezes.

### Análise ampliada
- **RF11** Medir a relação entre faturamento, nota e prazo de entrega por seller.
- **RF12** Separar o atraso causado pelo seller do atraso no transporte.
- **RF13** Mostrar prazo, atraso e nota por região do cliente.
- **RF14** Definir um critério de "melhor seller" que combine faturamento, nota ajustada e volume mínimo de avaliações.

### Visualização
- **RF15** Insights compreensíveis à primeira vista, sem depender só de tabelas.
- **RF16** Títulos que afirmam a conclusão, e não apenas o nome do gráfico.

## Requisitos não funcionais

- **RNF01 Reprodutível:** qualquer pessoa recria o banco com `python -m codigo.ingestao.carregar_raw` e confere os números com `python -m codigo.analises.diagnostico`.
- **RNF02 Rastreável:** a camada `raw` guarda as colunas como texto, sem transformação. As regras ficam no Power Query e são conferidas em SQL (`sql/03_validacao/`).
- **RNF03 Seguro:** credenciais só no `.env`, fora do Git. O repositório traz o `.env.example`.
- **RNF04 Licença:** os CSVs (CC BY-NC-SA 4.0) não são versionados; o README indica o download.
- **RNF05 Versionável:** o relatório fica em formato PBIP (PBIR + TMDL), em arquivos de texto.
- **RNF06 Consistente:** cada número do dashboard tem um equivalente no `diagnostico.py` e nas consultas de validação.
