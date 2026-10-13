# DIAGNÓSTICO · números do dashboard e do documento de análise

''' Recalcula, direto do PostgreSQL (camada raw), todos os números citados no
dashboard e em docs/05_analise_e_recomendacoes.md. Serve de conferência: se uma
medida DAX mudar, o número dela tem que bater com esta saída.

Regras (as mesmas do Power Query e das medidas DAX):
- Universo comercial: pedidos com status 'delivered'
- Faturamento: soma de price por item (sem frete; pedidos multi-seller contam por item)
- Ano: ano da compra (order_purchase_timestamp)
- Nota do pedido: média das avaliações do pedido (alguns pedidos têm mais de uma)
- Atraso: entrega ao cliente depois da data estimada
- Nota ajustada (Empirical Bayes): n/(n+m)·nota + m/(n+m)·média do ano
  (m = 13,88 para sellers e 16,36 para categorias)

Uso (na raiz do projeto):  python -m codigo.analises.diagnostico
'''

import math
import os

import numpy as np
import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine

M_SELLER, M_CATEGORIA = 13.88, 16.36


def conectar():
    load_dotenv(".env")
    return create_engine(
        f"postgresql+psycopg2://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}"
        f"@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
    )


def carregar(e):
    q = lambda s: pd.read_sql(s, e)
    ped = q("""SELECT order_id, customer_id, order_status,
                      order_purchase_timestamp::timestamp AS compra,
                      NULLIF(order_delivered_customer_date, '')::timestamp AS entrega,
                      NULLIF(order_estimated_delivery_date, '')::timestamp AS prevista
               FROM raw.orders""")
    itens = q("""SELECT order_id, product_id, seller_id, price::numeric AS preco, freight_value::numeric AS frete
                 FROM raw.order_items""")
    itens[["preco", "frete"]] = itens[["preco", "frete"]].astype(float)
    nota = q("SELECT order_id, AVG(review_score::numeric)::float AS nota FROM raw.order_reviews GROUP BY order_id")
    cli = q("SELECT customer_id, customer_state AS uf FROM raw.customers")
    sel = q("SELECT seller_id, seller_state AS uf_seller FROM raw.sellers")
    prod = q("""SELECT product_id, COALESCE(NULLIF(TRIM(product_category_name), ''), 'nao_informado') AS categoria
                FROM raw.products""")

    ent = ped[ped.order_status == "delivered"].merge(cli, on="customer_id").merge(nota, on="order_id", how="left")
    ent["ano"] = ent.compra.dt.year
    ent["atraso"] = (ent.entrega.dt.normalize() > ent.prevista).astype(int)
    ent["dias"] = (ent.entrega - ent.compra).dt.total_seconds() / 86400
    vend = (itens.merge(ent[["order_id", "ano", "nota", "atraso", "dias", "uf"]], on="order_id")
                 .merge(prod, on="product_id", how="left").merge(sel, on="seller_id"))
    vend["categoria"] = vend.categoria.fillna("nao_informado")
    return ent, vend


def nota_ajustada(df, chave, m):
    """Nota média e nota ajustada por (ano, chave); uma linha por pedido-chave avaliado."""
    av = df.dropna(subset=["nota"]).drop_duplicates(["order_id", chave])
    media_ano = av.groupby("ano").nota.mean()
    g = av.groupby(["ano", chave]).nota.agg(["mean", "count"]).rename(columns={"mean": "nota", "count": "n"})
    mu = g.index.get_level_values("ano").map(media_ano)
    g["nota_ajustada"] = g.n / (g.n + m) * g.nota + m / (g.n + m) * mu
    return g


def correlacao_postos(a, b):
    return a.rank().corr(b.rank())


