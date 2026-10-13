// Gráficos simples em SVG, só para o protótipo (no Power BI serão visuais nativos).
const AZ = "#1A6BF5", SEL = "#CFE0FF", VERM = "#FF3B3B", VERDE = "#00D980", G2 = "#5E5E5E", LINHA = "#EFEFED";
const fmt = (v, d = 1) => v.toLocaleString("pt-BR", { minimumFractionDigits: d, maximumFractionDigits: d });

const ICONES = {
  receita: '<rect x="2" y="6" width="20" height="12" rx="2"/><circle cx="12" cy="12" r="2"/>',
  lucro: '<polyline points="22 7 13.5 15.5 8.5 10.5 2 17"/><polyline points="16 7 22 7 22 13"/>',
  pedidos: '<path d="M6 2 3 6v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2V6l-3-4Z"/><path d="M3 6h18"/><path d="M16 10a4 4 0 0 1-8 0"/>',
  cancelamento: '<circle cx="12" cy="12" r="10"/><path d="m15 9-6 6"/><path d="m9 9 6 6"/>',
  alerta: '<path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3"/><path d="M12 9v4"/><path d="M12 17h.01"/>',
  meta: '<circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="6"/><circle cx="12" cy="12" r="2"/>',
  ticket: '<path d="M4 2v20l2-1 2 1 2-1 2 1 2-1 2 1 2-1 2 1V2l-2 1-2-1-2 1-2-1-2 1-2-1-2 1Z"/><path d="M16 8h-6a2 2 0 1 0 0 4h4a2 2 0 1 1 0 4H8"/>',
  estoque: '<rect x="3" y="3" width="8" height="8" rx="1"/><rect x="13" y="3" width="8" height="8" rx="1"/><rect x="8" y="13" width="8" height="8" rx="1"/>',
  voltar: '<path d="M19 12H5M11 18l-6-6 6-6"/>',
};
function icones() {
  document.querySelectorAll(".ico,[data-i]").forEach((e) => {
    e.innerHTML = `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="${e.dataset.c || AZ}" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">${ICONES[e.dataset.i]}</svg>`;
  });
}

function colunas(el, { labels, valores, meta, metaLbl, altura = 300, destaque = [], sufixo = "", decimais = 1, linhaMeta }) {
  const W = el.clientWidth, H = altura, pb = 30, pt = 26;
  const max = Math.max(...valores, meta || 0, ...(linhaMeta || [])) * 1.12, bw = (W / labels.length) * 0.56;
  const y = (v) => pt + (H - pt - pb) * (1 - v / max);
  let s = `<svg width="${W}" height="${H}">`;
  [0, 0.5, 1].forEach((f) => { const yy = y(max * f); s += `<line x1="0" x2="${W}" y1="${yy}" y2="${yy}" stroke="${LINHA}"/>`; });
  valores.forEach((v, i) => {
    const cx = (i + 0.5) * W / labels.length, on = destaque.includes(i);
    s += `<rect x="${cx - bw / 2}" y="${y(v)}" width="${bw}" height="${H - pb - y(v)}" rx="5" fill="${on ? AZ : SEL}"/>`;
    s += `<text x="${cx}" y="${y(v) - 7}" text-anchor="middle" font-size="13" font-weight="600" fill="${on ? "#111" : G2}">${fmt(v, decimais)}${sufixo}</text>`;
    s += `<text x="${cx}" y="${H - 9}" text-anchor="middle" font-size="13" fill="${G2}">${labels[i]}</text>`;
  });
  if (linhaMeta) {
    const pts = linhaMeta.map((v, i) => `${(i + 0.5) * W / labels.length},${y(v)}`).join(" ");
    s += `<polyline points="${pts}" fill="none" stroke="${VERM}" stroke-width="2.5" stroke-dasharray="7 5"/>`;
  }
  if (meta) {
    s += `<line x1="0" x2="${W}" y1="${y(meta)}" y2="${y(meta)}" stroke="${VERM}" stroke-width="2.5" stroke-dasharray="7 5"/>`;
    s += `<rect x="0" y="${y(meta) - 28}" width="${metaLbl ? metaLbl.length * 8 + 20 : 90}" height="21" rx="10" fill="#fff"/><text x="8" y="${y(meta) - 13}" font-size="13" font-weight="700" fill="${VERM}">${metaLbl || "meta"}</text>`;
  }
  el.innerHTML = s + "</svg>";
}

function barrasH(el, { itens, altura = 42, destaque = 0, cor, sufixo = "", max, referencia, decimais = 1, lw = 140 }) {
  const W = el.clientWidth, vw = 80, m = max || Math.max(...itens.map((i) => i[1]));
  let s = `<svg width="${W}" height="${itens.length * altura}">`;
  itens.forEach(([n, v], i) => {
    const y = i * altura, bw = (W - lw - vw) * Math.min(v / m, 1);
    const c = cor ? cor(v, i) : (i === destaque ? AZ : SEL);
    s += `<text x="0" y="${y + altura / 2 + 5}" font-size="14" fill="#3F3F3F">${n}</text>`;
    s += `<rect x="${lw}" y="${y + 8}" width="${bw}" height="${altura - 16}" rx="5" fill="${c}"/>`;
    s += `<text x="${lw + bw + 8}" y="${y + altura / 2 + 5}" font-size="14" font-weight="700">${fmt(v, decimais)}${sufixo}</text>`;
  });
  if (referencia) {
    const x = lw + (W - lw - vw) * (referencia.v / m);
    s += `<line x1="${x}" x2="${x}" y1="0" y2="${itens.length * altura}" stroke="#111" stroke-width="1.5" stroke-dasharray="4 4"/>`;
  }
  el.innerHTML = s + "</svg>";
}

function composicao(el, partes, total) {
  let s = `<div style="display:flex;height:64px;border-radius:12px;overflow:hidden">`;
  partes.forEach(([n, v, bg, fg]) => {
    s += `<div style="width:${(v / total) * 100}%;background:${bg};color:${fg};padding:10px 16px;display:flex;flex-direction:column;justify-content:center;min-width:0">`;
    // Segmentos estreitos ficam só com a cor; os valores aparecem na tabela abaixo da barra
    if (v / total >= 0.2) s += `<b style="font-size:18px;white-space:nowrap">R$ ${v >= 1 ? fmt(v, 2) + " Mi" : Math.round(v * 1000) + " mil"}</b><span style="font-size:13px;white-space:nowrap">${n}</span>`;
    s += `</div>`;
  });
  el.innerHTML = s + "</div>";
}
