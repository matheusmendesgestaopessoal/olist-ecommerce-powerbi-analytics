# Dicionário de Dados · Olist E-Commerce

Camada `raw` no PostgreSQL (espelho dos CSVs, todas as colunas como texto) e modelo dimensional do Power BI.
As seções do modelo e das medidas são geradas a partir dos arquivos TMDL do projeto (`dashboard/*.SemanticModel`),
então refletem exatamente o que está no Power BI.

---

## Camada raw (PostgreSQL, schema `raw`)

| Tabela | Linhas | Conteúdo | Usada no modelo |
|---|---:|---|:---:|
| orders | 99.441 | Pedido, cliente, status e datas (compra, aprovação, postagem, entrega, prazo estimado) | ✔ |
| order_items | 112.650 | Itens do pedido: produto, seller, preço, frete e prazo de postagem | ✔ |
| order_reviews | 99.224 | Avaliação do cliente (nota 1 a 5, título e comentário) | ✔ |
| products | 32.951 | Produto e categoria (em português) | ✔ |
| sellers | 3.095 | Seller: cidade e estado | ✔ |
| product_category_translation | 71 | Tradução oficial das categorias para o inglês | ✔ |
| customers | 99.441 | Cliente: cidade e estado | análise |
| order_payments | 103.886 | Forma e valor de pagamento (parcelas, vouchers) | auditoria |
| geolocation | 1.000.163 | Coordenadas por CEP | não usada |

---

## Modelo dimensional (Power BI)

Camadas do Power Query: `src_` (conexão com cada tabela) → `stg_` (limpeza e tipos) → `ft_` / `dm_` (modelo).


### ft_vendas
**Grão:** 1 linha por item de pedido entregue

| Coluna | Tipo |
|---|---|
| `order_id` | string |
| `order_item_id` | int64 |
| `product_id` | string |
| `seller_id` | string |
| `price` | double |
| `freight_value` | double |
| `order_purchase_date` | dateTime |
| `category_key` | string |
| `category_display_pt` | string |


### ft_avaliacoes_seller
**Grão:** 1 linha por pedido avaliado e seller

| Coluna | Tipo |
|---|---|
| `seller_id` | string |
| `order_id` | string |
| `order_purchase_date` | dateTime |
| `review_score_order` | double |


### ft_avaliacoes_categoria
**Grão:** 1 linha por pedido avaliado e categoria

| Coluna | Tipo |
|---|---|
| `order_id` | string |
| `category_key` | string |
| `order_purchase_date` | dateTime |
| `review_score_order` | double |
| `category_display_pt` | string |


### dm_seller
**Grão:** 1 linha por seller

| Coluna | Tipo |
|---|---|
| `seller_id` | string |
| `seller_city` | string |
| `seller_state` | string |


### dm_categoria
**Grão:** 1 linha por categoria

| Coluna | Tipo |
|---|---|
| `category_key` | string |
| `category_name_english` | string |
| `category_display` | string |
| `ranking_eligible` | boolean |
| `category_display_pt` | string |


### dm_data
**Grão:** 1 linha por dia (calendário entre a primeira e a última compra)

| Coluna | Tipo |
|---|---|
| `date` | dateTime |
| `year` | int64 |
| `month_number` | int64 |
| `month_name` | string |
| `quarter` | string |
| `year_month` | string |


### Perspectiva
Parâmetro de campo: troca a métrica dos rankings de categoria.


### Perspectiva Seller
Parâmetro de campo: troca a métrica dos rankings de seller.


### Eixo Concentracao
Tabela de apoio do gráfico de concentração de faturamento.


---

## Medidas DAX (26)

Todas ficam na tabela `_Medidas`.


**Faturamento**
```dax
SUM(ft_vendas[price])
```


**Volume Itens**
```dax
COUNTROWS(ft_vendas)
```


**Pedidos**
```dax
DISTINCTCOUNT(ft_vendas[order_id])
```


**Ticket Médio Seller**
```dax
AVERAGEX(
    VALUES(ft_vendas[order_id]),
    CALCULATE(
        SUM(ft_vendas[price])
    )
)
```


**Nota Média Seller**
```dax
AVERAGE(ft_avaliacoes_seller[review_score_order])
```


**Qtd Avaliações Seller**
```dax
COUNTROWS(ft_avaliacoes_seller)
```


**Nota Ajustada Seller**
```dax
VAR N =
    [Qtd Avaliações Seller]
VAR MediaSeller =
    [Nota Média Seller]
VAR MediaGeralAno =
    CALCULATE(
        [Nota Média Seller],
        REMOVEFILTERS(dm_seller)
    )
VAR M = 13.88
RETURN
    IF(
        N = 0,
        BLANK(),
        DIVIDE(N, N + M) * MediaSeller
            + DIVIDE(M, N + M) * MediaGeralAno
    )
```


**Nota Média Categoria**
```dax
AVERAGE(ft_avaliacoes_categoria[review_score_order])
```


**Qtd Avaliações Categoria**
```dax
COUNTROWS(ft_avaliacoes_categoria)
```


**Nota Ajustada Categoria**
```dax
VAR N =
    [Qtd Avaliações Categoria]
VAR MediaCategoria =
    [Nota Média Categoria]
VAR MediaGeralAno =
    CALCULATE(
        [Nota Média Categoria],
        REMOVEFILTERS(dm_categoria)
    )
VAR M = 16.36
RETURN
    IF(
        N = 0,
        BLANK(),
        DIVIDE(N, N + M) * MediaCategoria
            + DIVIDE(M, N + M) * MediaGeralAno
    )
```


**Ticket Médio Geral**
```dax
DIVIDE(
    [Faturamento],
    [Pedidos]
)
```


