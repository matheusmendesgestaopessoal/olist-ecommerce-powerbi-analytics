// Desenha as ligações (chave estrangeira → chave primária) entre os cards de tabela.
// RELACOES = [[tabelaFK, colunaFK, tabelaPK, colunaPK, opcoes?], ...]  opcoes: {lado: "esq"|"dir", folga: px, tracejado: true}
function desenharLigacoes(RELACOES) {
  const tela = document.getElementById("tela");
  const svg = document.querySelector("svg.ligacoes");
  const base = tela.getBoundingClientRect();
  const caixa = (el) => { const b = el.getBoundingClientRect(); return { x: b.left - base.left, y: b.top - base.top, w: b.width, h: b.height }; };
  const linha = (t, c) => document.querySelector(`#${t} [data-c="${c}"]`) || document.querySelector(`#${t} h4`);
  let s = "";
  const pe = (x, y, dir) => // pé de galinha (lado "muitos")
    `<path d="M${x} ${y - 7} L${x + dir * 12} ${y} L${x} ${y + 7} M${x} ${y} L${x + dir * 12} ${y}" stroke="#1A6BF5" stroke-width="1.6" fill="none"/>`;
  const barra = (x, y) => `<path d="M${x} ${y - 7} L${x} ${y + 7}" stroke="#1A6BF5" stroke-width="1.8"/>`;
  RELACOES.forEach(([tf, cf, tp, cp, op = {}]) => {
    const a = caixa(document.getElementById(tf)), b = caixa(document.getElementById(tp));
    const la = caixa(linha(tf, cf)), lb = caixa(linha(tp, cp));
    const ya = la.y + la.h / 2, yb = lb.y + lb.h / 2;
    const estilo = `stroke="#1A6BF5" stroke-opacity=".55" stroke-width="1.6" fill="none"${op.tracejado ? ' stroke-dasharray="6 5"' : ""}`;
    const sobrepoe = a.x < b.x + b.w && b.x < a.x + a.w;
    if (sobrepoe && op.vertical) {           // mesma coluna, uma em cima da outra: liga as bordas
      const cima = a.y < b.y ? a : b, baixo = a.y < b.y ? b : a, x = a.x + a.w / 2;
      s += `<path d="M${x} ${cima.y + cima.h} L${x} ${baixo.y}" ${estilo}/>`;
      const yf = a.y < b.y ? a.y + a.h : a.y, df = a.y < b.y ? 1 : -1;   // pé de galinha vertical no lado da FK
      s += `<path d="M${x - 7} ${yf} L${x} ${yf + df * 12} L${x + 7} ${yf} M${x} ${yf} L${x} ${yf + df * 12}" stroke="#1A6BF5" stroke-width="1.6" fill="none"/>`;
      const yp = a.y < b.y ? b.y : b.y + b.h;
      s += `<path d="M${x - 7} ${yp - df * 6} L${x + 7} ${yp - df * 6}" stroke="#1A6BF5" stroke-width="1.8"/>`;
      return;
    }
    if (sobrepoe) {                          // mesma coluna: laço pela lateral
      const lado = op.lado || "esq", f = op.folga || 36;
      const x0 = lado === "esq" ? a.x : a.x + a.w, x1 = lado === "esq" ? b.x : b.x + b.w;
      const xl = lado === "esq" ? Math.min(x0, x1) - f : Math.max(x0, x1) + f, d = lado === "esq" ? -1 : 1;
      s += `<path d="M${x0} ${ya} C${xl} ${ya}, ${xl} ${yb}, ${x1} ${yb}" ${estilo}/>`;
      s += pe(x0 + d * 0, ya, d) + barra(x1 + d * 6, yb);
      return;
    }
    const dir = b.x > a.x ? 1 : -1;          // colunas diferentes: curva horizontal
    const x0 = dir > 0 ? a.x + a.w : a.x, x1 = dir > 0 ? b.x : b.x + b.w;
    const m = Math.max(40, Math.abs(x1 - x0) / 2);
    s += `<path d="M${x0} ${ya} C${x0 + dir * m} ${ya}, ${x1 - dir * m} ${yb}, ${x1} ${yb}" ${estilo}/>`;
    s += pe(x0, ya, dir) + barra(x1 - dir * 6, yb);
  });
  svg.innerHTML = s;
}

function marcarAltura() {
  const pre = document.createElement("pre");
  pre.id = "posicoes"; pre.style.display = "none";
  const b = document.body.getBoundingClientRect();   // tamanho do conteúdo, não da janela
  pre.textContent = JSON.stringify({ altura: Math.ceil(b.height), largura: Math.ceil(b.width) });
  document.body.appendChild(pre);
}