def main():
    ent, vend = carregar(conectar())
    fat = vend.preco.sum()

    print("== VISÃO GERAL (pedidos entregues)")
    print(f"pedidos {ent.order_id.nunique():,} · itens {len(vend):,} · faturamento R$ {fat/1e6:.2f} Mi "
          f"· ticket médio R$ {fat/ent.order_id.nunique():,.0f} · sellers {vend.seller_id.nunique():,}")
    print(f"pedidos avaliados {ent.nota.notna().sum():,} · nota média {ent.nota.mean():.2f} "
          f"· notas 1: {(ent.nota.round() == 1).mean():.1%}")
    por_ano = vend.groupby("ano").agg(fat=("preco", "sum"), itens=("preco", "size"), pedidos=("order_id", "nunique"))
    meses = ent.groupby("ano").compra.agg(lambda s: s.dt.to_period("M").nunique())
    por_ano["meses"] = meses
    por_ano["fat_mes"] = por_ano.fat / por_ano.meses
    print(por_ano.assign(fat=lambda d: (d.fat / 1e6).round(2), fat_mes=lambda d: (d.fat_mes / 1e3).round(0)))

    print("\n== CAMPEÃS POR ANO (categorias, sem 'nao_informado')")
    cat = vend[vend.categoria != "nao_informado"]
    nc = nota_ajustada(cat, "categoria", M_CATEGORIA)
    vc = cat.groupby(["ano", "categoria"]).agg(fat=("preco", "sum"), itens=("preco", "size")).join(nc)
    for ano, g in vc.groupby(level="ano"):
        g = g.droplevel("ano")
        print(f"{ano}: faturamento {g.fat.idxmax()} · itens {g.itens.idxmax()} · nota ajustada {g.nota_ajustada.idxmax()}")

    print("\n== CAMPEÕES POR ANO (sellers)")
    ns = nota_ajustada(vend, "seller_id", M_SELLER)
    vs = vend.groupby(["ano", "seller_id"]).agg(fat=("preco", "sum"), itens=("preco", "size")).join(ns)
    for ano, g in vs.groupby(level="ano"):
        g = g.droplevel("ano")
        print(f"{ano}: faturamento {g.fat.idxmax()[:8]} · itens {g.itens.idxmax()[:8]} · nota ajustada {g.nota_ajustada.idxmax()[:8]}")

    print("\n== TICKET MÉDIO POR SELLER")
    t = vend.groupby("seller_id").agg(fat=("preco", "sum"), pedidos=("order_id", "nunique"))
    t["ticket"] = t.fat / t.pedidos
    print(f"mediana R$ {t.ticket.median():,.0f} · média R$ {t.ticket.mean():,.0f} · maior faturamento: "
          f"{t.fat.idxmax()[:8]} com ticket R$ {t.loc[t.fat.idxmax(), 'ticket']:,.2f}")

    print("\n== QUEM VENDE MAIS VENDE MELHOR?")
    s = vend.groupby("seller_id").agg(fat=("preco", "sum"))
    sv = vend.dropna(subset=["nota"]).drop_duplicates(["order_id", "seller_id"]).groupby("seller_id").agg(
        nota=("nota", "mean"), n=("nota", "size"), atraso=("atraso", "mean"))
    s = s.join(sv)
    ordem = s.sort_values("fat", ascending=False)
    k = math.ceil(len(ordem) * 0.10)
    print(f"top 10% ({k} sellers): {ordem.head(k).fat.sum()/fat:.0%} do faturamento")
    grandes = s[s.n >= 30]
    print(f"sellers com 30+ avaliações: {len(grandes)} · correlação de postos faturamento x nota: "
          f"{correlacao_postos(grandes.fat, grandes.nota):.2f} · atraso x nota: {correlacao_postos(grandes.atraso, grandes.nota):.2f}")
    top20 = ordem.head(20)
    print(f"dos 20 maiores em faturamento, {(top20.nota < ent.nota.mean()).sum()} têm nota abaixo da média ({ent.nota.mean():.2f})")
    c = cat.groupby("categoria").agg(fat=("preco", "sum"), itens=("preco", "size"))
    c = c.join(cat.dropna(subset=["nota"]).drop_duplicates(["order_id", "categoria"]).groupby("categoria").nota.mean())
    c["rk_itens"], c["rk_nota"] = c.itens.rank(ascending=False), c.nota.rank(ascending=False)
    top = c.sort_values("itens", ascending=False).head(1)
    print(f"categoria nº 1 em itens: {top.index[0]} · posição na nota: {int(top.rk_nota.iloc[0])}º de {len(c)}")

    print("\n== O QUE DECIDE A NOTA: A ENTREGA")
    av = ent.dropna(subset=["nota", "entrega"])
    g = av.groupby("atraso").agg(pedidos=("order_id", "size"), nota=("nota", "mean"),
                                 nota1=("nota", lambda x: (x.round() == 1).mean()))
    print(g.round(3))
    um = av[av.nota.round() == 1]
    print(f"atrasados: {av.atraso.mean():.1%} dos pedidos e {um.atraso.mean():.0%} das notas 1")
    faixas = pd.cut(av.dias, [0, 7, 14, 21, 30, 1000], labels=["até 7", "8 a 14", "15 a 21", "22 a 30", "mais de 30"])
    print(av.groupby(faixas, observed=True).agg(pedidos=("order_id", "size"), nota=("nota", "mean")).round(2))

    n_ok = av[av.atraso == 0].nota.mean()
    for parte in (0.5, 1.0):  # simulação: parte dos atrasados passa a ter a nota média de quem chega no prazo
        sim = av.nota.copy()
        sim.loc[av[av.atraso == 1].sample(frac=parte, random_state=1).index] = n_ok
        print(f"se {parte:.0%} dos atrasos chegassem no prazo: nota {av.nota.mean():.2f} → {sim.mean():.2f} "
              f"· notas 1 {(av.nota.round() == 1).mean():.1%} → {(sim.round() == 1).mean():.1%}")

    print("\n== QUEM ATRASA: SELLER OU TRANSPORTE")
    e = conectar()
    etapas = pd.read_sql("""SELECT o.order_id,
                                   NULLIF(o.order_delivered_carrier_date, '')::timestamp AS postado,
                                   MAX(NULLIF(i.shipping_limit_date, '')::timestamp)     AS limite
                            FROM raw.orders o JOIN raw.order_items i ON i.order_id = o.order_id
                            GROUP BY o.order_id, o.order_delivered_carrier_date""", e)
    x = ent.merge(etapas, on="order_id")
    x["seller_atrasou"] = (x.postado > x.limite).astype(int)
    x["dias_seller"] = (x.postado - x.compra).dt.total_seconds() / 86400
    x["dias_transporte"] = (x.entrega - x.postado).dt.total_seconds() / 86400
    at, ok = x[x.atraso == 1], x[x.atraso == 0]
    print(f"nos atrasados, o seller postou depois do limite em {at.seller_atrasou.mean():.0%} (no prazo: {ok.seller_atrasou.mean():.0%})")
    print(f"dias até postar: atrasados {at.dias_seller.mean():.1f} · no prazo {ok.dias_seller.mean():.1f}")
    print(f"dias de transporte: atrasados {at.dias_transporte.mean():.1f} · no prazo {ok.dias_transporte.mean():.1f}")
    print(f"prazo prometido médio {(x.prevista - x.compra).dt.days.mean():.1f} dias · entrega real média {x.dias.mean():.1f} dias "
          f"· {(x.entrega < x.prevista).mean():.0%} chegam antes do prometido")
    grandes = grandes.assign(faixa=pd.qcut(grandes.atraso.rank(method="first"), 4,
                                           labels=["menor atraso", "2º quartil", "3º quartil", "maior atraso"]))
    print(grandes.groupby("faixa", observed=True).agg(sellers=("fat", "size"), atraso=("atraso", "mean"),
                                                      nota=("nota", "mean")).round(3))

    print("\n== CRESCIMENTO (faturamento por mês, 2017 → 2018)")
    mensal = vend[vend.ano.isin([2017, 2018])].groupby(["categoria", "ano"]).preco.sum().unstack()
    mensal[2017], mensal[2018] = mensal[2017] / 12, mensal[2018] / 8
    total = (vend[vend.ano == 2018].preco.sum() / 8) / (vend[vend.ano == 2017].preco.sum() / 12) - 1
    print(f"marketplace {total:+.0%}")
    topo = mensal.sort_values(2018, ascending=False).head(6)
    print(((topo / 1e3).round(0)).assign(crescimento=(topo[2018] / topo[2017] - 1).round(2)))

    print("\n== ONDE DÓI: GEOGRAFIA")
    sp = vend.drop_duplicates("seller_id")
    print(f"sellers em SP: {(sp.uf_seller == 'SP').mean():.0%} · faturamento de sellers de SP: "
          f"{vend[vend.uf_seller == 'SP'].preco.sum()/fat:.0%}")
    reg = {"SP": "Sudeste", "RJ": "Sudeste", "MG": "Sudeste", "ES": "Sudeste", "PR": "Sul", "SC": "Sul", "RS": "Sul",
           "DF": "Centro-Oeste", "GO": "Centro-Oeste", "MT": "Centro-Oeste", "MS": "Centro-Oeste"}
    av = av.assign(regiao=av.uf.map(reg).fillna(av.uf.map(lambda u: "Norte" if u in {"AM", "PA", "AC", "RO", "RR", "AP", "TO"} else "Nordeste")))
    print(av.groupby("regiao").agg(pedidos=("order_id", "size"), dias=("dias", "mean"), atraso=("atraso", "mean"),
                                    nota=("nota", "mean")).sort_values("dias").round(2))


if __name__ == "__main__":
    main()
