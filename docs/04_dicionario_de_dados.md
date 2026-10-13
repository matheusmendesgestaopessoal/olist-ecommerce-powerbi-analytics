# Dicionário de Dados · Olist E-Commerce

Camada `raw` no PostgreSQL (espelho dos CSVs, todas as colunas como texto) e modelo dimensional do Power BI.
As seções do modelo e das medidas são geradas a partir dos arquivos TMDL do projeto (`dashboard/*.SemanticModel`),
então refletem exatamente o que está no Power BI.

---

## Camada raw (PostgreSQL, schema `raw`)

| Tabela | Linhas | Conteúdo | Usada no modelo |
|---|---:|---|:---:|
| orders | 99.441 | Pedido, cliente, status e datas (compra, postagem, entrega, prazo estimado) | ✔ |
| order_items | 112.650 | Itens do pedido: produto, seller, preço, frete e limite de postagem | ✔ |
| order_reviews | 99.224 | Avaliação do cliente (nota 1 a 5, título e comentário) | ✔ |
| products | 32.951 | Produto e categoria (chave em português) | ✔ |
| sellers | 3.095 | Seller: cidade e estado | ✔ |
| customers | 99.441 | Cliente: cidade e estado | ✔ |
| product_category_translation | 71 | Tradução oficial das categorias para o inglês | ✔ |
| order_payments | 103.886 | Forma e valor de pagamento (parcelas, vouchers) | auditoria |
| geolocation | 1.000.163 | Coordenadas por CEP | não usada |

---

## Modelo dimensional (Power BI)

Camadas do Power Query: `src_` (conexão com cada tabela) → `stg_` (limpeza e tipos) → `ft_` / `dm_` (modelo).
Esquema estrela: `ft_vendas` no centro, ligada a `dm_data` (data da compra), `dm_seller`, `dm_categoria` e
`dm_cliente_uf` (estado do cliente), todas um-para-muitos com filtro em direção única.


### ft_vendas
**Grão:** 1 linha por pedido entregue × seller × categoria. Traz faturamento, itens e frete, e os atributos do pedido (estado do cliente, prazo, atraso, etapas e nota), repetidos nas linhas do mesmo pedido.

| Coluna | Tipo |
|---|---|
| `order_id` | string |
| `seller_id` | string · oculta |
| `order_purchase_date` | dateTime · oculta |
| `category_key` | string · oculta |
| `customer_state` | string · oculta |
| `itens` | int64 |
| `faturamento` | double |
| `frete` | double |
| `nota_pedido` | double |
| `prazo_entrega_dias` | double |
| `dias_postagem` | double |
| `dias_transporte` | double |
| `atrasado` | int64 |
| `seller_postou_atrasado` | int64 |
| `faixa_prazo` | string |
| `faixa_prazo_ordem` | int64 · oculta |
| `faixa_prazo_seller` | string |
| `faixa_prazo_seller_ordem` | int64 · oculta |


### dm_seller
**Grão:** 1 linha por seller, com o grupo de atraso (sellers com 30+ avaliações).

| Coluna | Tipo |
|---|---|
| `seller_id` | string · oculta |
| `seller_city` | string |
| `seller_state` | string |
| `Seller Rótulo` | calculada (DAX) |
| `Avaliações` | calculada (DAX) · oculta |
| `Atraso Geral` | calculada (DAX) · oculta |
| `Grupo Atraso Ordem` | calculada (DAX) · oculta |
| `Grupo Atraso` | calculada (DAX) |


### dm_categoria
**Grão:** 1 linha por categoria, com nome de exibição em português.

| Coluna | Tipo |
|---|---|
| `category_key` | string · oculta |
| `category_name_english` | string |
| `ranking_eligible` | boolean · oculta |
| `categoria` | string |


### dm_cliente_uf
**Grão:** 1 linha por estado do cliente, com a região.

| Coluna | Tipo |
|---|---|
| `uf` | string |
| `estado` | string |
| `regiao` | string |
| `regiao_ordem` | int64 · oculta |


### dm_data
**Grão:** 1 linha por dia (calendário entre a primeira e a última compra).

