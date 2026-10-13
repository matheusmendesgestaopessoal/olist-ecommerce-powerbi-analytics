"""Gera as imagens do README (assets/*.png) na identidade visual do dashboard.

- modelo_dimensional.png  estrela do Power BI, lida dos arquivos TMDL do projeto
- power_query.png         linhagem das consultas src_ → stg_ → ft_/dm_, lida do TMDL
- banner, stack, arquitetura, jornada, gerador_pbir: páginas escritas à mão (*.html)
  com os logos de logos/ embutidos na cor da marca

Tabelas, colunas, relacionamentos e dependências saem do próprio modelo; só a posição dos cards é definida aqui.
Uso (na raiz do projeto):  python assets/fontes/gerar_diagramas.py
"""
import html as html_lib
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

AQUI = Path(__file__).parent
RAIZ = AQUI.parent.parent
MODELO = RAIZ / "dashboard" / "Dashboard_Matheus_Mendes.SemanticModel" / "definition"
CHROME = next((c for c in [r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                           r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"] if Path(c).exists()), None)


def ler(caminho):
    return caminho.read_text(encoding="utf-8").replace("\r\n", "\n")


# ------------------------------------------------------------------ leitura do TMDL
def tabela(nome):
    """Colunas visíveis e ocultas de uma tabela: [(nome, tipo, chave?)]."""
    cols = []
    for b in re.split(r"\n(?=\tcolumn |\tpartition |\tmeasure )", ler(MODELO / "tables" / f"{nome}.tmdl")):
        m = re.match(r"\tcolumn ('(?:[^']|'')+'|[^\s=]+)( =)?", b)
        if not m:
            continue
        tipo = re.search(r"\n\t\tdataType: (\w+)", b)
        tipo = {"string": "texto", "int64": "inteiro", "double": "decimal", "dateTime": "data", "boolean": "lógico"}.get(
            tipo.group(1) if tipo else "", "DAX")
        cols.append((m.group(1).strip("'"), tipo))
    return cols


def relacionamentos():
    return re.findall(r"fromColumn: (\w+)\.(\w+)\n\ttoColumn: (\w+)\.(\w+)", ler(MODELO / "relationships.tmdl"))


def consultas():
    """{consulta: (grupo, [consultas de que depende])} para expressões e partições do modelo."""
    nomes, corpos = {}, {}
    for m in re.finditer(r"^expression (\w+) =\n(.*?)(?=^expression |\Z)", ler(MODELO / "expressions.tmdl"), re.M | re.S):
        corpos[m.group(1)] = m.group(2)
        nomes[m.group(1)] = re.search(r"queryGroup: (\w+)", m.group(2)).group(1)
    for f in (MODELO / "tables").glob("*.tmdl"):
        t = ler(f)
        part = re.search(r"\tpartition [^\n]*= m\n(.*?)(?=\n\tannotation|\Z)", t, re.S)
        grupo = re.search(r"queryGroup: (\w+)", t)
        if part and grupo:
            corpos[f.stem] = part.group(1)
            nomes[f.stem] = grupo.group(1)
    return {n: (nomes[n], sorted(o for o in nomes if o != n and re.search(rf"\b{o}\b", corpos[n]))) for n in nomes}


# ------------------------------------------------------------------ peças HTML
def card(nome, cols, x, y, w, cab, cab_txt, subtitulo="", grao="", chaves=()):
    linhas = []
    for c, tipo in cols:
        if c in chaves:
            ch, classe = '<span class="ch fk">FK</span>' if nome.startswith("ft_") else '<span class="ch pk">PK</span>', "col pk"
        else:
            ch, classe = '<span class="ch"></span>', "col"
        linhas.append(f'<div class="{classe}" data-c="{c}">{ch}<span class="nome">{c}</span><span class="tipo">{tipo}</span></div>')
    sub = f"<small>{subtitulo}</small>" if subtitulo else ""
    g = f'<div class="grao">{grao}</div>' if grao else ""
    return (f'<div class="tabela card" id="{nome}" style="left:{x}px;top:{y}px;width:{w}px;--cab:{cab};--cab-txt:{cab_txt}">'
            f'<h4>{nome}{sub}</h4>{g}{"".join(linhas)}</div>')


def pagina(titulo, rotulo, texto, legenda, corpo, script, largura, altura):
    return f"""<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><title>{titulo}</title>
<link rel="stylesheet" href="diagramas.css"><style>body{{width:{largura}px}}#tela{{height:{altura}px;margin-top:34px}}</style></head><body>
<div class="topo"><span class="lbl">{rotulo}</span><h1>{titulo}</h1><p>{texto}</p><div class="legenda">{legenda}</div></div>
<div id="tela"><svg class="ligacoes"></svg>{corpo}</div>
<script src="ligacoes.js"></script><script>{script}marcarAltura();</script>
</body></html>"""


# ------------------------------------------------------------------ modelo dimensional
POS = {"dm_data": (90, 40), "dm_cliente_uf": (90, 470), "ft_vendas": (560, 120),
       "dm_seller": (1050, 40), "dm_categoria": (1050, 470)}
GRAO = {"ft_vendas": "Grão: pedido entregue × seller × categoria"}


def dimensional():
    rel = relacionamentos()
    chaves = {}
    for ft, cf, dm, cd in rel:
        chaves.setdefault(ft, set()).add(cf)
        chaves.setdefault(dm, set()).add(cd)
    cards = []
    for n, (x, y) in POS.items():
        fato = n.startswith("ft_")
        cards.append(card(n, tabela(n), x, y, 380 if fato else 330, "#1A6BF5" if fato else "#EEF4FF",
                          "#FFFFFF" if fato else "#0F4FD1", "FATO" if fato else "DIMENSÃO", GRAO.get(n, ""), chaves.get(n, ())))
    nota = ('<div class="nota" style="left:560px;top:790px;width:380px">Atributos do pedido (prazo, atraso, nota) se repetem nas '
            'linhas do mesmo pedido: as medidas de pedido agrupam por <code>order_id</code> com <code>SUMMARIZE</code> '
            'para contar cada pedido uma vez.</div>')
    ligacoes = [[ft, cf, dm, cd, {}] for ft, cf, dm, cd in rel]
    legenda = ('<span><i class="leg-cor" style="background:#1A6BF5"></i>Fato (eventos medidos)</span>'
               '<span><i class="leg-cor" style="background:#EEF4FF"></i>Dimensão (contexto da análise)</span>'
               '<span>Linha azul = relacionamento 1 : N, filtro da dimensão para o fato</span>')
    return pagina("Modelo dimensional no Power BI", "Modelo semântico · esquema estrela",
                  "1 fato e 4 dimensões, montados no Power Query. Juntar venda, entrega e avaliação na mesma linha deixa o filtro de "
                  "região, categoria e ano valer para todas as medidas, sem relacionamentos bidirecionais.",
                  legenda, "".join(cards) + nota, f"desenharLigacoes({json.dumps(ligacoes, ensure_ascii=False)});", 1480, 870)


# ------------------------------------------------------------------ linhagem do Power Query
GRUPOS = [("00_SOURCE", "src_ · conexão", "#F1F2F4", "#111111"), ("10_STAGING", "stg_ · limpeza e tipos", "#EEF4FF", "#0F4FD1"),
          ("20_DIMENSIONS", "dm_ · dimensões", "#5AB0FF", "#0B2E66"), ("30_FACTS", "ft_ · fato", "#1A6BF5", "#FFFFFF")]
FAZ = {
    "src_orders": "raw.orders", "src_order_items": "raw.order_items", "src_reviews": "raw.order_reviews",
    "src_products": "raw.products", "src_sellers": "raw.sellers", "src_customers": "raw.customers",
    "src_category_translation": "raw.product_category_translation",
    "stg_orders": "datas tipadas; vazio vira nulo", "stg_order_items": "preço e frete en-US; limite de postagem",
    "stg_reviews": "nota como inteiro", "stg_review_order": "1 nota por pedido (média)", "stg_products": "categoria limpa",
    "stg_sellers": "texto limpo", "stg_customers": "UF do cliente", "stg_category_translation": "texto limpo",
    "dm_data": "calendário da 1ª à última compra", "dm_seller": "+ grupo de atraso (DAX)", "dm_categoria": "nome em português",
    "dm_cliente_uf": "27 UFs e 5 regiões", "ft_vendas": "entregues · prazo · atraso · etapas · nota",
}


def power_query():
    q = consultas()
    colunas = {g: sorted((n for n, (gr, _) in q.items() if gr == g), key=lambda n: (len(q[n][1]) == 0, n)) for g, *_ in GRUPOS}
    colunas["20_DIMENSIONS"] = [n for n in ["dm_data", "dm_seller", "dm_categoria", "dm_cliente_uf"] if n in q]
    # ordem das fontes acompanha a ordem do staging, para as linhas cruzarem menos
    ordem_stg = ["stg_orders", "stg_customers", "stg_order_items", "stg_reviews", "stg_review_order", "stg_products",
                 "stg_category_translation", "stg_sellers"]
    colunas["10_STAGING"] = [n for n in ordem_stg if n in q]
    colunas["00_SOURCE"] = [n for n in ["src_orders", "src_customers", "src_order_items", "src_reviews", "src_products",
                                        "src_category_translation", "src_sellers"] if n in q]
    blocos, x = [], 60
    for g, titulo, cab, txt in GRUPOS:
        blocos.append(f'<div class="lbl" style="position:absolute;left:{x}px;top:0">{titulo}</div>')
        nomes = colunas[g]
        passo = 96 if g != "30_FACTS" else 0
        y0 = 36 if g != "30_FACTS" else 300
        for i, n in enumerate(nomes):
            blocos.append(f'<div class="tabela card" id="{n}" style="left:{x}px;top:{y0 + i * passo}px;width:300px;--cab:{cab};--cab-txt:{txt}">'
                          f'<h4>{n}</h4><div class="grao">{FAZ.get(n, "")}</div></div>')
        x += 380
    arestas = [[dep, n] for n, (_, deps) in q.items() for dep in deps]
    script = ("(function(){const tela=document.getElementById('tela'),b=tela.getBoundingClientRect(),svg=document.querySelector('svg.ligacoes');"
              "const cx=e=>{const r=document.getElementById(e).getBoundingClientRect();return{x:r.left-b.left,y:r.top-b.top,w:r.width,h:r.height}};"
              f"let s='';{json.dumps(arestas)}.forEach(([a,c])=>{{const p=cx(a),q=cx(c),x0=p.x+p.w,y0=p.y+p.h/2,x1=q.x,y1=q.y+q.h/2,m=(x1-x0)/2;"
              "s+=`<path d=\"M${x0} ${y0} C${x0+m} ${y0}, ${x1-m} ${y1}, ${x1-8} ${y1}\" stroke=\"#1A6BF5\" stroke-opacity=\".5\" stroke-width=\"1.6\" fill=\"none\"/>`;"
              "s+=`<path d=\"M${x1-9} ${y1-5} L${x1-1} ${y1} L${x1-9} ${y1+5}\" fill=\"#1A6BF5\"/>`});svg.innerHTML=s})();")
    legenda = ('<span><i class="leg-cor" style="background:#F1F2F4"></i>conecta numa tabela do schema raw</span>'
               '<span><i class="leg-cor" style="background:#EEF4FF"></i>limpa, tipa e consolida</span>'
               '<span><i class="leg-cor" style="background:#1A6BF5"></i>vira tabela do modelo</span>'
               '<span>Seta = a consulta da direita usa a da esquerda</span>')
    return pagina("Power Query em camadas", "Transformação · linguagem M",
                  f"{len(q)} consultas em 4 grupos. Só as tabelas dm_ e ft_ são carregadas no modelo; src_ e stg_ existem para separar "
                  "conexão, limpeza e regra de negócio, e cada camada pode ser conferida sozinha.",
                  legenda, "".join(blocos), script, 1600, 36 + 8 * 96)


# ------------------------------------------------------------------ render
def chrome(*args):
    return subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars", *args],
                          capture_output=True, text=True, encoding="utf-8", timeout=180)


def preparar(html):
    """Cópia para render: logos embutidos (cor da marca) e medição de altura no fim da página."""
    t = html.read_text(encoding="utf-8")

    def logo(m):
        svg = (AQUI / "logos" / f"{m.group(1)}.svg").read_text(encoding="utf-8")
        svg = svg[svg.index("<svg"):]
        if m.group(2):
            svg = svg.replace("<svg ", f'<svg fill="{m.group(2)}" ', 1)
        return f'<i class="logo">{svg}</i>'
    t = re.sub(r'<i class="logo" data-logo="([\w]+)"(?: data-cor="(#[0-9A-Fa-f]{6})")?></i>', logo, t)
    if "marcarAltura" not in t:
        t = t.replace("</body>", '<script src="ligacoes.js"></script><script>marcarAltura();</script></body>')
    tmp = html.with_name(f"_render_{html.name}")
    tmp.write_text(t, encoding="utf-8")
    return tmp


def fotografar(html, png):
    html = preparar(html)
    dom = chrome("--window-size=1900,1200", "--dump-dom", html.resolve().as_uri()).stdout
    m = re.search(r'<pre id="posicoes"[^>]*>(.*?)</pre>', dom, re.S)
    tam = json.loads(html_lib.unescape(m.group(1)))
    chrome(f"--window-size={tam['largura']},{tam['altura']}", "--force-device-scale-factor=2",
           f"--screenshot={png.resolve()}", html.resolve().as_uri())
    html.unlink()
    print(f"{png.name}: {tam['largura']}×{tam['altura']} (2x)")


if __name__ == "__main__":
    if not CHROME:
        sys.exit("Chrome ou Edge não encontrado.")
    (AQUI / "modelo_dimensional.html").write_text(dimensional(), encoding="utf-8")
    (AQUI / "power_query.html").write_text(power_query(), encoding="utf-8")
    # figuras do gerador: fundo gerado e resultado no Power BI (página de detalhe do seller)
    shutil.copyfile(RAIZ / "dashboard/Dashboard_Matheus_Mendes.Report/StaticResources/RegisteredResources/fundo_detalhe_seller.png",
                    AQUI / "_fundo.png")
    shutil.copyfile(RAIZ / "dashboard/prints/07_detalhe_seller.png", AQUI / "_resultado.png")
    nomes = sys.argv[1:] or ["banner", "stack", "jornada", "arquitetura", "power_query", "modelo_dimensional", "gerador_pbir"]
    for nome in nomes:
        fotografar(AQUI / f"{nome}.html", AQUI.parent / f"{nome}.png")
