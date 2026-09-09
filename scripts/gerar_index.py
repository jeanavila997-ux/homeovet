#!/usr/bin/env python3
"""gerar_index.py — gera o index.html do HomeoVet (dashboard educacional).

Design: identidade "farmacopeia" — papel-sálvia, tinta verde-profunda, acento
âmbar-frasco (os frascos de homeopatia), serif de farmacopeia nos títulos.
Estrutura: índice lateral por SISTEMA (categorias maiores que consolidam as
109 categorias da base AMHB em 12 grupos) + abas de estudo.

Fonte única de verdade: data/tutor_homeopatia_vet.json (v3.1.0, 125 meds).
Comportamentos preservados do app anterior: busca sem acentos, ficha completa
em modal, RAG offline no navegador, tutor IA local (Ollama) com filtro de
segurança por regras ANTES de qualquer chamada de LLM.

Uso: py scripts/gerar_index.py
"""
import json
import os
import unicodedata

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
JSON_PATH = os.path.join(BASE_DIR, "data", "tutor_homeopatia_vet.json")
SAIDA = os.path.join(BASE_DIR, "index.html")


# ---------------------------------------------------------------------------
# Categorias maiores (grupos) — consolidam as categorias combinatórias da base
# (ex.: "Cardíaco / Nervoso", "Pele / Supurações") em 12 sistemas navegáveis.
# Ordem de precedência: a primeira palavra-chave que casa na categoria
# (normalizada, sem acentos) define o grupo. "Cascos e Unhas" primeiro
# (pedido do usuário). Default: Geral e Constitucional.
# ---------------------------------------------------------------------------
GRUPOS = [
    ("Cascos e Unhas", ("casc", "unha")),
    ("Pele e Mucosas", ("pele", "mucos", "dermat", "verruc", "candid",
                        "couro cabel", "supurac", "eczem", "fistul")),
    ("Respiratório", ("respir", "toss", "bronquit", "gripe", "laring")),
    ("Digestivo e Metabolismo", ("digest", "hepat", "reto", "colic", "enjoo",
                                 "nausea", "diarre", "vomit", "gastr")),
    ("Feminino e Reprodução", ("feminin", "utero", "parto", "mamari",
                               "gesta", "leite", "cio")),
    ("Urinário", ("urin", "queimadur", "renal", "bexiga")),
    ("Cabeça e Sentidos", ("olho", "nariz", "otorrin", "dental", "cefale",
                           "enxaquec", "seios da face", "visao", "ouvid", "ocul")),
    ("Locomotor e Traumas", ("traumatolog", "articul", "osse", "tendon",
                             "tendin", "contratur", "reumat", "musculoesquel",
                             "picada", "fratur", "entorse")),
    ("Febre e Infecções", ("febre", "infecci", "septic", "imunid", "colaps",
                           "parasit", "inflamat", "edema", "gangli")),
    ("Nervoso e Comportamento", ("nervos", "mental", "comport", "emocion",
                                 "ansied", "deliri", "agitac", "convuls",
                                 "epilep", "espasm", "tremor", "paralis",
                                 "insoni", "panic", "traumatis", "exaust",
                                 "neuralg")),
    ("Coração e Circulação", ("cardiac", "circulat", "venos", "vascular",
                              "hemorrag", "tumor", "variz", "hemorroid",
                              "anemia")),
    ("Geral e Constitucional", ()),  # default
]


def sem_acentos(s):
    return "".join(
        c for c in unicodedata.normalize("NFD", s)
        if unicodedata.category(c) != "Mn"
    ).lower()


def grupo_de(categoria):
    cat = sem_acentos(categoria or "")
    for nome, palavras in GRUPOS:
        if any(p in cat for p in palavras):
            return nome
    return GRUPOS[-1][0]