| Coluna | Tipo |
|---|---|
| `date` | dateTime |
| `year` | int64 |
| `month_number` | int64 |
| `month_name` | string |
| `quarter` | string |
| `year_month` | string |
| `Mes Abrev` | calculada (DAX) |
| `Mes Ano` | calculada (DAX) |


---

## Medidas DAX (101)

Todas ficam na tabela `_Medidas`, em pastas. As medidas de pedido agrupam `ft_vendas` por `order_id`, porque o grão é pedido × seller × categoria.


### 01 Base


**Faturamento**
```dax
SUM ( ft_vendas[faturamento] )
```


**Pedidos**
```dax
DISTINCTCOUNT ( ft_vendas[order_id] )
```


### 04 Sellers e categorias


**Nota Ajustada Seller**
```dax
VAR _n = [Pedidos Avaliados]
VAR _m = 13.88
VAR _media = CALCULATE ( [Nota Média], REMOVEFILTERS ( dm_seller ) )
RETURN IF ( _n > 0, DIVIDE ( _n, _n + _m ) * [Nota Média] + DIVIDE ( _m, _n + _m ) * _media )
```


**Nota Ajustada Categoria**
```dax
VAR _n = [Pedidos Avaliados]
VAR _m = 16.36
VAR _media = CALCULATE ( [Nota Média], REMOVEFILTERS ( dm_categoria ) )
RETURN IF ( _n > 0, DIVIDE ( _n, _n + _m ) * [Nota Média] + DIVIDE ( _m, _n + _m ) * _media )
```


### 02 Nota


**Pedidos Avaliados**
```dax
COUNTROWS (
    FILTER ( SUMMARIZE ( ft_vendas, ft_vendas[order_id], ft_vendas[nota_pedido] ), NOT ISBLANK ( ft_vendas[nota_pedido] ) )
)
```


### 01 Base


**Faturamento Mi**
```dax
DIVIDE ( [Faturamento], 1000000 )
```


**Faturamento mil**
```dax
DIVIDE ( [Faturamento], 1000 )
```


**Itens**
```dax
SUM ( ft_vendas[itens] )
```


**Ticket Médio**
```dax
DIVIDE ( [Faturamento], [Pedidos] )
```


**Sellers**
```dax
DISTINCTCOUNT ( ft_vendas[seller_id] )
```


**Crescimento Mensal**
```dax
VAR _f17 = CALCULATE ( [Faturamento], REMOVEFILTERS ( dm_data ), dm_data[year] = 2017 )
VAR _f18 = CALCULATE ( [Faturamento], REMOVEFILTERS ( dm_data ), dm_data[year] = 2018 )
VAR _m17 = CALCULATE ( COUNTROWS ( SUMMARIZE ( ft_vendas, dm_data[year_month] ) ), REMOVEFILTERS ( dm_data ), dm_data[year] = 2017 )
VAR _m18 = CALCULATE ( COUNTROWS ( SUMMARIZE ( ft_vendas, dm_data[year_month] ) ), REMOVEFILTERS ( dm_data ), dm_data[year] = 2018 )
RETURN DIVIDE ( DIVIDE ( _f18, _m18 ), DIVIDE ( _f17, _m17 ) ) - 1
```


**% Faturamento Top 10%**
```dax
VAR _sellers = FILTER ( ALLSELECTED ( dm_seller[seller_id] ), [Faturamento] > 0 )
VAR _top = TOPN ( ROUNDUP ( COUNTROWS ( _sellers ) * 0.10, 0 ), _sellers, [Faturamento], DESC )
RETURN DIVIDE ( SUMX ( _top, [Faturamento] ), CALCULATE ( [Faturamento], ALLSELECTED ( dm_seller[seller_id] ) ) )
```


### 02 Nota


**Nota Média**
```dax
AVERAGEX (
    FILTER ( SUMMARIZE ( ft_vendas, ft_vendas[order_id], ft_vendas[nota_pedido] ), NOT ISBLANK ( ft_vendas[nota_pedido] ) ),
    ft_vendas[nota_pedido]
)
```


**% Notas 1**
```dax
VAR _p = FILTER ( SUMMARIZE ( ft_vendas, ft_vendas[order_id], ft_vendas[nota_pedido] ), NOT ISBLANK ( ft_vendas[nota_pedido] ) )
RETURN DIVIDE ( COUNTROWS ( FILTER ( _p, ROUND ( ft_vendas[nota_pedido], 0 ) = 1 ) ) + 0, COUNTROWS ( _p ) )
```


