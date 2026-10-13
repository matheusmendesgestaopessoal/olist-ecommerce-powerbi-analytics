# Dados

Os CSVs não são versionados neste repositório (121 MB e licença própria).

1. Baixe o dataset **Brazilian E-Commerce Public Dataset by Olist**: https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce
2. Extraia os 9 arquivos `.csv` em `dados/brutos/`.
3. Carregue no PostgreSQL: `python -m codigo.ingestao.carregar_raw`

Licença dos dados: CC BY-NC-SA 4.0 (Olist). Dados reais e anonimizados de pedidos de 2016 a 2018.