def principal():
    base = json.load(open(JSON_PATH, encoding="utf-8"))

    # grupo pré-computado por medicamento (apresentação, não muda os dados)
    for m in base["medicamentos"]:
        m["grupo"] = grupo_de(m["categoria"])
    base["medicamentos"].sort(key=lambda m: m["nome"].lower())

    # contagens por grupo (ordem canônica do índice)
    contagens = {g[0]: 0 for g in GRUPOS}
    for m in base["medicamentos"]:
        contagens[m["grupo"]] += 1
    grupos_json = [
        {"nome": nome, "n": contagens[nome]}
        for nome, _ in GRUPOS
        if contagens[nome] > 0
    ]

    meta = base.get("metadata", {})
    placeholders = {
        "__BASE_JSON__": json.dumps(base, ensure_ascii=False),
        "__GRUPOS_JSON__": json.dumps(grupos_json, ensure_ascii=False),
        "__VERSAO__": meta.get("versao", "?"),
        "__DATA__": meta.get("data_atualizacao", "?"),
        "__N_MEDS__": str(len(base["medicamentos"])),
        "__N_EV__": str(len(base.get("evidencias_cientificas", []))),
        "__N_REG__": str(len(base.get("regulamentacao_brasil", []))),
        "__N_GLOS__": str(len(base.get("glossario", {}))),
    }

    html = TEMPLATE
    for chave, valor in placeholders.items():
        html = html.replace(chave, valor)

    with open(SAIDA, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"index.html gerado — v{meta.get('versao')} · "
          f"{len(base['medicamentos'])} medicamentos em {len(grupos_json)} grupos")
    for g in grupos_json:
        print(f"  {g['n']:3d}  {g['nome']}")


# ---------------------------------------------------------------------------
# Template — identidade "farmacopeia": papel-sálvia, tinta verde, âmbar-frasco.
# ---------------------------------------------------------------------------
TEMPLATE = r"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>HomeoVet — farmacopeia didática de homeopatia veterinária</title>
<style>
:root {
  --papel: #EDF1E6;        /* fundo papel-sálvia */
  --folha: #FBFCF8;        /* superfícies (fichas, painéis) */
  --tinta: #1C2A24;        /* texto principal, verde-tinta profundo */
  --tinta-2: #55665C;      /* texto secundário */
  --ambar: #8A5A24;        /* acento único: frasco âmbar */
  --ambar-suave: #F0E4D2;  /* realce de linha ativa / chips ativos */
  --linha: #D8DECE;        /* hairlines */
  --alerta: #8F2F2F;       /* vermelho-veterinário, avisos */
  --raio: 6px;
  --serif: "Iowan Old Style", Palatino, "Palatino Linotype", "Book Antiqua", Georgia, serif;
  --sans: system-ui, "Segoe UI", Roboto, sans-serif;
}
* { box-sizing: border-box; }
html { scroll-behavior: smooth; }
body {
  margin: 0;
  background: var(--papel);
  color: var(--tinta);
  font-family: var(--sans);
  font-size: 15px;
  line-height: 1.55;
}
:focus-visible { outline: 2px solid var(--ambar); outline-offset: 2px; }

/* ---------- cabeçalho ---------- */
header.topo {
  display: flex;
  align-items: center;
  gap: 24px;
  flex-wrap: wrap;
  padding: 14px 28px;
  border-bottom: 1px solid var(--linha);
  background: var(--folha);
}
.marca {
  font-family: var(--serif);
  font-size: 24px;
  font-weight: 700;
  letter-spacing: .01em;
  margin: 0;
}
.marca small {
  font-family: var(--sans);
  font-size: 11px;
  font-weight: 400;
  color: var(--tinta-2);
  display: block;
  letter-spacing: .02em;
}
.busca {
  flex: 1 1 320px;
  display: flex;
  gap: 8px;
}
#busca {
  flex: 1;
  padding: 10px 14px;
  border: 1px solid var(--linha);
  border-radius: var(--raio);
  background: var(--papel);
  font: inherit;
  color: var(--tinta);
}
#busca::placeholder { color: var(--tinta-2); }
#limpar-busca {
  border: 1px solid var(--linha);
  background: var(--folha);
  border-radius: var(--raio);
  padding: 10px 16px;
  font: inherit;
  color: var(--tinta-2);
  cursor: pointer;
}
#limpar-busca:hover { color: var(--tinta); border-color: var(--tinta-2); }