**Nota No Prazo**
```dax
CALCULATE ( [Nota Média], ft_vendas[atrasado] = 0 )
```


**Nota Atrasado**
```dax
CALCULATE ( [Nota Média], ft_vendas[atrasado] = 1 )
```


**% Notas 1 No Prazo**
```dax
CALCULATE ( [% Notas 1], ft_vendas[atrasado] = 0 )
```


**% Notas 1 Atrasado**
```dax
CALCULATE ( [% Notas 1], ft_vendas[atrasado] = 1 )
```


**% Notas 1 de Atrasos**
```dax
VAR _p =
    FILTER (
        SUMMARIZE ( ft_vendas, ft_vendas[order_id], ft_vendas[nota_pedido], ft_vendas[atrasado] ),
        NOT ISBLANK ( ft_vendas[atrasado] ) && ROUND ( ft_vendas[nota_pedido], 0 ) = 1
    )
RETURN DIVIDE ( COUNTROWS ( FILTER ( _p, ft_vendas[atrasado] = 1 ) ) + 0, COUNTROWS ( _p ) )
```


### 03 Entrega


**Pedidos Analisados**
```dax
COUNTROWS (
    FILTER (
        SUMMARIZE ( ft_vendas, ft_vendas[order_id], ft_vendas[nota_pedido], ft_vendas[atrasado] ),
        NOT ISBLANK ( ft_vendas[nota_pedido] ) && NOT ISBLANK ( ft_vendas[atrasado] )
    )
)
```


**% Atraso**
```dax
VAR _p =
    FILTER (
        SUMMARIZE ( ft_vendas, ft_vendas[order_id], ft_vendas[nota_pedido], ft_vendas[atrasado] ),
        NOT ISBLANK ( ft_vendas[nota_pedido] ) && NOT ISBLANK ( ft_vendas[atrasado] )
    )
RETURN DIVIDE ( COUNTROWS ( FILTER ( _p, ft_vendas[atrasado] = 1 ) ) + 0, COUNTROWS ( _p ) )
```


**Prazo Médio**
```dax
AVERAGEX (
    FILTER (
        SUMMARIZE ( ft_vendas, ft_vendas[order_id], ft_vendas[nota_pedido], ft_vendas[prazo_entrega_dias] ),
        NOT ISBLANK ( ft_vendas[nota_pedido] ) && NOT ISBLANK ( ft_vendas[prazo_entrega_dias] )
    ),
    ft_vendas[prazo_entrega_dias]
)
```


**Prazo Médio UF**
```dax
IF ( [Pedidos Analisados] >= 300, [Prazo Médio] )
```


**Nota da Faixa**
```dax
IF ( NOT ISBLANK ( SELECTEDVALUE ( ft_vendas[faixa_prazo] ) ), [Nota Média] )
```


**Nota da Faixa Seller**
```dax
IF ( NOT ISBLANK ( SELECTEDVALUE ( ft_vendas[faixa_prazo_seller] ) ), [Nota Média] )
```


**Dias Postagem**
```dax
AVERAGEX (
    FILTER ( SUMMARIZE ( ft_vendas, ft_vendas[order_id], ft_vendas[dias_postagem] ), NOT ISBLANK ( ft_vendas[dias_postagem] ) ),
    ft_vendas[dias_postagem]
)
```


**Dias Transporte**
```dax
AVERAGEX (
    FILTER ( SUMMARIZE ( ft_vendas, ft_vendas[order_id], ft_vendas[dias_transporte] ), NOT ISBLANK ( ft_vendas[dias_transporte] ) ),
    ft_vendas[dias_transporte]
)
```


**% Atrasos do Seller**
```dax
VAR _p =
    FILTER (
        SUMMARIZE ( ft_vendas, ft_vendas[order_id], ft_vendas[atrasado], ft_vendas[seller_postou_atrasado] ),
        ft_vendas[atrasado] = 1
    )
RETURN DIVIDE ( COUNTROWS ( FILTER ( _p, ft_vendas[seller_postou_atrasado] = 1 ) ) + 0, COUNTROWS ( _p ) )
```


