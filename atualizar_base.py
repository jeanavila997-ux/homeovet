# -*- coding: utf-8 -*-
"""Atualiza a base HomeoVet com o conteúdo coletado (v2.0.0)."""
import re, json, io

PATH = r"C:\Users\JEANPC\homeovet\index.html"
html = open(PATH, encoding="utf-8").read()
m = re.search(r"const BASE = (\{.*?\});\n", html, re.S)
base = json.loads(m.group(1))

# ---------- 1. NOVOS MEDICAMENTOS (policrestos clássicos) ----------
novos_meds = [
    {
        "id": "CALCAREA_CARBONICA", "nome": "Calcarea Carbonica", "nome_popular": "Carbonato de Cálcio (ostra)",
        "origem": "Mineral (carbonato de cálcio da concha da ostra, Ostrea edulis)",
        "principio_ativo_declarado": "Calcarea carbonica, potenciado conforme farmacopeia homeopática",
        "categoria": "Constitucional / Nutrição", "potencias_comuns": ["6 CH", "12 CH", "30 CH", "200 CH"],
        "apresentacoes": "Glóbulos, comprimidos, solução oral",
        "conservacao": "Embalagem fechada, ao abrigo de luz, calor, umidade e campos eletromagnéticos.",
        "indicacoes_fabricante": "Constitucional: animais friorentos, fadiga fácil, problemas ósseos e de crescimento, distúrbios digestivos, tendência a obesidade.",
        "indicacoes_registro_mapa": "Conforme farmacopeia homeopática e matéria médica. Requer registro MAPA desde 2017.",
        "sintomas_homeopaticos": ["friorento", "fadiga", "suor na cabeça", "desejo de ovos e coisas indigestas", "crescimento lento", "ansiedade por segurança"],
        "contraindicacoes": "Não há contraindicações absolutas documentadas; eficácia não comprovada cientificamente.",
        "precaucoes": "Uso educacional; consulte médico-veterinário.",
        "uso_veterinario": "Utilizado na literatura homeopática para filhotes com desenvolvimento lento, problemas ósseos e constitucionais.",
        "fonte_informacao": "HMP_Brasil", "tipo_informacao": "Declaração de fabricantes/literatura homeopática",
        "evidencia_cientifica": "Sem ensaios clínicos controlados robustos em animais. Eficácia não comprovada (Bergh et al., 2021).",
        "notas": "Policresto clássico; um dos 20 essenciais do guia de estudo (Similia)."
    },
    {
        "id": "CHAMOMILLA", "nome": "Chamomilla", "nome_popular": "Camomila",
        "origem": "Planta (Matricaria chamomilla, Asteraceae)",
        "principio_ativo_declarado": "Chamomilla, potenciado conforme farmacopeia homeopática",
        "categoria": "Comportamental / Digestivo", "potencias_comuns": ["6 CH", "12 CH", "30 CH"],
        "apresentacoes": "Glóbulos, comprimidos, solução oral",
        "conservacao": "Embalagem fechada, ao abrigo de luz, calor e umidade.",
        "indicacoes_fabricante": "Irritabilidade, dor intolerável, dentição, cólicas, diarreia por raiva, sensibilidade à dor.",
        "indicacoes_registro_mapa": "Conforme farmacopeia homeopática. Requer registro MAPA desde 2017.",
        "sintomas_homeopaticos": ["irritabilidade", "dor intolerável", "dentição", "cólica", "uma bochecha vermelha e outra pálida", "piora com contrariedade"],
        "contraindicacoes": "Não há contraindicações absolutas documentadas.",
        "precaucoes": "Uso educacional; consulte médico-veterinário.",
        "uso_veterinario": "Literatura homeopática: filhotes irritadiços, dor de dentição, cólicas.",
        "fonte_informacao": "HMP_Brasil", "tipo_informacao": "Declaração de fabricantes/literatura homeopática",
        "evidencia_cientifica": "Sem ensaios clínicos controlados robustos em animais.",
        "notas": "Policresto de agudos; um dos 20 essenciais (Similia)."
    },
    {
        "id": "GELSEMIUM", "nome": "Gelsemium Sempervirens", "nome_popular": "Jasmim-amarelo",
        "origem": "Planta (Gelsemium sempervirens, Loganiaceae)",
        "principio_ativo_declarado": "Gelsemium, potenciado conforme farmacopeia homeopática",
        "categoria": "Comportamental / Febre", "potencias_comuns": ["6 CH", "12 CH", "30 CH"],
        "apresentacoes": "Glóbulos, comprimidos, solução oral",
        "conservacao": "Embalagem fechada, ao abrigo de luz, calor e umidade.",
        "indicacoes_fabricante": "Ansiedade antecipatória, tremores, fraqueza, febre com prostração, medo de palco/exames.",
        "indicacoes_registro_mapa": "Conforme farmacopeia homeopática. Requer registro MAPA desde 2017.",
        "sintomas_homeopaticos": ["ansiedade antecipatória", "tremores", "fraqueza", "pálpebras caídas", "cefaleia occipital", "febre sem sede"],
        "contraindicacoes": "Não há contraindicações absolutas documentadas.",
        "precaucoes": "Uso educacional; consulte médico-veterinário.",
        "uso_veterinario": "Literatura homeopática: animais ansiosos antes de eventos, tremores, fraqueza.",
        "fonte_informacao": "HMP_Brasil", "tipo_informacao": "Declaração de fabricantes/literatura homeopática",
        "evidencia_cientifica": "Sem ensaios clínicos controlados robustos em animais.",
        "notas": "Policresto de agudos; um dos 20 essenciais (Similia)."
    },
    {
        "id": "IGNATIA_AMARA", "nome": "Ignatia Amara", "nome_popular": "Feijão-de-Santo-Inácio",
        "origem": "Planta (Strychnos ignatii, Loganiaceae)",
        "principio_ativo_declarado": "Ignatia amara, potenciado conforme farmacopeia homeopática",
        "categoria": "Comportamental / Emocional", "potencias_comuns": ["6 CH", "12 CH", "30 CH", "200 CH"],
        "apresentacoes": "Glóbulos, comprimidos, solução oral",
        "conservacao": "Embalagem fechada, ao abrigo de luz, calor e umidade.",
        "indicacoes_fabricante": "Luto, emoções reprimidas, suspiros, soluços, mudanças de humor após perda ou decepção.",
        "indicacoes_registro_mapa": "Conforme farmacopeia homeopática. Requer registro MAPA desde 2017.",
        "sintomas_homeopaticos": ["luto", "emoções reprimidas", "suspiros", "soluços", "humor mutável", "sensação de nó na garganta"],
        "contraindicacoes": "Não há contraindicações absolutas documentadas.",
        "precaucoes": "Uso educacional; consulte médico-veterinário.",
        "uso_veterinario": "Literatura homeopática: animais que perderam companheiro/tutor, estresse emocional.",
        "fonte_informacao": "HMP_Brasil", "tipo_informacao": "Declaração de fabricantes/literatura homeopática",
        "evidencia_cientifica": "Sem ensaios clínicos controlados robustos em animais.",
        "notas": "Policresto de emoções; um dos 20 essenciais (Similia)."
    },
    {
        "id": "LACHESIS", "nome": "Lachesis Muta", "nome_popular": "Veneno de Surucucu",
        "origem": "Animal (veneno da serpente Lachesis muta, Viperidae)",
        "principio_ativo_declarado": "Lachesis muta, potenciado conforme farmacopeia homeopática",
        "categoria": "Geral / Circulatório", "potencias_comuns": ["6 CH", "12 CH", "30 CH", "200 CH"],
        "apresentacoes": "Glóbulos, comprimidos, solução oral",
        "conservacao": "Embalagem fechada, ao abrigo de luz, calor e umidade.",
        "indicacoes_fabricante": "Problemas circulatórios, menopausa, piora após dormir, ciúme, sensibilidade ao toque no pescoço, hemorragias.",
        "indicacoes_registro_mapa": "Conforme farmacopeia homeopática. Requer registro MAPA desde 2017.",
        "sintomas_homeopaticos": ["piora após dormir", "piora à esquerda", "ciúme", "sensibilidade ao colarinho", "hemorragia escura", "piora com pressão"],
        "contraindicacoes": "Não há contraindicações absolutas documentadas.",
        "precaucoes": "Uso educacional; consulte médico-veterinário.",
        "uso_veterinario": "Literatura homeopática: fêmeas no cio/gestação, problemas circulatórios.",
        "fonte_informacao": "HMP_Brasil", "tipo_informacao": "Declaração de fabricantes/literatura homeopática",
        "evidencia_cientifica": "Sem ensaios clínicos controlados robustos em animais.",
        "notas": "Policresto; um dos 20 essenciais (Similia)."
    },
    {
        "id": "NATRUM_MURIATICUM", "nome": "Natrum Muriaticum", "nome_popular": "Cloreto de Sódio (Sal de Cozinha)",
        "origem": "Mineral (cloreto de sódio, NaCl)",
        "principio_ativo_declarado": "Natrum muriaticum, potenciado conforme farmacopeia homeopática",
        "categoria": "Constitucional / Emocional", "potencias_comuns": ["6 CH", "12 CH", "30 CH", "200 CH"],
        "apresentacoes": "Glóbulos, comprimidos, solução oral",
        "conservacao": "Embalagem fechada, ao abrigo de luz, calor e umidade.",
        "indicacoes_fabricante": "Luto prolongado, retração, sede de sal, pele seca, herpes labial, enxaqueca, problemas de pele.",
        "indicacoes_registro_mapa": "Conforme farmacopeia homeopática. Requer registro MAPA desde 2017.",
        "sintomas_homeopaticos": ["luto prolongado", "retração", "sede de sal", "pele seca", "herpes labial", "piora com consolo"],
        "contraindicacoes": "Não há contraindicações absolutas documentadas.",
        "precaucoes": "Uso educacional; consulte médico-veterinário.",
        "uso_veterinario": "Literatura homeopática: animais retraídos após perda, problemas de pele seca.",
        "fonte_informacao": "HMP_Brasil", "tipo_informacao": "Declaração de fabricantes/literatura homeopática",
        "evidencia_cientifica": "Sem ensaios clínicos controlados robustos em animais.",
        "notas": "Policresto constitucional; um dos 20 essenciais (Similia)."
    },
    {
        "id": "PHOSPHORUS", "nome": "Phosphorus", "nome_popular": "Fósforo",
        "origem": "Mineral (fósforo branco)",
        "principio_ativo_declarado": "Phosphorus, potenciado conforme farmacopeia homeopática",
        "categoria": "Respiratório / Constitucional", "potencias_comuns": ["6 CH", "12 CH", "30 CH", "200 CH"],
        "apresentacoes": "Glóbulos, comprimidos, solução oral",
        "conservacao": "Embalagem fechada, ao abrigo de luz, calor e umidade.",
        "indicacoes_fabricante": "Problemas respiratórios, hemorragias de sangue vivo, sede de bebidas frias, sociabilidade, medo de trovoadas.",
        "indicacoes_registro_mapa": "Conforme farmacopeia homeopática. Requer registro MAPA desde 2017.",
        "sintomas_homeopaticos": ["sangramento vermelho-vivo", "sede de frias", "medo de trovoadas", "sociável", "piora à noite", "fraqueza após doença"],
        "contraindicacoes": "Não há contraindicações absolutas documentadas.",
        "precaucoes": "Uso educacional; consulte médico-veterinário.",
        "uso_veterinario": "Literatura homeopática: problemas respiratórios e hemorrágicos.",
        "fonte_informacao": "HMP_Brasil", "tipo_informacao": "Declaração de fabricantes/literatura homeopática",
        "evidencia_cientifica": "Sem ensaios clínicos controlados robustos em animais.",
        "notas": "Policresto; um dos 20 essenciais (Similia)."
    },
    {
        "id": "SILICEA", "nome": "Silicea Terra", "nome_popular": "Sílica (Quartzo)",
        "origem": "Mineral (dióxido de silício, SiO2)",
        "principio_ativo_declarado": "Silicea terra, potenciado conforme farmacopeia homeopática",
        "categoria": "Constitucional / Pele", "potencias_comuns": ["6 CH", "12 CH", "30 CH", "200 CH"],
        "apresentacoes": "Glóbulos, comprimidos, solução oral",
        "conservacao": "Embalagem fechada, ao abrigo de luz, calor e umidade.",
        "indicacoes_fabricante": "Timidez, baixa resistência, supurações, abscessos, unhas frágeis, problemas de pele, cicatrização lenta.",
        "indicacoes_registro_mapa": "Conforme farmacopeia homeopática. Requer registro MAPA desde 2017.",
        "sintomas_homeopaticos": ["timidez", "baixa resistência", "supurações", "abscessos", "cicatrização lenta", "piora com frio"],
        "contraindicacoes": "Não há contraindicações absolutas documentadas.",
        "precaucoes": "Uso educacional; consulte médico-veterinário.",
        "uso_veterinario": "Literatura homeopática: abscessos, problemas de pele, baixa imunidade.",
        "fonte_informacao": "HMP_Brasil", "tipo_informacao": "Declaração de fabricantes/literatura homeopática",
        "evidencia_cientifica": "Sem ensaios clínicos controlados robustos em animais.",
        "notas": "Policresto constitucional; um dos 20 essenciais (Similia)."
    },
    {
        "id": "SULPHUR", "nome": "Sulphur", "nome_popular": "Enxofre",
        "origem": "Mineral (enxofre sublimado)",
        "principio_ativo_declarado": "Sulphur, potenciado conforme farmacopeia homeopática",
        "categoria": "Pele / Constitucional", "potencias_comuns": ["6 CH", "12 CH", "30 CH", "200 CH"],
        "apresentacoes": "Glóbulos, comprimidos, solução oral",
        "conservacao": "Embalagem fechada, ao abrigo de luz, calor e umidade.",
        "indicacoes_fabricante": "Prurido, erupções cutâneas, calor, aversão a banho, fome às 11h, problemas de pele crônicos, antipsórico.",
        "indicacoes_registro_mapa": "Conforme farmacopeia homeopática. Requer registro MAPA desde 2017.",
        "sintomas_homeopaticos": ["prurido", "erupções cutâneas", "calor", "aversão a banho", "fome às 11h", "piora com calor da cama"],
        "contraindicacoes": "Não há contraindicações absolutas documentadas.",
        "precaucoes": "Uso educacional; consulte médico-veterinário.",
        "uso_veterinario": "Literatura homeopática: problemas de pele crônicos, prurido.",
        "fonte_informacao": "HMP_Brasil", "tipo_informacao": "Declaração de fabricantes/literatura homeopática",
        "evidencia_cientifica": "Sem ensaios clínicos controlados robustos em animais.",
        "notas": "O 'rei dos antipsóricos' hahnemanniano; um dos 20 essenciais (Similia)."
    },
    {
        "id": "BRYONIA_ALBA", "nome": "Bryonia Alba", "nome_popular": "Bryônia (Nabo-selvagem)",
        "origem": "Planta (Bryonia alba, Cucurbitaceae)",
        "principio_ativo_declarado": "Bryonia alba, potenciado conforme farmacopeia homeopática",
        "categoria": "Respiratório / Musculoesquelético", "potencias_comuns": ["6 CH", "12 CH", "30 CH"],
        "apresentacoes": "Glóbulos, comprimidos, solução oral",
        "conservacao": "Embalagem fechada, ao abrigo de luz, calor e umidade.",
        "indicacoes_fabricante": "Dor que piora com movimento, sede de grandes goles, irritabilidade, tosse seca, articulações inflamadas.",
        "indicacoes_registro_mapa": "Conforme farmacopeia homeopática. Requer registro MAPA desde 2017.",
        "sintomas_homeopaticos": ["piora com movimento", "sede de grandes goles", "irritabilidade", "tosse seca", "articulações quentes e inchadas", "piora com calor"],
        "contraindicacoes": "Não há contraindicações absolutas documentadas.",
        "precaucoes": "Uso educacional; consulte médico-veterinário.",
        "uso_veterinario": "Literatura homeopática: dores musculoesqueléticas, tosse seca.",
        "fonte_informacao": "HMP_Brasil", "tipo_informacao": "Declaração de fabricantes/literatura homeopática",
        "evidencia_cientifica": "Sem ensaios clínicos controlados robustos em animais.",
        "notas": "Policresto de agudos; um dos 20 essenciais (Similia)."
    },
    {
        "id": "HEPAR_SULPHURIS", "nome": "Hepar Sulphuris Calcareum", "nome_popular": "Sulfeto de Cálcio (Fígado de Enxofre)",
        "origem": "Mineral (sulfeto de cálcio preparado)",
        "principio_ativo_declarado": "Hepar sulphuris calcareum, potenciado conforme farmacopeia homeopática",
        "categoria": "Pele / Supurações", "potencias_comuns": ["6 CH", "12 CH", "30 CH"],
        "apresentacoes": "Glóbulos, comprimidos, solução oral",
        "conservacao": "Embalagem fechada, ao abrigo de luz, calor e umidade.",
        "indicacoes_fabricante": "Supurações, abscessos, sensibilidade extrema, irritabilidade, tosse produtiva, piora com frio.",
        "indicacoes_registro_mapa": "Conforme farmacopeia homeopática. Requer registro MAPA desde 2017.",
        "sintomas_homeopaticos": ["supurações", "abscessos", "sensibilidade extrema", "irritabilidade", "piora com frio", "desejo de vinagre"],
        "contraindicacoes": "Não há contraindicações absolutas documentadas.",
        "precaucoes": "Uso educacional; consulte médico-veterinário.",
        "uso_veterinario": "Literatura homeopática: abscessos, feridas supuradas.",
        "fonte_informacao": "HMP_Brasil", "tipo_informacao": "Declaração de fabricantes/literatura homeopática",
        "evidencia_cientifica": "Sem ensaios clínicos controlados robustos em animais.",
        "notas": "Um dos 24 policrestos de Hahnemann."
    },
    {
        "id": "MERCURIUS_SOLUBILIS", "nome": "Mercurius Solubilis", "nome_popular": "Mercúrio Solúvel",
        "origem": "Mineral (nitrato de mercúrio amoniacal)",
        "principio_ativo_declarado": "Mercurius solubilis, potenciado conforme farmacopeia homeopática",
        "categoria": "Geral / Inflamações", "potencias_comuns": ["6 CH", "12 CH", "30 CH"],
        "apresentacoes": "Glóbulos, comprimidos, solução oral",
        "conservacao": "Embalagem fechada, ao abrigo de luz, calor e umidade.",
        "indicacoes_fabricante": "Inflamações com secreção, mau hálito, salivação, sudorese, piora à noite, gânglios inchados.",
        "indicacoes_registro_mapa": "Conforme farmacopeia homeopática. Requer registro MAPA desde 2017.",
        "sintomas_homeopaticos": ["salivação", "mau hálito", "sudorese", "piora à noite", "gânglios inchados", "secreções amareladas"],
        "contraindicacoes": "Não há contraindicações absolutas documentadas.",
        "precaucoes": "Uso educacional; consulte médico-veterinário.",
        "uso_veterinario": "Literatura homeopática: estomatites, inflamações com secreção.",
        "fonte_informacao": "HMP_Brasil", "tipo_informacao": "Declaração de fabricantes/literatura homeopática",
        "evidencia_cientifica": "Sem ensaios clínicos controlados robustos em animais.",
        "notas": "Um dos 24 policrestos de Hahnemann."
    },
    {
        "id": "CARBO_VEGETABILIS", "nome": "Carbo Vegetabilis", "nome_popular": "Carvão Vegetal",
        "origem": "Vegetal (carvão de madeira)",
        "principio_ativo_declarado": "Carbo vegetabilis, potenciado conforme farmacopeia homeopática",
        "categoria": "Digestivo / Colapso", "potencias_comuns": ["6 CH", "12 CH", "30 CH"],
        "apresentacoes": "Glóbulos, comprimidos, solução oral",
        "conservacao": "Embalagem fechada, ao abrigo de luz, calor e umidade.",
        "indicacoes_fabricante": "Distensão abdominal, gases, flatulência, fraqueza, colapso, queimação, desejo de ar fresco.",
        "indicacoes_registro_mapa": "Conforme farmacopeia homeopática. Requer registro MAPA desde 2017.",
        "sintomas_homeopaticos": ["distensão abdominal", "gases", "fraqueza", "colapso", "desejo de ar fresco", "queimação"],
        "contraindicacoes": "Não há contraindicações absolutas documentadas.",
        "precaucoes": "Uso educacional; consulte médico-veterinário.",
        "uso_veterinario": "Literatura homeopática: distúrbios digestivos com gases.",
        "fonte_informacao": "HMP_Brasil", "tipo_informacao": "Declaração de fabricantes/literatura homeopática",
        "evidencia_cientifica": "Sem ensaios clínicos controlados robustos em animais.",
        "notas": "Um dos 24 policrestos de Hahnemann."
    },
    {
        "id": "CHINA_OFFICINALIS", "nome": "China Officinalis", "nome_popular": "Quina (Cinchona)",
        "origem": "Planta (Cinchona officinalis, Rubiaceae)",
        "principio_ativo_declarado": "China officinalis, potenciado conforme farmacopeia homeopática",
        "categoria": "Digestivo / Convalescença", "potencias_comuns": ["6 CH", "12 CH", "30 CH"],
        "apresentacoes": "Glóbulos, comprimidos, solução oral",
        "conservacao": "Embalagem fechada, ao abrigo de luz, calor e umidade.",
        "indicacoes_fabricante": "Fraqueza após perda de fluidos, anemia, diarreia indolor, distensão abdominal, sensibilidade ao toque.",
        "indicacoes_registro_mapa": "Conforme farmacopeia homeopática. Requer registro MAPA desde 2017.",
        "sintomas_homeopaticos": ["fraqueza após perda de fluidos", "anemia", "diarreia indolor", "distensão", "sensibilidade ao toque", "piora com toque"],
        "contraindicacoes": "Não há contraindicações absolutas documentadas.",
        "precaucoes": "Uso educacional; consulte médico-veterinário.",
        "uso_veterinario": "Literatura homeopática: convalescença, perda de fluidos.",
        "fonte_informacao": "HMP_Brasil", "tipo_informacao": "Declaração de fabricantes/literatura homeopática",
        "evidencia_cientifica": "Sem ensaios clínicos controlados robustos em animais.",
        "notas": "A substância do experimento fundador de Hahnemann (1790); um dos 24 policrestos."
    },
    {
        "id": "IPECACUANHA", "nome": "Ipecacuanha", "nome_popular": "Ipeca (Poaya)",
        "origem": "Planta (Psychotria ipecacuanha, Rubiaceae)",
        "principio_ativo_declarado": "Ipecacuanha, potenciado conforme farmacopeia homeopática",
        "categoria": "Digestivo / Respiratório", "potencias_comuns": ["6 CH", "12 CH", "30 CH"],
        "apresentacoes": "Glóbulos, comprimidos, solução oral",
        "conservacao": "Embalagem fechada, ao abrigo de luz, calor e umidade.",
        "indicacoes_fabricante": "Náusea persistente, vômito sem alívio, língua limpa, hemorragia, tosse com náusea.",
        "indicacoes_registro_mapa": "Conforme farmacopeia homeopática. Requer registro MAPA desde 2017.",
        "sintomas_homeopaticos": ["náusea persistente", "vômito sem alívio", "língua limpa", "hemorragia", "tosse com náusea", "salivação"],
        "contraindicacoes": "Não há contraindicações absolutas documentadas.",
        "precaucoes": "Uso educacional; consulte médico-veterinário.",
        "uso_veterinario": "Literatura homeopática: vômitos, náuseas.",
        "fonte_informacao": "HMP_Brasil", "tipo_informacao": "Declaração de fabricantes/literatura homeopática",
        "evidencia_cientifica": "Sem ensaios clínicos controlados robustos em animais.",
        "notas": "Um dos 24 policrestos de Hahnemann."
    },
    {
        "id": "VERATRUM_ALBUM", "nome": "Veratrum Album", "nome_popular": "Veratro (Helleboro Branco)",
        "origem": "Planta (Veratrum album, Melanthiaceae)",
        "principio_ativo_declarado": "Veratrum album, potenciado conforme farmacopeia homeopática",
        "categoria": "Digestivo / Colapso", "potencias_comuns": ["6 CH", "12 CH", "30 CH"],
        "apresentacoes": "Glóbulos, comprimidos, solução oral",
        "conservacao": "Embalagem fechada, ao abrigo de luz, calor e umidade.",
        "indicacoes_fabricante": "Diarreia profusa com colapso, suor frio, sede de frias, vômito, extremidades frias.",
        "indicacoes_registro_mapa": "Conforme farmacopeia homeopática. Requer registro MAPA desde 2017.",
        "sintomas_homeopaticos": ["diarreia profusa", "colapso", "suor frio", "sede de frias", "extremidades frias", "vômito"],
        "contraindicacoes": "Não há contraindicações absolutas documentadas.",
        "precaucoes": "Uso educacional; consulte médico-veterinário.",
        "uso_veterinario": "Literatura homeopática: diarreias graves com colapso.",
        "fonte_informacao": "HMP_Brasil", "tipo_informacao": "Declaração de fabricantes/literatura homeopática",
        "evidencia_cientifica": "Sem ensaios clínicos controlados robustos em animais.",
        "notas": "Um dos 24 policrestos de Hahnemann."
    },
]