/* ---------- herói ---------- */
.hero { padding: 34px 28px 26px; border-bottom: 1px solid var(--linha); }
.hero h1 {
  font-family: var(--serif);
  font-weight: 700;
  font-size: clamp(26px, 4vw, 40px);
  line-height: 1.12;
  margin: 0 0 10px;
  max-width: 30ch;
}
.hero p.sub {
  margin: 0 0 14px;
  max-width: 62ch;
  color: var(--tinta-2);
}
.dados-base {
  display: flex;
  gap: 26px;
  flex-wrap: wrap;
  font-variant-numeric: tabular-nums;
  color: var(--tinta-2);
  font-size: 13px;
}
.dados-base b { color: var(--tinta); font-weight: 600; }
.aviso-educacional {
  display: inline-block;
  margin-top: 16px;
  padding: 6px 12px;
  border: 1px solid var(--ambar);
  border-radius: var(--raio);
  background: var(--ambar-suave);
  color: var(--ambar);
  font-size: 13px;
}

/* ---------- corpo: índice lateral + conteúdo ---------- */
.corpo {
  display: grid;
  grid-template-columns: 250px minmax(0, 1fr);
  gap: 0;
  align-items: start;
}
nav.indice {
  position: sticky;
  top: 0;
  align-self: start;
  padding: 24px 18px 24px 28px;
  border-right: 1px solid var(--linha);
}
.indice h2 {
  font-family: var(--serif);
  font-size: 17px;
  font-weight: 700;
  margin: 0 0 4px;
}
.indice .nota-indice {
  font-size: 12px;
  color: var(--tinta-2);
  margin: 0 0 14px;
}
.indice button {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  gap: 10px;
  width: 100%;
  padding: 8px 10px;
  margin: 1px 0;
  border: 0;
  border-left: 3px solid transparent;
  border-radius: 0 var(--raio) var(--raio) 0;
  background: none;
  font: inherit;
  color: var(--tinta);
  cursor: pointer;
  text-align: left;
}
.indice button:hover { background: var(--folha); }
.indice button.ativo {
  background: var(--folha);
  border-left-color: var(--ambar);
  font-weight: 600;
}
.indice button .n {
  font-variant-numeric: tabular-nums;
  color: var(--tinta-2);
  font-size: 12px;
}
.indice button.ativo .n { color: var(--ambar); }

main.conteudo { padding: 24px 28px 40px; min-width: 0; }

/* ---------- abas ---------- */
.abas {
  display: flex;
  gap: 4px;
  border-bottom: 1px solid var(--linha);
  margin-bottom: 18px;
  flex-wrap: wrap;
}
.abas button {
  border: 0;
  background: none;
  font: inherit;
  color: var(--tinta-2);
  padding: 9px 12px;
  cursor: pointer;
  border-bottom: 2px solid transparent;
  margin-bottom: -1px;
}
.abas button:hover { color: var(--tinta); }
.abas button.ativa {
  color: var(--tinta);
  font-weight: 600;
  border-bottom-color: var(--ambar);
}
main section { display: none; }
main section.ativa { display: block; }

/* ---------- subcategorias (chips) ---------- */
.chips {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin: 0 0 18px;
}
.chips[hidden] { display: none; }
.chips button {
  border: 1px solid var(--linha);
  background: var(--folha);
  border-radius: var(--raio);
  padding: 4px 10px;
  font: inherit;
  font-size: 12.5px;
  color: var(--tinta-2);
  cursor: pointer;
}
.chips button:hover { border-color: var(--tinta-2); color: var(--tinta); }
.chips button.ativa {
  background: var(--ambar-suave);
  border-color: var(--ambar);
  color: var(--ambar);
}

