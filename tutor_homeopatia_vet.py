#!/usr/bin/env python3
"""
🎓 TUTOR IA - HOMEOPATIA VETERINÁRIA
Agente educacional com memória de aprendizagem
Uso estritamente educacional - NÃO substitui orientação médico-veterinária

Restrições éticas rigorosas:
- NÃO diagnostica
- NÃO prescreve
- NÃO recomenda tratamentos
- NÃO ajusta doses
- NÃO combina produtos
- NÃO sugere substituir acompanhamento veterinário
"""

import json
import os
import re
from datetime import datetime
from difflib import SequenceMatcher
from typing import List, Dict, Optional, Tuple

# ============================================================
# CONFIGURAÇÕES
# ============================================================
DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
BASE_FILE = os.path.join(DATA_DIR, "tutor_homeopatia_vet.json")
MEMORIA_FILE = os.path.join(DATA_DIR, "memoria_aprendizado.json")
HISTORICO_FILE = os.path.join(DATA_DIR, "historico_conversas.json")

# Palavras-chave de bloqueio - detectam tentativas de diagnóstico/prescrição
PALAVRAS_BLOQUEIO_DIAGNOSTICO = [
    "meu cão tem", "meu gato tem", "meu animal tem", "está doente",
    "diagnostique", "diagnóstico", "qual remédio devo dar", "qual dose",
    "quanto devo dar", "posso dar", "devo usar", "tratamento para",
    "cura para", "melhor remédio para", "indique um remédio",
    "receita para", "prescreva", "prescrição", "dosagem para",
    "combine", "misture", "substitua", "em vez de", "troque"
]

# ============================================================
# FUNÇÕES UTILITÁRIAS
# ============================================================
def similaridade(a: str, b: str) -> float:
    """Calcula similaridade entre strings."""
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()


def limpar_tela():
    """Limpa o terminal."""
    os.system("cls" if os.name == "nt" else "clear")


