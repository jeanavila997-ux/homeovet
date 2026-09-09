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
<script>
/* aplica o tema salvo (ou a preferência do sistema) antes do primeiro paint */
try {
  const t = localStorage.getItem("homeovet_tema") ||
    (matchMedia("(prefers-color-scheme: dark)").matches ? "escuro" : "claro");
  document.documentElement.dataset.tema = t;
} catch (e) { document.documentElement.dataset.tema = "claro"; }
</script>
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
/* tema escuro — mesma farmacopeia na prateleira escura */
html[data-tema="escuro"] {
  --papel: #131C16;        /* fundo verde-tinta profundo */
  --folha: #1C2820;        /* superfícies */
  --tinta: #E7ECDF;        /* texto claro esverdeado */
  --tinta-2: #A9B7A4;      /* secundário com contraste confortável */
  --ambar: #D2A262;        /* frasco âmbar à luz */
  --ambar-suave: #2C2517;  /* realce quente escuro */
  --linha: #37463B;        /* hairlines visíveis no escuro */
  --alerta: #E38B8B;       /* vermelho-veterinário claro */
  color-scheme: dark;
}
html[data-tema="escuro"] #limpar-busca,
html[data-tema="escuro"] #btn-tema { color: var(--tinta); }
* { box-sizing: border-box; }
html { scroll-behavior: smooth; color-scheme: light; }
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
#limpar-busca, #btn-tema {
  border: 1px solid var(--linha);
  background: var(--folha);
  border-radius: var(--raio);
  padding: 10px 16px;
  font: inherit;
  color: var(--tinta-2);
  cursor: pointer;
}
#limpar-busca:hover, #btn-tema:hover { color: var(--tinta); border-color: var(--tinta-2); }

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

