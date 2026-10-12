# Medidas DAX
Todas as medidas do modelo, exportadas do arquivo do Power BI.

## Tabela `_Medidas`

### Faturamento

```dax
Faturamento =
SUM(ft_vendas[price])
```

### Volume Itens

```dax
Volume Itens =
COUNTROWS(ft_vendas)
```

### Pedidos

```dax
Pedidos =
DISTINCTCOUNT(ft_vendas[order_id])
```

### Ticket Médio Seller

```dax
Ticket Médio Seller =
AVERAGEX(
    VALUES(ft_vendas[order_id]),
    CALCULATE(
        SUM(ft_vendas[price])
    )
)
```

### Nota Média Seller

```dax
Nota Média Seller =
AVERAGE(ft_avaliacoes_seller[review_score_order])
```

### Qtd Avaliações Seller

```dax
Qtd Avaliações Seller =
COUNTROWS(ft_avaliacoes_seller)
```

### Nota Ajustada Seller

```dax
Nota Ajustada Seller =
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

### Nota Média Categoria

```dax
Nota Média Categoria =
AVERAGE(ft_avaliacoes_categoria[review_score_order])
```

### Qtd Avaliações Categoria

```dax
Qtd Avaliações Categoria =
COUNTROWS(ft_avaliacoes_categoria)
```

### Nota Ajustada Categoria

```dax
Nota Ajustada Categoria =
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

### Ticket Médio Geral

```dax
Ticket Médio Geral =
DIVIDE(
    [Faturamento],
    [Pedidos]
)
```

### Top Categoria Faturamento

```dax
Top Categoria Faturamento =
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

### Pedidos Avaliados

```dax
Pedidos Avaliados =
DISTINCTCOUNT(ft_avaliacoes_seller[order_id])
```

### Valor Perspectiva Categoria

```dax
Valor Perspectiva Categoria =
SWITCH (
    SELECTEDVALUE ( Perspectiva[Ordem], 1 ),
    1, [Faturamento],
    2, [Volume Itens],
    3, [Nota Ajustada Categoria]
)
```

### Valor Perspectiva Seller

```dax
Valor Perspectiva Seller =
SWITCH (
    SELECTEDVALUE ( 'Perspectiva Seller'[Ordem], 1 ),
    1, [Faturamento],
    2, [Volume Itens],
    3, [Nota Ajustada Seller]
)
```

### Nota Média Geral

```dax
Nota Média Geral =
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

### Faturamento Top 10% Sellers

```dax
Faturamento Top 10% Sellers =
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

### % Faturamento Top 10% Sellers

```dax
% Faturamento Top 10% Sellers =
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

### Qtd Sellers Top 10%

```dax
Qtd Sellers Top 10% =
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

### Pedidos Seller

```dax
Pedidos Seller =
DISTINCTCOUNT(ft_vendas[order_id])
```

### Qtd Seller-Pedidos

```dax
Qtd Seller-Pedidos =
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

### Ticket Médio Global Sellers

```dax
Ticket Médio Global Sellers =
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

### Ticket Médio Ajustado

```dax
Ticket Médio Ajustado =
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

### % Notas 1 a 3

```dax
% Notas 1 a 3 =
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

### % Notas 4 a 5

```dax
% Notas 4 a 5 =
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

### % Pedidos Avaliados

```dax
% Pedidos Avaliados =
DIVIDE (
    [Pedidos Avaliados],
    CALCULATE ( [Pedidos Avaliados], REMOVEFILTERS ( ft_avaliacoes_seller[review_score_order] ) )
)
```

## Tabela `Eixo Concentracao`

### Qtd Sellers Ativos

```dax
Qtd Sellers Ativos =
COUNTROWS(
    FILTER(
        ALLSELECTED(dm_seller[seller_id]),
        CALCULATE([Faturamento]) > 0
    )
)
```

### Curva Concentracao Faturamento %

```dax
Curva Concentracao Faturamento % =
VAR PctSellers =
    DIVIDE(MAX('Eixo Concentracao'[Value]), 100, 0)

VAR SellersAtivos =
    FILTER(
        ALLSELECTED(dm_seller[seller_id]),
        CALCULATE([Faturamento]) > 0
    )

VAR QtdSellers =
    COUNTROWS(SellersAtivos)

VAR QtdTop =
    ROUNDUP(QtdSellers * PctSellers, 0)

VAR TopSellers =
    TOPN(
        QtdTop,
        SellersAtivos,
        [Faturamento],
        DESC,
        dm_seller[seller_id],
        ASC
    )

VAR FaturamentoTop =
    SUMX(
        TopSellers,
        CALCULATE([Faturamento])
    )

VAR FaturamentoTotal =
    CALCULATE(
        [Faturamento],
        ALLSELECTED(dm_seller[seller_id])
    )

RETURN
    IF(
        QtdSellers = 0,
        BLANK(),
        DIVIDE(FaturamentoTop, FaturamentoTotal, 0)
    )
```

### Ponto Top 10%

```dax
Ponto Top 10% =
IF(
    MAX('Eixo Concentracao'[Value]) = 10,
    [Curva Concentracao Faturamento %],
    BLANK()
)
```

## Colunas calculadas

### dm_seller[Seller Rótulo]

```dax
LEFT ( dm_seller[seller_id], 6 ) & " · " & dm_seller[seller_state]
```

### dm_data[Mes Abrev]

```dax
UPPER ( LEFT ( dm_data[month_name], 1 ) ) & LOWER ( MID ( dm_data[month_name], 2, 2 ) )
```

## Tabelas calculadas (parâmetros e eixos)

### Perspectiva

```dax
DATATABLE (
    "Perspectiva", STRING, "Ordem", INTEGER,
    { { "Faturamento", 1 }, { "Volume", 2 }, { "Nota média", 3 } }
)
```

### Perspectiva Seller

```dax
DATATABLE (
    "Perspectiva", STRING, "Ordem", INTEGER,
    { { "Faturamento", 1 }, { "Volume", 2 }, { "Nota média", 3 } }
)
```

### Eixo Concentracao

```dax
GENERATESERIES(0, 100, 1)
```
