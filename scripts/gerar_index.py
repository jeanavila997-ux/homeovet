#!/usr/bin/env python3
"""
🌐 Gerador da interface web standalone do HomeoVet
==================================================

Lê `data/tutor_homeopatia_vet.json` e injeta a base diretamente no
template HTML embutido, produzindo `index.html` — um arquivo ÚNICO que
funciona aberto no navegador (sem servidor, sem backend, sem CDN).

Recursos da interface gerada:
  - 4 abas: Medicamentos, Evidências Científicas, Regulamentação, Glossário
  - Busca com normalização de acentos + filtro por categoria
  - Modal com ficha técnica completa
  - Painel "Tutor IA local" (OPCIONAL): conversa com o Ollama local
    (http://localhost:11434) usando RAG sobre a própria base — com filtro
    de segurança por regras no navegador. Sem Ollama, o resto segue 100%
    funcional offline.

Uso:
    py scripts/gerar_index.py

O `index.html` já vem commitado no repositório; reexecute este script
sempre que alterar a base JSON.

⚠️ USO ESTRITAMENTE EDUCACIONAL — não diagnostica, não prescreve, não
recomenda doses. Não substitui médico-veterinário.
"""

import json
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DADOS = os.path.join(BASE_DIR, "data", "tutor_homeopatia_vet.json")
SAIDA = os.path.join(BASE_DIR, "index.html")