# ---------- 2. NOVAS EVIDÊNCIAS ----------
novas_evid = [
    {
        "estudo": "Embrapa Pecuária Sudeste — Boletim 49 (2021): complexo homeopático na prevenção de diarreia em bezerros leiteiros",
        "nivel_evidencia": "Ensaio controlado (37 bezerros, 3 grupos)",
        "conclusao": "O grupo tratado com complexo homeopático foi o único em que alguns animais não apresentaram episódio de diarreia (23,1% sem diarreia, p≤0,05). A zeólita preservou vilosidades intestinais mas não preveniu diarreia.",
        "relevancia": "Alta para homeopatia populacional em bovinos leiteiros; estudo independente (Embrapa).",
        "fonte": "https://www.infoteca.cnptia.embrapa.br/infoteca/bitstream/doc/1131493/1/BOLETIM-49.pdf"
    },
    {
        "estudo": "UFSC — Dissertação: homeopatia para mastite bovina em rebanhos leiteiros de SC",
        "nivel_evidencia": "Estudo de campo (2 rebanhos, anamnese do rebanho)",
        "conclusao": "Mitidiero (2002): redução da mastite subclínica de 44,5% para 3,9% (p<0,05) com homeopatia + bioterápicos + fitoterapia via ração. Aumento de CCS nos primeiros meses pode ocorrer (reação que antecede a cura).",
        "relevancia": "Média-alta; metodologia de anamnese do rebanho (Gênio Epidêmico).",
        "fonte": "https://repositorio.ufsc.br/bitstream/handle/123456789/175309/345473.pdf"
    },
    {
        "estudo": "Lumen et Virtus (2025) — Revisão: homeopatia no controle de parasitas em bovinos",
        "nivel_evidencia": "Revisão narrativa (SciELO, PubMed, Google Acadêmico, CAPES)",
        "conclusao": "A homeopatia pode reduzir significativamente a infestação por parasitas (ex.: Haematobia), fortalecer a imunidade e minimizar impactos ambientais — relevante para produção orgânica e sustentável.",
        "relevancia": "Média; revisão favorável, mas com limitações metodológicas dos estudos primários.",
        "fonte": "https://periodicos.newsciencepubl.com/LEV/article/download/6670/9121/26129"
    },
    {
        "estudo": "Archivos de Zootecnia (2010) — Homeopatia na terminação de novilhos em confinamento",
        "nivel_evidencia": "Estudo experimental (núcleo mineral homeopático)",
        "conclusao": "Avaliou núcleo mineral homeopático em confinamento; discute que a homeopatia é 'medicação exclusivamente energética' — sem risco de transmissão de resíduos por animais medicados.",
        "relevancia": "Média; resultados mistos, sem ganho consistente de peso.",
        "fonte": "https://www.redalyc.org/pdf/495/49520197008.pdf"
    },
    {
        "estudo": "IJRH (2019) — Lycopodium clavatum para urolitíase: ensaio randomizado duplo-cego controlado por placebo",
        "nivel_evidencia": "Ensaio clínico randomizado multicêntrico (7 centros, duplo-cego)",
        "conclusao": "Sem diferença significativa na expulsão de cálculos (P=0,31), mas diferença significativa na dor (P=0,039) e tendência positiva na disúria para o grupo verum.",
        "relevancia": "Alta metodologicamente; resultados mistos (dor sim, cálculo não).",
        "fonte": "https://www.ijrh.org/cgi/viewcontent.cgi?article=1416&context=journal"
    },
    {
        "estudo": "Medicines/MDPI (2021) — Arnica como adjuvante no manejo da dor: ensaios clínicos, mecanismos e efeitos adversos",
        "nivel_evidencia": "Revisão de ensaios clínicos",
        "conclusao": "Arnica reduziu significativamente a dor pós-cirúrgica em alguns estudos (ex.: cirurgia de mão, 2 semanas vs placebo). Efeitos mistos no geral; formulações orais não usadas na terapia moderna por citotoxicidade.",
        "relevancia": "Média; o remédio homeopático mais estudado clinicamente.",
        "fonte": "https://pmc.ncbi.nlm.nih.gov/articles/PMC8537440/"
    },
    {
        "estudo": "Teixeira MZ (2023/2024) — 'Homeopatia não é efeito placebo': dossiê de evidências (e-book trilingue)",
        "nivel_evidencia": "Dossiê com 9 revisões narrativas + centenas de artigos",
        "conclusao": "Reúne evidências sobre similitude terapêutica (efeito rebote), experimentação patogenética, ultradiluições e epidemiologia clínica homeopática. Revisão sistemática global (2023): efeitos positivos significativos da homeopatia vs placebo em metanálises.",
        "relevancia": "Alta como compilação; autoria favorável à homeopatia (Cremesp/AMHB).",
        "fonte": "https://docs.bvsalud.org/biblioref/2024/04/1551294/homeopathy-is-not-placebo-effect-proof-of-scientific-evidence-_IDHRIZT.pdf"
    },
    {
        "estudo": "Mathie RT (2003) — The research evidence base for homeopathy: fresh assessment",
        "nivel_evidencia": "Revisão de 93 RCTs (1975-2003)",
        "conclusao": "50 estudos com benefício significativo, 41 sem diferença, 2 com resposta inferior. Peso de evidência favorável em 8 condições: diarreia infantil, fibrosite, febre do feno, gripe, dor, efeitos colaterais de rádio/quimio, entorses e infecção respiratória alta.",
        "relevancia": "Alta; revisão independente (Faculty of Homeopathy, Reino Unido).",
        "fonte": "https://pubmed.ncbi.nlm.nih.gov/12725250/"
    },
    {
        "estudo": "Cochrane (2022) — Produtos homeopáticos orais para infecções respiratórias agudas em crianças",
        "nivel_evidencia": "Revisão sistemática Cochrane (11 RCTs, 1813 crianças)",
        "conclusao": "Sem benefício consistente da homeopatia vs placebo na recorrência ou cura de infecções respiratórias. Estudos com baixo risco de viés não mostraram benefício; certeza da evidência baixa a muito baixa.",
        "relevancia": "Alta; visão crítica independente (contraponto às evidências favoráveis).",
        "fonte": "https://pmc.ncbi.nlm.nih.gov/articles/PMC9746041/"
    },
]

