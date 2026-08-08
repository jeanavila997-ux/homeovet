#!/usr/bin/env python3
"""
🤖 Agente de Aprendizagem - Medicamentos Homeopáticos
Código simples, leve e 100% gratuito - Python puro!
"""

import json
import os
from datetime import datetime
from difflib import SequenceMatcher

# ============================================================
# CONFIGURAÇÕES
# ============================================================
DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
REMEDIOS_FILE = os.path.join(DATA_DIR, "remedios_homeopaticos.json")
FEEDBACK_FILE = os.path.join(DATA_DIR, "feedback.json")


def similaridade(a: str, b: str) -> float:
    """Calcula similaridade entre duas strings (0 a 1)."""
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()


def limpar_tela():
    """Limpa o terminal."""
    os.system("cls" if os.name == "nt" else "clear")


def mostrar_banner():
    """Mostra o banner inicial."""
    print("═" * 60)
    print("   🤖 AGENTE DE APRENDIZAGEM HOMEOPÁTICA")
    print("   Busca inteligente + Aprendizado contínuo")
    print("═" * 60)
    print()


# ============================================================
# CARREGAMENTO E PERSISTÊNCIA
# ============================================================
def carregar_remedios() -> list:
    """Carrega a base de dados de remédios."""
    if not os.path.exists(REMEDIOS_FILE):
        print(f"❌ Arquivo não encontrado: {REMEDIOS_FILE}")
        return []
    with open(REMEDIOS_FILE, "r", encoding="utf-8") as f:
        return json.load(f).get("remedios", [])


def salvar_remedios(remedios: list):
    """Salva a base de dados de remédios."""
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(REMEDIOS_FILE, "w", encoding="utf-8") as f:
        json.dump({"remedios": remedios}, f, ensure_ascii=False, indent=2)


