#!/usr/bin/env python3
"""
💻 CLI HomeoVet — v1.0.0
========================

CLI completa do projeto HomeoVet: fichas técnicas, evidências científicas,
regulamentação brasileira, glossário, quiz de aprendizagem, memória local
(favoritos, anotações, histórico, progresso) e exportação.

Modo IA local (OPCIONAL):
    - Se o Ollama estiver rodando em http://localhost:11434, a busca por
      sintomas usa embeddings semânticos (nomic-embed-text) e o comando
      `perguntar` usa RAG + LLM local com o protocolo pedagógico do tutor.
    - Sem Ollama (ou com --sem-ia), tudo funciona em Python puro:
      busca léxica (difflib) + motor de regras do tutor educacional.

⚠️  USO ESTRITAMENTE EDUCACIONAL. Não diagnostica, não prescreve, não
recomenda doses. Não substitui médico-veterinário ou médico. A eficácia da
homeopatia não é sustentada por evidências científicas robustas (Bergh et
al., 2021).

Dependências: Python 3.7+ (nenhuma obrigatória).
Opcional: rich>=13.0.0 para interface colorida (`pip install rich`).
"""

import argparse
import datetime
import hashlib
import json
import os
import random
import sys
import urllib.error
import urllib.request
from difflib import SequenceMatcher
from typing import Dict, List, Optional, Tuple

# Reuso dos módulos irmãos (fonte única de verdade do projeto)
from agente_homeopatico import (
    buscar_remedios as buscar_remedios_humano,
    carregar_remedios,
    similaridade,
)
from tutor_homeopatia_vet import (
    FiltroSeguranca,
    MotorBusca,
    TutorHomeopatiaVet,
    carregar_json,
)

# ============================================================
# CONFIGURAÇÕES
# ============================================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
BASE_VET_FILE = os.path.join(DATA_DIR, "tutor_homeopatia_vet.json")
RUNTIME_DIR = os.path.join(BASE_DIR, "runtime")

PROGRESSO_FILE = os.path.join(RUNTIME_DIR, "progresso.json")
FAVORITOS_FILE = os.path.join(RUNTIME_DIR, "favoritos.json")
ANOTACOES_FILE = os.path.join(RUNTIME_DIR, "anotacoes.json")
HISTORICO_FILE = os.path.join(RUNTIME_DIR, "historico.json")
EMBED_CACHE_FILE = os.path.join(RUNTIME_DIR, "embeddings_cache.json")
EXPORT_DEFAULT = os.path.join(BASE_DIR, "homeovet_export.md")

# Ollama (modo IA local — opcional)
OLLAMA_URL = "http://localhost:11434"
OLLAMA_TIMEOUT = 3  # segundos
MODELO_TUTOR = "homeovet-tutor"        # criado via Modelfile.homeovet
MODELO_TUTOR_FALLBACK = "nemotron-3-nano:4b"  # já instalado localmente
MODELO_EMBEDDINGS = "nomic-embed-text"  # ollama pull nomic-embed-text

VERSÃO = "1.0.0"

USO_IA = True  # desligado por --sem-ia


# ============================================================
# INTERFACE COLORIDA (rich opcional)
# ============================================================
class Impressora:
    """Wrapper de impressão: usa rich se instalado, senão texto puro."""

    def __init__(self):
        try:
            from rich.console import Console  # type: ignore
            from rich.theme import Theme  # type: ignore
            self._console = Console(theme=Theme({
                "titulo": "bold cyan",
                "info": "bold yellow",
                "ok": "bold green",
                "erro": "bold red",
                "aviso": "bold yellow",
                "nome": "bold magenta",
            }))
            self._rich = True
        except ImportError:
            self._console = None
            self._rich = False

    def titulo(self, texto: str):
        if self._rich:
            self._console.print(texto, style="titulo")
        else:
            print("\n" + texto)

    def info(self, texto: str):
        if self._rich:
            self._console.print(texto, style="info")
        else:
            print(texto)

    def ok(self, texto: str):
        if self._rich:
            self._console.print(texto, style="ok")
        else:
            print(texto)

    def erro(self, texto: str):
        if self._rich:
            self._console.print(texto, style="erro")
        else:
            print(texto)

    def aviso(self, texto: str):
        if self._rich:
            self._console.print(texto, style="aviso")
        else:
            print(texto)

    def nome(self, texto: str):
        if self._rich:
            self._console.print(texto, style="nome")
        else:
            print(texto)

    def texto(self, texto: str = ""):
        print(texto)


out = Impressora()


def linha(char: str = "─", n: int = 50) -> str:
    return char * n


