# Dashboard

- `Dashboard_Matheus_Mendes.pbip`: projeto do Power BI (abre no Power BI Desktop). O relatório fica em `Dashboard_Matheus_Mendes.Report/` e o modelo semântico em `Dashboard_Matheus_Mendes.SemanticModel/`.
- `tema_matheus.json`: tema da identidade visual (já aplicado no relatório; para outro arquivo: Exibir → Temas → Procurar temas).
- `prints/`: imagens tiradas do Power BI: `00` página Diagnóstico inteira, `01` primeira tela, `02` a `06` uma por seção (contexto, vender mais × melhor, o que decide a nota, onde dói, recomendação), `07` detalhe do seller (drill-through) e `08` dica de ferramenta do estado.
- `prototipo/`: protótipo em HTML aprovado antes da construção, já com os números reais.
- `gerador_pbir/`: gera as páginas do relatório a partir do layout aprovado (ver abaixo).

## Páginas

| Página | Tipo | O que responde |
|---|---|---|
| Diagnóstico | Rolagem (storytelling) | Quem vende mais é quem o cliente aprova? O que decide a nota, onde dói e o que fazer |
| Detalhe do seller | Drill-through (botão direito num seller → Drill-through) | Perfil do seller contra a rede, ponto de atenção e ação recomendada |
| Dica do estado | Dica de ferramenta | Prazo, atraso e nota do estado ao passar o mouse nas barras de estado |

Filtros da página: ano, região do cliente e categoria. Os títulos de seção são medidas de texto e mudam com eles.

## Como o layout é gerado

O visual do relatório é o do protótipo, sem retrabalho manual no Power BI:

1. `gerador_pbir/fundos/*.html` descreve cada página com o mesmo CSS do protótipo. Tudo o que é estático
   (cards, sombras, ícones, rótulos, legendas, recomendação) está no HTML.
2. Onde entra um dado, o HTML tem uma vaga vazia (`data-v="..."`).
3. `gerar_paginas.py` abre o HTML no Chrome sem janela, mede a posição de cada vaga e fotografa a página em 2x.
4. A foto vira a imagem de fundo da página, e cada visual (gráfico, número, título dinâmico, tabela, filtro, botão)
   é criado transparente exatamente em cima da sua vaga, clonado de modelos gravados pelo próprio Power BI (`gerador_pbir/modelos/`).

Para mudar o layout: editar o HTML (abrir com `?debug` no navegador mostra as vagas) e rodar, nesta pasta:

```bash
python gerador_pbir/gerar_paginas.py
```

Com o Power BI aberto, aparece "Apply external changes": basta aplicar. Mudanças no modelo (TMDL) pedem fechar e abrir o projeto de novo.

**Como ver funcionando:** abra `Dashboard_Matheus_Mendes.pbip` no Power BI Desktop (gratuito). Os dados vêm junto no `cache.abf`, sem precisar do PostgreSQL. Para atualizar a partir do banco, carregue os dados com `python -m codigo.ingestao.carregar_raw` e clique em **Atualizar**.