# ============================================================
# TEMPLATE HTML (standalone — dados injetados em __BASE_JSON__)
# ============================================================
TEMPLATE = r"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>🐾 HomeoVet — Base Educacional de Homeopatia Veterinária</title>
<style>
  :root{
    --bg:#0f1420; --panel:#171e2e; --panel2:#1d2740; --line:#2a3654;
    --txt:#e8edf7; --muted:#93a1bd; --accent:#4cc2ff; --accent2:#7ee0a3;
    --warn:#ffd166; --danger:#ff7b72; --violet:#c792ea;
  }
  *{box-sizing:border-box}
  body{margin:0;background:var(--bg);color:var(--txt);
       font-family:"Segoe UI",system-ui,-apple-system,sans-serif;line-height:1.55}
  header{padding:22px 18px 10px;text-align:center;
         background:linear-gradient(160deg,#141b2b 0%,#0f1420 100%);
         border-bottom:1px solid var(--line)}
  header h1{margin:0;font-size:1.6rem;letter-spacing:.5px}
  header h1 span{color:var(--accent)}
  header p{margin:6px 0 0;color:var(--muted);font-size:.9rem}
  .badge-edu{display:inline-block;margin-top:10px;padding:4px 12px;border-radius:999px;
             border:1px solid var(--warn);color:var(--warn);font-size:.78rem;font-weight:600}
  .wrap{max-width:1080px;margin:0 auto;padding:16px}
  /* Barra de busca */
  .toolbar{display:flex;gap:10px;flex-wrap:wrap;margin:14px 0 6px}
  .toolbar input,.toolbar select,.toolbar button{
    background:var(--panel2);color:var(--txt);border:1px solid var(--line);
    border-radius:10px;padding:10px 14px;font-size:.95rem}
  .toolbar input{flex:1;min-width:220px}
  .toolbar button{cursor:pointer}
  .toolbar button:hover{border-color:var(--accent)}
  /* Abas */
  nav{display:flex;gap:6px;flex-wrap:wrap;margin:14px 0 0}
  nav button{background:var(--panel);border:1px solid var(--line);color:var(--muted);
    padding:10px 16px;border-radius:12px 12px 0 0;cursor:pointer;font-size:.92rem;font-weight:600}
  nav button.ativa{background:var(--panel2);color:var(--accent);border-bottom-color:var(--panel2)}
  main section{display:none;background:var(--panel2);border:1px solid var(--line);
    border-radius:0 14px 14px 14px;padding:18px}
  main section.ativa{display:block}
  /* Cards */
  .grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:14px;margin-top:8px}
  .card{background:var(--panel);border:1px solid var(--line);border-radius:14px;
    padding:14px 16px;cursor:pointer;transition:border-color .15s,transform .15s}
  .card:hover{border-color:var(--accent);transform:translateY(-2px)}
  .card h3{margin:0 0 2px;font-size:1.05rem;color:var(--accent)}
  .card .pop{color:var(--muted);font-size:.85rem}
  .card .cat{display:inline-block;margin:8px 0;padding:2px 10px;border-radius:999px;
    background:#22304e;color:var(--violet);font-size:.75rem;font-weight:600}
  .card p{margin:6px 0 0;color:var(--muted);font-size:.86rem}
  .tag-evid{display:inline-block;margin-top:8px;color:var(--warn);font-size:.75rem;
    border:1px dashed var(--warn);border-radius:8px;padding:2px 8px}
  /* Listas (evidências, regulação, glossário) */
  .item{border-left:3px solid var(--accent);padding:10px 14px;margin:12px 0;
    background:var(--panel);border-radius:0 10px 10px 0}
  .item h3{margin:0;color:var(--accent);font-size:1rem}
  .item .meta{color:var(--violet);font-size:.8rem;margin-top:2px}
  .item p{margin:6px 0 0;color:var(--txt);font-size:.9rem}
  .item small{color:var(--muted)}
  dl.gloss dt{color:var(--accent);font-weight:700;margin-top:14px}
  dl.gloss dd{margin:4px 0 0;color:var(--txt)}
  /* Painel tutor IA */
  details.tutor{background:var(--panel);border:1px solid var(--line);border-radius:14px;
    padding:12px 16px;margin:14px 0}
  details.tutor summary{cursor:pointer;font-weight:700;color:var(--violet)}
  .ia-linha{display:flex;align-items:center;gap:10px;margin:10px 0;flex-wrap:wrap}
  .ia-linha label{color:var(--muted);font-size:.88rem}
  textarea#pergunta{width:100%;min-height:70px;background:var(--panel2);color:var(--txt);
    border:1px solid var(--line);border-radius:10px;padding:10px;font:inherit;resize:vertical}
  .resposta{white-space:pre-wrap;background:#101828;border:1px solid var(--line);
    border-radius:10px;padding:14px;margin-top:10px;font-size:.92rem;display:none}
  .resposta.ok{display:block}
  .resposta.erro{display:block;border-color:var(--danger);color:var(--danger)}
  .aviso-bloqueio{border-color:var(--warn);color:var(--warn)}
  /* Modal */
  .overlay{position:fixed;inset:0;background:rgba(5,8,15,.75);display:none;
    align-items:flex-start;justify-content:center;padding:5vh 16px;z-index:50;overflow:auto}
  .overlay.aberto{display:flex}
  .modal{background:var(--panel);border:1px solid var(--line);border-radius:16px;
    max-width:720px;width:100%;padding:22px}
  .modal h2{margin:0;color:var(--accent)}
  .modal .pop{color:var(--muted)}
  .modal .fechar{float:right;background:none;border:1px solid var(--line);color:var(--muted);
    border-radius:8px;padding:4px 12px;cursor:pointer}
  .modal .fechar:hover{color:var(--danger);border-color:var(--danger)}
  .modal dl{margin:14px 0 0}
  .modal dt{color:var(--violet);font-weight:700;margin-top:12px;font-size:.86rem}
  .modal dd{margin:2px 0 0;color:var(--txt);font-size:.93rem}
  .rodape-modal{margin-top:16px;border-top:1px dashed var(--warn);padding-top:10px;
    color:var(--warn);font-size:.82rem}
  footer{text-align:center;color:var(--muted);font-size:.8rem;padding:26px 16px 34px;
    border-top:1px solid var(--line);margin-top:22px}
  .vazio{color:var(--muted);text-align:center;padding:22px}
</style>
</head>
<body>