# ---------- 3. NOVA REGULAMENTAÇÃO ----------
novas_reg = [
    {
        "aspecto": "Resolução CFMV nº 1.318/2020 — Assistência veterinária e uso de produtos",
        "descricao": "Regulamenta distribuição, guarda, prescrição, manipulação e uso de produtos (inclusive de uso humano) em estabelecimentos veterinários. Produtos de uso humano prescritos para animais devem ser adquiridos em farmácia comum (Anvisa/CFF); produtos veterinários seguem normas do MAPA.",
        "fonte": "CFMV", "status": "Vigente"
    },
    {
        "aspecto": "Resolução CFMV nº 1.690/2026 — Atendimento veterinário domiciliar",
        "descricao": "Regulamenta o atendimento domiciliar a pets de pequeno porte: atividade privativa de médicos-veterinários inscritos no CFMV/CRMVs, com prontuário obrigatório e limites de procedimentos (sem cirurgias, anestesia geral, quimioterápicos injetáveis, transfusão).",
        "fonte": "CFMV", "status": "Vigente (21/01/2026)"
    },
    {
        "aspecto": "RDC Anvisa nº 1.027/2026 — Farmacopeia Homeopática Brasileira 4ª edição",
        "descricao": "Aprova a FHB 4ª edição (vigente desde 01/07/2026), publicada eletronicamente no site da Anvisa. Orienta farmácias, laboratórios, prescritores, fiscalização e ensino da farmacotécnica homeopática.",
        "fonte": "Anvisa", "status": "Vigente (01/07/2026)"
    },
    {
        "aspecto": "RDC Anvisa nº 930/2024 — Formulário Homeopático 3ª edição",
        "descricao": "Aprova o Formulário Homeopático da Farmacopeia Brasileira, 3ª edição: 140 monografias de uso interno + 8 de uso externo. Vigente desde 09/12/2024.",
        "fonte": "Anvisa", "status": "Vigente (09/12/2024)"
    },
    {
        "aspecto": "Portaria MAPA nº 52/2021 — Sistemas Orgânicos de Produção",
        "descricao": "Autoriza preparados homeopáticos na prevenção e tratamento de enfermidades de animais em sistemas orgânicos de produção (Regulamento Técnico para Sistemas Orgânicos).",
        "fonte": "MAPA", "status": "Vigente"
    },
    {
        "aspecto": "Resolução CFMV nº 625/95 — Especialidade Homeopatia Veterinária",
        "descricao": "Reconhece a Homeopatia Veterinária como uma das primeiras especialidades da Medicina Veterinária no Brasil. Títulos concedidos a especialistas (12 vigentes, dados CRMV-SP).",
        "fonte": "CFMV", "status": "Vigente"
    },
]