/* ---------- tutor local (chat) ---------- */
.chat { max-width: 860px; }
.chat-cabecalho {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  gap: 12px;
  flex-wrap: wrap;
  border-bottom: 1px solid var(--linha);
  padding-bottom: 10px;
  margin-bottom: 14px;
}
.chat-cabecalho h3 { font-family: var(--serif); font-size: 20px; margin: 0; }
.chat-status { font-size: 12.5px; color: var(--tinta-2); }
.chat-status .on { color: var(--ambar); font-weight: 600; }
#btn-limpar-chat {
  border: 1px solid var(--linha);
  background: var(--folha);
  border-radius: var(--raio);
  padding: 5px 12px;
  font: inherit;
  font-size: 12.5px;
  color: var(--tinta-2);
  cursor: pointer;
}
#btn-limpar-chat:hover { color: var(--alerta); border-color: var(--alerta); }
#chat-historico {
  display: flex;
  flex-direction: column;
  gap: 12px;
  max-height: 52vh;
  overflow-y: auto;
  padding: 4px 2px 10px;
}
.msg {
  max-width: 80%;
  padding: 10px 14px;
  border-radius: var(--raio);
  font-size: 14px;
  white-space: pre-wrap;
  line-height: 1.5;
}
.msg.usuario {
  align-self: flex-end;
  background: var(--ambar-suave);
  border: 1px solid var(--ambar);
}
.msg.tutor {
  align-self: flex-start;
  background: var(--folha);
  border: 1px solid var(--linha);
  border-left: 3px solid var(--ambar);
}
.msg.tutor .fonte {
  display: block;
  margin-top: 8px;
  padding-top: 6px;
  border-top: 1px solid var(--linha);
  font-size: 11.5px;
  color: var(--tinta-2);
  white-space: normal;
}
.msg.aviso {
  align-self: flex-start;
  background: var(--folha);
  border: 1px solid var(--alerta);
  color: var(--alerta);
}
.msg.erro {
  align-self: flex-start;
  background: var(--folha);
  border: 1px dashed var(--tinta-2);
  color: var(--tinta-2);
}
.msg.digitando {
  align-self: flex-start;
  background: var(--folha);
  border: 1px solid var(--linha);
  color: var(--tinta-2);
  font-size: 13px;
}
.msg.digitando .pontos span {
  display: inline-block;
  animation: piscar 1.2s infinite;
}
.msg.digitando .pontos span:nth-child(2) { animation-delay: .2s; }
.msg.digitando .pontos span:nth-child(3) { animation-delay: .4s; }
@keyframes piscar { 0%, 80%, 100% { opacity: .25; } 40% { opacity: 1; } }
.composer {
  border-top: 1px solid var(--linha);
  padding-top: 12px;
  margin-top: 4px;
}
.composer textarea {
  width: 100%;
  min-height: 56px;
  max-height: 170px;
  padding: 11px 13px;
  border: 1px solid var(--linha);
  border-radius: var(--raio);
  background: var(--folha);
  font: inherit;
  color: var(--tinta);
  resize: vertical;
}
.composer .acoes {
  display: flex;
  align-items: center;
  gap: 14px;
  margin-top: 8px;
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
.opcao-ia select {
  border: 1px solid var(--linha);
  border-radius: var(--raio);
  background: var(--folha);
  font: inherit;
  font-size: 12.5px;
  color: var(--tinta);
  padding: 5px 8px;
}
#key-9router {
  border: 1px solid var(--linha);
  border-radius: var(--raio);
  background: var(--folha);
  font: inherit;
  font-size: 12.5px;
  color: var(--tinta);
  padding: 5px 8px;
  flex: 1 1 220px;
  max-width: 280px;
}
.dica-enter { font-size: 11.5px; color: var(--tinta-2); margin-left: auto; }
.chat-nota { font-size: 12px; color: var(--tinta-2); margin: 10px 0 0; }

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
    <button id="btn-tema" type="button" aria-pressed="false" title="Alternar tema claro/escuro">Tema claro</button>
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
      <div class="chat">
        <div class="chat-cabecalho">
          <h3>Tutor local</h3>
          <span class="chat-status">segurança por regras antes da IA · motor: <span id="status-ia" class="on">Ollama local</span></span>
          <button id="btn-limpar-chat" type="button">Limpar conversa</button>
        </div>
        <div id="chat-historico" aria-live="polite"></div>
        <div class="composer">
          <textarea id="pergunta" placeholder="Pergunte sobre conceitos, terminologia, legislação ou evidências. Ex.: O que a base diz sobre Silicea em cascos e unhas?"></textarea>
          <div class="acoes">
            <button id="btn-perguntar" type="button">Enviar pergunta</button>
            <label class="opcao-ia">
              motor
              <select id="motor-ia" aria-label="Motor de IA do tutor">
                <option value="ollama" selected>Ollama local (offline)</option>
                <option value="9router">9Router local (gpt-6-astra)</option>
              </select>
            </label>
            <input id="key-9router" type="password" placeholder="API key do 9Router (Dashboard → Keys)" autocomplete="off" hidden>
            <span class="dica-enter">Enter envia, Shift+Enter quebra linha</span>
          </div>
        </div>
        <p class="chat-nota">Uso estritamente educacional: o tutor não diagnostica, não prescreve e não recomenda doses. Caso clínico real: procure um médico-veterinário.</p>
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

// ---------- tema claro/escuro ----------
function aplicarTema(tema) {
  document.documentElement.dataset.tema = tema;
  $("btn-tema").textContent = tema === "escuro" ? "Tema escuro" : "Tema claro";
  $("btn-tema").setAttribute("aria-pressed", tema === "escuro" ? "true" : "false");
  try { localStorage.setItem("homeovet_tema", tema); } catch (e) {}
}
$("btn-tema").addEventListener("click", () => {
  aplicarTema(document.documentElement.dataset.tema === "escuro" ? "claro" : "escuro");
});
aplicarTema(document.documentElement.dataset.tema || "claro");

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

// ---------- Tutor local: chat educacional multi-turno ----------
const historicoChat = [];   // [{role, content}] — contexto da conversa
const MAX_TURNO_CTX = 8;    // mensagens anteriores levadas ao modelo

function bolha(texto, tipo, fonte) {
  const div = document.createElement("div");
  div.className = "msg " + tipo;
  const conteudo = document.createElement("span");
  conteudo.textContent = texto;
  div.append(conteudo);
  if (fonte) {
    const f = document.createElement("span");
    f.className = "fonte";
    f.textContent = fonte;
    div.append(f);
  }
  $("chat-historico").append(div);
  $("chat-historico").scrollTop = $("chat-historico").scrollHeight;
  return div;
}

function bolhaDigitando() {
  const div = document.createElement("div");
  div.className = "msg digitando";
  div.innerHTML = 'Consultando a base e o Ollama local <span class="pontos"><span>·</span><span>·</span><span>·</span></span>';
  $("chat-historico").append(div);
  $("chat-historico").scrollTop = $("chat-historico").scrollHeight;
  return div;
}