**Top Categoria Faturamento**
```dax
VAR TopCategoria =
    TOPN(
        1,
        FILTER(
            ALLSELECTED(dm_categoria),
            dm_categoria[ranking_eligible] = TRUE()
        ),
        [Faturamento],
        DESC
    )
RETURN
    CONCATENATEX(
        TopCategoria,
        dm_categoria[category_display],
        ", "
    )
```


**Pedidos Avaliados**
```dax
DISTINCTCOUNT(ft_avaliacoes_seller[order_id])
```


**Valor Perspectiva Categoria**
```dax
SWITCH (
    SELECTEDVALUE ( Perspectiva[Ordem], 1 ),
    1, [Faturamento],
    2, [Volume Itens],
    3, [Nota Ajustada Categoria]
)
	SWITCH ( SELECTEDVALUE ( Perspectiva[Ordem], 1 ),
	    1, "R$ #,0", 2, "#,0", 3, "0.00" )
```


**Valor Perspectiva Seller**
```dax
SWITCH (
    SELECTEDVALUE ( 'Perspectiva Seller'[Ordem], 1 ),
    1, [Faturamento],
    2, [Volume Itens],
    3, [Nota Ajustada Seller]
)
	SWITCH ( SELECTEDVALUE ( 'Perspectiva Seller'[Ordem], 1 ),
	    1, "R$ #,0", 2, "#,0", 3, "0.00" )
```


**Nota Média Geral**
```dax
AVERAGEX(
    SUMMARIZE(
        ft_avaliacoes_seller,
        ft_avaliacoes_seller[order_id],
        "NotaPedido",
        MAX(ft_avaliacoes_seller[review_score_order])
    ),
    [NotaPedido]
)
```


**Faturamento Top 10% Sellers**
```dax
VAR SellersAtivos =
    FILTER(
        ALLSELECTED(dm_seller[seller_id]),
        CALCULATE([Faturamento]) > 0
    )
VAR QuantidadeSellers =
    COUNTROWS(SellersAtivos)
VAR QuantidadeTop10 =
    ROUNDUP(
        QuantidadeSellers * 0.10,
        0
    )
VAR TopSellers =
    TOPN(
        QuantidadeTop10,
        SellersAtivos,
        [Faturamento],
        DESC
    )
RETURN
    SUMX(
        TopSellers,
        CALCULATE([Faturamento])
    )
```


**% Faturamento Top 10% Sellers**
```dax
VAR FaturamentoTotal =
    CALCULATE(
        [Faturamento],
        ALLSELECTED(dm_seller[seller_id])
    )
RETURN
    DIVIDE(
        [Faturamento Top 10% Sellers],
        FaturamentoTotal
    )
```


**Qtd Sellers Top 10%**
```dax
VAR SellersAtivos =
    FILTER(
        ALLSELECTED(dm_seller[seller_id]),
        CALCULATE([Faturamento]) > 0
    )
RETURN
    ROUNDUP(
        COUNTROWS(SellersAtivos) * 0.10,
        0
    )
```


**Pedidos Seller**
```dax
DISTINCTCOUNT(ft_vendas[order_id])
```


**Qtd Seller-Pedidos**
```dax
CALCULATE(
    SUMX(
        VALUES(dm_seller[seller_id]),
        CALCULATE(
            DISTINCTCOUNT(ft_vendas[order_id])
        )
    ),
    REMOVEFILTERS(dm_seller)
)
```


**Ticket Médio Global Sellers**
```dax
VAR ReceitaGlobal =
    CALCULATE(
        [Faturamento],
        REMOVEFILTERS(dm_seller)
    )
RETURN
    DIVIDE(
        ReceitaGlobal,
        [Qtd Seller-Pedidos]
    )
```


**Ticket Médio Ajustado**
```dax
VAR N =
    [Pedidos Seller]
VAR TicketSeller =
    [Ticket Médio Seller]
VAR TicketGlobal =
    [Ticket Médio Global Sellers]
VAR M =
    0.8398
VAR PesoSeller =
    DIVIDE(
        N,
        N + M
    )
RETURN
    IF(
        N = 0,
        BLANK(),
        PesoSeller * TicketSeller
            + (1 - PesoSeller) * TicketGlobal
    )
```


**% Notas 1 a 3**
```dax
VAR PedidosAvaliados =
    SUMMARIZE(
        ft_avaliacoes_seller,
        ft_avaliacoes_seller[order_id],
        "Nota",
        MAX(ft_avaliacoes_seller[review_score_order])
    )
VAR QtdNotas1a3 =
    COUNTROWS(
        FILTER(
            PedidosAvaliados,
            [Nota] >= 1 &&
            [Nota] <= 3.9
        )
    )
RETURN
    DIVIDE(
        QtdNotas1a3,
        COUNTROWS(PedidosAvaliados)
    )
```


**% Notas 4 a 5**
```dax
VAR PedidosAvaliados =
    SUMMARIZE(
        ft_avaliacoes_seller,
        ft_avaliacoes_seller[order_id],
        "Nota",
        MAX(ft_avaliacoes_seller[review_score_order])
    )
VAR QtdNotas4a5 =
    COUNTROWS(
        FILTER(
            PedidosAvaliados,
            [Nota] >= 4 &&
            [Nota] <= 5
        )
    )
RETURN
    DIVIDE(
        QtdNotas4a5,
        COUNTROWS(PedidosAvaliados)
    )
```


**% Pedidos Avaliados**
```dax
DIVIDE (
    [Pedidos Avaliados],
    CALCULATE ( [Pedidos Avaliados], REMOVEFILTERS ( ft_avaliacoes_seller[review_score_order] ) )
)
```