**% Atrasos do Transporte**
```dax
IF ( NOT ISBLANK ( [% Atrasos do Seller] ), 1 - [% Atrasos do Seller] )
```


### 04 Sellers e categorias


**Faturamento mil 30+**
```dax
IF ( [Pedidos Avaliados] >= 30, [Faturamento mil] )
```


**Nota Média do Grupo**
```dax
IF (
    NOT ISBLANK ( SELECTEDVALUE ( dm_seller[Grupo Atraso Ordem] ) ),
    AVERAGEX ( VALUES ( dm_seller[seller_id] ), [Nota Média] )
)
```


**Posição Faturamento**
```dax
IF ( [Faturamento] > 0, RANKX ( ALL ( dm_seller ), [Faturamento], , DESC ) )
```


**Campeã Faturamento**
```dax
VAR _c = TOPN ( 1, CALCULATETABLE ( VALUES ( dm_categoria[categoria] ), dm_categoria[ranking_eligible] = TRUE () ), [Faturamento], DESC )
RETURN MAXX ( _c, dm_categoria[categoria] & " · R$ " & FORMAT ( [Faturamento mil], "#,0" ) & " mil" )
```


**Campeã Itens**
```dax
VAR _c = TOPN ( 1, CALCULATETABLE ( VALUES ( dm_categoria[categoria] ), dm_categoria[ranking_eligible] = TRUE () ), [Itens], DESC )
RETURN MAXX ( _c, dm_categoria[categoria] & " · " & FORMAT ( [Itens], "#,0" ) & " itens" )
```


**Campeã Nota**
```dax
VAR _elegiveis =
    FILTER (
        CALCULATETABLE ( VALUES ( dm_categoria[categoria] ), dm_categoria[ranking_eligible] = TRUE () ),
        [Pedidos Avaliados] >= 30
    )
VAR _c = TOPN ( 1, _elegiveis, [Nota Ajustada Categoria], DESC )
RETURN MAXX ( _c, dm_categoria[categoria] & " · " & FORMAT ( [Nota Ajustada Categoria], "0.00" ) )
```


### 05 Rede


**Ticket Médio Rede**
```dax
CALCULATE ( [Ticket Médio], REMOVEFILTERS ( dm_seller ) )
```


**Nota Média Rede**
```dax
CALCULATE ( [Nota Média], REMOVEFILTERS ( dm_seller ) )
```


**% Atraso Rede**
```dax
CALCULATE ( [% Atraso], REMOVEFILTERS ( dm_seller ) )
```


**Prazo Médio Rede**
```dax
CALCULATE ( [Prazo Médio], REMOVEFILTERS ( dm_seller ) )
```


**Sellers Rede**
```dax
CALCULATE ( [Sellers], REMOVEFILTERS ( dm_seller ) )
```


**Ticket vs Rede**
```dax
DIVIDE ( [Ticket Médio], [Ticket Médio Rede] ) - 1
```


**Nota vs Rede**
```dax
[Nota Ajustada Seller] - [Nota Média Rede]
```


**Atraso vs Rede**
```dax
[% Atraso] - [% Atraso Rede]
```


### 10 Textos


**Txt Resposta**
```dax
"Não. Faturamento e nota quase não se relacionam. O que decide a nota é a entrega: pedido atrasado recebe "
    & FORMAT ( [Nota Atrasado], "0.00" ) & ", contra " & FORMAT ( [Nota No Prazo], "0.00" ) & " no prazo."
```


**Txt KPI Faturamento**
```dax
IF (
    [Faturamento] >= 1000000,
    "R$ " & FORMAT ( [Faturamento Mi], "0.00" ) & " Mi",
    "R$ " & FORMAT ( [Faturamento mil], "#,0" ) & " mil"
)
```


**Txt Pill Crescimento**
```dax
FORMAT ( [Crescimento Mensal], "+0%;-0%" )
```


**Txt KPI Pedidos**
```dax
IF ( [Pedidos] >= 10000, FORMAT ( [Pedidos] / 1000, "#,0.0" ) & " mil", FORMAT ( [Pedidos], "#,0" ) )
```


**Txt Ctx Ticket**
```dax
"Ticket médio R$ " & FORMAT ( [Ticket Médio], "#,0" )
```