def carregar_json(caminho: str) -> dict:
    """Carrega arquivo JSON com tratamento de erro."""
    try:
        with open(caminho, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def salvar_json(caminho: str, dados: dict):
    """Salva dados em arquivo JSON."""
    os.makedirs(os.path.dirname(caminho), exist_ok=True)
    with open(caminho, "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)


# ============================================================
# SISTEMA DE MEMÓRIA DE APRENDIZAGEM
# ============================================================
class MemoriaAprendizado:
    """Gerencia a memória persistente de aprendizado do tutor."""

    def __init__(self):
        self.dados = carregar_json(MEMORIA_FILE)
        if not self.dados:
            self.dados = {
                "sessoes": 0,
                "topicos_mais_consultados": {},
                "feedback_usuarios": [],
                "dificuldades_comuns": [],
                "ultima_sessao": None
            }

    def registrar_consulta(self, topico: str):
        """Registra que um tópico foi consultado."""
        self.dados["sessoes"] += 1
        self.dados["topicos_mais_consultados"][topico] = \
            self.dados["topicos_mais_consultados"].get(topico, 0) + 1
        self.dados["ultima_sessao"] = datetime.now().isoformat()
        self._salvar()

    def registrar_feedback(self, pergunta: str, util: bool, comentario: str = ""):
        """Registra feedback do usuário sobre a utilidade da resposta."""
        self.dados["feedback_usuarios"].append({
            "data": datetime.now().isoformat(),
            "pergunta": pergunta,
            "util": util,
            "comentario": comentario
        })
        self._salvar()

    def registrar_dificuldade(self, conceito: str):
        """Registra que um conceito gerou dificuldade."""
        if conceito not in self.dados["dificuldades_comuns"]:
            self.dados["dificuldades_comuns"].append(conceito)
        self._salvar()

    def topicos_populares(self, n: int = 5) -> List[Tuple[str, int]]:
        """Retorna os tópicos mais consultados."""
        ordenados = sorted(
            self.dados["topicos_mais_consultados"].items(),
            key=lambda x: x[1], reverse=True
        )
        return ordenados[:n]

    def _salvar(self):
        salvar_json(MEMORIA_FILE, self.dados)


# ============================================================
# SISTEMA DE HISTÓRICO DE CONVERSAS
# ============================================================
class HistoricoConversas:
    """Mantém histórico de conversas para contexto."""

    def __init__(self, limite: int = 10):
        self.limite = limite
        self.dados = carregar_json(HISTORICO_FILE)
        if not self.dados:
            self.dados = {"conversas": []}

    def adicionar(self, papel: str, conteudo: str):
        """Adiciona uma mensagem ao histórico."""
        self.dados["conversas"].append({
            "data": datetime.now().isoformat(),
            "papel": papel,
            "conteudo": conteudo
        })
        # Mantém apenas as últimas N mensagens
        self.dados["conversas"] = self.dados["conversas"][-self.limite:]
        salvar_json(HISTORICO_FILE, self.dados)

    def obter_contexto(self) -> str:
        """Retorna o contexto recente como string."""
        if not self.dados["conversas"]:
            return ""
        linhas = []
        for c in self.dados["conversas"][-5:]:
            linhas.append(f"{c['papel']}: {c['conteudo']}")
        return "\n".join(linhas)


# ============================================================
# FILTRO DE SEGURANÇA ÉTICA
# ============================================================
class FiltroSeguranca:
    """Filtra consultas para evitar diagnóstico e prescrição."""

    @staticmethod
    def detectar_tentativa_diagnostico(texto: str) -> Tuple[bool, List[str]]:
        """Detecta se o usuário está tentando obter diagnóstico/prescrição."""
        texto_lower = texto.lower()
        palavras_detectadas = []
        for palavra in PALAVRAS_BLOQUEIO_DIAGNOSTICO:
            if palavra in texto_lower:
                palavras_detectadas.append(palavra)
        return len(palavras_detectadas) > 0, palavras_detectadas

    @staticmethod
    def gerar_aviso_seguranca() -> str:
        """Gera aviso de segurança padrão."""
        return """
⚠️  AVISO DE SEGURANÇA
────────────────────────────────────────
Sou um tutor EDUCACIONAL sobre homeopatia veterinária.

NÃO posso:
  ❌ Diagnosticar doenças
  ❌ Prescrever medicamentos
  ❌ Recomendar doses
  ❌ Substituir acompanhamento veterinário
  ❌ Indicar tratamentos para casos individuais

SE seu animal apresenta sintomas:
  👉 Consulte um MÉDICO-VETERINÁRIO
  👉 Em emergências, procure atendimento imediato

Posso ajudar com:
  ✅ Conceitos teóricos de homeopatia
  ✅ Terminologia e composições
  ✅ Legislação e regulamentação
  ✅ Evidências científicas disponíveis
  ✅ História e princípios fundamentais
────────────────────────────────────────
"""

    @staticmethod
    def verificar_sintomas_urgentes(texto: str) -> Optional[str]:
        """Verifica se há menção a sintomas que requerem atenção veterinária urgente."""
        sintomas_urgentes = [
            "dificuldade para respirar", "respiração ofegante", "cianose",
            "desmaio", "convulsão", "sangramento", "hemorragia",
            "vômito persistente", "diarreia com sangue", "não urina",
            "abdome distendido", "traumatismo", "fratura", "envenenamento",
            "intoxicação", "paralisia", "não se move", "inconsciente"
        ]
        texto_lower = texto.lower()
        for sintoma in sintomas_urgentes:
            if sintoma in texto_lower:
                return f"""
🚨 ATENÇÃO - POSSÍVEL EMERGÊNCIA
────────────────────────────────────────
Detectei menção a: "{sintoma}"

Isso pode indicar uma SITUAÇÃO DE URGÊNCIA VETERINÁRIA.

AÇÕES IMEDIATAS:
  1. Procure um MÉDICO-VETERINÁRIO URGENTEMENTE
  2. Se não houver atendimento imediato, procure a clínica 24h mais próxima
  3. NÃO espere pela resposta de um tutor educacional

A homeopatia NÃO substitui o atendimento de emergência.
────────────────────────────────────────
"""
        return None


# ============================================================
# MOTOR DE BUSCA NA BASE DE DADOS
# ============================================================
class MotorBusca:
    """Busca informações na base de dados educacional."""

    def __init__(self, base_dados: dict):
        self.base = base_dados

    def buscar_medicamento(self, termo: str) -> Optional[Dict]:
        """Busca medicamento pelo nome ou ID."""
        medicamentos = self.base.get("medicamentos", [])
        termo_lower = termo.lower()

        melhor_match = None
        melhor_score = 0.0

        for med in medicamentos:
            nomes = [med.get("nome", "").lower(),
                     med.get("nome_popular", "").lower(),
                     med.get("id", "").lower()]
            for nome in nomes:
                score = similaridade(termo_lower, nome)
                if score > melhor_score and score > 0.4:
                    melhor_score = score
                    melhor_match = med

        return melhor_match

    def buscar_conceito(self, termo: str) -> Optional[Dict]:
        """Busca conceito fundamental."""
        conceitos = self.base.get("conceitos_fundamentais", [])
        termo_lower = termo.lower()

        for conceito in conceitos:
            if similaridade(termo_lower, conceito.get("termo", "").lower()) > 0.5:
                return conceito
        return None

    def buscar_regulamentacao(self, termo: str) -> List[Dict]:
        """Busca informações regulatórias."""
        regs = self.base.get("regulamentacao_brasil", [])
        termo_lower = termo.lower()
        resultados = []

        for reg in regs:
            texto = f"{reg.get('aspecto', '')} {reg.get('descricao', '')}".lower()
            if similaridade(termo_lower, texto) > 0.3 or termo_lower in texto:
                resultados.append(reg)
        return resultados

    def buscar_evidencia(self, termo: str) -> List[Dict]:
        """Busca evidências científicas."""
        evids = self.base.get("evidencias_cientificas", [])
        termo_lower = termo.lower()
        resultados = []

        for ev in evids:
            texto = f"{ev.get('estudo', '')} {ev.get('conclusao', '')}".lower()
            if termo_lower in texto or similaridade(termo_lower, texto) > 0.2:
                resultados.append(ev)
        return resultados

    def buscar_no_glossario(self, termo: str) -> Optional[Tuple[str, str]]:
        """Busca termo no glossário."""
        glossario = self.base.get("glossario", {})
        termo_lower = termo.lower()

        for chave, valor in glossario.items():
            if termo_lower in chave.lower() or similaridade(termo_lower, chave.lower()) > 0.6:
                return (chave, valor)
        return None

    def listar_medicamentos(self) -> List[Dict]:
        """Retorna lista de todos os medicamentos."""
        return self.base.get("medicamentos", [])


# ============================================================
# FORMATADOR DE RESPOSTAS EDUCACIONAIS
# ============================================================
class FormatadorRespostas:
    """Formata respostas no padrão educacional exigido."""

    @staticmethod
    def formatar_resposta_objetiva(conteudo: str) -> str:
        return f"\n📌 RESPOSTA OBJETIVA\n{'─' * 50}\n{conteudo}\n"

    @staticmethod
    def formatar_explicacao_didatica(conteudo: str) -> str:
        return f"\n📚 EXPLICAÇÃO DIDÁTICA\n{'─' * 50}\n{conteudo}\n"

    @staticmethod
    def formatar_fonte(tipo: str, nome: str, url: str = "") -> str:
        url_str = f"\n   URL: {url}" if url else ""
        return f"\n📖 INFORMAÇÃO DA FONTE\n{'─' * 50}\n   Tipo: {tipo}\n   Fonte: {nome}{url_str}\n"

    @staticmethod
    def formatar_evidencias(evidencia: str, limitacoes: str) -> str:
        return f"\n🔬 EVIDÊNCIAS E LIMITAÇÕES\n{'─' * 50}\n   Evidência: {evidencia}\n   Limitações: {limitacoes}\n"

    @staticmethod
    def formatar_perguntas_revisao(perguntas: List[str]) -> str:
        if not perguntas:
            return ""
        texto = f"\n❓ PERGUNTAS PARA REVISÃO\n{'─' * 50}\n"
        for i, p in enumerate(perguntas[:3], 1):
            texto += f"   {i}. {p}\n"
        return texto

    @staticmethod
    def formatar_aviso_seguranca(mensagem: str) -> str:
        return f"\n⚠️  AVISO DE SEGURANÇA\n{'─' * 50}\n{mensagem}\n"


# ============================================================
# TUTOR IA PRINCIPAL
# ============================================================
class TutorHomeopatiaVet:
    """Agente tutor de homeopatia veterinária com memória."""

    def __init__(self):
        self.base = carregar_json(BASE_FILE)
        self.memoria = MemoriaAprendizado()
        self.historico = HistoricoConversas()
        self.busca = MotorBusca(self.base)
        self.formatador = FormatadorRespostas()
        self.filtro = FiltroSeguranca()

        # Verifica se a base carregou
        if not self.base:
            print("❌ ERRO CRÍTICO: Base de dados não encontrada!")
            print(f"   Esperado: {BASE_FILE}")
            exit(1)

    def processar_consulta(self, pergunta: str) -> str:
        """Processa uma consulta do usuário e retorna resposta formatada."""
        # Registra no histórico
        self.historico.adicionar("usuário", pergunta)

        # 1. Verifica sintomas urgentes
        aviso_urgente = self.filtro.verificar_sintomas_urgentes(pergunta)
        if aviso_urgente:
            self.historico.adicionar("tutor", "[AVISO DE EMERGÊNCIA]")
            return aviso_urgente + "\n" + self.filtro.gerar_aviso_seguranca()

        # 2. Verifica tentativa de diagnóstico/prescrição
        eh_diagnostico, palavras = self.filtro.detectar_tentativa_diagnostico(pergunta)
        if eh_diagnostico:
            resposta = self._resposta_bloqueio_diagnostico(palavras)
            self.historico.adicionar("tutor", "[BLOQUEIO - TENTATIVA DE DIAGNÓSTICO]")
            return resposta

        # 3. Identifica intenção e busca resposta
        resposta = self._identificar_e_responder(pergunta)

        # Registra consulta na memória
        topico = self._extrair_topico(pergunta)
        self.memoria.registrar_consulta(topico)
        self.historico.adicionar("tutor", resposta[:200] + "...")

        return resposta

    def _identificar_e_responder(self, pergunta: str) -> str:
        """Identifica o tipo de pergunta e gera resposta apropriada."""
        p_lower = pergunta.lower()

        # Busca por medicamento específico
        med = self.busca.buscar_medicamento(pergunta)
        if med:
            return self._resposta_medicamento(med)

        # Busca por conceito
        conceito = self.busca.buscar_conceito(pergunta)
        if conceito:
            return self._resposta_conceito(conceito)

        # Busca no glossário
        glossario = self.busca.buscar_no_glossario(pergunta)
        if glossario:
            return self._resposta_glossario(glossario)

        # Perguntas sobre regulamentação
        if any(p in p_lower for p in ["regulamentação", "lei", "resolução", "mapa", "cfmv", "registro", "legal"]):
            return self._resposta_regulamentacao(pergunta)

        # Perguntas sobre evidências científicas
        if any(p in p_lower for p in ["evidência", "ciência", "estudo", "funciona", "prova", "revisão", "sistemática"]):
            return self._resposta_evidencias(pergunta)

        # Perguntas sobre composições
        if any(p in p_lower for p in ["composição", "princípio ativo", "o que é", "origem", "de onde vem"]):
            return self._resposta_composicao(pergunta)

        # Perguntas sobre potências
        if any(p in p_lower for p in ["potência", "ch", "dh", "diluição", "dinamização", "centesimal"]):
            return self._resposta_potencias()

        # Pergunta genérica - lista opções
        return self._resposta_generica()

    def _resposta_medicamento(self, med: Dict) -> str:
        """Formata resposta sobre medicamento homeopático."""
        resposta = ""

        # Resposta objetiva
        obj = f"""{med['nome']} ({med['nome_popular']})
Origem: {med['origem']}
Categoria: {med['categoria']}
Potências comuns: {', '.join(med.get('potencias_comuns', []))}
Apresentações: {med.get('apresentacoes', 'N/A')}"""
        resposta += self.formatador.formatar_resposta_objetiva(obj)

        # Explicação didática
        didatica = f"""O medicamento homeopático {med['nome']} é preparado a partir de {med['origem']}.

Composição declarada: {med.get('principio_ativo_declarado', 'N/A')}

Como funciona segundo a teoria homeopática:
  → Baseia-se no princípio do semelhante (Similia similibus curentur)
  → A substância, em doses infinitesimais, supostamente estimularia a 'força vital' a restaurar o equilíbrio
  → A escolha depende da repertorização (correspondência entre sintomas do paciente e patogenesia do remédio)

Conservação: {med.get('conservacao', 'N/A')}

IMPORTANTE: O princípio ativo em potências acima de 12 CH está além do limite de Avogadro, ou seja, não há moléculas detectáveis da substância original."""
        resposta += self.formatador.formatar_explicacao_didatica(didatica)

        # Fonte
        fonte_id = med.get("fonte_informacao", "")
        fonte_nome = self._resolver_fonte(fonte_id)
        resposta += self.formatador.formatar_fonte(
            med.get("tipo_informacao", "Não classificado"),
            fonte_nome
        )

        # Evidências e limitações
        evidencia = med.get("evidencia_cientifica", "Não disponível")
        limitacoes = "Não há ensaios clínicos controlados robustos em medicina veterinária. A eficácia não foi comprovada pelo método científico."
        resposta += self.formatador.formatar_evidencias(evidencia, limitacoes)

        # Perguntas para revisão
        perguntas = [
            "Por que potências acima de 12 CH não contêm moléculas da substância original?",
            "Qual a diferença entre sintomas homeopáticos e indicações farmacológicas?",
            f"Por que a substância bruta de {med['nome']} é tóxica, mas é usada em homeopatia?"
        ]
        resposta += self.formatador.formatar_perguntas_revisao(perguntas)

        # Aviso de segurança
        aviso = f"""Este medicamento é mencionado apenas para fins EDUCACIONAIS.

⚠️  NÃO prescrevo, NÃO indico doses, NÃO recomendo uso individual.
⚠️  A eficácia de {med['nome']} em animais NÃO foi comprovada cientificamente.
⚠️  Para qualquer decisão clínica, consulte um MÉDICO-VETERINÁRIO."""
        resposta += self.formatador.formatar_aviso_seguranca(aviso)

        return resposta

    def _resposta_conceito(self, conceito: Dict) -> str:
        """Formata resposta sobre conceito."""
        resposta = ""

        resposta += self.formatador.formatar_resposta_objetiva(
            f"{conceito['termo']}: {conceito['definicao'][:150]}..."
        )

        resposta += self.formatador.formatar_explicacao_didatica(conceito['definicao'])

        resposta += self.formatador.formatar_fonte(
            conceito.get("tipo_informacao", "Conhecimento geral"),
            self._resolver_fonte(conceito.get("fonte", ""))
        )

        evidencia = conceito.get("evidencia_cientifica", "Não disponível")
        limitacoes = "Conceito teórico da homeopatia. Não comprovado pelo método científico convencional."
        resposta += self.formatador.formatar_evidencias(evidencia, limitacoes)

        if conceito.get("notas"):
            resposta += f"\n💡 NOTA COMPLEMENTAR\n{'─' * 50}\n{conceito['notas']}\n"

        return resposta

    def _resposta_glossario(self, glossario: Tuple[str, str]) -> str:
        """Formata resposta de glossário."""
        termo, definicao = glossario
        return f"""
📖 GLOSSÁRIO
{'─' * 50}
{termo}:
{definicao}
{'─' * 50}
"""

    def _resposta_regulamentacao(self, pergunta: str) -> str:
        """Resposta sobre regulamentação."""
        resposta = ""
        resposta += self.formatador.formatar_resposta_objetiva(
            "Regulamentação de Homeopatia Veterinária no Brasil"
        )

        regs = self.busca.buscar_regulamentacao(pergunta)
        if regs:
            for reg in regs:
                resposta += self.formatador.formatar_explicacao_didatica(
                    f"{reg['aspecto']}:\n{reg['descricao']}\n\nStatus: {reg.get('status', 'N/A')}"
                )
                resposta += self.formatador.formatar_fonte(
                    reg.get("tipo_informacao", "Regulatória"),
                    self._resolver_fonte(reg.get("fonte", ""))
                )
        else:
            resposta += self.formatador.formatar_explicacao_didatica(
                """Principais marcos regulatórios:

1. Resolução CFMV nº 625/95 - Reconhece Homeopatia Veterinária como especialidade
2. Ofício-Circular MAPA nº 8/2017 - Produtos homeopáticos devem ser registrados no MAPA
3. Decreto-Lei 467/1969 - Define produtos de uso veterinário
4. Decreto 5.053/2004 - Regulamento de fiscalização
5. Portaria 798/2023 - Produtos para alimentação animal com medicamentos homeopáticos
6. Nota Técnica 13/2026 - Propõe registro automatizado de preparados homeopáticos"""
            )

        return resposta

    def _resposta_evidencias(self, pergunta: str) -> str:
        """Resposta sobre evidências científicas."""
        resposta = ""
        resposta += self.formatador.formatar_resposta_objetiva(
            "Evidências Científicas sobre Homeopatia Veterinária"
        )

        didatica = """A homeopatia veterinária é uma das terapias complementares mais controversas.

SÍNTESE DAS EVIDÊNCIAS:

📊 Revisão Sistemática Bergh et al. (2021):
   • Analisou 982 publicações sobre 24 terapias complementares
   • Apenas 42 estudos elegíveis sobre 9 terapias (incluindo homeopatia)
   • Risco de viés: ALTO em 17 estudos, MODERADO em 10, BAIXO em apenas 1
   • Conclusão: "A evidência científica NÃO é forte o suficiente para definir eficácia clínica"

📊 ScienceDirect - Veterinary Homeopathy Overview:
   • "Não há evidências reprodutíveis e rigorosas de que a homeopatia funcione"
   • "Não há mecanismo de ação racional"
   • Benefícios em humanos podem ser atribuídos ao efeito placebo/contextual

📊 Estudos específicos:
   • Mastite caprina (2025): homeopatia não demonstrou eficácia significativa
   • Engystol® (2017): possível efeito adjuvante em camundongos - estudo preliminar
   • Crescimento em suínos (Camerlink 2010): menos de 20 ensaios controlados publicados

LIMITAÇÕES METODOLÓGICAS:
   → Poucos ensaios randomizados controlados
   → Alto risco de viés nos estudos existentes
   → Dificuldade de reprodução dos resultados
   → Ausência de mecanismo de ação explicável pela ciência atual"""

        resposta += self.formatador.formatar_explicacao_didatica(didatica)

        resposta += self.formatador.formatar_fonte(
            "Revisão Sistemática / Revisão de Literatura",
            "PubMed / ScienceDirect - Fontes acadêmicas revisadas por pares"
        )

        resposta += self.formatador.formatar_evidencias(
            "Evidências científicas sobre eficácia da homeopatia veterinária são insuficientes e de baixa qualidade metodológica.",
            "Falta de ensaios clínicos robustos, reprodutibilidade questionável, ausência de mecanismo de ação conhecido."
        )

        resposta += self.formatador.formatar_aviso_seguranca(
            """A ausência de evidências robustas não significa necessariamente ineficácia absoluta,
mas significa que NÃO SE PODE AFIRMAR com segurança que a homeopatia veterinária funcione.

Decisões clínicas devem basear-se em evidências científicas sólidas.
Consulte sempre um MÉDICO-VETERINÁRIO."""
        )

        return resposta

    def _resposta_composicao(self, pergunta: str) -> str:
        """Resposta sobre composição de medicamentos."""
        med = self.busca.buscar_medicamento(pergunta)
        if med:
            return self._resposta_medicamento(med)

        return self.formatador.formatar_explicacao_didatica(
            """Os medicamentos homeopáticos são classificados por sua origem:

🌿 REINO VEGETAL: Arnica, Nux Vomica, Pulsatilla, Belladonna, Bryonia, etc.
   → Preparados a partir de plantas, folhas, raízes, sementes

🪨 REINO MINERAL: Arsenicum Album, Calcarea Carbonica, Sulphur, Silicea, etc.
   → Preparados a partir de sais minerais, metais, elementos químicos

🦋 REINO ANIMAL: Apis Mellifica (abelha), Sepia (lula), Cantharis (besouro), etc.
   → Preparados a partir de partes ou secreções de animais

⚗️ PROCESSO DE PREPARAÇÃO:
   1. Extração da substância original (matriz)
   2. Diluição em solução hidroalcoólica
   3. Sucussão (agitação vigorosa)
   4. Repetição do processo até a potência desejada

⚠️ IMPORTANTE: Acima de 12 CH, não há moléculas da substância original.
   O produto é essencialmente álcool diluído em água + açúcar (glóbulos)."""
        )

    def _resposta_potencias(self) -> str:
        """Resposta sobre potências."""
        return self.formatador.formatar_explicacao_didatica(
            """POTÊNCIAS HOMEOPÁTICAS

As potências indicam o grau de diluição do medicamento:

📉 ESCALA DECIMAL (DH / X / D):
   1 DH = diluição 1:10 (1 parte em 9 de veículo)
   Ex: 6 DH = 10^-6 da concentração original

📉 ESCALA CENTESIMAL (CH / K / C):
   1 CH = diluição 1:100 (1 parte em 99 de veículo)
   Ex: 6 CH = 100^-6 = 10^-12 da concentração original

📊 CLASSIFICAÇÃO POR POTÊNCIA:
   • BAIXAS: 1 CH a 12 CH — podem conter moléculas da substância original
   • MÉDIAS: 30 CH a 200 CH — além do limite de Avogadro
   • ALTAS: Acima de 200 CH — diluições extremas

🔬 LIMITE DE AVOGADRO:
   • Aproximadamente 6,022 × 10^23 moléculas por mol
   • A potência 12 CH corresponde a diluição de 10^-24
   • NÃO É FISICAMENTE POSSÍVEL haver moléculas da substância original

🤔 PARADOXO:
   Segundo a teoria homeopática, QUANTO MAIOR a diluição,
   MAIOR seria a 'potência terapêutica'. Isso contradiz a farmacologia
   convencional, onde a dose-resposta é proporcional.

A ciência convencional não possui mecanismo explicativo para esse paradoxo."""
        )

    def _resposta_generica(self) -> str:
        """Resposta genérica com menu de opções."""
        return """
🎓 TUTOR DE HOMEOPATIA VETERINÁRIA
══════════════════════════════════════════════════

Sou um agente educacional sobre homeopatia veterinária.
Posso ajudar com os seguintes tópicos:

📚 CONCEITOS FUNDAMENTAIS
   • Lei do Semelhante (Similia similibus curentur)
   • Potenciação e Dinamização
   • Patogenesia e Matéria Médica
   • Repertorização

💊 MEDICAMENTOS HOMEOPÁTICOS
   • Composição e origem
   • Apresentações e conservação
   • Indicações declaradas (teoria homeopática)
   • Potências comuns

⚖️ REGULAMENTAÇÃO
   • Reconhecimento como especialidade (CFMV)
   • Registro de produtos (MAPA)
   • Legislação brasileira

🔬 EVIDÊNCIAS CIENTÍFICAS
   • Revisões sistemáticas disponíveis
   • Qualidade dos estudos
   • Limitações metodológicas
   • Nível de evidência atual

❓ GLOSSÁRIO
   • CH, DH, sucussão, similimum, policresto, etc.

══════════════════════════════════════════════════
💡 DICA: Digite o nome de um medicamento (ex: "Arnica Montana")
   ou um conceito (ex: "potência", "regulamentação", "evidência")
══════════════════════════════════════════════════
"""

    def _resposta_bloqueio_diagnostico(self, palavras_detectadas: List[str]) -> str:
        """Resposta quando detecta tentativa de diagnóstico."""
        return f"""
🚫 CONSULTA NÃO PERMITIDA
══════════════════════════════════════════════════

Detectei termos que indicam busca por diagnóstico ou prescrição:
   → {', '.join(palavras_detectadas)}

SOU UM TUTOR EDUCACIONAL. NÃO posso:
  ❌ Diagnosticar doenças
  ❌ Prescrever medicamentos
  ❌ Recomendar doses
  ❌ Indicar tratamentos individuais
  ❌ Substituir consulta veterinária

SE SEU ANIMAL ESTÁ COM SINTOMAS:
  👉 Consulte um MÉDICO-VETERINÁRIO
  👉 Não administre medicamentos sem orientação profissional
  👉 Em emergências, procure atendimento imediato

Posso ajudar com:
  ✅ Conceitos teóricos de homeopatia
  ✅ Informações sobre medicamentos (contexto educacional)
  ✅ Legislação e regulamentação
  ✅ Nível de evidência científica
══════════════════════════════════════════════════
"""

    def _resolver_fonte(self, fonte_id: str) -> str:
        """Resolve ID da fonte para nome legível."""
        fontes = self.base.get("metadata", {}).get("fontes_principais", [])
        for f in fontes:
            if f.get("id") == fonte_id:
                return f"{f.get('nome', fonte_id)} ({f.get('tipo', '')})"
        return fonte_id

    def _extrair_topico(self, pergunta: str) -> str:
        """Extrai tópico principal da pergunta."""
        # Tenta encontrar medicamento
        med = self.busca.buscar_medicamento(pergunta)
        if med:
            return med["nome"]
        # Tenta conceito
        conceito = self.busca.buscar_conceito(pergunta)
        if conceito:
            return conceito["termo"]
        # Tópico genérico
        return "geral"

    def mostrar_estatisticas_memoria(self) -> str:
        """Mostra estatísticas de aprendizado do tutor."""
        stats = self.memoria.dados
        texto = f"""
📊 ESTATÍSTICAS DO TUTOR
══════════════════════════════════════════════════
Sessões realizadas: {stats.get('sessoes', 0)}
Última sessão: {stats.get('ultima_sessao', 'N/A')}

📈 TÓPICOS MAIS CONSULTADOS:
"""
        for topico, count in self.memoria.topicos_populares(5):
            texto += f"   • {topico}: {count} consultas\n"

        feedbacks = stats.get('feedback_usuarios', [])
        if feedbacks:
            uteis = sum(1 for f in feedbacks if f.get('util'))
            texto += f"\n👍 Feedbacks positivos: {uteis}/{len(feedbacks)}\n"

        return texto


# ============================================================
# INTERFACE DO USUÁRIO
# ============================================================
def mostrar_banner():
    print("""
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║     🎓 TUTOR IA - HOMEOPATIA VETERINÁRIA                     ║
║     Agente Educacional com Memória de Aprendizagem           ║
║                                                              ║
║     Uso estritamente EDUCACIONAL                             ║
║     NÃO substitui orientação médico-veterinária              ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
""")


def mostrar_menu():
    print("""
📋 MENU PRINCIPAL
────────────────────────────────────────
   [1] 💬 Fazer uma pergunta
   [2] 📖 Listar medicamentos disponíveis
   [3] 🔬 Ver evidências científicas
   [4] ⚖️  Ver regulamentação brasileira
   [5] 📊 Estatísticas de aprendizado
   [6] ❓ Perguntas para revisão
   [7] 📖 Glossário de termos
   [0] 🚪 Sair
────────────────────────────────────────
""")


def listar_medicamentos(tutor: TutorHomeopatiaVet):
    """Lista todos os medicamentos da base."""
    limpar_tela()
    print("═" * 60)
    print("💊 MEDICAMENTOS HOMEOPÁTICOS VETERINÁRIOS NA BASE")
    print("═" * 60)
    print("\n⚠️  Estes dados são para FINS EDUCACIONAIS apenas.\n")

    medicamentos = tutor.busca.listar_medicamentos()
    for i, med in enumerate(medicamentos, 1):
        print(f"   {i:2d}. {med['nome']:<25} | {med['categoria']:<20}")
        print(f"       Origem: {med['origem'][:50]}...")
        print()

    print("═" * 60)
    print("💡 Digite o nome do medicamento para saber mais.")
    input("\nPressione ENTER para voltar...")


def mostrar_perguntas_revisao(tutor: TutorHomeopatiaVet):
    """Mostra perguntas para revisão."""
    limpar_tela()
    print("═" * 60)
    print("❓ PERGUNTAS PARA REVISÃO")
    print("═" * 60)

    perguntas = tutor.base.get("perguntas_revisao", [])
    for i, p in enumerate(perguntas, 1):
        print(f"\n{i}. {p}")

    input("\n\nPressione ENTER para voltar...")


def mostrar_glossario(tutor: TutorHomeopatiaVet):
    """Mostra glossário de termos."""
    limpar_tela()
    print("═" * 60)
    print("📖 GLOSSÁRIO DE TERMOS HOMEOPÁTICOS")
    print("═" * 60)

    glossario = tutor.base.get("glossario", {})
    for termo, definicao in sorted(glossario.items()):
        print(f"\n📌 {termo}")
        print(f"   {definicao[:120]}...")

    print("\n" + "═" * 60)
    termo = input("\nDigite um termo para buscar (ou ENTER para voltar): ").strip()
    if termo:
        resultado = tutor.busca.buscar_no_glossario(termo)
        if resultado:
            print(f"\n📌 {resultado[0]}")
            print(f"   {resultado[1]}")
        else:
            print("\n❌ Termo não encontrado no glossário.")
        input("\nPressione ENTER...")


def menu_principal():
    """Loop principal do menu."""
    tutor = TutorHomeopatiaVet()

    while True:
        limpar_tela()
        mostrar_banner()
        mostrar_menu()

        escolha = input("👉 Escolha uma opção: ").strip()

        if escolha == "1":
            limpar_tela()
            print("═" * 60)
            print("💬 MODO CONVERSA")
            print("═" * 60)
            print("Digite sua pergunta sobre homeopatia veterinária.")
            print("Digite 'voltar' para retornar ao menu.\n")

            while True:
                pergunta = input("📝 Você: ").strip()
                if pergunta.lower() in ("voltar", "sair", "menu"):
                    break
                if not pergunta:
                    continue

                resposta = tutor.processar_consulta(pergunta)
                print(resposta)
                print("\n" + "─" * 60 + "\n")

                # Pergunta feedback
                fb = input("👍 Esta resposta foi útil? (s/n/voltar): ").strip().lower()
                if fb == "s":
                    tutor.memoria.registrar_feedback(pergunta, True)
                    print("✅ Obrigado pelo feedback! Isso ajuda meu aprendizado.\n")
                elif fb == "n":
                    tutor.memoria.registrar_feedback(pergunta, False)
                    print("📝 Registrado. Vou melhorar nas próximas respostas.\n")
                elif fb == "voltar":
                    break

        elif escolha == "2":
            listar_medicamentos(tutor)

        elif escolha == "3":
            limpar_tela()
            print(tutor.processar_consulta("evidências científicas homeopatia veterinária"))
            input("\nPressione ENTER para voltar...")

        elif escolha == "4":
            limpar_tela()
            print(tutor.processar_consulta("regulamentação brasileira homeopatia veterinária"))
            input("\nPressione ENTER para voltar...")

        elif escolha == "5":
            limpar_tela()
            print(tutor.mostrar_estatisticas_memoria())
            input("\nPressione ENTER para voltar...")

        elif escolha == "6":
            mostrar_perguntas_revisao(tutor)

        elif escolha == "7":
            mostrar_glossario(tutor)

        elif escolha == "0":
            limpar_tela()
            print("""
🙏 Obrigado por usar o Tutor de Homeopatia Veterinária!

📌 Lembre-se:
   • Este é um agente EDUCACIONAL
   • NÃO substitui orientação médico-veterinária
   • Consulte um profissional para decisões clínicas

🧠 O tutor aprendeu com esta sessão e melhorará futuras respostas.

Até logo! 👋
""")
            break
        else:
            print("\n⚠️  Opção inválida.")
            input("Pressione ENTER...")


# ============================================================
# PONTO DE ENTRADA
# ============================================================
if __name__ == "__main__":
    try:
        menu_principal()
    except KeyboardInterrupt:
        print("\n\n👋 Sessão encerrada pelo usuário.")