/* ---------- fichas ---------- */
.grid-fichas {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(255px, 1fr));
  gap: 14px;
}
.ficha {
  border: 1px solid var(--linha);
  border-radius: var(--raio);
  background: var(--folha);
  padding: 16px 16px 14px;
  cursor: pointer;
  transition: border-color .15s ease;
}
.ficha:hover { border-color: var(--ambar); }
.ficha h3 {
  font-family: var(--serif);
  font-size: 19px;
  font-weight: 700;
  margin: 0 0 2px;
}
.ficha .pop { color: var(--tinta-2); font-size: 13px; margin: 0 0 8px; }
.ficha .sub {
  font-size: 12.5px;
  color: var(--ambar);
  border-top: 1px solid var(--linha);
  padding-top: 8px;
  margin: 0 0 8px;
}
.ficha p { margin: 0; font-size: 13.5px; }
.ficha .evid {
  display: block;
  margin-top: 10px;
  font-size: 12px;
  color: var(--tinta-2);
}
.vazio {
  border: 1px dashed var(--linha);
  border-radius: var(--raio);
  padding: 26px;
  color: var(--tinta-2);
  text-align: center;
}

/* ---------- listas (evidências, regulação) ---------- */
.item {
  border-left: 3px solid var(--ambar);
  background: var(--folha);
  border-radius: 0 var(--raio) var(--raio) 0;
  padding: 14px 18px;
  margin-bottom: 12px;
}
.item h3 { font-family: var(--serif); margin: 0 0 4px; font-size: 18px; }
.item .meta { font-size: 12.5px; color: var(--ambar); margin: 0 0 8px; }
.item p { margin: 0; }
.item small { color: var(--tinta-2); }

dl.glossario dt {
  font-family: var(--serif);
  font-weight: 700;
  font-size: 17px;
  margin-top: 16px;
}
dl.glossario dt:first-child { margin-top: 0; }
dl.glossario dd { margin: 2px 0 0; color: var(--tinta-2); }

/* ---------- tutor local ---------- */
.tutor { max-width: 760px; }
.tutor textarea {
  width: 100%;
  min-height: 84px;
  padding: 12px 14px;
  border: 1px solid var(--linha);
  border-radius: var(--raio);
  background: var(--folha);
  font: inherit;
  color: var(--tinta);
  resize: vertical;
}
.tutor .acoes {
  display: flex;
  align-items: center;
  gap: 14px;
  margin: 10px 0 16px;
  flex-wrap: wrap;
}
#btn-perguntar {
  border: 0;
  border-radius: var(--raio);
  background: var(--ambar);
  color: var(--folha);
  font: inherit;
  font-weight: 600;
  padding: 10px 22px;
  cursor: pointer;
}
#btn-perguntar:hover { filter: brightness(1.12); }
#btn-perguntar:disabled { opacity: .55; cursor: wait; }
.opcao-ia { display: flex; align-items: center; gap: 6px; color: var(--tinta-2); font-size: 13px; }
.resposta {
  border: 1px solid var(--linha);
  border-radius: var(--raio);
  background: var(--folha);
  padding: 16px 18px;
  white-space: pre-wrap;
  font-size: 14px;
}
.resposta.aviso-bloqueio { border-color: var(--alerta); color: var(--alerta); }
.resposta.erro { border-color: var(--tinta-2); color: var(--tinta-2); }