**Txt KPI Nota**
```dax
FORMAT ( [Nota Média], "0.00" )
```


**Txt Pill Notas 1**
```dax
FORMAT ( [% Notas 1], "0.0%" )
```


**Txt KPI Atraso**
```dax
FORMAT ( [% Atraso], "0.0%" )
```


**Txt Pill Nota Atrasado**
```dax
FORMAT ( [Nota Atrasado], "0.00" )
```


**Txt KPI Sellers**
```dax
FORMAT ( [Sellers], "#,0" )
```


**Txt Ctx Top 10**
```dax
"10% maiores = " & FORMAT ( [% Faturamento Top 10%], "0%" ) & " do faturamento"
```


**Txt Titulo Contexto**
```dax
"O marketplace cresceu " & FORMAT ( [Crescimento Mensal], "0%" ) & " por mês, e os campeões mudam conforme a métrica"
```


**Txt Titulo Vender**
```dax
VAR _top20 = TOPN ( 20, FILTER ( VALUES ( dm_seller[seller_id] ), [Faturamento] > 0 ), [Faturamento], DESC )
VAR _media = [Nota Média]
VAR _abaixo = COUNTROWS ( FILTER ( _top20, [Nota Média] < _media ) )
VAR _total = COUNTROWS ( _top20 )
RETURN
    IF (
        _abaixo > 0,
        _abaixo & " dos " & _total & " sellers que mais faturam têm nota abaixo da média",
        "Os " & _total & " sellers que mais faturam têm nota acima da média"
    )
```


**Txt Titulo Nota**
```dax
"Atrasos são " & FORMAT ( [% Atraso], "0.0%" ) & " dos pedidos, mas geram "
    & FORMAT ( [% Notas 1 de Atrasos], "0%" ) & " de todas as notas 1"
```


**Txt Titulo Regiao**
```dax
VAR _t = FILTER ( ADDCOLUMNS ( VALUES ( dm_cliente_uf[regiao] ), "@prazo", [Prazo Médio], "@atraso", [% Atraso] ), NOT ISBLANK ( [@prazo] ) )
VAR _pior = TOPN ( 1, _t, [@atraso], DESC )
VAR _melhor = TOPN ( 1, _t, [@prazo], ASC )
VAR _nomePior = MAXX ( _pior, dm_cliente_uf[regiao] )
VAR _prazoPior = MAXX ( _pior, [@prazo] )
VAR _nomeMelhor = MAXX ( _melhor, dm_cliente_uf[regiao] )
VAR _razao = DIVIDE ( _prazoPior, MAXX ( _melhor, [@prazo] ) )
RETURN
    IF (
        COUNTROWS ( _t ) <= 1 || _nomePior = _nomeMelhor,
        "O cliente do " & _nomePior & " espera " & FORMAT ( _prazoPior, "0.0" ) & " dias pela entrega",
        "O cliente do " & _nomePior & " espera " & FORMAT ( _prazoPior, "0.0" ) & " dias, "
            & SWITCH ( TRUE (), _razao >= 2.1, "mais que o dobro do ", _razao >= 1.75, "quase o dobro do ", FORMAT ( _razao, "0.0" ) & "× o prazo do " )
            & _nomeMelhor
    )
```


**Txt Nota No Prazo**
```dax
FORMAT ( [Nota No Prazo], "0.00" )
```


**Txt Nota Atrasado**
```dax
FORMAT ( [Nota Atrasado], "0.00" )
```


**Txt Ctx No Prazo**
```dax
"nota média · " & FORMAT ( [% Notas 1 No Prazo], "0.0%" ) & " de notas 1"
```


**Txt Ctx Atrasado**
```dax
"nota média · " & FORMAT ( [% Notas 1 Atrasado], "0%" ) & " de notas 1"
```


**Txt Postagem No Prazo**
```dax
FORMAT ( CALCULATE ( [Dias Postagem], ft_vendas[atrasado] = 0 ), "0.0" )
```


**Txt Postagem Atrasado**
```dax
FORMAT ( CALCULATE ( [Dias Postagem], ft_vendas[atrasado] = 1 ), "0.0" )
```