const BOAS_VINDAS =
`Olá! Sou o Tutor HomeoVet, educacional.
Posso explicar conceitos de homeopatia veterinária, a ficha de cada medicamento da base (125 remédios, incluindo o sistema de cascos e unhas), a regulamentação brasileira e o que as evidências científicas dizem — ou não dizem.
Para conversar com a IA, escolha o motor abaixo: Ollama local (offline, sem key) ou 9Router local (gpt-6-astra, pede a API key do painel).
Pergunte, por exemplo: "O que a base diz sobre o uso de Silicea em cascos e unhas?"`;
bolha(BOAS_VINDAS, "tutor");

$("motor-ia").addEventListener("change", () => {
  const motor = $("motor-ia").value;
  $("status-ia").textContent = motor === "9router" ? "9Router local" : "Ollama local";
  $("key-9router").hidden = motor !== "9router";
  if (motor === "9router") {
    try { $("key-9router").value = localStorage.getItem("homeovet_9router_key") || ""; } catch (e) {}
  }
});
$("key-9router").addEventListener("change", () => {
  try { localStorage.setItem("homeovet_9router_key", $("key-9router").value.trim()); } catch (e) {}
});

$("btn-limpar-chat").addEventListener("click", () => {
  historicoChat.length = 0;
  $("chat-historico").innerHTML = "";
  bolha(BOAS_VINDAS, "tutor");
});