/* ---------- modal ---------- */
#overlay {
  display: none;
  position: fixed;
  inset: 0;
  background: rgba(28, 42, 36, .55);
  padding: 4vh 16px;
  overflow-y: auto;
  z-index: 10;
}
#overlay.aberto { display: block; }
.modal {
  background: var(--folha);
  border-radius: var(--raio);
  max-width: 720px;
  margin: 0 auto;
  padding: 28px 30px 26px;
}
.modal .fechar {
  float: right;
  border: 1px solid var(--linha);
  background: none;
  border-radius: var(--raio);
  padding: 4px 12px;
  font: inherit;
  color: var(--tinta-2);
  cursor: pointer;
}
.modal .fechar:hover { color: var(--alerta); border-color: var(--alerta); }
.modal h2 {
  font-family: var(--serif);
  font-size: 26px;
  margin: 0 0 2px;
}
.modal .sub { color: var(--ambar); font-size: 13.5px; margin: 0 0 6px; }
.modal dl { margin: 14px 0 0; border-top: 1px solid var(--linha); }
.modal dt {
  font-size: 12px;
  color: var(--tinta-2);
  margin-top: 12px;
}
.modal dd { margin: 1px 0 0; }

/* ---------- rodapé ---------- */
footer {
  border-top: 1px solid var(--linha);
  padding: 20px 28px 30px;
  color: var(--tinta-2);
  font-size: 13px;
}
footer .restricao { color: var(--alerta); }

/* ---------- responsivo ---------- */
@media (max-width: 880px) {
  .corpo { grid-template-columns: 1fr; }
  nav.indice {
    position: static;
    border-right: 0;
    border-bottom: 1px solid var(--linha);
    padding: 14px 20px;
  }
  .indice .lista-grupos {
    display: flex;
    flex-wrap: nowrap;
    overflow-x: auto;
    gap: 6px;
    padding-bottom: 6px;
  }
  .indice button {
    width: auto;
    white-space: nowrap;
    border-left: 0;
    border: 1px solid var(--linha);
    border-radius: var(--raio);
    padding: 6px 12px;
  }
  .indice button.ativa { border-color: var(--ambar); background: var(--ambar-suave); }
  main.conteudo { padding: 18px 20px 32px; }
  header.topo, .hero, footer { padding-left: 20px; padding-right: 20px; }
}
@media (prefers-reduced-motion: reduce) {
  * { transition: none !important; animation: none !important; }
  html { scroll-behavior: auto; }
}
</style>
</head>
<body>

<header class="topo">
  <p class="marca">HomeoVet
    <small>farmacopeia didática, uso educacional</small></p>
  <div class="busca">
    <input id="busca" type="search" placeholder="Buscar por sintoma, nome, origem ou sistema" aria-label="Buscar na base educacional">
    <button id="limpar-busca" type="button">Limpar</button>
  </div>
</header>

<section class="hero">
  <h1>Homeopatia veterinária, ficha por ficha.</h1>
  <p class="sub">Base de consulta e estudo com fichas completas de medicamentos
  homeopáticos, evidências científicas independentes e a regulamentação
  brasileira. Organizada por sistema do corpo — de cascos e unhas a mente e
  emoções.</p>
  <div class="dados-base">
    <span><b>__N_MEDS__</b> medicamentos</span>
    <span><b>__N_EV__</b> evidências científicas</span>
    <span><b>__N_REG__</b> normas e ofícios</span>
    <span><b>__N_GLOS__</b> termos de glossário</span>
  </div>
  <span class="aviso-educacional">Estritamente educacional — não substitui o médico-veterinário e não orienta diagnóstico, dose ou tratamento.</span>
</section>

