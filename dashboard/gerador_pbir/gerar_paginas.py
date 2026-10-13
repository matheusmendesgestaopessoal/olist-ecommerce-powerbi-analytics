"""Gera as páginas do dashboard Olist (Power BI Project, formato PBIR) fiéis ao protótipo aprovado.

Como funciona
  1. O layout de cada página é um HTML em fundos/ (mesmo CSS do protótipo). Tudo o que é
     estático (cards, sombras, ícones, rótulos, legendas, recomendação) fica no HTML.
  2. Onde entra um dado, o HTML tem uma "vaga" vazia (atributo data-v).
  3. O Chrome sem janela mede a posição de cada vaga e fotografa a página (2x, para ficar nítida).
  4. A foto vira a imagem de fundo da página no Power BI, e cada visual (gráfico, número,
     título dinâmico, filtro) é criado transparente exatamente em cima da sua vaga.
  Resultado: o relatório fica igual ao protótipo e os números continuam vivos (filtros,
  drill-through, dica de ferramenta).

Os visuais são clonados de modelos que o próprio Power BI gravou (pasta modelos/), trocando só
posição, campos e formatação, para o visual.json continuar válido.

Uso (na pasta dashboard/):  python gerador_pbir/gerar_paginas.py
"""
import copy
import html as html_lib
import json
import re
import shutil
import subprocess
import sys
import uuid
from pathlib import Path

AQUI = Path(__file__).parent
REPORT = AQUI.parent / "Dashboard_Matheus_Mendes.Report"
DEF = REPORT / "definition"
MODELOS = AQUI / "modelos"
FUNDOS = AQUI / "fundos"
TEMA = AQUI.parent / "tema_matheus.json"
RECURSOS = REPORT / "StaticResources" / "RegisteredResources"
ESCALA = 2  # resolução da imagem de fundo (2x = nítida em telas de alta densidade)
MED = "_Medidas"  # tabela das medidas

