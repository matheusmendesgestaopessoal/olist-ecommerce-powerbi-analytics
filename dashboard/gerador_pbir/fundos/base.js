// Ícones (mesmos do protótipo) e medição das vagas dos visuais.
const ICONES = {
  receita: '<rect x="2" y="6" width="20" height="12" rx="2"/><circle cx="12" cy="12" r="2"/>',
  lucro: '<polyline points="22 7 13.5 15.5 8.5 10.5 2 17"/><polyline points="16 7 22 7 22 13"/>',
  pedidos: '<path d="M6 2 3 6v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2V6l-3-4Z"/><path d="M3 6h18"/><path d="M16 10a4 4 0 0 1-8 0"/>',
  cancelamento: '<circle cx="12" cy="12" r="10"/><path d="m15 9-6 6"/><path d="m9 9 6 6"/>',
  meta: '<circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="6"/><circle cx="12" cy="12" r="2"/>',
  ticket: '<path d="M4 2v20l2-1 2 1 2-1 2 1 2-1 2 1 2-1 2 1V2l-2 1-2-1-2 1-2-1-2 1-2-1-2 1Z"/><path d="M16 8h-6a2 2 0 1 0 0 4h4a2 2 0 1 1 0 4H8"/>',
  estoque: '<rect x="3" y="3" width="8" height="8" rx="1"/><rect x="13" y="3" width="8" height="8" rx="1"/><rect x="8" y="13" width="8" height="8" rx="1"/>',
  voltar: '<path d="M19 12H5M11 18l-6-6 6-6"/>',
  seta: '<path d="M5 12h14M13 6l6 6-6 6"/>',
};
document.querySelectorAll("[data-i]").forEach((e) => {
  const t = e.dataset.t || 18;
  e.innerHTML = `<svg width="${t}" height="${t}" viewBox="0 0 24 24" fill="none" stroke="${e.dataset.c || "#1A6BF5"}" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">${ICONES[e.dataset.i]}</svg>`;
});
if (location.search.includes("debug")) document.body.classList.add("debug");

// Posição de cada vaga, lida pelo gerador (chrome --dump-dom).
function medir() {
  const v = {};
  document.querySelectorAll("[data-v]").forEach((e) => {
    const b = e.getBoundingClientRect();
    v[e.dataset.v] = [Math.round(b.left), Math.round(b.top + scrollY), Math.round(b.width), Math.round(b.height)];
  });
  const pre = document.createElement("pre");
  pre.id = "posicoes";
  pre.style.display = "none";
  pre.textContent = JSON.stringify({ altura: document.documentElement.scrollHeight, vagas: v });
  document.body.appendChild(pre);
}
