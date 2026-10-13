# Análise e Recomendações · Olist E-Commerce

**Período:** set/2016 a ago/2018 · **Universo:** 96.478 pedidos entregues · **Autor:** Matheus Mendes

Todos os números podem ser recalculados com `python -m codigo.analises.diagnostico`.
Cada recomendação segue o cartão de decisão: Fato → Interpretação → Causas → Validação → Ação → Resultado → Acompanhamento.

---

## Recomendação

> **Recomendo trocar o critério de "melhor seller" e atacar o atraso no transporte: quem vende mais não é quem o cliente aprova, e o que decide a nota é a entrega.**

| Ordem | Frente | Decisão | Dono | Prazo | Indicador (hoje → meta) | Esforço | Confiança |
|:---:|---|---|---|---|---|---|---|
| 1 | Atraso no transporte | Monitorar pedidos em risco e cobrar as rotas com mais atraso | Logística | 90 dias | Atraso 6,7% → 3,5% | Médio | Alta |
| 2 | Critério de melhor seller | Ranquear por faturamento, nota ajustada e pontualidade juntos | Comercial / Sellers | 30 dias | Sellers referência com atraso < 4% | Baixo | Alta |
| 3 | Nordeste e Norte | Prazo realista e sellers mais perto do cliente | Logística + Comercial | 6 meses | Prazo NE 19,9 → 15 dias | Alto | Média |

### Por que essa ordem
O atraso é o fator que mais derruba a nota e a primeira ação (monitorar pedidos em risco) usa dados que a empresa já tem.
O novo critério de seller é barato e muda quem é premiado. A frente regional é estrutural e leva mais tempo.

---

## Visão geral

| Indicador | Valor |
|---|---:|
| Faturamento (itens entregues, sem frete) | R$ 13,22 Mi |
| Pedidos entregues · itens | 96.478 · 110.197 |
| Ticket médio | R$ 137 |
| Sellers com venda | 2.970 |
| Nota média · notas 1 | 4,16 · 9,7% dos pedidos avaliados |
| Crescimento do faturamento por mês, 2017 → 2018 | +82% |

### Campeões por ano (pergunta original)

| Ano | Faturamento | Volume de itens | Nota ajustada |
|---|---|---|---|
| 2016 (set–dez) | Móveis e decoração (R$ 6 mil) | Móveis e decoração (65) | Perfumaria (4,33) |
| 2017 | Cama, mesa e banho (R$ 491 mil) | Cama, mesa e banho (5.135) | Livros de interesse geral (4,50) |
| 2018 (jan–ago) | Beleza e saúde (R$ 756 mil) | Beleza e saúde (5.841) | Livros de interesse geral (4,52) |

Em sellers, o maior faturamento de 2018 (código 4869f7, R$ 136 mil) tem nota 4,13, abaixo da média. O seller com a
melhor nota ajustada de 2018 (d13e50, nota 4,70) faturou R$ 7,1 mil. **Os campeões nunca coincidem**, e é daí que nasce
a pergunta deste projeto.

Ticket médio por seller: mediana R$ 105, média R$ 196.

---

## O fio da história

1. **Quem vende mais não é quem o cliente aprova.** Entre os 623 sellers com 30 ou mais avaliações, a correlação entre
   faturamento e nota é **−0,08**: praticamente nenhuma. Dos 20 sellers que mais faturam, **9 têm nota abaixo da média**.
   Cama, mesa e banho é a 1ª categoria em itens vendidos e a **59ª de 73** em nota.
2. **O que decide a nota é a entrega.** A correlação entre atraso e nota é **−0,47**, seis vezes mais forte. Pedido no
   prazo tem nota **4,29**; atrasado, **2,27**. Os atrasos são 6,7% dos pedidos, mas geram **37% de todas as notas 1**.
3. **O gargalo é o transporte.** Em **72% dos pedidos atrasados o seller postou dentro do prazo**. O tempo de transporte
   dos atrasados é de 27,9 dias, contra 8 dias nos pedidos no prazo.
4. **O Nordeste é quem mais sofre.** 60% dos sellers estão em SP. O cliente do Nordeste espera 19,9 dias em média
   (Sudeste: 10,7), o atraso chega a 12% e a nota cai para 3,97.

---

## Cartão 1 · Atraso no transporte
**Prioridade:** Alta · **Esforço:** Médio · **Confiança na causa:** Alta · **Dono:** Logística

**1. Fato**
6.381 pedidos avaliados chegaram depois do prazo prometido (6,7%). A nota média deles é **2,27** e **54%** recebem nota 1;
nos pedidos no prazo, a nota é **4,29** e só 6,6% recebem nota 1. A nota cai com o prazo: até 7 dias, 4,42; mais de 30 dias, 2,25.
*Fonte:* `diagnostico.py`, seção "O que decide a nota".

**2. Interpretação**
O cliente avalia a experiência, não o produto. Um atraso apaga a boa venda feita pelo seller.
O prazo prometido é folgado (23,4 dias em média, contra 12,6 dias de entrega real; 92% chegam antes), então os atrasos
são exceções longas, que podem ser previstas e acompanhadas.
*O que ainda não sabemos:* a transportadora e o motivo do atraso, que não existem no dataset.