CHROME = next((c for c in [r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                           r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"] if Path(c).exists()), None)

# ------------------------------------------------------------------ identidade
AZUL, AZUL_TINTA, AZUL_PASTA, AZUL_SEL, AZUL_FUNDO = "#1A6BF5", "#0F4FD1", "#5AB0FF", "#CFE0FF", "#EEF4FF"
VERMELHO, VERM_ESC, VERDE_ESC = "#FF3B3B", "#C41F1F", "#00995A"
GRAFITE, GRAFITE2, TEXTO, DIVISOR, FUNDO = "#111111", "#5E5E5E", "#3F3F3F", "#EFEFED", "#F7F8FA"
FONTES = {
    400: "'''Segoe UI'', wf_segoe-ui_normal, helvetica, arial, sans-serif'",
    600: "'''Segoe UI Semibold'', wf_segoe-ui_semibold, helvetica, arial, sans-serif'",
    700: "'''Segoe UI Bold'', wf_segoe-ui_bold, helvetica, arial, sans-serif'",
    900: "'''Segoe UI Black'', ''Segoe UI Bold'', helvetica, arial, sans-serif'",
}

def pt(px):
    """Tamanho do CSS (px) para o Power BI (pt)."""
    return round(px * 0.75, 1)

# ------------------------------------------------------------------ utilitários JSON
def lit(v):
    return {"expr": {"Literal": {"Value": v}}}

def cor(hexa):
    return {"solid": {"color": lit(f"'{hexa}'")}}

def medida(nome):
    return {"Measure": {"Expression": {"SourceRef": {"Entity": MED}}, "Property": nome}}

def cor_medida(nome):
    return {"solid": {"color": {"expr": medida(nome)}}}

def coluna(entidade, prop):
    return {"Column": {"Expression": {"SourceRef": {"Entity": entidade}}, "Property": prop}}

def ref(campo):
    """queryRef de um campo (Tabela.Campo)."""
    c = campo[next(iter(campo))]
    return f"{c['Expression']['SourceRef']['Entity']}.{c['Property']}"

def proj(campo, ativo=False, nome=None):
    p = {"field": campo, "queryRef": ref(campo), "nativeQueryRef": campo[next(iter(campo))]["Property"]}
    if ativo:
        p["active"] = True
    if nome:
        p["displayName"] = nome
    return p

def novo_id():
    return uuid.uuid4().hex[:20]

T = {n: json.loads((MODELOS / f"{n}.json").read_text(encoding="utf-8"))
     for n in ["card", "bar", "slicer", "table", "combo", "button"]}

def filtro_topn(campo, nome_medida, n, direcao):
    """Filtro de visual 'N primeiros' (direcao: 2 = maiores, 1 = menores)."""
    entidade = campo["Column"]["Expression"]["SourceRef"]["Entity"]
    prop = campo["Column"]["Property"]
    return {"name": novo_id(), "field": campo, "type": "TopN", "filter": {"Version": 2, "From": [
        {"Name": "subquery", "Expression": {"Subquery": {"Query": {
            "Version": 2,
            "From": [{"Name": "d", "Entity": entidade, "Type": 0}, {"Name": "_", "Entity": MED, "Type": 0}],
            "Select": [{"Column": {"Expression": {"SourceRef": {"Source": "d"}}, "Property": prop}, "Name": "field"}],
            "OrderBy": [{"Direction": direcao, "Expression": {"Measure": {"Expression": {"SourceRef": {"Source": "_"}}, "Property": nome_medida}}}],
            "Top": n}}}, "Type": 2},
        {"Name": "d", "Entity": entidade, "Type": 0}],
        "Where": [{"Condition": {"In": {
            "Expressions": [{"Column": {"Expression": {"SourceRef": {"Source": "d"}}, "Property": prop}}],
            "Table": {"SourceRef": {"Source": "subquery"}}}}}]}}

def filtro_valores(campo, valores):
    """Filtro de visual por lista de valores (ex.: só 2017 e 2018)."""
    entidade = campo["Column"]["Expression"]["SourceRef"]["Entity"]
    prop = campo["Column"]["Property"]
    return {"name": novo_id(), "field": campo, "type": "Categorical", "filter": {"Version": 2,
        "From": [{"Name": "d", "Entity": entidade, "Type": 0}],
        "Where": [{"Condition": {"In": {
            "Expressions": [{"Column": {"Expression": {"SourceRef": {"Source": "d"}}, "Property": prop}}],
            "Values": [[{"Literal": {"Value": v}}] for v in valores]}}}]}}


# ------------------------------------------------------------------ fundo: medir e fotografar o HTML
def chrome(*args):
    return subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars", *args],
                          capture_output=True, text=True, encoding="utf-8", timeout=180)

def medir(html):
    saida = chrome("--window-size=1920,1080", "--dump-dom", html.resolve().as_uri()).stdout
    m = re.search(r'<pre id="posicoes"[^>]*>(.*?)</pre>', saida, re.S)
    if not m:
        sys.exit(f"não consegui medir {html.name}")
    return json.loads(html_lib.unescape(m.group(1)))

def fotografar(html, largura, altura, png):
    chrome(f"--window-size={largura},{altura}", f"--force-device-scale-factor={ESCALA}",
           f"--screenshot={png.resolve()}", html.resolve().as_uri())
    if not png.exists():
        sys.exit(f"não consegui fotografar {html.name}")


class Pagina:
    def __init__(self, nome, titulo, html, largura, tipo=None, oculta=False, binding=None, filtros=None):
        self.id, self.visuais, self.z = nome, [], 0
        pos = medir(FUNDOS / html)
        self.vagas = pos["vagas"]
        altura = pos["altura"] if largura == 1920 and pos["altura"] > 1080 else {1920: 1080, 320: 240}[largura]
        self.imagem = f"fundo_{Path(html).stem}.png"
        RECURSOS.mkdir(parents=True, exist_ok=True)
        fotografar(FUNDOS / html, largura, altura, RECURSOS / self.imagem)
        self.pagina = {
            "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/page/2.1.0/schema.json",
            "name": nome, "displayName": titulo,
            "displayOption": "FitToWidth" if altura > 1080 else "FitToPage",
            "height": altura, "width": largura,
            "objects": {
                "background": [{"properties": {"image": {"image": {
                    "name": lit(f"'{self.imagem}'"),
                    "url": {"expr": {"ResourcePackageItem": {"PackageName": "RegisteredResources", "PackageType": 1,
                                                              "ItemName": self.imagem}}},
                    "scaling": lit("'Fit'")}}, "transparency": lit("0D")}}],
                "outspace": [{"properties": {"color": cor(FUNDO)}}],
            },
        }
        if tipo:
            self.pagina["type"] = tipo
        if oculta:
            self.pagina["visibility"] = "HiddenInViewMode"
        if binding:
            self.pagina["pageBinding"] = binding
        if filtros:
            self.pagina["filterConfig"] = {"filters": filtros}

    def _base(self, modelo, vaga):
        x, y, w, h = self.vagas[vaga]
        v = copy.deepcopy(T[modelo])
        v["name"] = novo_id()
        self.z += 1
        v["position"] = {"x": x, "y": y, "z": self.z * 100, "height": h, "width": w, "tabOrder": self.z * 100}
        for k in ("parentGroupName", "howCreated", "filterConfig"):
            v.pop(k, None)
        self.visuais.append(v)
        return v

    @staticmethod
    def _limpo(vis, dica=None):
        """Container transparente: sem título, fundo, borda, sombra ou cabeçalho (o fundo é a imagem)."""
        vis["visualContainerObjects"] = {
            "title": [{"properties": {"show": lit("false")}}],
            "subTitle": [{"properties": {"show": lit("false")}}],
            "background": [{"properties": {"show": lit("false")}}],
            "border": [{"properties": {"show": lit("false")}}],
            "dropShadow": [{"properties": {"show": lit("false")}}],
            "visualHeader": [{"properties": {"show": lit("false")}}],
            "padding": [{"properties": {"top": lit("0D"), "bottom": lit("0D"), "left": lit("0D"), "right": lit("0D")}}],
            "visualTooltip": [{"properties": {"show": lit("true")}}],
        }
        if dica:
            vis["visualContainerObjects"]["visualTooltip"] = [
                {"properties": {"show": lit("true"), "type": lit("'Canvas'"), "section": lit(f"'{dica}'")}}]

    @staticmethod
    def _filtros(v, filtros):
        if filtros:
            v.setdefault("filterConfig", {"filters": []})["filters"] += filtros

    # ---------------- texto vivo (medida de texto num card sem moldura)
    def texto(self, vaga, nome_medida, px=14, c=TEXTO, peso=400, alinhar="left", quebra=False, vertical="top", c_medida=None):
        v = self._base("card", vaga)
        vis = v["visual"]
        vis["query"] = {"queryState": {"Data": {"projections": [proj(medida(nome_medida))]}}}
        o = vis["objects"]
        o["layout"][0]["properties"]["alignment"] = lit(f"'{vertical}'")
        o["value"] = [
            {"properties": {"show": lit("true")}},
            {"properties": {"fontSize": lit(f"{pt(px)}D"), "bold": lit("false"), "fontFamily": lit(FONTES[peso]),
                            "horizontalAlignment": lit(f"'{alinhar}'"), "textWrap": lit("true" if quebra else "false"),
                            "fontColor": cor_medida(c_medida) if c_medida else cor(c)},
             "selector": {"id": "default"}},
        ]
        o["padding"] = [{"properties": {"paddingUniform": lit("0L"), "paddingIndividual": lit("true"), "leftMargin": lit("0L"),
                                        "bottomMargin": lit("0L"), "rightMargin": lit("0L"), "topMargin": lit("0L")},
                         "selector": {"id": "default"}}]
        self._limpo(vis)
        vis["visualContainerObjects"]["visualTooltip"] = [{"properties": {"show": lit("false")}}]  # texto não tem dica
        return v

    def _eixos(self, o, rotulos_px=13):
        o["legend"] = [{"properties": {"show": lit("false")}}]
        o["categoryAxis"] = [{"properties": {"show": lit("true"), "fontFamily": lit(FONTES[400]), "fontSize": lit(f"{pt(rotulos_px)}D"),
                                             "labelColor": cor(GRAFITE2), "showAxisTitle": lit("false"),
                                             "concatenateLabels": lit("false")}}]
        o["valueAxis"] = [{"properties": {"show": lit("false"), "showAxisTitle": lit("false"), "gridlineShow": lit("false"),
                                          "secShow": lit("false"), "secShowAxisTitle": lit("false"), "logAxisScale": lit("false")}}]
        o["zoom"] = [{"properties": {"show": lit("false")}}]

    @staticmethod
    def _rotulos(extra=None, casas=None, c=GRAFITE, px=13):
        p = {"show": lit("true"), "color": cor(c), "fontSize": lit(f"{pt(px)}D"), "fontFamily": lit(FONTES[600]),
             "enableBackground": lit("false"), "labelDisplayUnits": lit("1D")}  # número cheio, sem "Mil"/"Mi" automático
        if casas is not None:
            p["labelPrecision"] = lit(f"{casas}L")
        r = [{"properties": p}]
        if extra:
            r += extra
        return r

    # ---------------- barras horizontais (ou colunas)
    def barras(self, vaga, categoria, nome_medida, ordem="Descending", c=AZUL, c_medida=None, topn=None, dica=None,
               espaco=30, colunas=False, casas=None, por_categoria=False, inicio=None, fim=None, filtros=None):
        v = self._base("bar", vaga)
        vis = v["visual"]
        vis["visualType"] = "clusteredColumnChart" if colunas else "clusteredBarChart"
        m = medida(nome_medida)
        pela_categoria = colunas or por_categoria  # colunas no tempo e faixas seguem a ordem da categoria
        vis["query"] = {
            "queryState": {"Category": {"projections": [proj(categoria, ativo=True)]}, "Y": {"projections": [proj(m)]}},
            "sortDefinition": {"sort": [{"field": categoria if pela_categoria else m,
                                         "direction": "Ascending" if pela_categoria else ordem}]},
        }
        o = vis["objects"]
        self._eixos(o)
        o["categoryAxis"][0]["properties"]["innerPadding"] = lit(f"{espaco}L")
        if inicio is not None:
            o["valueAxis"][0]["properties"]["start"] = lit(f"{inicio}D")
        if fim is not None:
            o["valueAxis"][0]["properties"]["end"] = lit(f"{fim}D")
        dp = [{"properties": {"fill": cor(c)}}]
        if c_medida:
            dp.append({"properties": {"fill": cor_medida(c_medida)},
                       "selector": {"data": [{"dataViewWildcard": {"matchingOption": 1}}]}})
        o["dataPoint"] = dp
        o["labels"] = self._rotulos(casas=casas)
        self._limpo(vis, dica)
        if topn:
            self._filtros(v, [filtro_topn(categoria, topn[2] if len(topn) > 2 else nome_medida, topn[0], topn[1])])
        self._filtros(v, filtros)
        return v

    # ---------------- composição (uma barra 100% empilhada, uma série por medida, rótulo branco dentro)
    def composicao(self, vaga, series, espessura=3.2, rotulo_px=20):
        v = self._base("bar", vaga)
        # o Power BI desenha a barra única com ~1/5 da altura do visual: o visual (transparente) cresce
        # em volta do centro da vaga para a barra ficar com a altura da vaga
        pos = v["position"]
        centro = pos["y"] + pos["height"] / 2
        pos["height"] = round(pos["height"] * espessura)
        pos["y"] = round(centro - pos["height"] / 2)
        vis = v["visual"]
        vis["visualType"] = "hundredPercentStackedBarChart"
        vis["query"] = {"queryState": {"Y": {"projections": [proj(medida(n)) for n, _ in series]}}}
        o = vis["objects"]
        self._eixos(o)
        # eixo ligado (sem campo de categoria ele não mostra nada): desligado, o Power BI ignora os espaçamentos
        o["categoryAxis"][0]["properties"]["innerPadding"] = lit("0L")
        o["categoryAxis"][0]["properties"]["maxMarginFactor"] = lit("0L")
        o["dataPoint"] = [{"properties": {"fill": cor(c)}, "selector": {"metadata": f"{MED}.{n}"}} for n, c in series]
        rot = self._rotulos(c="#FFFFFF", px=rotulo_px, casas=0)
        rot[0]["properties"]["fontFamily"] = lit(FONTES[700])
        rot[0]["properties"]["labelPosition"] = lit("'InsideCenter'")
        o["labels"] = rot
        self._limpo(vis)
        return v

    # ---------------- dispersão (um ponto por item da categoria)
    def dispersao(self, vaga, detalhe, x, y, c_medida=None, log_x=True, y_inicio=None, y_fim=None, linha_y=None):
        v = self._base("bar", vaga)
        vis = v["visual"]
        vis["visualType"] = "scatterChart"
        vis["query"] = {"queryState": {
            "Category": {"projections": [proj(detalhe, ativo=True)]},
            "X": {"projections": [proj(medida(x))]},
            "Y": {"projections": [proj(medida(y))]},
        }}
        eixo = lambda: {"show": lit("true"), "fontFamily": lit(FONTES[400]), "fontSize": lit(f"{pt(12)}D"),
                        "labelColor": cor(GRAFITE2), "showAxisTitle": lit("false"), "gridlineShow": lit("true"),
                        "gridlineColor": cor(DIVISOR), "gridlineStyle": lit("'solid'")}
        cx, cy = eixo(), eixo()
        if log_x:
            cx["logAxisScale"] = lit("true")  # nome que o próprio Power BI grava
        if y_inicio is not None:
            cy["start"] = lit(f"{y_inicio}D")
        if y_fim is not None:
            cy["end"] = lit(f"{y_fim}D")
        o = {
            "categoryAxis": [{"properties": cx}],
            "valueAxis": [{"properties": cy}],
            "legend": [{"properties": {"show": lit("false")}}],
            "categoryLabels": [{"properties": {"show": lit("false")}}],
            "dataPoint": [{"properties": {"fill": cor(AZUL)}}],
            "markers": [{"properties": {"markerSize": lit("5L")}}],
        }
        if c_medida:
            o["dataPoint"].append({"properties": {"fill": cor_medida(c_medida)},
                                   "selector": {"data": [{"dataViewWildcard": {"matchingOption": 1}}]}})
        if linha_y:  # linha de referência (constante) no eixo Y, ex.: nota média da rede
            nome, rotulo = linha_y
            o["y1AxisReferenceLine"] = [{"properties": {
                "show": lit("true"), "displayName": lit(f"'{rotulo}'"), "value": {"expr": medida(nome)},
                "lineColor": cor(GRAFITE), "transparency": lit("30D"), "style": lit("'dashed'"), "width": lit("2D"),
                "position": lit("'front'"), "dataLabelShow": lit("true"), "dataLabelColor": cor(GRAFITE2),
                "dataLabelText": lit("'Name'"), "dataLabelHorizontalPosition": lit("'left'"),
                "dataLabelVerticalPosition": lit("'above'"), "dataLabelDecimalPoints": lit("2L")},
                "selector": {"id": "1"}}]
        vis["objects"] = o
        self._limpo(vis)
        return v

    # ---------------- tabela (cabeçalho em maiúsculas, linhas finas, sem moldura)
    def tabela(self, vaga, campos, ordenar=None, direcao="Descending", topn=None, linha=8, cores=None, quebra=False,
               filtros=None, px=15):
        v = self._base("table", vaga)
        vis = v["visual"]
        vis["query"] = {"queryState": {"Values": {"projections": [proj(c, nome=n) for c, n in campos]}}}
        if ordenar:
            vis["query"]["sortDefinition"] = {"sort": [{"field": ordenar, "direction": direcao}]}
        valores = [{"properties": {"fontFamily": lit(FONTES[400]), "fontSize": lit(f"{pt(px)}D"), "fontColorPrimary": cor(TEXTO),
                                   "fontColorSecondary": cor(TEXTO), "backColorPrimary": cor("#FFFFFF"),
                                   "backColorSecondary": cor("#FFFFFF"), "wordWrap": lit("true" if quebra else "false"),
                                   "outlineStyle": lit("0D")}}]
        for nome_medida, nome_cor in (cores or {}).items():  # cor do texto da coluna vinda de uma medida
            valores.append({"properties": {"fontColor": cor_medida(nome_cor)},
                            "selector": {"data": [{"dataViewWildcard": {"matchingOption": 1}}],
                                         "metadata": f"{MED}.{nome_medida}"}})
        vis["objects"] = {
            "columnHeaders": [{"properties": {"fontFamily": lit(FONTES[600]), "fontSize": lit(f"{pt(12)}D"), "fontColor": cor(GRAFITE2),
                                              "backColor": cor(FUNDO), "alignment": lit("'Left'"), "wordWrap": lit("true"),
                                              "outlineStyle": lit("0D")}}],
            "values": valores,
            "grid": [{"properties": {"gridHorizontal": lit("true"), "gridHorizontalColor": cor(DIVISOR), "gridHorizontalWeight": lit("1D"),
                                     "gridVertical": lit("false"), "outlineColor": cor("#FFFFFF"), "outlineWeight": lit("0D"),
                                     "rowPadding": lit(f"{linha}D")}}],
            "total": [{"properties": {"totals": lit("false")}}],
        }
        self._limpo(vis)
        if topn:
            self._filtros(v, [filtro_topn(*topn)])
        self._filtros(v, filtros)
        return v

    # ---------------- filtro (lista suspensa sem cabeçalho; o rótulo está no fundo)
    def filtro(self, vaga, campo):
        v = self._base("slicer", vaga)
        vis = v["visual"]
        vis["query"] = {"queryState": {"Values": {"projections": [proj(campo, ativo=True)]}}}
        o = vis["objects"]
        o["header"] = [{"properties": {"show": lit("false")}}]
        o["items"] = [{"properties": {"fontFamily": lit(FONTES[600]), "textSize": lit(f"{pt(15)}D"), "fontColor": cor(GRAFITE),
                                      "outlineStyle": lit("0D"), "padding": lit("0D")}}]
        o["selectionIcon"] = [{"properties": {"color": cor(AZUL)}}]
        self._limpo(vis)
        return v

    # ---------------- botão invisível sobre o botão desenhado no fundo
    def botao(self, vaga, acao):
        v = self._base("button", vaga)
        vis = v["visual"]
        o = vis["objects"]
        o["icon"] = [{"properties": {"show": lit("false")}}]
        o["text"] = [{"properties": {"show": lit("false")}}]
        o["outline"] = [{"properties": {"show": lit("false")}}]
        o["fill"] = [{"properties": {"show": lit("true"), "fillColor": cor(AZUL_FUNDO), "transparency": lit("100D")},
                      "selector": {"id": "default"}}]
        o["shape"] = [{"properties": {"tileShape": lit("'rectangle'")}, "selector": {"id": "default"}}]
        vis["visualContainerObjects"] = {
            "visualLink": [{"properties": {"show": lit("true"), "type": lit(f"'{acao}'")}}],
            "title": [{"properties": {"show": lit("false")}}],
            "background": [{"properties": {"show": lit("false")}}],
            "border": [{"properties": {"show": lit("false")}}],
            "visualHeader": [{"properties": {"show": lit("false")}}],
        }
        return v

    def gravar(self):
        pasta = DEF / "pages" / self.id
        if pasta.exists():
            shutil.rmtree(pasta)
        (pasta / "visuals").mkdir(parents=True)
        (pasta / "page.json").write_text(json.dumps(self.pagina, ensure_ascii=False, indent=2), encoding="utf-8")
        for v in self.visuais:
            d = pasta / "visuals" / v["name"]
            d.mkdir()
            (d / "visual.json").write_text(json.dumps(v, ensure_ascii=False, indent=2), encoding="utf-8")
        return len(self.visuais)


# ====================================================================== campos usados
ANO = coluna("dm_data", "year")
MES = coluna("dm_data", "Mes Ano")
REGIAO = coluna("dm_cliente_uf", "regiao")
UF = coluna("dm_cliente_uf", "uf")
CATEGORIA = coluna("dm_categoria", "categoria")
SELLER = coluna("dm_seller", "Seller Rótulo")  # código curto + UF, também usado no drill-through
GRUPO_ATRASO = coluna("dm_seller", "Grupo Atraso")
FAIXA = coluna("ft_vendas", "faixa_prazo")
FAIXA_SELLER = coluna("ft_vendas", "faixa_prazo_seller")
SO_2017_2018 = lambda: [filtro_valores(ANO, ["2017L", "2018L"])]

ID_DIAG, ID_SELLER, ID_DICA = "a1d1a9n0o0s1t1i1c0o1", "d2e2t2a2l2h2e2s2e2l2", "d3i3c3a3e3s3t3a3d3o3"


# ====================================================================== PÁGINA 1 · DIAGNÓSTICO
def pagina_diagnostico():
    p = Pagina(ID_DIAG, "Diagnóstico", "diagnostico.html", 1920)

    # cabeçalho: filtros e limpar
    for vaga, campo in [("f_ano", ANO), ("f_regiao", REGIAO), ("f_categoria", CATEGORIA)]:
        p.filtro(vaga, campo)
    p.botao("b_limpar", "ClearAllSlicers")

    # pergunta + resposta + nota por prazo
    p.texto("t_resposta", "Txt Resposta", px=20, c=TEXTO, quebra=True)
    p.barras("g_faixas", FAIXA, "Nota da Faixa", colunas=True, c_medida="Cor Faixa Prazo", espaco=40, casas=2)

    # KPIs
    p.texto("k_fat", "Txt KPI Faturamento", px=38, c="#FFFFFF", peso=900)
    p.texto("p_cresc", "Txt Pill Crescimento", px=13, c="#FFFFFF", peso=700, alinhar="center", vertical="middle")
    p.texto("k_pedidos", "Txt KPI Pedidos", px=38, c=GRAFITE, peso=900)
    p.texto("c_ticket", "Txt Ctx Ticket", px=14, c=GRAFITE2, vertical="middle")
    p.texto("k_nota", "Txt KPI Nota", px=38, c=GRAFITE, peso=900)
    p.texto("p_notas1", "Txt Pill Notas 1", px=13, c=VERM_ESC, peso=700, alinhar="center", vertical="middle")
    p.texto("k_atraso", "Txt KPI Atraso", px=38, c=VERMELHO, peso=900)
    p.texto("p_nota_atrasado", "Txt Pill Nota Atrasado", px=13, c=VERM_ESC, peso=700, alinhar="center", vertical="middle")
    p.texto("k_sellers", "Txt KPI Sellers", px=38, c=GRAFITE, peso=900)
    p.texto("c_top10", "Txt Ctx Top 10", px=14, c=GRAFITE2, vertical="middle")

    # 01 · contexto
    p.texto("h_contexto", "Txt Titulo Contexto", px=34, c=GRAFITE, peso=700)
    p.barras("g_mensal", MES, "Faturamento mil", colunas=True, c_medida="Cor Faturamento Mes", espaco=30, casas=0,
             filtros=SO_2017_2018())
    p.tabela("t_campeoes", [(ANO, "ANO"), (medida("Campeã Faturamento"), "FATURAMENTO"),
                            (medida("Campeã Itens"), "ITENS"), (medida("Campeã Nota"), "NOTA")],
             ordenar=ANO, direcao="Ascending", quebra=True, linha=10, px=14, filtros=SO_2017_2018())

    # 02 · vender mais × vender melhor
    p.texto("h_vender", "Txt Titulo Vender", px=34, c=GRAFITE, peso=700)
    p.dispersao("g_scatter", SELLER, "Faturamento mil 30+", "Nota Ajustada Seller", c_medida="Cor Atraso Seller",
                y_inicio=2, y_fim=5, linha_y=("Nota Média Rede", "nota média da rede"))
    p.tabela("t_top10", [(SELLER, "SELLER"), (medida("Faturamento mil"), "FATURAMENTO (R$ MIL)"),
                         (medida("Nota Ajustada Seller"), "NOTA"), (medida("% Atraso"), "ATRASO")],
             ordenar=medida("Faturamento"), topn=(SELLER, "Faturamento", 10, 2), linha=6,
             cores={"Nota Ajustada Seller": "Cor Nota Tabela", "% Atraso": "Cor Atraso Tabela"})

    # 03 · o que decide a nota
    p.texto("h_nota", "Txt Titulo Nota", px=34, c=GRAFITE, peso=700)
    p.texto("v_prazo", "Txt Nota No Prazo", px=58, c=GRAFITE, peso=900)
    p.texto("c_prazo", "Txt Ctx No Prazo", px=15, c=GRAFITE2, vertical="middle")
    p.texto("v_atrasado", "Txt Nota Atrasado", px=58, c=VERMELHO, peso=900)
    p.texto("c_atrasado", "Txt Ctx Atrasado", px=15, c="#7A1414", vertical="middle")
    p.barras("g_grupos", GRUPO_ATRASO, "Nota Média do Grupo", c_medida="Cor Grupo Atraso", espaco=40, casas=2,
             por_categoria=True, inicio=3.5, fim=4.5)
    p.composicao("g_partes", [("% Atrasos do Transporte", AZUL), ("% Atrasos do Seller", VERMELHO)])
    for vaga, nome, c, peso in [("d_post_ok", "Txt Postagem No Prazo", TEXTO, 400), ("d_post_at", "Txt Postagem Atrasado", GRAFITE, 700),
                                ("d_transp_ok", "Txt Transporte No Prazo", TEXTO, 400), ("d_transp_at", "Txt Transporte Atrasado", VERM_ESC, 700)]:
        p.texto(vaga, nome, px=15, c=c, peso=peso, alinhar="right", vertical="middle")
    p.texto("t_leitura", "Txt Leitura Etapas", px=16, c=TEXTO, quebra=True)

    # 04 · onde dói
    p.texto("h_regiao", "Txt Titulo Regiao", px=34, c=GRAFITE, peso=700)
    p.barras("g_uf", UF, "Prazo Médio UF", c_medida="Cor Prazo UF", topn=(12, 2), dica=ID_DICA, espaco=30, casas=1)
    p.tabela("t_regioes", [(REGIAO, "REGIÃO"), (medida("Prazo Médio"), "PRAZO"), (medida("% Atraso"), "ATRASO"),
                           (medida("Nota Média"), "NOTA")],
             ordenar=medida("Prazo Médio"), direcao="Ascending", linha=10,
             cores={"% Atraso": "Cor Atraso Tabela", "Nota Média": "Cor Nota Regiao"})
    return p


# ====================================================================== PÁGINA 2 · DETALHE DO SELLER
def pagina_seller():
    filtro_nome = novo_id()
    p = Pagina(ID_SELLER, "Detalhe do seller", "detalhe_seller.html", 1920, tipo="Drillthrough", oculta=True,
               binding={"name": novo_id(), "type": "Drillthrough",
                        "parameters": [{"name": novo_id(), "boundFilter": filtro_nome, "fieldExpr": SELLER}]},
               filtros=[{"name": filtro_nome, "field": SELLER, "type": "Categorical", "howCreated": "Drillthrough"}])
    p.botao("b_voltar", "Back")
    p.texto("h_seller", "Txt Titulo Seller", px=19, c=GRAFITE, peso=700)

    p.texto("k_fat", "Txt KPI Faturamento", px=34, c=GRAFITE, peso=900)
    p.texto("c_pos", "Txt Ctx Posicao", px=14, c=GRAFITE2, vertical="middle")
    for chave, val, ctx, pill, c_val in [
        ("ticket", "Txt KPI Ticket", "Txt Ctx Ticket Rede", "Ticket", None),
        ("nota", "Txt KPI Nota Seller", "Txt Ctx Nota Rede", "Nota", None),
        ("atraso", "Txt KPI Atraso", "Txt Ctx Atraso Rede", "Atraso", "Cor KPI Atraso Seller"),
    ]:
        p.texto(f"k_{chave}", val, px=34, c=GRAFITE, peso=900, c_medida=c_val)
        p.texto(f"c_{chave}", ctx, px=14, c=GRAFITE2, vertical="middle")
        p.texto(f"p_{chave}", f"Txt Pill {pill}", px=13, peso=700, alinhar="center", vertical="middle", c_medida=f"Cor Pill {pill}")
    p.texto("k_prazo", "Txt KPI Prazo", px=34, c=GRAFITE, peso=900)
    p.texto("c_prazo", "Txt Ctx Prazo Rede", px=14, c=GRAFITE2, vertical="middle")

    p.barras("g_mes", MES, "Faturamento mil", colunas=True, c_medida="Cor Faturamento Mes", espaco=30, casas=1,
             filtros=SO_2017_2018())
    p.texto("t_perfil", "Txt Perfil Seller", px=15, c=TEXTO, quebra=True)
    p.texto("t_atencao", "Txt Atencao Seller", px=15, c=TEXTO, quebra=True)
    p.texto("t_acao", "Txt Acao Seller", px=15, c=TEXTO, quebra=True)

    p.barras("g_cat", CATEGORIA, "Faturamento mil", c_medida="Cor Categoria Seller", topn=(5, 2, "Faturamento"), espaco=40, casas=1)
    p.barras("g_uf", UF, "Pedidos", c=AZUL_SEL, topn=(6, 2), espaco=35, casas=0)
    p.barras("g_faixa", FAIXA_SELLER, "Nota da Faixa Seller", c_medida="Cor Faixa Seller", espaco=45, casas=2, por_categoria=True)
    return p


# ====================================================================== PÁGINA 3 · DICA DO ESTADO
def pagina_dica():
    p = Pagina(ID_DICA, "Dica do estado", "dica_estado.html", 320, tipo="Tooltip", oculta=True,
               binding={"name": novo_id(), "type": "Tooltip", "parameters": []})
    p.texto("h_estado", "Txt Dica Estado", px=17, c=GRAFITE, peso=700)
    p.texto("t_sub", "Txt Dica Sub", px=12, c=GRAFITE2)
    p.texto("v_prazo", "Txt Dica Prazo", px=15, c=GRAFITE, peso=700, alinhar="right", vertical="middle")
    p.texto("v_atraso", "Txt Dica Atraso", px=15, c=VERMELHO, peso=700, alinhar="right", vertical="middle")
    p.texto("v_nota", "Txt Dica Nota", px=15, c=GRAFITE, peso=700, alinhar="right", vertical="middle")
    return p


# ====================================================================== gravação e limpeza
def registrar_recursos(paginas):
    """Registra o tema e as imagens de fundo em report.json e apaga fundos antigos que ninguém usa."""
    shutil.copyfile(TEMA, RECURSOS / TEMA.name)
    caminho = DEF / "report.json"
    rel = json.loads(caminho.read_text(encoding="utf-8-sig"))
    rel["themeCollection"]["customTheme"] = {"name": TEMA.name, "reportVersionAtImport": rel["themeCollection"]["baseTheme"]["reportVersionAtImport"],
                                             "type": "RegisteredResources"}
    pacotes = rel.setdefault("resourcePackages", [])
    pacote = next((p for p in pacotes if p["name"] == "RegisteredResources"), None)
    if not pacote:
        pacote = {"name": "RegisteredResources", "type": "RegisteredResources", "items": []}
        pacotes.append(pacote)
    imagens = {p.imagem for p in paginas}
    pacote["items"] = [{"name": TEMA.name, "path": TEMA.name, "type": "CustomTheme"}] + \
                      [{"name": n, "path": n, "type": "Image"} for n in sorted(imagens)]
    caminho.write_text(json.dumps(rel, ensure_ascii=False, indent=2), encoding="utf-8")
    for f in RECURSOS.glob("*.png"):
        if f.name not in imagens:
            f.unlink()


if __name__ == "__main__":
    if not CHROME:
        sys.exit("Chrome ou Edge não encontrado: é usado para medir e fotografar os fundos.")
    paginas = [pagina_diagnostico(), pagina_seller(), pagina_dica()]

    for pasta in (DEF / "pages").iterdir():
        if pasta.is_dir() and pasta.name not in {p.id for p in paginas}:
            shutil.rmtree(pasta)
    if (DEF / "bookmarks").exists():
        shutil.rmtree(DEF / "bookmarks")

    total = sum(p.gravar() for p in paginas)
    registrar_recursos(paginas)
    (DEF / "pages" / "pages.json").write_text(json.dumps({
        "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/pagesMetadata/1.1.0/schema.json",
        "pageOrder": [p.id for p in paginas], "activePageName": paginas[0].id}, ensure_ascii=False, indent=2), encoding="utf-8")
    for p in paginas:
        tam = (RECURSOS / p.imagem).stat().st_size / 1e6
        print(f"{p.pagina['displayName']:<18} {p.pagina['width']}×{p.pagina['height']:<5} {len(p.visuais):>3} visuais · fundo {tam:.1f} MB")
    print(f"total: {total} visuais")