def carregar_feedback() -> list:
    """Carrega o histórico de feedback."""
    if not os.path.exists(FEEDBACK_FILE):
        return []
    with open(FEEDBACK_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def salvar_feedback(feedback: list):
    """Salva o histórico de feedback."""
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(FEEDBACK_FILE, "w", encoding="utf-8") as f:
        json.dump(feedback, f, ensure_ascii=False, indent=2)


# ============================================================
# MOTOR DE BUSCA INTELIGENTE
# ============================================================
def calcular_score(remedio: dict, sintomas_usuario: list) -> float:
    """
    Calcula o score de um remédio baseado nos sintomas informados.
    Usa similaridade de texto + score de aprendizado.
    """
    sintomas_remedio = remedio.get("sintomas", [])
    score_base = 0.0
    matches = 0

    for sintoma_user in sintomas_usuario:
        melhor_match = 0.0
        for sintoma_remedio in sintomas_remedio:
            sim = similaridade(sintoma_user, sintoma_remedio)
            if sim > melhor_match:
                melhor_match = sim
        # Considera match se similaridade > 0.5 (50%)
        if melhor_match >= 0.5:
            score_base += melhor_match
            matches += 1

    # Bonus por quantidade de matches
    bonus_matches = min(matches * 0.1, 0.5)

    # Fator de aprendizado (score acumulado)
    score_aprendizado = remedio.get("score", 0) * 0.05

    return score_base + bonus_matches + score_aprendizado


def buscar_remedios(remedios: list, sintomas_raw: str, top_n: int = 5) -> list:
    """
    Busca os remédios mais relevantes para os sintomas informados.
    Retorna lista ordenada por relevância.
    """
    # Processa sintomas do usuário
    sintomas_list = [s.strip() for s in sintomas_raw.replace(",", " ").split() if s.strip()]
    if not sintomas_list:
        return []

    resultados = []
    for remedio in remedios:
        score = calcular_score(remedio, sintomas_list)
        if score > 0:
            resultados.append({
                **remedio,
                "score_busca": round(score, 2),
                "matches": len([s for s in sintomas_list if any(
                    similaridade(s, sr) >= 0.5 for sr in remedio.get("sintomas", [])
                )])
            })

    # Ordena por score decrescente
    resultados.sort(key=lambda x: x["score_busca"], reverse=True)
    return resultados[:top_n]


# ============================================================
# SISTEMA DE APRENDIZADO (FEEDBACK)
# ============================================================
def registrar_feedback(remedio_id: int, funcionou: bool, remedios: list):
    """
    Registra feedback do usuário e atualiza o score do remédio.
    funcionou: True = ajudou, False = não ajudou
    """
    feedback = carregar_feedback()

    entrada = {
        "data": datetime.now().isoformat(),
        "remedio_id": remedio_id,
        "funcionou": funcionou
    }
    feedback.append(entrada)
    salvar_feedback(feedback)

    # Atualiza score do remédio
    for r in remedios:
        if r["id"] == remedio_id:
            r["score"] = r.get("score", 0) + (1 if funcionou else -1)
            r["total_feedback"] = r.get("total_feedback", 0) + 1
            break

    salvar_remedios(remedios)


def mostrar_estatisticas(remedios: list):
    """Mostra estatísticas de aprendizado do agente."""
    feedback = carregar_feedback()

    if not feedback:
        print("\n📊 Ainda não há feedback registrado. Use o agente mais vezes!")
        return

    total = len(feedback)
    positivos = sum(1 for f in feedback if f["funcionou"])
    negativos = total - positivos
    taxa_sucesso = (positivos / total) * 100

    print("\n" + "═" * 50)
    print("📊 ESTATÍSTICAS DE APRENDIZADO")
    print("═" * 50)
    print(f"   Total de feedbacks: {total}")
    print(f"   ✅ Funcionou: {positivos}")
    print(f"   ❌ Não funcionou: {negativos}")
    print(f"   📈 Taxa de sucesso: {taxa_sucesso:.1f}%")
    print("═" * 50)

    # Top 5 remédios mais bem avaliados
    print("\n🏆 TOP REMÉDIOS (por score de aprendizado):")
    ordenados = sorted(remedios, key=lambda x: x.get("score", 0), reverse=True)
    for i, r in enumerate(ordenados[:5], 1):
        score = r.get("score", 0)
        total_fb = r.get("total_feedback", 0)
        if total_fb > 0:
            print(f"   {i}. {r['nome']} — Score: {score:+d} ({total_fb} avaliações)")

    print()


# ============================================================
# INTERFACE DO USUÁRIO
# ============================================================
def mostrar_remedio(remedio: dict, posicao: int = None):
    """Exibe os detalhes de um remédio formatado."""
    prefixo = f"[{posicao}] " if posicao else ""
    score_busca = remedio.get("score_busca", 0)
    score_aprendizado = remedio.get("score", 0)
    total_fb = remedio.get("total_feedback", 0)

    print(f"\n{'─' * 50}")
    print(f"💊 {prefixo}{remedio['nome']} (Score: {score_busca:.2f})")
    print(f"{'─' * 50}")
    print(f"   📌 Princípio Ativo: {remedio['principio_ativo']}")
    print(f"   📁 Categoria: {remedio['categoria']}")
    print(f"   🩺 Indicações: {remedio['indicacoes']}")
    print(f"   💉 Dosagem: {remedio['dosagem']}")
    print(f"   ⚠️  Contraindicações: {remedio['contraindicacoes']}")
    print(f"   🏷️  Sintomas: {', '.join(remedio['sintomas'])}")

    # Mostra score de aprendizado se houver
    if total_fb > 0:
        confianca = "Alta" if score_aprendizado > 5 else "Média" if score_aprendizado > 0 else "Baixa"
        print(f"   🧠 Aprendizado: {score_aprendizado:+d} pontos ({total_fb} avaliações) — Confiança: {confianca}")
    print(f"{'─' * 50}")


def menu_buscar(remedios: list):
    """Fluxo de busca por sintomas."""
    limpar_tela()
    print("═" * 50)
    print("🔍 BUSCAR POR SINTOMAS")
    print("═" * 50)
    print("\n💡 Dica: Digite os sintomas separados por espaço ou vírgula")
    print("   Exemplo: dor de cabeca nausea ansiedade\n")

    sintomas = input("📝 Quais são os sintomas? ").strip()
    if not sintomas:
        print("\n⚠️  Nenhum sintoma informado.")
        input("\nPressione ENTER para voltar...")
        return

    print(f"\n🔎 Buscando remédios para: '{sintomas}'...")
    resultados = buscar_remedios(remedios, sintomas)

    if not resultados:
        print("\n😕 Nenhum remédio encontrado para esses sintomas.")
        print("💡 Tente descrever com outras palavras ou consulte um homeopata.")
        input("\nPressione ENTER para voltar...")
        return

    print(f"\n✅ {len(resultados)} remédio(s) encontrado(s):\n")

    for i, remedio in enumerate(resultados, 1):
        mostrar_remedio(remedio, i)

    # Pergunta feedback
    print("\n📢 O remédio indicado ajudou?")
    print("   [1] Sim, funcionou! ✅")
    print("   [2] Não funcionou ❌")
    print("   [0] Pular feedback")

    escolha = input("\n👉 Sua resposta: ").strip()

    if escolha in ("1", "2"):
        try:
            num = int(input("👉 Qual número do remédio? "))
            if 1 <= num <= len(resultados):
                remedio_escolhido = resultados[num - 1]
                funcionou = escolha == "1"
                registrar_feedback(remedio_escolhido["id"], funcionou, remedios)

                if funcionou:
                    print(f"\n🎉 Obrigado! O agente APRENDEU que '{remedio_escolhido['nome']}' é eficaz!")
                else:
                    print(f"\n📝 Registrado. O agente ajustará futuras recomendações.")
            else:
                print("\n⚠️  Número inválido.")
        except ValueError:
            print("\n⚠️  Entrada inválida.")

    input("\nPressione ENTER para voltar...")


def menu_listar(remedios: list):
    """Lista todos os remédios cadastrados."""
    limpar_tela()
    print("═" * 50)
    print("📋 LISTA DE REMÉDIOS HOMEOPÁTICOS")
    print("═" * 50)
    print(f"\nTotal: {len(remedios)} remédios cadastrados\n")

    for i, r in enumerate(remedios, 1):
        score_str = f" (Score: {r.get('score', 0):+d})" if r.get("total_feedback", 0) > 0 else ""
        print(f"   {i:2d}. {r['nome']:<25} | {r['categoria']:<18}{score_str}")

    print("\n" + "═" * 50)
    ver = input("\n👉 Digite o número para ver detalhes (ou ENTER para voltar): ").strip()

    if ver.isdigit():
        idx = int(ver)
        if 1 <= idx <= len(remedios):
            mostrar_remedio(remedios[idx - 1])
            input("\nPressione ENTER para voltar...")


def menu_adicionar(remedios: list):
    """Adiciona um novo remédio à base."""
    limpar_tela()
    print("═" * 50)
    print("➕ ADICIONAR NOVO REMÉDIO")
    print("═" * 50)

    nome = input("\n💊 Nome do remédio: ").strip()
    if not nome:
        print("❌ Nome é obrigatório.")
        input("Pressione ENTER...")
        return

    principio = input("🔬 Princípio ativo: ").strip()
    categoria = input("📁 Categoria: ").strip()
    sintomas_raw = input("🏷️  Sintomas (separados por vírgula): ").strip()
    indicacoes = input("🩺 Indicações: ").strip()
    dosagem = input("💉 Dosagem: ").strip()
    contras = input("⚠️  Contraindicações: ").strip()

    novo_id = max((r["id"] for r in remedios), default=0) + 1

    novo_remedio = {
        "id": novo_id,
        "nome": nome,
        "principio_ativo": principio or nome,
        "categoria": categoria or "Geral",
        "sintomas": [s.strip() for s in sintomas_raw.split(",") if s.strip()],
        "indicacoes": indicacoes or "Consultar homeopata",
        "dosagem": dosagem or "Consultar homeopata",
        "contraindicacoes": contras or "Nenhuma conhecida",
        "score": 0,
        "total_feedback": 0
    }

    remedios.append(novo_remedio)
    salvar_remedios(remedios)

    print(f"\n✅ Remédio '{nome}' adicionado com sucesso! (ID: {novo_id})")
    input("\nPressione ENTER para voltar...")


# ============================================================
# MENU PRINCIPAL
# ============================================================
def menu_principal():
    """Loop principal do menu."""
    remedios = carregar_remedios()

    if not remedios:
        print("❌ Erro ao carregar base de dados. Verifique o arquivo JSON.")
        return

    while True:
        limpar_tela()
        mostrar_banner()

        print("📋 MENU PRINCIPAL")
        print("─" * 40)
        print("   [1] 🔍 Buscar por sintomas")
        print("   [2] 📋 Listar todos os remédios")
        print("   [3] 📊 Ver estatísticas de aprendizado")
        print("   [4] ➕ Adicionar novo remédio")
        print("   [0] 🚪 Sair")
        print("─" * 40)

        escolha = input("\n👉 Escolha uma opção: ").strip()

        if escolha == "1":
            menu_buscar(remedios)
        elif escolha == "2":
            menu_listar(remedios)
        elif escolha == "3":
            limpar_tela()
            mostrar_estatisticas(remedios)
            input("Pressione ENTER para voltar...")
        elif escolha == "4":
            menu_adicionar(remedios)
        elif escolha == "0":
            limpar_tela()
            print("\n🙏 Obrigado por usar o Agente Homeopático!")
            print("💡 Lembre-se: este agente é um auxiliar, não substitui")
            print("   a consulta com um profissional qualificado.\n")
            break
        else:
            print("\n⚠️  Opção inválida. Tente novamente.")
            input("Pressione ENTER...")


# ============================================================
# PONTO DE ENTRADA
# ============================================================
if __name__ == "__main__":
    try:
        menu_principal()
    except KeyboardInterrupt:
        print("\n\n👋 Até logo!")
