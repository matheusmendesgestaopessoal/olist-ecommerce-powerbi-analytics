let
  // ---- nível do pedido: só entregues, com cliente, etapas, atraso e nota
  Entregues = Table.SelectRows(stg_orders, each [order_status] = "delivered"),
  ComCliente = Table.ExpandTableColumn(Table.NestedJoin(Entregues, {"customer_id"}, stg_customers, {"customer_id"}, "cli", JoinKind.LeftOuter), "cli", {"customer_state"}),
  LimitePostagem = Table.Group(stg_order_items, {"order_id"}, {{"limite_postagem", each List.Max([shipping_limit_date]), type nullable datetime}}),
  ComLimite = Table.ExpandTableColumn(Table.NestedJoin(ComCliente, {"order_id"}, LimitePostagem, {"order_id"}, "lim", JoinKind.LeftOuter), "lim", {"limite_postagem"}),
  ComNota = Table.ExpandTableColumn(Table.NestedJoin(ComLimite, {"order_id"}, stg_review_order, {"order_id"}, "av", JoinKind.LeftOuter), "av", {"review_score_order"}, {"nota_pedido"}),
  Dias = (inicio, fim) => if inicio = null or fim = null then null else Duration.TotalDays(fim - inicio),
  Prazo = Table.AddColumn(ComNota, "prazo_entrega_dias", each Dias([order_purchase_timestamp], [order_delivered_customer_date]), type nullable number),
  Postagem = Table.AddColumn(Prazo, "dias_postagem", each Dias([order_purchase_timestamp], [order_delivered_carrier_date]), type nullable number),
  Transporte = Table.AddColumn(Postagem, "dias_transporte", each Dias([order_delivered_carrier_date], [order_delivered_customer_date]), type nullable number),
  Atrasado = Table.AddColumn(Transporte, "atrasado", each
      if [order_delivered_customer_date] = null or [order_estimated_delivery_date] = null then null
      else if DateTime.Date([order_delivered_customer_date]) > DateTime.Date([order_estimated_delivery_date]) then 1 else 0, Int64.Type),
  SellerAtrasou = Table.AddColumn(Atrasado, "seller_postou_atrasado", each
      if [order_delivered_carrier_date] <> null and [limite_postagem] <> null and [order_delivered_carrier_date] > [limite_postagem] then 1 else 0, Int64.Type),
  Faixa = Table.AddColumn(SellerAtrasou, "faixa", each
      let d = [prazo_entrega_dias] in
      if d = null then {null, null, null, null}
      else if d <= 7 then {"até 7", 1, "até 14", 1}
      else if d <= 14 then {"8–14", 2, "até 14", 1}
      else if d <= 21 then {"15–21", 3, "15–21", 2}
      else if d <= 30 then {"22–30", 4, "22+", 3}
      else {"30+", 5, "22+", 3}),
  FaixaColunas = Table.SplitColumn(Faixa, "faixa", each _, {"faixa_prazo", "faixa_prazo_ordem", "faixa_prazo_seller", "faixa_prazo_seller_ordem"}),
  Pedidos = Table.SelectColumns(FaixaColunas, {"order_id", "customer_state", "order_purchase_date", "nota_pedido", "prazo_entrega_dias", "dias_postagem", "dias_transporte", "atrasado", "seller_postou_atrasado", "faixa_prazo", "faixa_prazo_ordem", "faixa_prazo_seller", "faixa_prazo_seller_ordem"}),

  // ---- itens agrupados por pedido × seller × categoria
  ItensProduto = Table.ExpandTableColumn(Table.NestedJoin(stg_order_items, {"product_id"}, stg_products, {"product_id"}, "p", JoinKind.LeftOuter), "p", {"product_category_name"}, {"category_key"}),
  CategoriaPadrao = Table.TransformColumns(ItensProduto, {{"category_key", each if _ = null or Text.Trim(_) = "" then "nao_informado" else _, type text}}),
  Agrupado = Table.Group(CategoriaPadrao, {"order_id", "seller_id", "category_key"}, {
      {"itens", each Table.RowCount(_), Int64.Type},
      {"faturamento", each List.Sum([price]), type number},
      {"frete", each List.Sum([freight_value]), type number}}),

  // ---- junta (inner: só pedidos entregues)
  Juntado = Table.ExpandTableColumn(Table.NestedJoin(Agrupado, {"order_id"}, Pedidos, {"order_id"}, "ped", JoinKind.Inner), "ped",
      List.RemoveItems(Table.ColumnNames(Pedidos), {"order_id"})),
  Tipos = Table.TransformColumnTypes(Juntado, {
      {"order_purchase_date", type date}, {"nota_pedido", type number}, {"prazo_entrega_dias", type number},
      {"dias_postagem", type number}, {"dias_transporte", type number}, {"atrasado", Int64.Type},
      {"seller_postou_atrasado", Int64.Type}, {"faixa_prazo", type text}, {"faixa_prazo_ordem", Int64.Type},
      {"faixa_prazo_seller", type text}, {"faixa_prazo_seller_ordem", Int64.Type}, {"customer_state", type text}})
in
  Tipos
