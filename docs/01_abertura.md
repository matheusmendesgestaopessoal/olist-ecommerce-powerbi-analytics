# Abertura do Projeto · Olist E-Commerce

**Autor:** Matheus Mendes · **Dados:** Brazilian E-Commerce Public Dataset by Olist (Kaggle) · **Período:** set/2016 a ago/2018

---

## 1. Contexto

A Olist conecta pequenos e médios lojistas (sellers) aos grandes marketplaces brasileiros. O dataset público reúne cerca de 99 mil pedidos reais e anonimizados, com itens, vendedores, produtos, pagamentos, avaliações dos clientes e datas de cada etapa da entrega.

O projeto nasceu de um desafio técnico para uma vaga de analista de dados. O desafio pedia para identificar, ano a ano, as melhores categorias e os melhores sellers sob três perspectivas (faturamento, volume de itens e nota média) e o ticket médio por seller, com um modelo dimensional construído no Power Query.

Depois da entrega, o projeto foi revisado e ampliado: a pergunta passou de "quem é o melhor" para "o que faz um seller ser bem avaliado", porque os dados mostraram que essas duas coisas não andam juntas.

## 2. Problema de negócio

Um marketplace precisa decidir quais vendedores e categorias destacar, apoiar e cobrar. O critério mais óbvio é o faturamento, mas um seller que vende muito com clientes insatisfeitos é um risco para a reputação de toda a plataforma.

Sem uma análise que separe volume de qualidade, a empresa corre o risco de premiar quem vende mais e ignorar o que realmente derruba a satisfação do cliente.

## 3. Pergunta central

> **Quem vende mais é quem o cliente aprova? E, se não for, o que decide a nota do cliente?**

**Perguntas de apoio**
1. Quais categorias e sellers lideram, por ano, em faturamento, volume de itens e nota média?
2. Qual é o ticket médio de cada seller?
3. O faturamento de um seller se relaciona com a nota que ele recebe?
4. O prazo de entrega explica a nota? Quem atrasa: o seller ou o transporte?
5. Onde estão os clientes que mais sofrem com atraso?

## 4. Objetivos

- Responder às perguntas do desafio original com rankings anuais e ticket médio por seller.
- Medir a relação entre volume de vendas, nota e prazo de entrega.
- Construir um critério de "melhor seller" que combine faturamento, avaliação e pontualidade.
- Recomendar ações priorizadas, com dono, prazo e indicador de acompanhamento.

## 5. Escopo

| Inclui | Não inclui |
|---|---|
| Pedidos entregues (`delivered`), 96.478 pedidos | Pedidos cancelados, indisponíveis ou em trânsito |
| Faturamento pelo preço dos itens | Frete como receita e valores de pagamento |
| Avaliações dos clientes, uma nota por pedido | Texto dos comentários (análise de sentimento) |
| Datas de compra, postagem, entrega e prazo prometido | Custos logísticos e margem (não existem no dataset) |
| Estado do cliente e do seller | Geolocalização fina (CEP) |

## 6. Entregáveis

| Entregável | Onde |
|---|---|
| Ingestão dos CSVs no PostgreSQL | `codigo/ingestao/` |
| Auditoria e validação em SQL | `sql/02_auditoria/`, `sql/03_validacao/` |
| Modelo dimensional e transformações | `power-query/` e `dashboard/*.SemanticModel` |
| Dashboard em Power BI | `dashboard/` |
| Diagnóstico reprodutível dos números | `codigo/analises/diagnostico.py` |
| Documentação (este e os documentos 02 a 06) | `docs/` |

## 7. Premissas e limitações

- Os dados são reais, mas anonimizados: sellers aparecem pelo código, não pelo nome.
- 2016 (set a dez) e 2018 (jan a ago) são anos parciais. Comparações entre anos usam faturamento por mês.
- O dataset não informa motivo de atraso nem transportadora. A separação entre "atraso do seller" e "atraso do transporte" usa o prazo de postagem do item (`shipping_limit_date`).
- Os valores de impacto são estimativas para priorização, não resultados medidos.
