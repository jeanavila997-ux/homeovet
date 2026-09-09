#!/usr/bin/env python3
"""Sincroniza a base do index.html (v3.0.0, 123 medicamentos) de volta para o
data/tutor_homeopatia_vet.json, corrige a dessincronização criada pelos
scripts de expansão direta no HTML e adiciona a categoria "Cascos e Unhas"
(bovinos, equinos e unhas humanas) — v3.1.0.

Depois desta sincronização, o data/*.json volta a ser a fonte única de verdade
do projeto: index.html passa a ser regenerado por scripts/gerar_index.py sem
perder os 123 medicamentos adicionados por atualizar_base.py/expandir_amhb.py.
"""
import json
import os
import re

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HTML = os.path.join(BASE_DIR, "index.html")
JSON_PATH = os.path.join(BASE_DIR, "data", "tutor_homeopatia_vet.json")

html = open(HTML, encoding="utf-8").read()
m = re.search(r"const BASE = (\{.*?\});\n", html, re.S)
if not m:
    raise SystemExit("BASE não encontrada no index.html")
base = json.loads(m.group(1))

# ---------------------------------------------------------------------------
# 1. Medicamentos da nova categoria "Cascos e Unhas"
#    (matéria médica clássica; uso EDUCACIONAL; eficácia não comprovada)
# ---------------------------------------------------------------------------
novos = [
    {
        "id": "ANTIMONIUM_CRUDUM",
        "nome": "Antimonium Crudum",
        "nome_popular": "Antimônio cru",
        "origem": "Mineral (trissulfeto de antimônio, estibinita)",
        "principio_ativo_declarado": "Antimonium crudum, potenciado conforme farmacopeia homeopática",
        "categoria": "Cascos e Unhas",
        "potencias_comuns": ["6 CH", "12 CH", "30 CH"],
        "apresentacoes": "Glóbulos, comprimidos, solução oral",
        "conservacao": "Embalagem fechada, ao abrigo de luz, calor, umidade e campos eletromagnéticos.",
        "indicacoes_fabricante": "Unhas grossas, deformadas e de crescimento lento; cascos defeituosos e quebradiços em equinos e bovinos segundo a literatura homeopática.",
        "indicacoes_registro_mapa": "Conforme farmacopeia homeopática e matéria médica. Requer registro MAPA desde 2017.",
        "sintomas_homeopaticos": [
            "unhas grossas e deformadas",
            "unhas que crescem devagar",
            "cascos defeituosos",
            "casco quebradico",
            "rachaduras na parede do casco",
            "irritabilidade"
        ],
        "contraindicacoes": "Não há contraindicações absolutas documentadas; eficácia não comprovada cientificamente.",
        "precaucoes": "Uso educacional; consulte médico-veterinário. Manejo de casco (casqueamento/ferrageamento) é questão de bem-estar animal e não deve ser substituído.",
        "uso_veterinario": "Literatura homeopática veterinária cita uso em cascos defeituosos de equinos e bovinos; em humanos, nas unhas grossas e de crescimento lento.",
        "fonte_informacao": "MATERIA_MEDICA_CLASSICA",
        "tipo_informacao": "Declaração de fabricantes/literatura homeopática",
        "evidencia_cientifica": "Sem ensaios clínicos controlados robustos em animais. Eficácia não comprovada cientificamente (Bergh et al., 2021).",
        "notas": "Policresto clássico da matéria médica. Quadro 'cascos/unhas' é tradição homeopática, não evidência."
    },
    {
        "id": "FLUORICUM_ACIDUM",
        "nome": "Fluoricum Acidum",
        "nome_popular": "Ácido fluorídrico",
        "origem": "Químico (ácido fluorídrico, HF)",
        "principio_ativo_declarado": "Acidum fluoricum, potenciado conforme farmacopeia homeopática",
        "categoria": "Cascos e Unhas",
        "potencias_comuns": ["6 CH", "12 CH", "30 CH"],
        "apresentacoes": "Glóbulos, comprimidos, solução oral",
        "conservacao": "Embalagem fechada, ao abrigo de luz, calor, umidade e campos eletromagnéticos.",
        "indicacoes_fabricante": "Unhas estriadas e deformadas; cárie de casco e fistulas perioculares do casco em equinos segundo a literatura homeopática.",
        "indicacoes_registro_mapa": "Conforme farmacopeia homeopática e matéria médica. Requer registro MAPA desde 2017.",
        "sintomas_homeopaticos": [
            "unhas deformadas e estriadas",
            "caries de casco",
            "fistula no casco",
            "cascos fragilizados",
            "doencas de fistulas",
            "piora com o calor"
        ],
        "contraindicacoes": "Substância bruta é extremamente corrosiva; uso apenas em preparados homeopáticos potenciados. Não há contraindicações absolutas documentadas para a forma potenciada.",
        "precaucoes": "Uso educacional; consulte médico-veterinário. Cárie de casco exige tratamento veterinário e ferrageamento corretivo.",
        "uso_veterinario": "Matéria médica homeopática veterinária clássica cita uso em cárie e fragilidade de casco de equinos; em humanos, unhas deformadas.",
        "fonte_informacao": "MATERIA_MEDICA_CLASSICA",
        "tipo_informacao": "Declaração de fabricantes/literatura homeopática",
        "evidencia_cientifica": "Sem ensaios clínicos controlados robustos em animais. Eficácia não comprovada cientificamente (Bergh et al., 2021).",
        "notas": "Semi-policresto. A forma bruta é tóxica/corrosiva; a potenciada não contém moléculas acima de 12 CH (limite de Avogadro)."
    },
    {
        "id": "GRAPHITES",
        "nome": "Graphites",
        "nome_popular": "Grafite",
        "origem": "Mineral (carbono grafite)",
        "principio_ativo_declarado": "Graphites, potenciado conforme farmacopeia homeopática",
        "categoria": "Cascos e Unhas",
        "potencias_comuns": ["6 CH", "12 CH", "30 CH"],
        "apresentacoes": "Glóbulos, comprimidos, solução oral",
        "conservacao": "Embalagem fechada, ao abrigo de luz, calor, umidade e campos eletromagnéticos.",
        "indicacoes_fabricante": "Unhas quebradiças e com rachaduras; eczemas crônicos com transudação adocicada segundo a literatura homeopática.",
        "indicacoes_registro_mapa": "Conforme farmacopeia homeopática e matéria médica. Requer registro MAPA desde 2017.",
        "sintomas_homeopaticos": [
            "unhas quebradicas",
            "rachaduras nas unhas",
            "rachaduras no casco",
            "eczema cronico",
            "pele seca e fissurada",
            "obesidade com intolerancia ao frio"
        ],
        "contraindicacoes": "Não há contraindicações absolutas documentadas; eficácia não comprovada cientificamente.",
        "precaucoes": "Uso educacional; consulte médico-veterinário.",
        "uso_veterinario": "Literatura homeopática cita uso em fissuras de casco e unhas, e eczema crônico em cães e gatos; em humanos, unhas e pele fissuradas.",
        "fonte_informacao": "MATERIA_MEDICA_CLASSICA",
        "tipo_informacao": "Declaração de fabricantes/literatura homeopática",
        "evidencia_cientifica": "Sem ensaios clínicos controlados robustos em animais. Eficácia não comprovada cientificamente (Bergh et al., 2021).",
        "notas": "Policresto constitucional clássico ('tipo Graphites')."
    },
]