# ---------- 4. NOVO GLOSSÁRIO ----------
novo_gloss = {
    "Miasma": "Predisposição crônica e profunda que, segundo Hahnemann (Doenças Crônicas, 1828), está na raiz das doenças crônicas. Os três miasmas clássicos: Psora (deficiência/prurido), Sicose (excesso/verrugas) e Sífilis (destruição/ulceração).",
    "Psora": "Miasma fundamental de Hahnemann (~85% das doenças crônicas): deficiência, prurido, hipersensibilidade, secura. Remédios: Sulphur, Calcarea carbonica, Lycopodium, Psorinum.",
    "Sicose": "Miasma ligado à gonorreia suprimida: excesso, sobrecrescimento, verrugas, catarro. Remédios: Thuja, Medorrhinum, Nitricum acidum.",
    "Sífilis (miasma)": "Miasma ligado à sífilis: destruição, ulceração, degeneração tecidual. Remédios: Mercurius, Syphilinum, Aurum.",
    "Miasma Tuberculínico": "4º miasma (J.H. Allen): mistura hereditária de Psora + Sífilis; instabilidade, mudança rápida, patologia alternante.",
    "Escala LM (Cinquenta Milesimal)": "Escala de dinamização criada por Hahnemann na 6ª edição do Organon (§270): diluição 1:50.000 por passo, 100 sucussões. Indicada para crônicos sensíveis; repetição diária. Notação: LM1, LM2... ou 0/1, 0/2...",
    "Escala Korsakoviana (K)": "Método de dinamização em frasco único (descarta o conteúdo e reutiliza o frasco): diluição centesimal aproximada. Pouco usado no Brasil.",
    "Homeopatia Populacional": "Método criado pelo Prof. Dr. Claudio Martins Real (1987): medicamentos homeopáticos incorporados aos suplementos minerais para tratar o rebanho como população. Pioneirismo da Real H (Campo Grande/MS).",
    "Efeito Rebote": "Reação secundária e paradoxal do organismo após a ação primária de um fármaco — base farmacológica moderna do princípio da similitude (estudos desde 1998).",
    "Policresto": "Medicamento de ampla esfera de ação, extensamente experimentado, que cobre muitos quadros sintomáticos. Hahnemann listou 24; a maioria dos autores conta 50-60 verdadeiros policrestos.",
    "Similimum": "O medicamento que mais se aproxima da totalidade dos sintomas característicos do paciente — o 'remédio semelhante' ideal na prescrição homeopática.",
    "Lei de Hering": "Direção da cura: os sintomas desaparecem de dentro para fora, de órgãos vitais para menos vitais, e do último para o primeiro a aparecer.",
    "Agravação Homeopática": "Piora transitória dos sintomas após a dose — interpretada na homeopatia como sinal de que o remédio agiu. Potências altas em patologia avançada podem causar agravações graves (motivo da criação da escala LM).",
    "Gênio Epidêmico": "Abordagem da homeopatia populacional/unicista: anamnese do rebanho para escolher o medicamento simillimum coletivo (ex.: Pulsatilla ou Phosphorus em rebanhos leiteiros).",
    "Farmacopeia Homeopática Brasileira (FHB)": "Compêndio oficial da Anvisa: 1ª ed. 1977; 3ª ed. 2011 (RDC 39/2011, 85 monografias); 4ª ed. 2026 (RDC 1.027/2026, vigente).",
}

