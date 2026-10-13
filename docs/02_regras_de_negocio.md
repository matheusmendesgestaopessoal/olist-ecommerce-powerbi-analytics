# Regras de Negócio e Critérios Analíticos

Cada regra abaixo foi decidida depois da auditoria dos dados (`sql/02_auditoria/`) e é aplicada igual no Power Query, nas medidas DAX e no `diagnostico.py`.

---

## 1. Universo e métricas

| Regra | Definição | Por quê |
|---|---|---|
| Universo comercial | Apenas pedidos com status `delivered` | Cancelados e em trânsito não são venda concluída |
| Faturamento | Soma de `price` por item | O frete não é receita do seller pelo produto; `payment_value` mistura parcelas e vouchers |
| Volume | Quantidade de itens (linhas de `order_items`) | Um pedido pode ter vários itens de sellers diferentes |
| Pedidos | Pedidos distintos | Ticket médio = faturamento ÷ pedidos |
| Ano | Ano da compra (`order_purchase_timestamp`) | Data em que a venda aconteceu |
| Ticket médio do seller | Faturamento do seller ÷ pedidos em que ele participou | Em pedidos com vários sellers, cada um conta só os próprios itens |

## 2. Avaliações

| Regra | Definição | Por quê |
|---|---|---|
| Nota do pedido | Média das avaliações do pedido | 547 pedidos têm mais de uma avaliação (202 com notas diferentes) |
| Nota do seller | Média das notas dos pedidos em que ele participou, uma vez por pedido | Um pedido com cinco itens não pode pesar cinco vezes |
| Nota da categoria | Mesma lógica, uma vez por pedido e categoria | Idem |
| Nota ajustada | `N/(N+m) × nota + m/(N+m) × média do ano` | Um seller com nota 5 em 3 avaliações não é comparável a um com 4,7 em mil |
| Parâmetro `m` | 13,88 para sellers e 16,36 para categorias | Funciona como avaliações "virtuais" com a média geral: com poucas avaliações, a nota fica perto da média |
| Ranking por nota | Usa a nota ajustada | Evita premiar amostras pequenas (534 sellers têm um único pedido avaliado) |

## 3. Entrega

| Regra | Definição |
|---|---|
| Prazo de entrega | Dias entre a compra e a entrega ao cliente |
| Atraso | Entrega ao cliente depois da data estimada informada na compra |
| Atraso do seller | Postagem (`order_delivered_carrier_date`) depois do limite do item (`shipping_limit_date`) |
| Tempo de transporte | Dias entre a postagem e a entrega |
| Região | Região do estado do cliente (Norte, Nordeste, Centro-Oeste, Sudeste, Sul) |

## 4. Categorias e sellers

| Regra | Definição | Por quê |
|---|---|---|
| Categoria vazia | Vira "Não informado": entra nos totais, fica fora dos rankings | 610 produtos sem categoria (R$ 170,7 mil); não dá para premiar uma categoria que não existe |
| Nome da categoria | Exibido em português, com a tradução oficial do dataset para o inglês guardada em `dm_categoria` | Leitura do público brasileiro |
| Identificação do seller | Código abreviado (6 primeiros caracteres) | O dataset é anonimizado |
| Elegibilidade para "melhor seller" | Pelo menos 30 pedidos avaliados no período | Amostra mínima para a nota ser confiável |

## 5. Comparações no tempo

- 2016 (set a dez) e 2018 (jan a ago) são parciais. Crescimento entre anos é medido por **faturamento médio por mês**.
- Rankings são feitos dentro de cada ano, nunca somando anos parciais com anos completos.

## 6. Achados da auditoria que viraram regra

| Achado | Evidência | Decisão |
|---|---|---|
| Itens em pedidos cancelados | 461 pedidos cancelados com itens | Universo = `delivered` |
| Pedidos multi-seller | 1.278 pedidos | Faturamento por item, nunca pelo total do pedido |
| Pedidos com várias avaliações | 547 pedidos (202 com notas diferentes) | Uma nota por pedido (média) |
| Produtos sem categoria | 610 produtos, R$ 170,7 mil | "Não informado", fora dos rankings |
| Pagamentos parcelados ou múltiplos | Até 29 linhas por pedido | `payment_value` não é faturamento |
| Amostras desiguais de avaliação | 534 sellers com 1 pedido avaliado | Nota ajustada e mínimo de 30 avaliações |
| Cobertura temporal desigual | 2016 set–dez, 2018 jan–ago | Comparação por mês |
