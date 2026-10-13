# Registro de Revisão · 13/10/2026

Revisão do projeto depois da entrega original. Os números do dashboard foram recalculados fora do Power BI e
**conferem**. A revisão organizou o repositório, corrigiu dois erros na auditoria em SQL e ampliou a pergunta.

---

## 1. Números conferidos

`codigo/analises/diagnostico.py` recalcula do PostgreSQL os números do dashboard com as mesmas regras do Power Query.

| Indicador | Dashboard | Diagnóstico |
|---|---:|---:|
| Faturamento | R$ 13,22 Mi | R$ 13,22 Mi |
| Pedidos entregues · itens | 96 mil · 110 mil | 96.478 · 110.197 |
| Pedidos avaliados · nota média | 95.832 · 4,16 | 95.832 · 4,16 |
| Ticket médio | R$ 137 | R$ 137 |
| Faturamento dos 10% maiores sellers | 67% | 67% |

As 33 consultas de `sql/02_auditoria` e `sql/03_validacao` rodam sem erro sobre a camada `raw`.

## 2. Correções

| O que estava errado | Efeito | Correção |
|---|---|---|
| A auditoria e o README diziam "572 sellers com um único pedido avaliado" | Número documentado não batia com a consulta | A consulta retorna **534**; documentação atualizada |
| `01_create_raw.sql` e `06_categorias_ausentes.sql` usavam a tabela `raw.product_category_name_translation` | A consulta 06 falhava: a ingestão (e o Power BI) criam `raw.product_category_translation` | Nome unificado para `product_category_translation` |

## 3. Organização

- Os SQLs de auditoria e validação, o script de ingestão e os dados estavam em pastas separadas. Agora tudo está no repositório, na estrutura `codigo/`, `sql/`, `dados/`, `dashboard/`, `docs/`.
- O relatório passou para o formato **PBIP** (PBIR + TMDL), em arquivos de texto versionáveis.
- O banco local passou a se chamar `olist`; as consultas `src_` do Power Query apontam para ele.
- Credenciais só no `.env` (fora do Git), com `.env.example` no repositório. Os CSVs não são versionados.

## 4. Pergunta ampliada

O desafio original pedia os melhores sellers e categorias por ano. Os campeões em faturamento e em nota nunca
coincidiram, então a análise passou a investigar **o que decide a nota do cliente**. O resultado (o prazo de entrega,
com o transporte como principal gargalo) está em `05_analise_e_recomendacoes.md`.

## 5. Dashboard reconstruído

Para responder à pergunta ampliada, o modelo do Power BI foi refeito:

| Antes | Depois |
|---|---|
| 3 fatos (`ft_vendas` por item, `ft_avaliacoes_seller`, `ft_avaliacoes_categoria`) | 1 fato `ft_vendas` no grão pedido × seller × categoria, com prazo, atraso, etapas, estado do cliente e nota |
| Sem datas de entrega nem estado do cliente | Novas consultas `src_customers`/`stg_customers`; `stg_orders` com postagem, entrega e data estimada |
| 4 dimensões | 5 dimensões: nova `dm_cliente_uf` (estado e região); `dm_categoria` com nomes em português |
| 26 medidas, 3 tabelas de apoio (parâmetros de campo) | Medidas organizadas em pastas (base, nota, entrega, sellers, rede, textos, cores); tabelas de apoio removidas |
| Relatório de 1 página montado à mão | 3 páginas geradas por `dashboard/gerador_pbir/gerar_paginas.py` a partir de fundos em HTML: diagnóstico, detalhe do seller (drill-through) e dica do estado |

Os números do dashboard novo foram conferidos por consulta DAX contra a saída de `diagnostico.py`
(nota no prazo 4,29 × atrasado 2,27, atraso 6,7%, 37% das notas 1, 72% dos atrasos no transporte, regiões e faixas de prazo).
`docs/medidas-dax.md` saiu: as medidas estão no dicionário de dados (`04`), gerado do próprio modelo.

## Como reproduzir

```bash
python -m codigo.ingestao.carregar_raw        # CSVs → PostgreSQL (schema raw)
python -m codigo.analises.diagnostico         # todos os números da análise
```