<div class="corpo">
  <nav class="indice" aria-label="Índice por sistema">
    <h2>Índice por sistema</h2>
    <p class="nota-indice">Categorias maiores da base. Dentro de cada sistema, as categorias específicas aparecem como filtros.</p>
    <div class="lista-grupos" id="lista-grupos"></div>
  </nav>

  <main class="conteudo">
    <div class="abas" role="tablist">
      <button class="ativa" data-aba="meds" type="button">Medicamentos</button>
      <button data-aba="evid" type="button">Evidências</button>
      <button data-aba="reg" type="button">Regulamentação</button>
      <button data-aba="gloss" type="button">Glossário</button>
      <button data-aba="tutor" type="button">Tutor local</button>
    </div>

    <section id="aba-meds" class="ativa">
      <div class="chips" id="chips-categorias" hidden></div>
      <div class="grid-fichas" id="lista-meds"></div>
    </section>

    <section id="aba-evid">
      <div class="itens" id="lista-evid"></div>
    </section>

    <section id="aba-reg">
      <div class="itens" id="lista-reg"></div>
    </section>

    <section id="aba-gloss">
      <dl class="glossario" id="lista-gloss"></dl>
    </section>

    <section id="aba-tutor">
      <div class="tutor">
        <p class="sub" style="color:var(--tinta-2); margin:0 0 12px;">
          Pergunte sobre conceitos, terminologia, legislação e evidências.
          O filtro de segurança roda antes da IA: perguntas com caso clínico,
          pedido de diagnóstico ou dose são respondidas com orientação para
          procurar um médico-veterinário.
        </p>
        <textarea id="pergunta" placeholder="Ex.: O que a base diz sobre o uso de Silicea em cascos e unhas?"></textarea>
        <div class="acoes">
          <button id="btn-perguntar" type="button">Perguntar ao tutor</button>
          <label class="opcao-ia">
            <input type="checkbox" id="ia-toggle"> usar IA local (Ollama)
          </label>
        </div>
        <div id="resposta" class="resposta" hidden></div>
      </div>
    </section>
  </main>
</div>

<footer>
  <span id="versao-base"></span><br>
  <span class="restricao">Uso estritamente educacional. A eficácia da homeopatia não é sustentada por evidências científicas robustas. Nunca utilize esta base para diagnosticar, prescrever ou definir doses — consulte um médico-veterinário.</span>
</footer>

<div id="overlay" role="dialog" aria-modal="true" aria-label="Ficha completa do medicamento">
  <div class="modal">
    <button class="fechar" id="fechar-modal" type="button">Fechar</button>
    <h2 id="m-nome"></h2>
    <p class="sub" id="m-pop"></p>
    <dl id="m-campos"></dl>
  </div>
</div>

<script>
"use strict";
const BASE = __BASE_JSON__;
const GRUPOS = __GRUPOS_JSON__;

// ---------- utilidades ----------
const norm = s => (s || "").normalize("NFD").replace(/[\u0300-\u036f]/g, "").toLowerCase();
const $ = id => document.getElementById(id);
const esc = s => String(s == null ? "" : s)
  .replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;");

// ---------- estado ----------
let abaAtiva = "meds";
let grupoAtivo = null;   // null = todos
let categoriaAtiva = null;

// ---------- abas ----------
document.querySelectorAll(".abas button").forEach(btn => {
  btn.addEventListener("click", () => {
    abaAtiva = btn.dataset.aba;
    document.querySelectorAll(".abas button").forEach(b => b.classList.toggle("ativa", b === btn));
    document.querySelectorAll("main section").forEach(s => s.classList.toggle("ativa", s.id === "aba-" + abaAtiva));
    render();
  });
});

// ---------- índice por sistema (categorias maiores) ----------
function renderIndice() {
  $("lista-grupos").innerHTML =
    `<button type="button" class="${grupoAtivo === null ? "ativo" : ""}" data-grupo="">
       <span>Todos os sistemas</span><span class="n">${BASE.medicamentos.length}</span></button>` +
    GRUPOS.map(g =>
      `<button type="button" class="${grupoAtivo === g.nome ? "ativo" : ""}" data-grupo="${esc(g.nome)}">
        <span>${esc(g.nome)}</span><span class="n">${g.n}</span></button>`).join("");
}
$("lista-grupos").addEventListener("click", ev => {
  const btn = ev.target.closest("button");
  if (!btn) return;
  grupoAtivo = btn.dataset.grupo || null;
  categoriaAtiva = null;
  renderIndice();
  render();
});