async function enviarPergunta() {
  const pergunta = $("pergunta").value.trim();
  if (!pergunta || $("btn-perguntar").disabled) return;

  // 1) Emergência — regras antes de qualquer LLM (nunca vai ao modelo)
  const urg = SINTOMAS_URGENTES.find(s => norm(pergunta).includes(norm(s)));
  if (urg) {
    bolha(pergunta, "usuario");
    bolha(`🚨 ATENÇÃO — POSSÍVEL EMERGÊNCIA
Detectei menção a: "${urg}"
Procure um MÉDICO-VETERINÁRIO URGENTEMENTE ou uma clínica 24h.
A homeopatia NÃO substitui atendimento de emergência.`, "aviso");
    $("pergunta").value = "";
    return;
  }

  // 2) Tentativa de diagnóstico/prescrição — bloqueio por regras (nunca LLM)
  const bloq = PALAVRAS_BLOQUEIO.find(p => norm(pergunta).includes(norm(p)));
  if (bloq) {
    bolha(pergunta, "usuario");
    bolha(`⚠️ AVISO DE SEGURANÇA
Sou um tutor EDUCACIONAL sobre homeopatia veterinária.
NÃO posso: diagnosticar, prescrever, recomendar doses ou substituir o veterinário.
Posso ajudar com: conceitos teóricos, terminologia, legislação e evidências científicas.
Consulte um MÉDICO-VETERINÁRIO para qualquer caso individual.`, "aviso");
    $("pergunta").value = "";
    return;
  }

  // 3) Motor 9Router sem API key — orienta (conforme a skill: Dashboard → Keys)
  if ($("motor-ia").value === "9router" && !$("key-9router").value.trim()) {
    bolha(pergunta, "usuario");
    bolha(`Para usar o 9Router local, cole a API key no campo ao lado do seletor de motor.
Gere ou copie uma key no painel do 9Router: http://localhost:20128 (Dashboard → Keys).
A key fica salva apenas neste navegador (localStorage) — não vai para o arquivo HTML nem para o GitHub.
Alternativa imediata: motor Ollama local (sem key) ou a CLI: py homeovet_cli.py perguntar "sua pergunta".`, "erro");
    $("pergunta").value = "";
    return;
  }

  bolha(pergunta, "usuario");
  $("pergunta").value = "";
  const digitando = bolhaDigitando();
  $("btn-perguntar").disabled = true;

  // contexto RAG da pergunta atual + histórico recente (multi-turno)
  const contexto = contextoPara(pergunta);
  const user = `PERGUNTA: ${pergunta}\n\nCONTEXTO DA BASE EDUCACIONAL HomeoVet (use SOMENTE isto):\n` +
               contexto.join("\n---\n");
  const mensagens = [
    { role: "system", content: SYSTEM_RAG },
    ...historicoChat.slice(-MAX_TURNO_CTX),
    { role: "user", content: user }
  ];

  const controlador = new AbortController();
  const limite = setTimeout(() => controlador.abort(), 120000);
  let resposta = null, erroFinal = null, modeloUsado = null;

  if ($("motor-ia").value === "9router") {
    // 9Router local — gateway OpenAI-compatível (skill 9router): Bearer key em
    // /v1/chat/completions; 401 = key inválida, 503 = contas indisponíveis
    const key = $("key-9router").value.trim();
    if (key) { try { localStorage.setItem("homeovet_9router_key", key); } catch (e) {} }
    try {
      const r = await fetch("http://localhost:20128/v1/chat/completions", {
        method: "POST",
        headers: { "Content-Type": "application/json", "Authorization": "Bearer " + key },
        signal: controlador.signal,
        body: JSON.stringify({
          model: "cx/gpt-6-astra",
          messages: mensagens,
          stream: false,
          max_tokens: 2048
        })
      });
      if (r.status === 401) {
        erroFinal = "401 — API key inválida ou ausente. Gere ou copie uma key no painel do 9Router (localhost:20128, Dashboard → Keys).";
      } else if (r.status === 503) {
        erroFinal = "503 — todas as contas do provedor estão indisponíveis agora. Aguarde e reenvie, ou troque o motor para Ollama.";
      } else if (!r.ok) {
        erroFinal = `HTTP ${r.status}`;
      } else {
        const dados = await r.json();
        resposta = (dados.choices && dados.choices[0] && dados.choices[0].message &&
                    dados.choices[0].message.content) || "";
        if (resposta.trim()) modeloUsado = "cx/gpt-6-astra (9Router)";
      }
    } catch (e) {
      erroFinal = e.name === "AbortError" ? "tempo esgotado (120s)" : e.message;
    }
  } else {
    // Ollama local — sem key; modelo do tutor com fallback para o nano
    const modelos = ["homeovet-tutor", "nemotron-3-nano:4b"];
    for (const modelo of modelos) {
      try {
        const r = await fetch("http://localhost:11434/api/chat", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          signal: controlador.signal,
          body: JSON.stringify({
            model: modelo,
            messages: mensagens,
            stream: false,
            think: false,
            options: { temperature: 0.2, num_ctx: 4096 }
          })
        });
        if (!r.ok) { erroFinal = `HTTP ${r.status}`; continue; }
        const dados = await r.json();
        resposta = (dados.message || {}).content || "";
        if (resposta.trim()) { modeloUsado = modelo; break; }
      } catch (e) {
        erroFinal = e.name === "AbortError" ? "tempo esgotado (120s)" : e.message;
      }
    }
  }
  clearTimeout(limite);
  $("btn-perguntar").disabled = false;
  digitando.remove();

  if (resposta && resposta.trim()) {
    historicoChat.push({ role: "user", content: user },
                       { role: "assistant", content: resposta.trim() });
    bolha(resposta.trim(), "tutor",
      `IA local: ${modeloUsado}. Resposta EDUCACIONAL ancorada na base do projeto — confirme sempre com um médico-veterinário.`);
  } else {
    bolha(`Não consegui responder com o motor selecionado (${erroFinal || "sem resposta"}).

Ollama: verifique "ollama serve" e o modelo do tutor (ollama create homeovet-tutor -f Modelfile.homeovet; fallback nemotron-3-nano:4b). Em arquivo local, CORS: OLLAMA_ORIGINS=* ollama serve.
9Router: verifique o painel em localhost:20128 e a API key (Dashboard → Keys).

A interface continua 100% funcional offline (abas, busca, fichas).`, "erro");
  }
  $("pergunta").focus();
}

$("btn-perguntar").addEventListener("click", enviarPergunta);
$("pergunta").addEventListener("keydown", ev => {
  if (ev.key === "Enter" && !ev.shiftKey) { ev.preventDefault(); enviarPergunta(); }
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

// deep-link: #meds, #evid, #reg, #gloss ou #tutor abre a aba direto
const abaHash = (location.hash || "").replace("#", "");
if (["meds", "evid", "reg", "gloss", "tutor"].includes(abaHash)) {
  const botao = document.querySelector(`.abas button[data-aba="${abaHash}"]`);
  if (botao) botao.click();
}
</script>
</body>
</html>
"""


if __name__ == "__main__":
    principal()