existentes = {x["nome"].lower() for x in base["medicamentos"]}
adicionados = 0
for med in novos:
    if med["nome"].lower() in existentes:
        continue
    base["medicamentos"].append(med)
    existentes.add(med["nome"].lower())
    adicionados += 1

# Policrestos do quadro de cascos e unhas passam a integrar a nova categoria.
# Nomes conforme a base AMHB (ex.: "Silicea Terra", não "Silicea").
QUADRO_CASCOS_UNHAS = {
    "silicea terra": ("cascos frageis", "casco quebradico", "unhas fracas"),
    "antimonium crudum": ("unhas grossas e deformadas", "cascos defeituosos", "unhas que crescem devagar"),
    "fluoricum acidum": ("caries de casco", "fistula no casco", "unhas deformadas e estriadas"),
    "graphites": ("unhas quebradicas", "rachaduras no casco"),
    "graphites naturalis": ("unhas quebradicas", "rachaduras no casco"),
}
for med in base["medicamentos"]:
    extra = QUADRO_CASCOS_UNHAS.get(med["nome"].lower())
    if extra:
        med["categoria"] = "Cascos e Unhas"
        sint = med.setdefault("sintomas_homeopaticos", [])
        for novo_sintoma in extra:
            if novo_sintoma not in sint:
                sint.append(novo_sintoma)

# ---------------------------------------------------------------------------
# 2. Metadata v3.1.0
# ---------------------------------------------------------------------------
base["metadata"]["versao"] = "3.1.0"
base["metadata"]["data_atualizacao"] = "2026-09-09"
base["metadata"]["descricao"] = (
    "Base educacional de homeopatia veterinária — 126 medicamentos (lista AMHB TEH 2025 "
    "+ policrestos clássicos + categoria Cascos e Unhas), evidências independentes e "
    "regulamentação brasileira."
)

# ---------------------------------------------------------------------------
# 3. Salvar JSON (fonte única de verdade, legível e versionável)
# ---------------------------------------------------------------------------
with open(JSON_PATH, "w", encoding="utf-8") as f:
    json.dump(base, f, ensure_ascii=False, indent=2)

print(f"=== Base sincronizada v3.1.0 ===")
print(f"Medicamentos: {len(base['medicamentos'])} (adicionados agora: {adicionados})")
print(f"Evidências: {len(base['evidencias_cientificas'])}")
print(f"Regulamentação: {len(base['regulamentacao_brasil'])}")
print(f"Glossário: {len(base['glossario'])} termos")
print(f"Conceitos: {len(base['conceitos_fundamentais'])}")
categorias = sorted({x["categoria"] for x in base["medicamentos"]})
print(f"Categorias ({len(categorias)}): {', '.join(categorias[:12])}...")
print(f"JSON salvo em: {JSON_PATH}")