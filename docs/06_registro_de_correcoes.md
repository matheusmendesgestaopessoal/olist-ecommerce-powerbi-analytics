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

O modelo do Power BI ainda não tem as datas de entrega nem o estado do cliente: elas entram na reconstrução do
dashboard, com uma tabela fato de pedidos.

## Como reproduzir

```bash
python -m codigo.ingestao.carregar_raw        # CSVs → PostgreSQL (schema raw)
python -m codigo.analises.diagnostico         # todos os números da análise
```