# ---------- 5. NOVOS CONCEITOS ----------
novos_conc = [
    {
        "termo": "Miasmas e Doenças Crônicas",
        "definicao": "Teoria de Hahnemann (1828): doenças crônicas têm raiz em miasmas profundos (Psora, Sicose, Sífilis) que progridem mesmo com boa higiene; exigem remédios antimiasmáticos. A supressão de erupções empurra o miasma para dentro.",
        "tipo_informacao": "Conhecimento teórico homeopático",
        "evidencia_cientifica": "Sem validação científica; conceito histórico da doutrina homeopática.",
        "notas": "Base da prescrição de fundo na homeopatia clássica."
    },
    {
        "termo": "Homeopatia Populacional (Real H)",
        "definicao": "Método do Prof. Claudio Martins Real (1987): homeopatia aplicada a populações/rebanhos via suplementos minerais. Objetivos: ganho produtivo, redução de estresse, racionalização de químicos. Experimento fundador: fêmeas e bezerros mais pesados que controle.",
        "tipo_informacao": "Método comercial/empresarial (Real H Nutrição e Saúde Animal)",
        "evidencia_cientifica": "Estudos independentes limitados; Embrapa (2021) mostrou redução de diarreia em bezerros com complexo homeopático.",
        "notas": "Pioneirismo brasileiro; base da linha CMR Saúde (Carbo/MD/Farma)."
    },
    {
        "termo": "Efeito Rebote e a Lei dos Semelhantes",
        "definicao": "Fundamentação farmacológica da similitude: a reação secundária do organismo, oposta à ação primária do medicamento (efeito rebote/paradoxal), é análoga à cura homeopática. Estudada desde 1998 (Rev. Assoc. Med. Bras.).",
        "tipo_informacao": "Hipótese científica (farmacologia)",
        "evidencia_cientifica": "Linha de pesquisa publicada em periódicos revisados; interpretação debatida.",
        "notas": "Base do e-book 'Homeopathy is not placebo effect' (Teixeira, 2023/2024)."
    },
]