<header>
  <h1>🐾 Homeo<span>Vet</span></h1>
  <p>Base educacional de homeopatia veterinária — busca, evidências e regulamentação</p>
  <span class="badge-edu">⚠️ USO ESTRITAMENTE EDUCACIONAL — NÃO diagnostica, NÃO prescreve, NÃO substitui o médico-veterinário</span>
</header>

<div class="wrap">

  <!-- Painel: Tutor IA local (opcional) -->
  <details class="tutor">
    <summary>🤖 Pergunte ao Tutor (IA local via Ollama — opcional)</summary>
    <div class="ia-linha">
      <input type="checkbox" id="ia-toggle">
      <label for="ia-toggle">Ativar modo IA local (requer Ollama rodando em <code>http://localhost:11434</code>)</label>
    </div>
    <textarea id="pergunta" placeholder="Ex.: O que é a Lei do Semelhante? / O que diz a regulamentação do MAPA? (perguntas EDUCACIONAIS — diagnóstico e dose são bloqueados)"></textarea>
    <div class="ia-linha">
      <button id="btn-perguntar">Perguntar</button>
      <small style="color:var(--muted)">Respostas ancoradas apenas na base abaixo (RAG). Sem Ollama, use a CLI: <code>py homeovet_cli.py perguntar "..."</code></small>
    </div>
    <div id="resposta" class="resposta"></div>
  </details>

  <!-- Busca global -->
  <div class="toolbar">
    <input id="busca" type="search" placeholder="🔎 Buscar (ignora acentos): remédio, sintoma, termo, estudo...">
    <select id="filtro-categoria"><option value="">Todas as categorias</option></select>
  </div>

  <!-- Abas -->
  <nav>
    <button data-aba="meds" class="ativa">💊 Medicamentos</button>
    <button data-aba="evid">🔬 Evidências Científicas</button>
    <button data-aba="reg">⚖️ Regulamentação</button>
    <button data-aba="gloss">📖 Glossário</button>
  </nav>

  <main>
    <section id="aba-meds" class="ativa"><div id="lista-meds" class="grid"></div></section>
    <section id="aba-evid"><div id="lista-evid"></div></section>
    <section id="aba-reg"><div id="lista-reg"></div></section>
    <section id="aba-gloss"><dl class="gloss" id="lista-gloss"></dl></section>
  </main>
</div>

<!-- Modal de ficha -->
<div class="overlay" id="overlay">
  <div class="modal" role="dialog" aria-modal="true">
    <button class="fechar" id="fechar-modal">✕ Fechar</button>
    <h2 id="m-nome"></h2>
    <div class="pop" id="m-pop"></div>
    <dl id="m-campos"></dl>
    <div class="rodape-modal">⚠️ Ficha EDUCACIONAL. Declarações de fabricante ≠ evidência científica. Consulte um médico-veterinário para qualquer decisão clínica.</div>
  </div>
</div>

<footer>
  <div id="versao-base"></div>
  <div style="margin-top:6px">HomeoVet — agentes educacionais de homeopatia (Python puro + Ollama opcional).
  A eficácia da homeopatia não é sustentada por evidências científicas robustas (Bergh et al., 2021).</div>
</footer>

<script>
"use strict";
// __BASE_JSON__ é injetado por scripts/gerar_index.py (fonte: data/tutor_homeopatia_vet.json)
const BASE = __BASE_JSON__;

// ---------- utilidades ----------
const norm = s => (s || "").normalize("NFD").replace(/[\u0300-\u036f]/g, "").toLowerCase();
const $ = id => document.getElementById(id);
const esc = s => String(s == null ? "" : s)
  .replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;");

// ---------- estado ----------
let abaAtiva = "meds";

// ---------- abas ----------
document.querySelectorAll("nav button").forEach(btn => {
  btn.addEventListener("click", () => {
    abaAtiva = btn.dataset.aba;
    document.querySelectorAll("nav button").forEach(b => b.classList.toggle("ativa", b === btn));
    document.querySelectorAll("main section").forEach(s => s.classList.toggle("ativa", s.id === "aba-" + abaAtiva));
    render();
  });
});

// ---------- dados derivados ----------
const categorias = [...new Set(BASE.medicamentos.map(m => m.categoria))].sort();
$("filtro-categoria").innerHTML += categorias
  .map(c => `<option value="${esc(c)}">${esc(c)}</option>`).join("");

const versao = BASE.metadata || {};
$("versao-base").textContent =
  `Base educacional v${versao.versao || "?"} — atualizada em ${versao.data_atualizacao || "?"} · ${BASE.medicamentos.length} medicamentos · ${BASE.evidencias_cientificas.length} evidências · ${Object.keys(BASE.glossario || {}).length} termos`;

// ---------- renderização ----------
function render() {
  const q = norm($("busca").value.trim());
  const cat = $("filtro-categoria").value;

  if (abaAtiva === "meds") {
    const meds = BASE.medicamentos.filter(m => {
      const okCat = !cat || m.categoria === cat;
      const alvo = norm([m.nome, m.nome_popular, m.categoria,
        (m.sintomas_homeopaticos || []).join(" "),
        m.indicacoes_fabricante, m.uso_veterinario].join(" "));
      return okCat && (!q || alvo.includes(q));
    });
    $("lista-meds").innerHTML = meds.length ? meds.map(cardMed).join("")
      : `<div class="vazio">Nenhum medicamento encontrado para os filtros atuais.</div>`;
  }

  if (abaAtiva === "evid") {
    const evids = BASE.evidencias_cientificas.filter(e => {
      const alvo = norm([e.estudo, e.conclusao, e.nivel_evidencia, e.relevancia].join(" "));
      return !q || alvo.includes(q);
    });
    $("lista-evid").innerHTML = evids.length ? evids.map(e => `
      <div class="item">
        <h3>${esc(e.estudo)}</h3>
        <div class="meta">${esc(e.nivel_evidencia)}</div>
        <p>${esc(e.conclusao)}</p>
        <p><small>Relevância: ${esc(e.relevancia)}</small></p>
      </div>`).join("") : `<div class="vazio">Nenhuma evidência encontrada.</div>`;
  }

  if (abaAtiva === "reg") {
    const regs = BASE.regulamentacao_brasil.filter(r => {
      const alvo = norm([r.aspecto, r.descricao, r.fonte, r.status].join(" "));
      return !q || alvo.includes(q);
    });
    $("lista-reg").innerHTML = regs.length ? regs.map(r => `
      <div class="item">
        <h3>${esc(r.aspecto)}</h3>
        <div class="meta">${esc(r.fonte)} · Status: ${esc(r.status)}</div>
        <p>${esc(r.descricao)}</p>
      </div>`).join("") : `<div class="vazio">Nada encontrado na regulamentação.</div>`;
  }

  if (abaAtiva === "gloss") {
    const itens = Object.entries(BASE.glossario || {}).filter(([t, d]) => {
      const alvo = norm(t + " " + d);
      return !q || alvo.includes(q);
    });
    $("lista-gloss").innerHTML = itens.length ? itens.map(([t, d]) =>
      `<dt>${esc(t)}</dt><dd>${esc(d)}</dd>`).join("")
      : `<div class="vazio">Termo não encontrado no glossário.</div>`;
  }
}

function cardMed(m) {
  return `<div class="card" data-nome="${esc(m.nome)}">
    <h3>${esc(m.nome)}</h3>
    <div class="pop">${esc(m.nome_popular || "")}</div>
    <span class="cat">${esc(m.categoria)}</span>
    <p>${esc((m.indicacoes_fabricante || "").slice(0, 140))}${(m.indicacoes_fabricante || "").length > 140 ? "…" : ""}</p>
    <span class="tag-evid">🔬 ${esc((m.evidencia_cientifica || "").slice(0, 60))}…</span>
  </div>`;
}

// ---------- modal de ficha completa ----------
$("lista-meds").addEventListener("click", ev => {
  const card = ev.target.closest(".card");
  if (!card) return;
  const m = BASE.medicamentos.find(x => x.nome === card.dataset.nome);
  if (!m) return;
  $("m-nome").textContent = m.nome;
  $("m-pop").textContent = m.nome_popular ? `“${m.nome_popular}” · ${m.categoria}` : m.categoria;
  const campos = [
    ["Origem", m.origem], ["Composição declarada", m.principio_ativo_declarado],
    ["Potências comuns", (m.potencias_comuns || []).join(", ")],
    ["Apresentações", m.apresentacoes], ["Conservação", m.conservacao],
    ["Indicações (fabricante)", m.indicacoes_fabricante],
    ["Registro MAPA", m.indicacoes_registro_mapa],
    ["Sintomas homeopáticos", (m.sintomas_homeopaticos || []).join("; ")],
    ["Contraindicações", m.contraindicacoes], ["Precauções", m.precaucoes],
    ["Uso veterinário", m.uso_veterinario],
    ["Tipo de informação", m.tipo_informacao],
    ["Evidência científica", m.evidencia_cientifica], ["Notas", m.notas],
  ];
  $("m-campos").innerHTML = campos.filter(([_, v]) => v)
    .map(([k, v]) => `<dt>${esc(k)}</dt><dd>${esc(v)}</dd>`).join("");
  $("overlay").classList.add("aberto");
});
$("fechar-modal").addEventListener("click", () => $("overlay").classList.remove("aberto"));
$("overlay").addEventListener("click", ev => { if (ev.target === $("overlay")) $("overlay").classList.remove("aberto"); });
document.addEventListener("keydown", ev => { if (ev.key === "Escape") $("overlay").classList.remove("aberto"); });

// ---------- filtros ----------
$("busca").addEventListener("input", render);
$("filtro-categoria").addEventListener("change", render);

// ---------- Tutor IA local (opcional) ----------
// Espelho das listas de tutor_homeopatia_vet.py (fonte de verdade em Python).
const PALAVRAS_BLOQUEIO = [
  "meu cão tem", "meu gato tem", "meu animal tem", "está doente",
  "diagnostique", "diagnóstico", "qual remédio devo dar", "qual dose",
  "quanto devo dar", "posso dar", "devo usar", "tratamento para",
  "cura para", "melhor remédio para", "indique um remédio",
  "receita para", "prescreva", "prescrição", "dosagem para",
  "combine", "misture", "substitua", "em vez de", "troque"
];
const SINTOMAS_URGENTES = [
  "dificuldade para respirar", "respiração ofegante", "cianose",
  "desmaio", "convulsão", "sangramento", "hemorragia",
  "vômito persistente", "diarreia com sangue", "não urina",
  "abdome distendido", "traumatismo", "fratura", "envenenamento",
  "intoxicação", "paralisia", "não se move", "inconsciente",
  // Radicais/flexões: cobrem formas sem acento e conjugadas (a comparação usa norm())
  "convuls", "vomitando sangue", "vômito com sangue",
  "vomitando muito", "não consegue respirar", "não consegue andar",
  "não consegue levantar", "envenenado", "intoxicado"
];

const SYSTEM_RAG =
`Você é o Tutor HomeoVet, um agente EDUCACIONAL de homeopatia veterinária.

REGRAS INVIOLÁVEIS:
1. NUNCA diagnostique, prescreva, recomende doses ou tratamentos para casos individuais.
2. Responda EXCLUSIVAMENTE com o CONTEXTO fornecido abaixo (base educacional do projeto).
3. Se a informação não estiver no contexto, diga: "Informação não disponível na base educacional."
4. NÃO invente fontes, estudos ou números.
5. Lembre sempre que a eficácia da homeopatia não é sustentada por evidências científicas robustas (Bergh et al., 2021).
6. Se houver indício de emergência ou caso clínico real, oriente procurar um MÉDICO-VETERINÁRIO com urgência.

FORMATO OBRIGATÓRIO DA RESPOSTA (em português do Brasil):
📌 RESPOSTA OBJETIVA — 2 a 4 linhas diretas.
📚 EXPLICAÇÃO DIDÁTICA — desenvolvimento com o contexto disponível.
📖 FONTE — diga se é declaração de fabricante, evidência científica ou conhecimento teórico.
🔬 EVIDÊNCIAS E LIMITAÇÕES — o que a ciência diz (ou a falta de evidência).
⚠️ AVISO — lembrete educacional final (sem diagnóstico/prescrição; consulte veterinário).`;

function documentos() {
  const docs = [];
  BASE.medicamentos.forEach(m => docs.push(
    `MEDICAMENTO ${m.nome} (${m.nome_popular}) — categoria ${m.categoria}. ` +
    `Origem: ${m.origem}. Composição declarada: ${m.principio_ativo_declarado}. ` +
    `Indicações do fabricante: ${m.indicacoes_fabricante}. ` +
    `Sintomas homeopáticos: ${(m.sintomas_homeopaticos || []).join("; ")}. ` +
    `Contraindicações: ${m.contraindicacoes}. Uso veterinário: ${m.uso_veterinario}. ` +
    `Tipo de informação: ${m.tipo_informacao}. Evidência científica: ${m.evidencia_cientifica}.`));
  (BASE.conceitos_fundamentais || []).forEach(c => docs.push(
    `CONCEITO ${c.termo}: ${c.definicao} Tipo: ${c.tipo_informacao}. ` +
    `Evidência: ${c.evidencia_cientifica}. Notas: ${c.notas}.`));
  BASE.evidencias_cientificas.forEach(e => docs.push(
    `EVIDÊNCIA CIENTÍFICA — ${e.estudo}: ${e.conclusao} Nível: ${e.nivel_evidencia}.`));
  BASE.regulamentacao_brasil.forEach(r => docs.push(
    `REGULAMENTAÇÃO — ${r.aspecto}: ${r.descricao} Status: ${r.status}.`));
  Object.entries(BASE.glossario || {}).forEach(([t, d]) => docs.push(`GLOSSÁRIO — ${t}: ${d}`));
  return docs;
}

function contextoPara(pergunta, n = 6) {
  // RAG offline no navegador: ranqueia documentos pela pergunta (tokens normalizados)
  const termos = norm(pergunta).split(/\s+/).filter(t => t.length > 2);
  const pontuado = documentos().map(doc => {
    const alvo = norm(doc);
    let pts = 0;
    termos.forEach(t => { if (alvo.includes(t)) pts += 1; });
    return [pts, doc];
  });
  pontuado.sort((a, b) => b[0] - a[0]);
  return pontuado.slice(0, n).map(p => p[1]);
}

function mostrarResposta(texto, classe) {
  const el = $("resposta");
  el.className = "resposta " + (classe || "ok");
  el.textContent = texto;
}

$("btn-perguntar").addEventListener("click", async () => {
  const pergunta = $("pergunta").value.trim();
  if (!pergunta) { mostrarResposta("Digite uma pergunta educacional acima.", "erro"); return; }

  // 1) Emergência — sempre antes de tudo
  const urg = SINTOMAS_URGENTES.find(s => norm(pergunta).includes(norm(s)));
  if (urg) {
    mostrarResposta(
`🚨 ATENÇÃO — POSSÍVEL EMERGÊNCIA
Detectei menção a: "${urg}"
Procure um MÉDICO-VETERINÁRIO URGENTEMENTE ou uma clínica 24h.
A homeopatia NÃO substitui atendimento de emergência.`, "resposta aviso-bloqueio");
    return;
  }

  // 2) Tentativa de diagnóstico/prescrição — bloqueio por regras (nunca LLM)
  const bloq = PALAVRAS_BLOQUEIO.find(p => norm(pergunta).includes(norm(p)));
  if (bloq) {
    mostrarResposta(
`⚠️ AVISO DE SEGURANÇA
Sou um tutor EDUCACIONAL sobre homeopatia veterinária.
NÃO posso: diagnosticar, prescrever, recomendar doses ou substituir o veterinário.
Posso ajudar com: conceitos teóricos, terminologia, legislação e evidências científicas.
👉 Consulte um MÉDICO-VETERINÁRIO para qualquer caso individual.`, "resposta aviso-bloqueio");
    return;
  }

  // 3) Modo IA local
  if (!$("ia-toggle").checked) {
    mostrarResposta("Ative o checkbox “modo IA local” para conversar com o tutor via Ollama — ou use a CLI: py homeovet_cli.py perguntar \"sua pergunta\"", "erro");
    return;
  }

  const contexto = contextoPara(pergunta);
  const user = `PERGUNTA: ${pergunta}\n\nCONTEXTO DA BASE EDUCACIONAL HomeoVet (use SOMENTE isto):\n` +
               contexto.join("\n---\n");
  mostrarResposta("🧠 Consultando o Ollama local…", "ok");

  const controlador = new AbortController();
  const limite = setTimeout(() => controlador.abort(), 120000);
  const modelos = ["homeovet-tutor", "nemotron-3-nano:4b"];
  let resposta = null, erroFinal = null;

  for (const modelo of modelos) {
    try {
      const r = await fetch("http://localhost:11434/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        signal: controlador.signal,
        body: JSON.stringify({
          model: modelo,
          messages: [
            { role: "system", content: SYSTEM_RAG },
            { role: "user", content: user }
          ],
          stream: false,
          options: { temperature: 0.2, num_ctx: 4096 }
        })
      });
      if (!r.ok) { erroFinal = `HTTP ${r.status}`; continue; }
      const dados = await r.json();
      resposta = (dados.message || {}).content || "";
      if (resposta.trim()) {
        clearTimeout(limite);
        mostrarResposta(`🎓 Tutor HomeoVet (IA local: ${modelo})\n\n${resposta.trim()}\n\n⚠️ Resposta EDUCACIONAL, ancorada na base do projeto. Confirme sempre com um médico-veterinário.`, "ok");
        return;
      }
    } catch (e) {
      erroFinal = e.name === "AbortError" ? "tempo esgotado (120s)" : e.message;
    }
  }
  clearTimeout(limite);
  mostrarResposta(
`❌ Não consegui falar com o Ollama local (${erroFinal || "indisponível"}).

Checklist:
1. Ollama instalado e rodando: ollama serve
2. Modelo do tutor criado: ollama create homeovet-tutor -f Modelfile.homeovet
   (sem ele, o fallback nemotron-3-nano:4b é usado — ollama pull nemotron-3-nano:4b)
3. Se o navegador bloquear (CORS em arquivo local), inicie o Ollama permitindo a origem:
   OLLAMA_ORIGINS=* ollama serve

Enquanto isso, a interface continua 100% funcional offline (abas, busca, fichas).`, "erro");
});

// ---------- inicialização ----------
render();
</script>
</body>
</html>
"""


def main():
    with open(DADOS, "r", encoding="utf-8") as f:
        base = json.load(f)

    # Injeção segura: escapa "</" para não fechar a tag <script> acidentalmente
    base_json = json.dumps(base, ensure_ascii=False, separators=(",", ":"))
    base_json = base_json.replace("</", "<\\/")

    html = TEMPLATE.replace("__BASE_JSON__", base_json)

    with open(SAIDA, "w", encoding="utf-8") as f:
        f.write(html)

    resumo = {
        "medicamentos": len(base.get("medicamentos", [])),
        "evidencias": len(base.get("evidencias_cientificas", [])),
        "regulamentacao": len(base.get("regulamentacao_brasil", [])),
        "glossario": len(base.get("glossario", {})),
    }
    print(f"✅ index.html gerado ({len(html) / 1024:.1f} KB): {SAIDA}")
    print(f"   {resumo['medicamentos']} medicamentos · {resumo['evidencias']} evidências · "
          f"{resumo['regulamentacao']} normas · {resumo['glossario']} termos de glossário")


if __name__ == "__main__":
    main()