**Txt Transporte No Prazo**
```dax
FORMAT ( CALCULATE ( [Dias Transporte], ft_vendas[atrasado] = 0 ), "0.0" )
```


**Txt Transporte Atrasado**
```dax
FORMAT ( CALCULATE ( [Dias Transporte], ft_vendas[atrasado] = 1 ), "0.0" )
```


**Txt Leitura Etapas**
```dax
IF (
    [% Atrasos do Transporte] >= 0.5,
    "O gargalo é o transporte: em " & FORMAT ( [% Atrasos do Transporte], "0%" ) & " dos atrasos, o seller postou no prazo.",
    "O gargalo é a postagem: em " & FORMAT ( [% Atrasos do Seller], "0%" ) & " dos atrasos, o seller postou depois do limite."
)
```


**Txt Dica Estado**
```dax
SELECTEDVALUE ( dm_cliente_uf[estado] ) & " (" & SELECTEDVALUE ( dm_cliente_uf[uf] ) & ")"
```


**Txt Dica Sub**
```dax
"Região " & SELECTEDVALUE ( dm_cliente_uf[regiao] ) & " · " & FORMAT ( [Pedidos Analisados], "#,0" ) & " pedidos avaliados"
```


**Txt Dica Prazo**
```dax
FORMAT ( [Prazo Médio], "0.0" ) & " dias"
```


**Txt Dica Atraso**
```dax
FORMAT ( [% Atraso], "0.0%" )
```


**Txt Dica Nota**
```dax
FORMAT ( [Nota Média], "0.00" )
```


**Txt Titulo Seller**
```dax
VAR _uf = SELECTEDVALUE ( dm_seller[seller_state] )
VAR _estado = LOOKUPVALUE ( dm_cliente_uf[estado], dm_cliente_uf[uf], _uf )
RETURN
    "Seller " & LEFT ( SELECTEDVALUE ( dm_seller[seller_id] ), 6 ) & " · " & _estado & " (" & _uf & ") · "
        & FORMAT ( [Pedidos], "#,0" ) & " pedidos"
```


**Txt Ctx Posicao**
```dax
FORMAT ( [Posição Faturamento], "0" ) & "º lugar entre " & FORMAT ( [Sellers Rede], "#,0" ) & " sellers"
```


**Txt KPI Ticket**
```dax
"R$ " & FORMAT ( [Ticket Médio], "#,0" )
```


**Txt Ctx Ticket Rede**
```dax
"Rede: R$ " & FORMAT ( [Ticket Médio Rede], "#,0" )
```


**Txt Pill Ticket**
```dax
FORMAT ( [Ticket vs Rede], "+0%;-0%" )
```


**Txt KPI Nota Seller**
```dax
FORMAT ( [Nota Ajustada Seller], "0.00" )
```


**Txt Ctx Nota Rede**
```dax
"Rede: " & FORMAT ( [Nota Média Rede], "0.00" )
```


**Txt Pill Nota**
```dax
FORMAT ( [Nota vs Rede], "+0.00;−0.00;0.00" )
```


**Txt Ctx Atraso Rede**
```dax
"Rede: " & FORMAT ( [% Atraso Rede], "0.0%" )
```


**Txt Pill Atraso**
```dax
FORMAT ( [Atraso vs Rede] * 100, "+0.0;−0.0;0.0" ) & " p.p."
```


**Txt KPI Prazo**
```dax
FORMAT ( [Prazo Médio], "0.0" ) & " dias"
```


**Txt Ctx Prazo Rede**
```dax
"Rede: " & FORMAT ( [Prazo Médio Rede], "0.0" ) & " dias"
```


**Txt Perfil Seller**
```dax
VAR _pos = [Posição Faturamento]
VAR _topo = _pos <= ROUNDUP ( [Sellers Rede] * 0.10, 0 )
VAR _nota = [Nota vs Rede]
VAR _porte = IF ( _topo, "Vende muito", "Vende pouco" )
VAR _qual = SWITCH ( TRUE (), _nota >= 0.05, "nota acima da média", _nota <= -0.05, "nota abaixo da média", "nota na média" )
VAR _ticket = [Ticket vs Rede]
RETURN
    _porte & ", " & _qual & ": " & _pos & "º em faturamento, com ticket "
        & IF ( ABS ( _ticket ) < 0.05, "próximo da rede.", FORMAT ( ABS ( _ticket ), "0%" ) & IF ( _ticket > 0, " acima", " abaixo" ) & " da rede." )
```