# ---------- 6. NOVAS PERGUNTAS DE REVISÃO ----------
novas_perg = [
    "O que são os três miasmas de Hahnemann e como influenciam a prescrição de fundo?",
    "O que é a Homeopatia Populacional e quem a criou no Brasil?",
    "Quais são as diferenças entre as escalas CH, DH, LM e Korsakoviana?",
    "O que diz a Farmacopeia Homeopática Brasileira 4ª edição (RDC 1.027/2026)?",
    "Quais evidências independentes existem para homeopatia em bovinos (Embrapa, UFSC)?",
    "O que é o efeito rebote e como se relaciona com a lei dos semelhantes?",
    "Quais são os 20 policrestos essenciais que todo estudante deve conhecer?",
    "Como a Portaria MAPA 52/2021 trata a homeopatia em sistemas orgânicos?",
    "Qual a diferença entre matéria médica e repertório na prática homeopática?",
    "O que diz a revisão Cochrane (2022) sobre homeopatia em infecções respiratórias infantis?",
]

# ---------- 7. METADATA ATUALIZADA ----------
base["metadata"]["versao"] = "2.0.0"
base["metadata"]["data_atualizacao"] = "2026-09-09"
base["metadata"]["descricao"] = "Base de dados educacional sobre homeopatia veterinária com rastreamento de fontes — expandida com policrestos clássicos, evidências independentes (Embrapa, UFSC, Cochrane) e regulamentação 2024-2026"
base["metadata"]["fontes_principais"].extend([
    {"id": "EMBRAPA_2021", "nome": "Embrapa Pecuária Sudeste — Boletim 49 (2021)", "tipo": "Científico", "url": "https://www.infoteca.cnptia.embrapa.br/infoteca/bitstream/doc/1131493/1/BOLETIM-49.pdf", "resumo": "Complexo homeopático reduziu diarreia em bezerros leiteiros (p≤0,05)"},
    {"id": "UFSC_MASTITE", "nome": "UFSC — Homeopatia para mastite bovina (dissertação)", "tipo": "Científico", "url": "https://repositorio.ufsc.br/bitstream/handle/123456789/175309/345473.pdf", "resumo": "Redução de mastite subclínica de 44,5% para 3,9% (p<0,05)"},
    {"id": "COCHRANE_2022", "nome": "Cochrane (2022) — Homeopatia oral em infecções respiratórias infantis", "tipo": "Científico", "url": "https://pmc.ncbi.nlm.nih.gov/articles/PMC9746041/", "resumo": "Sem benefício consistente vs placebo; certeza baixa a muito baixa"},
    {"id": "ANVISA_FHB4", "nome": "RDC Anvisa 1.027/2026 — Farmacopeia Homeopática 4ª ed.", "tipo": "Regulatório", "url": "https://www.gov.br/anvisa/pt-br/assuntos/farmacopeia/farmacopeia-homeopatica", "resumo": "FHB 4ª edição vigente desde 01/07/2026"},
    {"id": "CFMV_1690_2026", "nome": "Resolução CFMV 1.690/2026 — Atendimento domiciliar", "tipo": "Regulatório", "url": "https://www.cfmv.gov.br", "resumo": "Regulamenta atendimento veterinário domiciliar (21/01/2026)"},
    {"id": "REALH_HP", "nome": "Real H — Homeopatia Populacional (Claudio Martins Real)", "tipo": "Técnico", "url": "https://www.realh.com.br", "resumo": "Método populacional de homeopatia em suplementos minerais; linhas CMR Saúde"},
    {"id": "AMHB_LISTA_2025", "nome": "AMHB — Lista de medicamentos TEH 2025", "tipo": "Profissional", "url": "https://amhb.org.br", "resumo": "116 medicamentos para o Exame de Suficiência em Homeopatia 2025"},
])