// ---------- subcategorias do sistema ativo ----------
function renderChips() {
  // Sem sistema ativo, a nuvem com ~100 categorias seria uma parede — esconder.
  if (!grupoAtivo) { $("chips-categorias").hidden = true; return; }
  $("chips-categorias").hidden = false;
  const noGrupo = BASE.medicamentos.filter(m => m.grupo === grupoAtivo);
  const cats = [...new Set(noGrupo.map(m => m.categoria))].sort((a, b) => a.localeCompare(b, "pt-BR"));
  $("chips-categorias").innerHTML =
    `<button type="button" class="${categoriaAtiva === null ? "ativa" : ""}" data-cat="">Todas as categorias (${noGrupo.length})</button>` +
    cats.map(c =>
      `<button type="button" class="${categoriaAtiva === c ? "ativa" : ""}" data-cat="${esc(c)}">${esc(c)}</button>`).join("");
}
$("chips-categorias").addEventListener("click", ev => {
  const btn = ev.target.closest("button");
  if (!btn) return;
  categoriaAtiva = btn.dataset.cat || null;
  renderChips();
  render();
});

// ---------- renderização ----------
function render() {
  const q = norm($("busca").value.trim());

  if (abaAtiva === "meds") {
    const meds = BASE.medicamentos.filter(m => {
      const okGrupo = !grupoAtivo || m.grupo === grupoAtivo;
      const okCat = !categoriaAtiva || m.categoria === categoriaAtiva;
      const alvo = norm([m.nome, m.nome_popular, m.categoria, m.grupo,
        (m.sintomas_homeopaticos || []).join(" "),
        m.indicacoes_fabricante, m.uso_veterinario, m.origem].join(" "));
      return okGrupo && okCat && (!q || alvo.includes(q));
    });
    $("lista-meds").innerHTML = meds.length ? meds.map(cardMed).join("")
      : `<div class="vazio">Nenhum medicamento corresponde a essa combinação de busca e filtros. Limpe a busca ou escolha outro sistema.</div>`;
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
      </div>`).join("") : `<div class="vazio">Nenhuma evidência encontrada para esta busca.</div>`;
  }

  if (abaAtiva === "reg") {
    const regs = BASE.regulamentacao_brasil.filter(r => {
      const alvo = norm([r.aspecto, r.descricao, r.fonte, r.status].join(" "));
      return !q || alvo.includes(q);
    });
    $("lista-reg").innerHTML = regs.length ? regs.map(r => `
      <div class="item">
        <h3>${esc(r.aspecto)}</h3>
        <div class="meta">${esc(r.fonte)} — status: ${esc(r.status)}</div>
        <p>${esc(r.descricao)}</p>
      </div>`).join("") : `<div class="vazio">Nada encontrado na regulamentação para esta busca.</div>`;
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
  const indic = m.indicacoes_fabricante || "";
  return `<div class="ficha" data-nome="${esc(m.nome)}" role="button" tabindex="0">
    <h3>${esc(m.nome)}</h3>
    <div class="pop">${esc(m.nome_popular || "")}</div>
    <div class="sub">${esc(m.categoria)}</div>
    <p>${esc(indic.slice(0, 130))}${indic.length > 130 ? "…" : ""}</p>
    <span class="evid">Evidência: ${esc((m.evidencia_cientifica || "").slice(0, 90))}…</span>
  </div>`;
}

// ---------- modal de ficha completa ----------
function abrirFicha(nome) {
  const m = BASE.medicamentos.find(x => x.nome === nome);
  if (!m) return;
  $("m-nome").textContent = m.nome;
  $("m-pop").textContent = m.nome_popular
    ? `${m.nome_popular} — ${m.grupo}, categoria ${m.categoria}`
    : `${m.grupo}, categoria ${m.categoria}`;
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
}
$("lista-meds").addEventListener("click", ev => {
  const card = ev.target.closest(".ficha");
  if (card) abrirFicha(card.dataset.nome);
});
$("lista-meds").addEventListener("keydown", ev => {
  if (ev.key !== "Enter" && ev.key !== " ") return;
  const card = ev.target.closest(".ficha");
  if (card) { ev.preventDefault(); abrirFicha(card.dataset.nome); }
});
$("fechar-modal").addEventListener("click", () => $("overlay").classList.remove("aberto"));
$("overlay").addEventListener("click", ev => { if (ev.target === $("overlay")) $("overlay").classList.remove("aberto"); });
document.addEventListener("keydown", ev => { if (ev.key === "Escape") $("overlay").classList.remove("aberto"); });

// ---------- filtros ----------
$("busca").addEventListener("input", render);
$("limpar-busca").addEventListener("click", () => {
  $("busca").value = "";
  grupoAtivo = null;
  categoriaAtiva = null;
  renderIndice();
  render();
});

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
  // Radicais/flexões: cobrem formas sem acento e conjugadas (comparação via norm())
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
    `MEDICAMENTO ${m.nome} (${m.nome_popular}) — sistema ${m.grupo}, categoria ${m.categoria}. ` +
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

function contextoPara(pergunta, n = 4) {
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
  el.hidden = false;
  el.className = "resposta " + (classe || "");
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
A homeopatia NÃO substitui atendimento de emergência.`, "aviso-bloqueio");
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
Consulte um MÉDICO-VETERINÁRIO para qualquer caso individual.`, "aviso-bloqueio");
    return;
  }

  // 3) IA local desligada — orienta como ativar
  if (!$("ia-toggle").checked) {
    mostrarResposta("Ative a opção \u201cusar IA local (Ollama)\u201d para conversar com o tutor — ou use a CLI: py homeovet_cli.py perguntar \u201csua pergunta\u201d", "erro");
    return;
  }

  const contexto = contextoPara(pergunta);
  const user = `PERGUNTA: ${pergunta}\n\nCONTEXTO DA BASE EDUCACIONAL HomeoVet (use SOMENTE isto):\n` +
               contexto.join("\n---\n");
  mostrarResposta("Consultando o Ollama local…", "");
  $("btn-perguntar").disabled = true;

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
          think: false,
          options: { temperature: 0.2, num_ctx: 4096 }
        })
      });
      if (!r.ok) { erroFinal = `HTTP ${r.status}`; continue; }
      const dados = await r.json();
      resposta = (dados.message || {}).content || "";
      if (resposta.trim()) {
        clearTimeout(limite);
        mostrarResposta(`Tutor HomeoVet (IA local: ${modelo})\n\n${resposta.trim()}\n\n⚠️ Resposta EDUCACIONAL, ancorada na base do projeto. Confirme sempre com um médico-veterinário.`, "");
        $("btn-perguntar").disabled = false;
        return;
      }
    } catch (e) {
      erroFinal = e.name === "AbortError" ? "tempo esgotado (120s)" : e.message;
    }
  }
  clearTimeout(limite);
  $("btn-perguntar").disabled = false;
  mostrarResposta(
`Não consegui falar com o Ollama local (${erroFinal || "indisponível"}).

Checklist:
1. Ollama instalado e rodando: ollama serve
2. Modelo do tutor criado: ollama create homeovet-tutor -f Modelfile.homeovet
   (sem ele, o fallback nemotron-3-nano:4b é usado — ollama pull nemotron-3-nano:4b)
3. Se o navegador bloquear (CORS em arquivo local), inicie o Ollama permitindo a origem:
   OLLAMA_ORIGINS=* ollama serve

Enquanto isso, a interface continua 100% funcional offline (abas, busca, fichas).`, "erro");
});

// ---------- rodapé ----------
const versao = BASE.metadata || {};
$("versao-base").textContent =
  `Base educacional v${versao.versao || "?"}, atualizada em ${versao.data_atualizacao || "?"} — ` +
  `${BASE.medicamentos.length} medicamentos, ${BASE.evidencias_cientificas.length} evidências, ` +
  `${Object.keys(BASE.glossario || {}).length} termos de glossário.`;

// ---------- inicialização ----------
renderIndice();
renderChips();
render();
</script>
</body>
</html>
"""


if __name__ == "__main__":
    principal()