**Txt Atencao Seller**
```dax
VAR _a = [% Atraso]
VAR _ar = [% Atraso Rede]
VAR _p = [Prazo Médio]
VAR _pr = [Prazo Médio Rede]
RETURN
    SWITCH (
        TRUE (),
        _a > _ar * 1.3, "Atraso de " & FORMAT ( _a, "0.0%" ) & ", acima da rede (" & FORMAT ( _ar, "0.0%" ) & "). É o que mais pesa na nota.",
        _p > _pr * 1.2, "Prazo médio de " & FORMAT ( _p, "0.0" ) & " dias, acima da rede (" & FORMAT ( _pr, "0.0" ) & "): o cliente espera mais.",
        [Nota vs Rede] <= -0.05, "Nota abaixo da média mesmo com entrega em dia: olhar produto, descrição e atendimento.",
        "Nenhum ponto crítico: atraso e prazo dentro da média da rede."
    )
```


**Txt Acao Seller**
```dax
VAR _atrasa = [% Atraso] > [% Atraso Rede] * 1.3
VAR _topo = [Posição Faturamento] <= ROUNDUP ( [Sellers Rede] * 0.10, 0 )
RETURN
    SWITCH (
        TRUE (),
        _atrasa && _topo, "Plano de pontualidade antes de entrar no programa de sellers referência.",
        _atrasa, "Plano de pontualidade: revisar a postagem e as rotas com mais atraso.",
        [Nota vs Rede] <= -0.05, "Ler as avaliações negativas e corrigir produto ou anúncio.",
        _topo, "Candidato a seller referência: vende muito e entrega bem.",
        "Acompanhar: sem ação prioritária."
    )
```


### 11 Cores


**Cor Faturamento Mes**
```dax
VAR _max = MAXX ( ALLSELECTED ( dm_data[Mes Ano], dm_data[year_month] ), [Faturamento] )
RETURN IF ( [Faturamento] = _max, "#1A6BF5", "#CFE0FF" )
```


**Cor Faixa Prazo**
```dax
IF ( [Nota Média] < 4, "#1A6BF5", "#CFE0FF" )
```


**Cor Faixa Seller**
```dax
IF ( [Nota Média] < 3.5, "#FF3B3B", "#CFE0FF" )
```


**Cor Atraso Seller**
```dax
IF ( [% Atraso] > 0.10, "#FF3B3B", "#1A6BF5" )
```


**Cor Grupo Atraso**
```dax
IF ( SELECTEDVALUE ( dm_seller[Grupo Atraso Ordem] ) = 4, "#FF3B3B", "#1A6BF5" )
```


**Cor Prazo UF**
```dax
IF ( [Prazo Médio UF] > 18, "#FF3B3B", "#CFE0FF" )
```


**Cor Nota Tabela**
```dax
IF ( [Nota Ajustada Seller] < [Nota Média Rede], "#C41F1F", "#00995A" )
```


**Cor Nota Regiao**
```dax
IF ( [Nota Média] < 4.1, "#C41F1F", "#111111" )
```


**Cor Atraso Tabela**
```dax
IF ( [% Atraso] > 0.10, "#C41F1F", "#3F3F3F" )
```


**Cor Pill Ticket**
```dax
IF ( [Ticket vs Rede] >= 0, "#00995A", "#C41F1F" )
```


**Cor Pill Nota**
```dax
IF ( [Nota vs Rede] >= 0, "#00995A", "#C41F1F" )
```


**Cor Pill Atraso**
```dax
IF ( [Atraso vs Rede] <= 0, "#00995A", "#C41F1F" )
```


**Cor KPI Atraso Seller**
```dax
IF ( [% Atraso] > [% Atraso Rede], "#FF3B3B", "#111111" )
```


**Cor Categoria Seller**
```dax
VAR _max = MAXX ( ALLSELECTED ( dm_categoria[categoria] ), [Faturamento] )
RETURN IF ( [Faturamento] = _max, "#1A6BF5", "#CFE0FF" )
```