# ---------- 8. APLICAR ----------
base["medicamentos"].extend(novos_meds)
base["evidencias_cientificas"].extend(novas_evid)
base["regulamentacao_brasil"].extend(novas_reg)
base["glossario"].update(novo_gloss)
base["conceitos_fundamentais"].extend(novos_conc)
base["perguntas_revisao"].extend(novas_perg)

# Reescrever o HTML com o novo BASE
novo_json = json.dumps(base, ensure_ascii=False, separators=(",", ":"))
html_novo = html[:m.start(1)] + novo_json + html[m.end(1):]
open(PATH, "w", encoding="utf-8").write(html_novo)

print("=== ATUALIZAÇÃO CONCLUÍDA (v2.0.0) ===")
print(f"Medicamentos: {len(base['medicamentos'])} (antes 12)")
print(f"Evidências: {len(base['evidencias_cientificas'])} (antes 5)")
print(f"Regulamentação: {len(base['regulamentacao_brasil'])} (antes 4)")
print(f"Glossário: {len(base['glossario'])} termos (antes 10)")
print(f"Conceitos: {len(base['conceitos_fundamentais'])} (antes 4)")
print(f"Perguntas de revisão: {len(base['perguntas_revisao'])} (antes 10)")
print(f"Tamanho do HTML: {len(html_novo)} bytes")