**3. Causas prováveis**
| Hipótese | Evidência | Confiança |
|---|---|---|
| Transporte lento em rotas longas | 72% dos atrasados foram postados no prazo; transporte de 27,9 dias | Alta |
| Seller posta depois do limite | Acontece em 28% dos atrasados (8% nos no prazo) | Média |
| Distância até o cliente | Nordeste e Norte com os maiores prazos | Alta |

**4. Validação**
Cruzar os pedidos atrasados com a transportadora e a rota (dado interno, fora do dataset) para achar onde o atraso se concentra.

**5. Ação**
| Passo | Responsável | Prazo |
|---|---|---|
| Alerta de pedido em risco: postado e ainda em trânsito perto do prazo prometido | Logística + Dados | 30 dias |
| Avisar o cliente antes do atraso, com novo prazo | Atendimento | 30 dias |
| Revisar transportadoras nas rotas com mais atraso | Logística | 90 dias |

**6. Resultado esperado**
| Cenário | Atraso | Nota média | Notas 1 |
|---|---:|---:|---:|
| Hoje | 6,7% | 4,16 | 9,7% |
| Metade dos atrasos evitada | ~3,4% | 4,22 | 7,9% |
| Todos os atrasos evitados | 0% | 4,29 | 6,1% |

Simulação: os pedidos que deixam de atrasar passam a ter a nota média dos pedidos no prazo.

**7. Acompanhamento**
- **KPI:** % de pedidos atrasados por semana e por região.
- **Gatilho:** região com atraso acima de 10% por duas semanas seguidas entra em revisão de rota.

---

## Cartão 2 · Critério de melhor seller
**Prioridade:** Alta · **Esforço:** Baixo · **Confiança:** Alta · **Dono:** Comercial / Gestão de sellers

**1. Fato**
O faturamento não prevê a nota (correlação −0,08). Separando os sellers com 30 ou mais avaliações em quatro grupos pelo atraso:

| Grupo | Atraso médio | Nota média |
|---|---:|---:|
| Menor atraso | 1,5% | 4,32 |
| 2º | 4,1% | 4,23 |
| 3º | 6,9% | 4,13 |
| Maior atraso | 12,9% | 3,95 |

Os 10% maiores sellers concentram **67%** do faturamento.

**2. Interpretação**
Um ranking só por faturamento premia sellers que podem estar desgastando a marca. E a nota simples engana: 534 sellers
têm um único pedido avaliado.

**3. Causas prováveis**
O ranking usado no desafio original mede tamanho, não qualidade. A nota precisa de ajuste pelo tamanho da amostra.

**4. Validação**
Testar o novo critério em um trimestre: os sellers "referência" devem manter nota e pontualidade acima da média.

**5. Ação**
| Passo | Responsável | Prazo |
|---|---|---|
| Critério "seller referência": faturamento acima da média + nota ajustada acima da média + 30 avaliações ou mais | Comercial | 30 dias |
| Incluir pontualidade (atraso abaixo de 4%) no critério | Comercial + Logística | 30 dias |
| Alertar os grandes sellers com atraso no 4º grupo | Gestão de sellers | 60 dias |

**6. Resultado esperado**
Destaque e benefícios passam a premiar quem vende bem **e** entrega bem; os grandes com atraso alto recebem plano de correção.

**7. Acompanhamento**
- **KPI:** nota ajustada e atraso dos sellers referência, por trimestre.
- **Gatilho:** seller referência com atraso acima de 6% perde o selo.

---

## Cartão 3 · Nordeste e Norte
**Prioridade:** Média · **Esforço:** Alto · **Confiança na causa:** Média · **Dono:** Logística + Comercial

**1. Fato**
| Região | Pedidos | Prazo médio | Atraso | Nota |
|---|---:|---:|---:|---:|
| Sudeste | 65.731 | 10,7 dias | 6% | 4,18 |
| Sul | 13.745 | 14,0 dias | 6% | 4,19 |
| Centro-Oeste | 5.594 | 15,0 dias | 6% | 4,13 |
| Nordeste | 8.975 | 19,9 dias | 12% | 3,97 |
| Norte | 1.779 | 22,5 dias | 8% | 4,03 |

60% dos sellers estão em SP e respondem por 64% do faturamento.

**2. Interpretação**
O produto viaja longe até o cliente do Nordeste e do Norte. Prazo maior e atraso maior derrubam a nota da região.

**3. Causas prováveis**
Concentração de sellers e estoque no Sudeste; rotas longas.

**4. Validação**
Comparar, dentro do Nordeste, pedidos de sellers locais e de sellers de SP (prazo e nota).

**5. Ação**
| Passo | Responsável | Prazo |
|---|---|---|
| Prazo prometido por região, mais realista para Nordeste e Norte | Logística | 60 dias |
| Atrair sellers das categorias mais vendidas no Nordeste | Comercial | 6 meses |

**6. Resultado esperado**
Prazo médio do Nordeste de 19,9 para 15 dias e atraso abaixo de 8% em 6 meses.

**7. Acompanhamento**
- **KPI:** prazo, atraso e nota por região, mensal.

---

## Premissas e limitações
- Dados reais e anonimizados de 2016 a 2018; sellers aparecem pelo código.
- Correlação não é causa: a relação entre atraso e nota é forte e consistente, mas a confirmação exige os dados internos de transporte.
- A simulação de impacto é uma estimativa para priorização.
- O dataset não tem custo logístico, então as ações de transporte não têm valor financeiro calculado.