# ============================================================
# MEMÓRIA LOCAL (runtime/)
# ============================================================
def _carregar_runtime(caminho: str, padrao) -> list:
    try:
        with open(caminho, "r", encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return padrao


def _salvar_runtime(caminho: str, dados) -> bool:
    os.makedirs(RUNTIME_DIR, exist_ok=True)
    try:
        with open(caminho, "w", encoding="utf-8") as f:
            json.dump(dados, f, ensure_ascii=False, indent=2)
        return True
    except OSError as e:
        out.erro(f"❌ Falha ao salvar {os.path.basename(caminho)}: {e}")
        return False


def agora() -> str:
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def registrar_historico(comando: str, detalhe: str = ""):
    historico = _carregar_runtime(HISTORICO_FILE, [])
    historico.append({"data": agora(), "comando": comando, "detalhe": detalhe[:200]})
    # Mantém os 500 registros mais recentes
    _salvar_runtime(HISTORICO_FILE, historico[-500:])


# ============================================================
# CAMADA OLLAMA (modo IA local — 100% opcional)
# ============================================================
def _post_api(endpoint: str, payload: dict, timeout: float = OLLAMA_TIMEOUT) -> Optional[dict]:
    """POST JSON na API do Ollama; None em caso de falha."""
    url = f"{OLLAMA_URL}{endpoint}"
    dados = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url, data=dados, headers={"Content-Type": "application/json"}
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except (urllib.error.URLError, urllib.error.HTTPError, ValueError, OSError):
        return None


def ia_disponivel() -> bool:
    """Verifica se o Ollama está acessível localmente."""
    if not USO_IA:
        return False
    try:
        req = urllib.request.Request(f"{OLLAMA_URL}/api/tags")
        with urllib.request.urlopen(req, timeout=OLLAMA_TIMEOUT) as resp:
            json.loads(resp.read().decode("utf-8"))
        return True
    except (urllib.error.URLError, ValueError, OSError):
        return False


def modelos_instalados() -> List[str]:
    """Lista nomes dos modelos instalados no Ollama (vazio se indisponível)."""
    try:
        req = urllib.request.Request(f"{OLLAMA_URL}/api/tags")
        with urllib.request.urlopen(req, timeout=OLLAMA_TIMEOUT) as resp:
            dados = json.loads(resp.read().decode("utf-8"))
        return [m.get("name", "") for m in dados.get("models", [])]
    except (urllib.error.URLError, ValueError, OSError):
        return []


def resolver_modelo_tutor() -> Optional[str]:
    """Escolhe o modelo do tutor: Modelfile homeovet-tutor, senão fallback local."""
    instalados = modelos_instalados()
    if not instalados:
        return None
    if any(m.startswith(MODELO_TUTOR) for m in instalados):
        return MODELO_TUTOR
    if any(m.startswith(MODELO_TUTOR_FALLBACK) for m in instalados):
        return MODELO_TUTOR_FALLBACK
    return None  # nenhum modelo local adequado


def _cache_embedding_chave(texto: str, modelo: str) -> str:
    return hashlib.md5(f"{modelo}::{texto}".encode("utf-8")).hexdigest()


def embedding(texto: str) -> Optional[List[float]]:
    """Gera embedding do texto via Ollama, com cache local em runtime/."""
    cache = _carregar_runtime(EMBED_CACHE_FILE, {})
    chave = _cache_embedding_chave(texto, MODELO_EMBEDDINGS)
    if chave in cache:
        return cache[chave]

    resposta = _post_api("/api/embeddings", {
        "model": MODELO_EMBEDDINGS,
        "prompt": texto,
    }, timeout=30)
    if not resposta or "embedding" not in resposta:
        return None

    cache[chave] = resposta["embedding"]
    _salvar_runtime(EMBED_CACHE_FILE, cache)
    return resposta["embedding"]


def cosseno(a: List[float], b: List[float]) -> float:
    """Similaridade de cosseno entre dois vetores."""
    if not a or not b or len(a) != len(b):
        return 0.0
    prod = sum(x * y for x, y in zip(a, b))
    na = sum(x * x for x in a) ** 0.5
    nb = sum(y * y for y in b) ** 0.5
    if na == 0 or nb == 0:
        return 0.0
    return prod / (na * nb)


def chat_llm(system: str, user: str, modelo: str) -> Optional[str]:
    """Chamada de chat no LLM local; None em caso de falha."""
    resposta = _post_api("/api/chat", {
        "model": modelo,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        "stream": False,
        "options": {"temperature": 0.2, "num_ctx": 4096},
    }, timeout=180)
    if not resposta:
        return None
    conteudo = resposta.get("message", {}).get("content", "")
    return conteudo.strip() if conteudo else None


# ============================================================
# CARREGAMENTO DAS BASES
# ============================================================
def base_vet() -> dict:
    return carregar_json(BASE_VET_FILE)


# ============================================================
# BUSCA POR SINTOMAS (léxica + semântica opcional)
# ============================================================
def _buscar_vet_lexical(query: str, remedios_vet: List[dict], top_n: int) -> List[Tuple[dict, float]]:
    """Busca léxica na base veterinária (sintomas_homeopaticos)."""
    query_lower = query.lower()
    resultados = []
    for med in remedios_vet:
        melhor = 0.0
        for sintoma in med.get("sintomas_homeopaticos", []):
            s = sintoma.lower()
            score = similaridade(query_lower, s)
            if query_lower in s or s in query_lower:
                score = max(score, 0.8)
            melhor = max(melhor, score)
        # Também considera nome e categoria
        melhor = max(melhor, similaridade(query_lower, med.get("nome", "").lower()) * 0.9)
        if melhor > 0.25:
            resultados.append((med, melhor))
    resultados.sort(key=lambda par: par[1], reverse=True)
    return resultados[:top_n]


def _rrf(rankings: List[List[str]], k: int = 60) -> Dict[str, float]:
    """Reciprocal Rank Fusion: funde rankings por posição, sem depender de escala."""
    pontuacao: Dict[str, float] = {}
    for ranking in rankings:
        for pos, item in enumerate(ranking, start=1):
            pontuacao[item] = pontuacao.get(item, 0.0) + 1.0 / (k + pos)
    return pontuacao


def cmd_buscar(args):
    """Busca por sintomas nas bases humana e veterinária."""
    query = " ".join(args.termos)
    top_n = args.top
    remedios_humano = carregar_remedios()
    remedios_vet = base_vet().get("medicamentos", [])

    fonte_humana = remedios_humano if not args.vet else []
    fonte_vet = remedios_vet if not args.humano else []

    out.titulo(f"🔍 BUSCA POR SINTOMAS: “{query}”")
    out.texto()

    semantica_ativa = False
    if not args.sem_ia and (fonte_humana or fonte_vet):
        consulta_vec = embedding(query)
        if consulta_vec is not None:
            semantica_ativa = True

    modo = "semântica (embeddings) + léxica, fusão RRF" if semantica_ativa else "léxica (difflib)"
    ia = "IA local ATIVA" if semantica_ativa else ("IA local inativa (Ollama offline/--sem-ia)" if not args.sem_ia else "IA local desligada (--sem-ia)")
    out.info(f"⚙️  Modo: {modo} — {ia}")

    # ---- Ranking léxico
    lex_humano = [(r["nome"], s) for r, s in _rank_humano(fonte_humana, query, top_n * 2)]
    lex_vet = [(m["nome"], s) for m, s in _buscar_vet_lexical(query, fonte_vet, top_n * 2)]

    # ---- Ranking semântico (opcional)
    sem_humano: List[str] = []
    sem_vet: List[str] = []
    if semantica_ativa:
        consulta_vec = embedding(query)
        sem_humano = _rank_semantico_humano(fonte_humano, consulta_vec, top_n * 2)
        sem_vet = _rank_semantico_vet(fonte_vet, consulta_vec, top_n * 2)

    # ---- Fusão por base
    pontuacao_humano = _rrf([[n for n, _ in lex_humano], sem_humano])
    pontuacao_vet = _rrf([[n for n, _ in lex_vet], sem_vet])

    mapa_humano = {r["nome"]: r for r in fonte_humana}
    mapa_vet = {m["nome"]: m for m in fonte_vet}

    if pontuacao_humano:
        out.texto()
        out.titulo("📋 BASE HUMANA (24 remédios — uso educacional)")
        for nome, pts in sorted(pontuacao_humano.items(), key=lambda par: par[1], reverse=True)[:top_n]:
            r = mapa_humano.get(nome)
            if r:
                out.nome(f"  • {r['nome']} ({r.get('categoria', '—')})")
                out.texto(f"      Indicações: {r.get('indicacoes', '—')}")
                out.texto(f"      Aprendizado: {r.get('total_feedback', 0)} feedbacks "
                          f"(score {r.get('score', 0):+.1f})")

    if pontuacao_vet:
        out.texto()
        out.titulo("🐾 BASE VETERINÁRIA (12 medicamentos — educacional)")
        for nome, pts in sorted(pontuacao_vet.items(), key=lambda par: par[1], reverse=True)[:top_n]:
            m = mapa_vet.get(nome)
            if m:
                out.nome(f"  • {m['nome']} — {m.get('categoria', '—')}")
                out.texto(f"      Indicações (fabricante): {m.get('indicacoes_fabricante', '—')[:120]}")
                out.texto(f"      Evidência: {m.get('evidencia_cientifica', '—')[:120]}")

    if not pontuacao_humano and not pontuacao_vet:
        out.aviso("Nenhum resultado. Tente outros termos (ex.: “contusão queda dor muscular”).")

    out.texto()
    out.aviso("⚠️  Resultado EDUCACIONAL — não é indicação de tratamento.")
    out.texto("    Para dar feedback e treinar o ranking, use o agente interativo:")
    out.texto("    py agente_homeopatico.py")
    registrar_historico("buscar", query)


def _rank_humano(remedios: List[dict], query: str, top_n: int) -> List[Tuple[dict, float]]:
    """Ranking léxico na base humana (reusa o motor do agente)."""
    if not remedios:
        return []
    # buscar_remedios devolve remédios enriquecidos com "score_busca", já ordenados
    return [(r, r.get("score_busca", 0.0))
            for r in buscar_remedios_humano(remedios, query, top_n=top_n)]


def _rank_semantico_humano(remedios: List[dict], consulta_vec: List[float], top_n: int) -> List[str]:
    """Ranking por embeddings na base humana (média dos sintomas)."""
    ranking: List[Tuple[str, float]] = []
    for r in remedios:
        texto = "; ".join(r.get("sintomas", [])) + "; " + r.get("indicacoes", "")
        vec = embedding(texto)
        if vec:
            ranking.append((r["nome"], cosseno(consulta_vec, vec)))
    ranking.sort(key=lambda par: par[1], reverse=True)
    return [nome for nome, _ in ranking[:top_n]]


def _rank_semantico_vet(medicamentos: List[dict], consulta_vec: List[float], top_n: int) -> List[str]:
    """Ranking por embeddings na base veterinária."""
    ranking: List[Tuple[str, float]] = []
    for m in medicamentos:
        texto = "; ".join(m.get("sintomas_homeopaticos", [])) + "; " + m.get("indicacoes_fabricante", "")
        vec = embedding(texto)
        if vec:
            ranking.append((m["nome"], cosseno(consulta_vec, vec)))
    ranking.sort(key=lambda par: par[1], reverse=True)
    return [nome for nome, _ in ranking[:top_n]]


# ============================================================
# FICHA TÉCNICA
# ============================================================
def cmd_ficha(args):
    """Ficha técnica completa de um medicamento veterinário."""
    busca = MotorBusca(base_vet())
    med = busca.buscar_medicamento(" ".join(args.nome))
    if not med:
        out.erro(f"❌ Medicamento “{' '.join(args.nome)}” não encontrado na base veterinária.")
        out.texto("   Use `py homeovet_cli.py medicamentos` para listar os 12 disponíveis.")
        sys.exit(1)

    out.titulo(f"💊 FICHA TÉCNICA: {med['nome']} ({med.get('nome_popular', '')})")
    out.texto(linha())
    campos = [
        ("Origem", med.get("origem")),
        ("Princípio ativo (declarado)", med.get("principio_ativo_declarado")),
        ("Categoria", med.get("categoria")),
        ("Potências comuns", ", ".join(med.get("potencias_comuns", []))),
        ("Apresentações", med.get("apresentacoes")),
        ("Conservação", med.get("conservacao")),
        ("Indicações (fabricante)", med.get("indicacoes_fabricante")),
        ("Registro MAPA", med.get("indicacoes_registro_mapa")),
        ("Sintomas homeopáticos", "; ".join(med.get("sintomas_homeopaticos", []))),
        ("Contraindicações", med.get("contraindicacoes")),
        ("Precauções", med.get("precaucoes")),
        ("Uso veterinário", med.get("uso_veterinario")),
        ("Fonte da informação", med.get("tipo_informacao")),
    ]
    for rotulo, valor in campos:
        if valor:
            out.info(f"  {rotulo}:")
            for trecho in str(valor).split("\n"):
                out.texto(f"      {trecho}")

    out.texto()
    out.titulo("🔬 EVIDÊNCIA CIENTÍFICA")
    out.texto(f"      {med.get('evidencia_cientifica', 'Não disponível')}")
    out.texto(f"      Notas: {med.get('notas', '—')}")
    out.texto()
    out.aviso("⚠️  Ficha EDUCACIONAL. Declarações de fabricante ≠ evidência científica.")
    out.texto("    Consulte um médico-veterinário para qualquer decisão clínica.")
    registrar_historico("ficha", med["nome"])


def cmd_medicamentos(_args):
    """Lista os medicamentos veterinários da base."""
    medicamentos = base_vet().get("medicamentos", [])
    out.titulo(f"🐾 MEDICAMENTOS VETERINÁRIOS NA BASE ({len(medicamentos)})")
    out.texto()
    for i, med in enumerate(medicamentos, 1):
        out.nome(f"  [{i:02d}] {med['nome']} ({med.get('nome_popular', '')})")
        out.texto(f"       Categoria: {med.get('categoria', '—')}")
        out.texto(f"       Fonte: {med.get('tipo_informacao', '—')}")
    out.texto()
    out.info("Ficha completa: py homeovet_cli.py ficha “Arnica Montana”")
    registrar_historico("medicamentos")


# ============================================================
# EVIDÊNCIAS / REGULAMENTAÇÃO / GLOSSÁRIO
# ============================================================
def cmd_evidencias(args):
    """Lista evidências científicas da base."""
    evids = base_vet().get("evidencias_cientificas", [])
    if args.termo:
        termo = " ".join(args.termo).lower()
        evids = [e for e in evids if termo in (e.get("estudo", "") + e.get("conclusao", "")).lower()]
    out.titulo(f"🔬 EVIDÊNCIAS CIENTÍFICAS ({len(evids)})")
    for ev in evids:
        out.texto()
        out.nome(f"  📄 {ev.get('estudo', '—')}")
        out.texto(f"      Conclusão: {ev.get('conclusao', '—')}")
        out.texto(f"      Nível de evidência: {ev.get('nivel_evidencia', '—')}")
        out.texto(f"      Relevância: {ev.get('relevancia', '—')}")
    out.texto()
    out.aviso("⚠️  Síntese honesta: as evidências atuais são INSUFICIENTES para afirmar eficácia.")
    registrar_historico("evidencias")


def cmd_regulamentacao(_args):
    """Lista a regulamentação brasileira da base."""
    regs = base_vet().get("regulamentacao_brasil", [])
    out.titulo(f"⚖️  REGULAMENTAÇÃO BRASILEIRA ({len(regs)})")
    for reg in regs:
        out.texto()
        out.nome(f"  📌 {reg.get('aspecto', '—')}")
        out.texto(f"      {reg.get('descricao', '—')}")
        out.texto(f"      Fonte: {reg.get('fonte', '—')} | Status: {reg.get('status', '—')}")
    out.texto()
    out.info("Resumo: CFMV nº 625/95 (especialidade) e MAPA (registro desde 2017).")
    registrar_historico("regulamentacao")


def cmd_glossario(args):
    """Glossário de termos (todos ou um termo específico)."""
    glossario: Dict[str, str] = base_vet().get("glossario", {})
    out.titulo(f"📖 GLOSSÁRIO ({len(glossario)} termos)")
    if args.termo:
        alvo = " ".join(args.termo).lower()
        achados = [(t, d) for t, d in glossario.items() if alvo in t.lower()]
        if not achados:
            out.aviso(f"Termo “{alvo}” não encontrado. Termos disponíveis abaixo.")
            achados = list(glossario.items())
    else:
        achados = list(glossario.items())
    for termo, definicao in achados:
        out.texto()
        out.nome(f"  🔎 {termo}")
        out.texto(f"      {definicao}")
    registrar_historico("glossario", " ".join(args.termo) if args.termo else "")


# ============================================================
# PERGUNTAR (tutor: RAG + LLM local opcional, senão motor de regras)
# ============================================================
SYSTEM_PROMPT_RAG = """Você é o Tutor HomeoVet, um agente EDUCACIONAL de homeopatia veterinária.

REGRAS INVIOLÁVEIS:
1. NUNCA diagnostique, prescreva, recomende doses ou tratamentos para casos individuais.
2. Responda EXCLUSIVAMENTE com o CONTEXTO fornecido abaixo (base educacional do projeto).
3. Se a informação não estiver no contexto, diga: “Informação não disponível na base educacional.”
4. NÃO invente fontes, estudos ou números.
5. Lembre sempre que a eficácia da homeopatia não é sustentada por evidências científicas robustas (Bergh et al., 2021).
6. Se houver indício de emergência ou caso clínico real, oriente procurar um MÉDICO-VETERINÁRIO com urgência.

FORMATO OBRIGATÓRIO DA RESPOSTA (em português do Brasil):
📌 RESPOSTA OBJETIVA — 2 a 4 linhas diretas.
📚 EXPLICAÇÃO DIDÁTICA — desenvolvimento com o contexto disponível.
📖 FONTE — diga se é declaração de fabricante, evidência científica ou conhecimento teórico.
🔬 EVIDÊNCIAS E LIMITAÇÕES — o que a ciência diz (ou a falta de evidência).
⚠️ AVISO — lembrete educacional final (sem diagnóstico/prescrição; consulte veterinário)."""


def _documentos_base() -> List[Tuple[str, str]]:
    """Converte a base vet em documentos recuperáveis para RAG."""
    base = base_vet()
    docs: List[Tuple[str, str]] = []
    for m in base.get("medicamentos", []):
        texto = (
            f"MEDICAMENTO {m.get('nome')} ({m.get('nome_popular')}) — categoria {m.get('categoria')}. "
            f"Origem: {m.get('origem')}. Composição declarada: {m.get('principio_ativo_declarado')}. "
            f"Indicações do fabricante: {m.get('indicacoes_fabricante')}. "
            f"Sintomas homeopáticos: {'; '.join(m.get('sintomas_homeopaticos', []))}. "
            f"Contraindicações: {m.get('contraindicacoes')}. Uso veterinário: {m.get('uso_veterinario')}. "
            f"Tipo de informação: {m.get('tipo_informacao')}. "
            f"Evidência científica: {m.get('evidencia_cientifica')}."
        )
        docs.append((m.get("nome", ""), texto))
    for c in base.get("conceitos_fundamentais", []):
        docs.append((c.get("termo", ""),
                     f"CONCEITO {c.get('termo')}: {c.get('definicao')} "
                     f"Tipo: {c.get('tipo_informacao')}. Evidência: {c.get('evidencia_cientifica')}. "
                     f"Notas: {c.get('notas')}"))
    for e in base.get("evidencias_cientificas", []):
        docs.append((e.get("estudo", ""),
                     f"EVIDÊNCIA CIENTÍFICA — {e.get('estudo')}: {e.get('conclusao')} "
                     f"Nível: {e.get('nivel_evidencia')}. Relevância: {e.get('relevancia')}."))
    for r in base.get("regulamentacao_brasil", []):
        docs.append((r.get("aspecto", ""),
                     f"REGULAMENTAÇÃO — {r.get('aspecto')}: {r.get('descricao')} "
                     f"Status: {r.get('status')}."))
    for termo, definicao in base.get("glossario", {}).items():
        docs.append((termo, f"GLOSSÁRIO — {termo}: {definicao}"))
    return docs


def _recuperar_contexto(pergunta: str, n: int = 6) -> List[str]:
    """Recupera os documentos mais relevantes (embeddings se ativo, senão léxico)."""
    docs = _documentos_base()
    consulta_vec = embedding(pergunta) if ia_disponivel() else None
    if consulta_vec is not None:
        pontuado = [(titulo, cosseno(consulta_vec, embedding(texto) or []), texto)
                    for titulo, texto in docs]
        pontuado.sort(key=lambda t: t[1], reverse=True)
    else:
        p_lower = pergunta.lower()
        pontuado = [(titulo, max(similaridade(p_lower, texto.lower()),
                                 similaridade(p_lower, titulo.lower())), texto)
                    for titulo, texto in docs]
        pontuado.sort(key=lambda t: t[1], reverse=True)
    return [texto for _, _, texto in pontuado[:n]]


def cmd_perguntar(args):
    """Tutor educacional: filtro de segurança → RAG → LLM local (ou motor de regras)."""
    pergunta = " ".join(args.pergunta)

    # 1) Sintomas de emergência — sempre antes de qualquer coisa
    urgente = FiltroSeguranca.verificar_sintomas_urgentes(pergunta)
    if urgente:
        print(urgente)
        print(FiltroSeguranca.gerar_aviso_seguranca())
        registrar_historico("perguntar", "[EMERGÊNCIA]")
        return

    # 2) Tentativa de diagnóstico/prescrição — bloqueio por regras (nunca LLM)
    bloqueio, _ = FiltroSeguranca.detectar_tentativa_diagnostico(pergunta)
    if bloqueio:
        print(FiltroSeguranca.gerar_aviso_seguranca())
        registrar_historico("perguntar", "[BLOQUEIO]")
        return

    # 3) IA local ativa → RAG + LLM com o protocolo pedagógico
    modelo = resolver_modelo_tutor()
    if not args.sem_ia and modelo:
        contexto = _recuperar_contexto(pergunta)
        user = (f"PERGUNTA: {pergunta}\n\n"
                "CONTEXTO DA BASE EDUCACIONAL HomeoVet (use SOMENTE isto):\n"
                + "\n---\n".join(contexto))
        resposta = chat_llm(SYSTEM_PROMPT_RAG, user, modelo)
        if resposta:
            out.titulo(f"🎓 TUTOR HOMEOVET — resposta gerada por IA local ({modelo})")
            out.texto()
            print(resposta)
            out.texto()
            out.aviso("⚠️  Resposta EDUCACIONAL gerada com base restrita à base do projeto.")
            out.texto("    Sempre confirme com literatura e um médico-veterinário.")
            registrar_historico("perguntar", f"[IA local: {modelo}] {pergunta}")
            return
        out.aviso("⚠️  LLM local indisponível agora — caindo para o motor de regras.")

    # 4) Sem IA → motor de regras original do tutor (fonte única de verdade)
    tutor = TutorHomeopatiaVet()
    print(tutor.processar_consulta(pergunta))
    registrar_historico("perguntar", f"[regras] {pergunta}")


# ============================================================
# QUIZ (15 perguntas derivadas da base educacional)
# ============================================================
QUIZ = [
    {
        "pergunta": "Qual resolução reconheceu a Homeopatia Veterinária como especialidade pelo CFMV?",
        "opcoes": ["Resolução CFMV nº 625/95", "Resolução CFMV nº 1.000/2010",
                   "Ofício-Circular MAPA nº 8/2017", "RDC ANVISA nº 26/2014"],
        "correta": 0,
        "explicacao": "A Resolução CFMV nº 625, de 1995, reconheceu a homeopatia veterinária como especialidade.",
    },
    {
        "pergunta": "Em que ano a AMVHB foi habilitada a realizar provas de título de especialista?",
        "opcoes": ["1995", "2000", "2010", "2017"],
        "correta": 1,
        "explicacao": "A AMVHB foi habilitada em 2000, conforme a base regulatória do projeto.",
    },
    {
        "pergunta": "Na revisão sistemática de Bergh et al. (2021), quantos estudos foram elegíveis entre 982 analisados?",
        "opcoes": ["982", "120", "42", "9"],
        "correta": 2,
        "explicacao": "Dos 982 estudos analisados, apenas 42 foram elegíveis — e com risco de viés alto na maioria.",
    },
    {
        "pergunta": "Quem propôs a Lei do Semelhante (Similia similibus curentur) e em que século?",
        "opcoes": ["Paracelso, século XVI", "Samuel Hahnemann, século XVIII",
                   "Hippocrates, século V a.C.", "Constantin Hering, século XIX"],
        "correta": 1,
        "explicacao": "A Lei do Semelhante foi proposta por Samuel Hahnemann no século XVIII. Não comprovada pelo método científico.",
    },
    {
        "pergunta": "O que significa “Similia similibus curentur”?",
        "opcoes": ["“O semelhante cura o semelhante”", "“A dose faz o veneno”",
                   "“Semelhante trata diferente”", "“Dilua para curar”"],
        "correta": 0,
        "explicacao": "É o princípio fundador: substância que causa sintomas no sadio trataria sintomas semelhantes no doente.",
    },
    {
        "pergunta": "Qual medicamento é tradicionalmente associado a traumas, contusões e hematomas?",
        "opcoes": ["Nux Vomica", "Sepia", "Arnica Montana", "Thuja Occidentalis"],
        "correta": 2,
        "explicacao": "Arnica Montana é o medicamento traumático clássico da literatura homeopática (declaração de fabricante, não evidência comprovada).",
    },
    {
        "pergunta": "Qual é a contraindicação clássica do uso EXTERNO da Arnica?",
        "opcoes": ["Pele oleosa", "Feridas abertas", "Exposição ao sol", "Uso em equinos"],
        "correta": 1,
        "explicacao": "Uso externo em feridas abertas é contraindicado; a planta bruta é tóxica.",
    },
    {
        "pergunta": "Desde quando produtos homeopáticos de uso veterinário requerem registro no MAPA?",
        "opcoes": ["1995", "2000", "2017", "2021"],
        "correta": 2,
        "explicacao": "A exigência de registro no MAPA aplica-se desde 2017 (Ofício-Circular nº 8/2017 e normativa correlata).",
    },
    {
        "pergunta": "O que é a escala CH (Centesimal Hahnemanniana)?",
        "opcoes": ["Diluição de 1 parte em 9 partes de veículo",
                   "Diluição de 1 parte em 99 partes de veículo",
                   "Escala de potências decimais de Hering",
                   "Forma de apresentação em glóbulos"],
        "correta": 1,
        "explicacao": "CH: 1 parte da substância em 99 partes de veículo, seguida de sucussão (dinamização).",
    },
    {
        "pergunta": "Na escala decimal (DH), a proporção de diluição é:",
        "opcoes": ["1:9", "1:99", "1:100", "1:1000"],
        "correta": 0,
        "explicacao": "DH (Decimal de Hering) dilui 1 parte da substância em 9 partes de veículo a cada dinamização.",
    },
    {
        "pergunta": "O que significa ultrapassar o “limite de Avogadro” em potências homeopáticas?",
        "opcoes": ["A substância fica mais concentrada", "O medicamento vira tóxico",
                   "Não restam moléculas detectáveis da substância original",
                   "A diluição passa a exigir receita"],
        "correta": 2,
        "explicacao": "Acima de ~12 CH, a diluição excede o limite de Avogadro: estatisticamente não há moléculas da substância original.",
    },
    {
        "pergunta": "Na base do projeto, qual é a categoria do Aconitum Napellus?",
        "opcoes": ["Traumatologia", "Febre / Pânico", "Urinário / Queimaduras", "Pele / Verrugas"],
        "correta": 1,
        "explicacao": "Aconitum Napellus está mapeado como “Febre / Pânico” — quadros agudos de início súbito na literatura homeopática.",
    },
    {
        "pergunta": "Na base do projeto, qual é a categoria do Cantharis?",
        "opcoes": ["Urinário / Queimaduras", "Digestivo / Comportamental",
                   "Feminino / Constitucional", "Reumatismo / Dermatite"],
        "correta": 0,
        "explicacao": "Cantharis está mapeado como “Urinário / Queimaduras”.",
    },
    {
        "pergunta": "Segundo as revisões sistemáticas citadas no projeto, o nível de evidência da homeopatia veterinária é:",
        "opcoes": ["Alto — eficácia comprovada", "Moderado — funciona em algumas espécies",
                   "Insuficiente / de baixa qualidade metodológica", "Conclusivo apenas para bovinos"],
        "correta": 2,
        "explicacao": "Bergh et al. (2021): evidência científica não é forte o suficiente para definir eficácia clínica.",
    },
    {
        "pergunta": "O que o Tutor HomeoVet NUNCA faz?",
        "opcoes": ["Citar fontes", "Explicar conceitos teóricos",
                   "Diagnosticar, prescrever ou recomendar doses", "Mencionar limitações de evidência"],
        "correta": 2,
        "explicacao": "O projeto é estritamente educacional: diagnóstico, prescrição e dose são bloqueados por filtro ativo.",
    },
]


def cmd_quiz(_args):
    """Quiz interativo de 15 perguntas com registro de progresso."""
    out.titulo("🎯 QUIZ HOMEOVET — 15 perguntas (uso educacional)")
    out.texto()
    perguntas = QUIZ[:]
    if not args_sem_ia_shuffle_disabled():
        random.shuffle(perguntas)

    acertos = 0
    detalhes = []
    for i, q in enumerate(perguntas, 1):
        out.nome(f"\n[{i:02d}/15] {q['pergunta']}")
        for j, opcao in enumerate(q["opcoes"]):
            out.texto(f"    ({j + 1}) {opcao}")
        try:
            resposta = input("    👉 Sua resposta (1-4): ").strip()
        except EOFError:
            out.aviso("\nQuiz interrompido — nada foi registrado.")
            return
        if resposta == str(q["correta"] + 1):
            acertos += 1
            out.ok(f"    ✅ Correto! {q['explicacao']}")
            detalhes.append({"pergunta": q["pergunta"], "acerto": True})
        else:
            correta_txt = q["opcoes"][q["correta"]]
            out.erro(f"    ❌ Incorreto. Resposta certa: ({q['correta'] + 1}) {correta_txt}")
            out.texto(f"       {q['explicacao']}")
            detalhes.append({"pergunta": q["pergunta"], "acerto": False})

    percentual = round(100.0 * acertos / len(perguntas), 1)
    out.texto()
    out.titulo(f"🏁 RESULTADO: {acertos}/{len(perguntas)} ({percentual:.1f}%)")
    if percentual >= 80:
        out.ok("🎉 Excelente domínio do conteúdo educacional!")
    elif percentual >= 50:
        out.info("👍 Bom caminho — revise os temas errados com `glossario` e `evidencias`.")
    else:
        out.info("📚 Vale revisar: perguntar, evidencias, regulamentacao e glossario.")

    # Registra progresso
    progresso = _carregar_runtime(PROGRESSO_FILE, {"quizzes": []})
    if not isinstance(progresso, dict):
        progresso = {"quizzes": []}
    progresso.setdefault("quizzes", []).append({
        "data": agora(), "acertos": acertos, "total": len(perguntas),
        "percentual": percentual, "detalhes": detalhes,
    })
    _salvar_runtime(PROGRESSO_FILE, progresso)
    registrar_historico("quiz", f"{acertos}/{len(perguntas)}")
    out.texto()
    out.info("Progresso salvo em runtime/progresso.json")


def args_sem_ia_shuffle_disabled() -> bool:
    """Quiz mantém ordem estável quando --sem-ia (reprodutibilidade offline)."""
    return not USO_IA


def cmd_progresso(_args):
    """Mostra progresso de aprendizado (quiz + histórico)."""
    progresso = _carregar_runtime(PROGRESSO_FILE, {"quizzes": []})
    quizzes = progresso.get("quizzes", []) if isinstance(progresso, dict) else []
    historico = _carregar_runtime(HISTORICO_FILE, [])
    out.titulo("📊 PROGRESSO DE APRENDIZADO")
    out.texto()
    if not quizzes:
        out.info("Nenhum quiz registrado ainda. Rode: py homeovet_cli.py quiz")
    else:
        total = sum(q["total"] for q in quizzes)
        acertos = sum(q["acertos"] for q in quizzes)
        out.info(f"  Quizzes realizados: {len(quizzes)}")
        out.info(f"  Acumulado: {acertos}/{total} ({100.0 * acertos / max(total, 1):.1f}%)")
        out.texto()
        for q in quizzes[-5:]:
            out.texto(f"  • {q['data']} — {q['acertos']}/{q['total']} ({q.get('percentual', 0):.1f}%)")
    out.texto()
    out.info(f"  Comandos registrados no histórico: {len(historico)}")
    if historico:
        for h in historico[-5:]:
            out.texto(f"  • {h['data']} — {h['comando']} {h.get('detalhe', '')[:60]}")
    registrar_historico("progresso")


# ============================================================
# FAVORITOS / ANOTAÇÕES / HISTÓRICO
# ============================================================
def cmd_favoritos(args):
    """Gerencia favoritos: add|rm|ls."""
    favoritos = _carregar_runtime(FAVORITOS_FILE, [])
    if args.acao == "ls":
        out.titulo(f"⭐ FAVORITOS ({len(favoritos)})")
        busca = MotorBusca(base_vet())
        for nome in favoritos:
            med = next((m for m in busca.listar_medicamentos()
                        if m["nome"].lower() == nome.lower()), None)
            if med:
                out.nome(f"  • {med['nome']} — {med.get('categoria', '—')}")
            else:
                out.texto(f"  • {nome} (fora da base veterinária)")
    elif args.acao == "add":
        nome = " ".join(args.nome)
        if nome.lower() in [f.lower() for f in favoritos]:
            out.info("Já está nos favoritos.")
        else:
            favoritos.append(nome)
            _salvar_runtime(FAVORITOS_FILE, favoritos)
            out.ok(f"⭐ Adicionado: {nome}")
    elif args.acao == "rm":
        nome = " ".join(args.nome).lower()
        favoritos = [f for f in favoritos if f.lower() != nome]
        _salvar_runtime(FAVORITOS_FILE, favoritos)
        out.ok(f"Removido (se existia): {nome}")
    registrar_historico("favoritos", args.acao)


def cmd_anotacoes(args):
    """Gerencia anotações: add|ls|rm."""
    anotacoes = _carregar_runtime(ANOTACOES_FILE, [])
    if args.acao == "ls":
        out.titulo(f"📝 ANOTAÇÕES ({len(anotacoes)})")
        for a in anotacoes:
            out.nome(f"  [{a['id']}] {a['data']}")
            out.texto(f"      {a['texto']}")
    elif args.acao == "add":
        texto = " ".join(args.texto)
        proximo_id = (max((a["id"] for a in anotacoes), default=0) + 1)
        anotacoes.append({"id": proximo_id, "data": agora(), "texto": texto})
        _salvar_runtime(ANOTACOES_FILE, anotacoes)
        out.ok(f"📝 Anotação #{proximo_id} salva.")
    elif args.acao == "rm":
        anotacoes = [a for a in anotacoes if a["id"] != args.id]
        _salvar_runtime(ANOTACOES_FILE, anotacoes)
        out.ok(f"Removida anotação #{args.id} (se existia).")
    registrar_historico("anotacoes", args.acao)


def cmd_historico(_args):
    """Mostra o histórico de comandos da CLI."""
    historico = _carregar_runtime(HISTORICO_FILE, [])
    out.titulo(f"🧾 HISTÓRICO ({len(historico)} registros)")
    for h in historico[-20:]:
        out.texto(f"  • {h['data']} — {h['comando']} {h.get('detalhe', '')[:80]}")


# ============================================================
# EXPORTAÇÃO
# ============================================================
def cmd_exportar(args):
    """Exporta favoritos, anotações, progresso e fichas em Markdown ou JSON."""
    favoritos = _carregar_runtime(FAVORITOS_FILE, [])
    anotacoes = _carregar_runtime(ANOTACOES_FILE, [])
    progresso = _carregar_runtime(PROGRESSO_FILE, {"quizzes": []})
    medicamentos = base_vet().get("medicamentos", [])
    fichas_favoritas = [m for m in medicamentos
                        if m["nome"].lower() in [f.lower() for f in favoritos]]

    saida = args.saida or (
        os.path.join(BASE_DIR, "homeovet_export.json")
        if args.formato == "json" else EXPORT_DEFAULT
    )

    if args.formato == "json":
        pacote = {
            "gerado_em": agora(),
            "projeto": f"HomeoVet CLI v{VERSÃO}",
            "favoritos": favoritos,
            "anotacoes": anotacoes,
            "progresso": progresso,
            "fichas_favoritas": fichas_favoritas,
        }
        with open(saida, "w", encoding="utf-8") as f:
            json.dump(pacote, f, ensure_ascii=False, indent=2)
    else:
        linhas_md = [
            f"# 📦 Exportação HomeoVet — {agora()}",
            "",
            f"Projeto: HomeoVet CLI v{VERSÃO} (uso estritamente educacional)",
            "",
            "## ⭐ Favoritos",
        ]
        linhas_md += [f"- {nome}" for nome in favoritos] or ["- (nenhum)"]
        linhas_md += ["", "## 📝 Anotações"]
        if anotacoes:
            linhas_md += [f"- **[{a['id']}] {a['data']}** — {a['texto']}" for a in anotacoes]
        else:
            linhas_md += ["- (nenhuma)"]
        quizzes = progresso.get("quizzes", []) if isinstance(progresso, dict) else []
        linhas_md += ["", "## 📊 Progresso (quiz)"]
        if quizzes:
            for q in quizzes:
                linhas_md.append(f"- {q['data']} — {q['acertos']}/{q['total']} ({q.get('percentual', 0):.1f}%)")
        else:
            linhas_md.append("- (nenhum quiz registrado)")
        if fichas_favoritas:
            linhas_md += ["", "## 💊 Fichas dos favoritos"]
            for m in fichas_favoritas:
                linhas_md += [
                    "", f"### {m['nome']} ({m.get('nome_popular', '')})",
                    f"- Categoria: {m.get('categoria', '—')}",
                    f"- Origem: {m.get('origem', '—')}",
                    f"- Indicações (fabricante): {m.get('indicacoes_fabricante', '—')}",
                    f"- Contraindicações: {m.get('contraindicacoes', '—')}",
                    f"- Evidência científica: {m.get('evidencia_cientifica', '—')}",
                ]
        linhas_md += ["", "---",
                      "⚠️ Conteúdo EDUCACIONAL — não substitui médico-veterinário.", ""]
        with open(saida, "w", encoding="utf-8") as f:
            f.write("\n".join(linhas_md))

    out.ok(f"📦 Exportado para: {saida} (formato {args.formato})")
    registrar_historico("exportar", saida)


# ============================================================
# ARGPARSE — CLI
# ============================================================
def montar_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="homeovet_cli",
        description="💻 HomeoVet CLI v%s — fichas, evidências, regulamentação, "
                    "glossário, quiz, memória local e tutor com IA local opcional "
                    "(Ollama). USO ESTRITAMENTE EDUCACIONAL." % VERSÃO,
        epilog="Exemplos:\n"
               "  py homeovet_cli.py ficha \"Arnica Montana\"\n"
               "  py homeovet_cli.py buscar \"contusão queda dor muscular\"\n"
               "  py homeovet_cli.py perguntar \"O que é a Lei do Semelhante?\"\n"
               "  py homeovet_cli.py quiz\n"
               "  py homeovet_cli.py exportar --formato md\n",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--sem-ia", action="store_true",
                        help="desativa o modo IA local (força Python puro)")
    sub = parser.add_subparsers(dest="comando", metavar="COMANDO")

    p = sub.add_parser("ficha", help="ficha técnica de um medicamento veterinário")
    p.add_argument("nome", nargs="+", help="nome do medicamento (ex.: Arnica Montana)")
    p.set_defaults(func=cmd_ficha)

    p = sub.add_parser("buscar", help="busca por sintomas (humano + veterinário)")
    p.add_argument("termos", nargs="+", help="sintomas (livre)")
    p.add_argument("--top", type=int, default=5, help="resultados por base (padrão 5)")
    p.add_argument("--vet", action="store_true", help="apenas base veterinária")
    p.add_argument("--humano", action="store_true", help="apenas base humana")
    p.add_argument("--sem-ia", action="store_true", help="força busca léxica")
    p.set_defaults(func=cmd_buscar)

    p = sub.add_parser("medicamentos", help="lista os 12 medicamentos veterinários")
    p.set_defaults(func=cmd_medicamentos)

    p = sub.add_parser("evidencias", help="evidências científicas")
    p.add_argument("termo", nargs="*", help="filtra por termo (opcional)")
    p.set_defaults(func=cmd_evidencias)

    p = sub.add_parser("regulamentacao", help="regulamentação brasileira (CFMV, MAPA)")
    p.set_defaults(func=cmd_regulamentacao)

    p = sub.add_parser("glossario", help="glossário de termos homeopáticos")
    p.add_argument("termo", nargs="*", help="busca um termo (opcional)")
    p.set_defaults(func=cmd_glossario)

    p = sub.add_parser("perguntar", help="tutor educacional (RAG + IA local opcional)")
    p.add_argument("pergunta", nargs="+", help="a pergunta educacional")
    p.add_argument("--sem-ia", action="store_true",
                   help="força o motor de regras (sem LLM)")
    p.set_defaults(func=cmd_perguntar)

    p = sub.add_parser("quiz", help="quiz de 15 perguntas com progresso")
    p.set_defaults(func=cmd_quiz)

    p = sub.add_parser("progresso", help="estatísticas de aprendizado")
    p.set_defaults(func=cmd_progresso)

    p = sub.add_parser("favoritos", help="favoritos: add | rm | ls")
    p.add_argument("acao", choices=["add", "rm", "ls"])
    p.add_argument("nome", nargs="*", help="nome do medicamento (add/rm)")
    p.set_defaults(func=cmd_favoritos)

    p = sub.add_parser("anotacoes", help="anotações: add | ls | rm ID")
    p.add_argument("acao", choices=["add", "ls", "rm"])
    p.add_argument("texto", nargs="*", help="texto (add) ou vazio (ls)")
    p.add_argument("--id", type=int, default=0, help="id da anotação (rm)")
    p.set_defaults(func=cmd_anotacoes)

    p = sub.add_parser("historico", help="histórico de comandos da CLI")
    p.set_defaults(func=cmd_historico)

    p = sub.add_parser("exportar", help="exporta favoritos, anotações, progresso e fichas")
    p.add_argument("--formato", choices=["md", "json"], default="md")
    p.add_argument("--saida", default=None, help="caminho do arquivo de saída")
    p.set_defaults(func=cmd_exportar)

    return parser


def main():
    global USO_IA
    parser = montar_parser()
    args = parser.parse_args()

    if getattr(args, "sem_ia", False):
        USO_IA = False

    if not hasattr(args, "func"):
        parser.print_help()
        return

    args.func(args)


if __name__ == "__main__":
    main()