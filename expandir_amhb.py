# -*- coding: utf-8 -*-
"""Expande HomeoVet para os 123 medicamentos da lista AMHB TEH 2025 (v3.0.0)."""
import re, json

PATH = r"C:\Users\JEANPC\homeovet\index.html"
html = open(PATH, encoding="utf-8").read()
m = re.search(r"const BASE = (\{.*?\});\n", html, re.S)
base = json.loads(m.group(1))

existentes = {x["nome"].lower() for x in base["medicamentos"]}

# (nome, nome_popular, origem, categoria, indicacoes, sintomas)
# Categorias seguem o padrão já usado (Sistema / Esfera)
NOVOS = [
    ("Actaea Racemosa", "Cimicífuga (Black Cohosh)", "Planta (Actaea racemosa, Ranunculaceae)", "Feminino / Musculoesquelético", "Dores musculares e articulares, cólicas menstruais, parto difícil, insônia por dores.", ["dores musculares", "cólica menstrual", "parto difícil", "insônia por dor", "piora com menstruação"]),
    ("Actaea Spicata", "Cimicífuga Racemosa (variedade)", "Planta (Actaea spicata, Ranunculaceae)", "Articular / Traumatologia", "Dores articulares agudas, punho e mãos, contusões, reumatismo articular.", ["dor articular aguda", "punho", "mãos", "contusão", "piora com movimento"]),
    ("Aesculus Hippocastanum", "Castanha-da-Índia", "Planta (Aesculus hippocastanum, Sapindaceae)", "Circulatório / Venoso", "Varizes, hemorroidas, congestão venosa, dor lombar com sensação de plenitude.", ["varizes", "hemorroidas", "congestão venosa", "dor lombar", "sensação de plenitude"]),
    ("Agaricus Muscarius", "Amanita (Cogumelo)", "Fungo (Amanita muscaria)", "Nervoso / Tremores", "Tremores, espasmos, formigamento, coreia, sensação de agulhadas, hipersensibilidade.", ["tremores", "espasmos", "formigamento", "agulhadas", "hipersensibilidade"]),
    ("Agraphis Nutans", "Jacinto-dos-Bosques", "Planta (Hyacinthoides non-scripta)", "Otorrino / Seios da face", "Congestão nasal, adenoides, surdez por obstrução tubária, secreção espessa.", ["congestão nasal", "adenoides", "surdez", "secreção espessa"]),
    ("Ailanthus Glandulosa", "Árvore-do-Céu", "Planta (Ailanthus altissima)", "Febre / Infeccioso", "Febres eruptivas, escarlatina, difteria, prostração, língua vermelha.", ["febre eruptiva", "escarlatina", "difteria", "prostração", "língua vermelha"]),
    ("Allium Cepa", "Cebola", "Planta (Allium cepa, Amaryllidaceae)", "Nariz / Olhos", "Coriza aquosa e irritante, lacrimejamento, espirros, piora em ambientes quentes.", ["coriza aquosa", "lacrimejamento", "espirros", "piora em ambiente quente"]),
    ("Aloe Socotrina", "Babosa (Aloe)", "Planta (Aloe socotrina, Asphodelaceae)", "Digestivo / Reto", "Diarreia matinal, urgência fecal, hemorroidas, sensação de peso no reto.", ["diarreia matinal", "urgência fecal", "hemorroidas", "peso no reto"]),
    ("Anacardium Orientale", "Castanha-de-Caju (semilha)", "Planta (Semecarpus anacardium)", "Mental / Digestivo", "Falta de confiança, irritabilidade, sensação de prego na cabeça, azia, piora com estômago vazio.", ["falta de confiança", "irritabilidade", "prego na cabeça", "azia", "piora em jejum"]),
    ("Antimonium Crudum", "Sulfeto de Antimônio", "Mineral (Sb2S3)", "Digestivo / Pele", "Distúrbios digestivos por excessos, língua branca espessa, verrugas, calos, irritabilidade em crianças.", ["língua branca", "verrugas", "calos", "excessos alimentares", "irritabilidade"]),
    ("Antimonium Tartaricum", "Tártaro Emético", "Mineral (tartarato de antimônio e potássio)", "Respiratório / Bronquite", "Bronquite com secreção abundante, respiração ruidosa, sonolência, náusea, fraqueza.", ["bronquite", "secreção abundante", "respiração ruidosa", "sonolência", "náusea"]),
    ("Argentum Nitricum", "Nitrato de Prata", "Mineral (AgNO3)", "Mental / Digestivo", "Ansiedade antecipatória, pressa, medo de fracassar, diarreia por ansiedade, flatulência.", ["ansiedade antecipatória", "pressa", "medo de fracassar", "diarreia por ansiedade", "flatulência"]),
    ("Artemisia Vulgaris", "Artemísia", "Planta (Artemisia vulgaris, Asteraceae)", "Nervoso / Epilepsia", "Epilepsia, sonambulismo, histeria, convulsões, pesadelos.", ["epilepsia", "sonambulismo", "histeria", "convulsões", "pesadelos"]),
    ("Aurum Metallicum", "Ouro", "Mineral (Au)", "Mental / Cardíaco", "Depressão profunda, autodesprezo, hipertensão, cardiopatias, dores ósseas noturnas.", ["depressão profunda", "autodesprezo", "hipertensão", "cardiopatia", "dor óssea noturna"]),
    ("Baptisia Tinctoria", "Índigo Selvagem", "Planta (Baptisia tinctoria, Fabaceae)", "Febre / Infeccioso", "Febres tifoides, prostração, sensação de corpo dividido, odor fétido, língua marrom.", ["febre tifoide", "prostração", "corpo dividido", "odor fétido", "língua marrom"]),
    ("Baryta Carbonica", "Carbonato de Bário", "Mineral (BaCO3)", "Constitucional / Desenvolvimento", "Crianças com desenvolvimento lento, timidez, adenoides, hipertensão em idosos, medo de estranhos.", ["desenvolvimento lento", "timidez", "adenoides", "hipertensão", "medo de estranhos"]),
    ("Borax Veneta", "Borato de Sódio", "Mineral (Na2B4O7)", "Mucosas / Candidíase", "Aftas, candidíase oral, sensibilidade a ruídos, medo de movimento para baixo, mucosas inflamadas.", ["aftas", "candidíase", "sensibilidade a ruídos", "medo de movimento para baixo"]),
    ("Cactus Grandiflorus", "Cacto (Flor da Noite)", "Planta (Selenicereus grandiflorus)", "Cardíaco / Circulatório", "Palpitações, sensação de constrição (como arame), dor cardíaca, congestão.", ["palpitações", "constrição", "dor cardíaca", "congestão"]),
    ("Calcarea Fluorica", "Fluoreto de Cálcio", "Mineral (CaF2)", "Tecidos / Varizes", "Varizes, fissuras, hérnias, endurecimentos, tendência a luxações, cicatrizes queloides.", ["varizes", "fissuras", "hérnias", "luxações", "queloides"]),
    ("Calcarea Phosphorica", "Fosfato de Cálcio", "Mineral (Ca3(PO4)2)", "Ósseo / Crescimento", "Problemas ósseos, dentição difícil, crescimento rápido, dores que pioram com mudança de tempo, anemia.", ["problemas ósseos", "dentição difícil", "crescimento rápido", "piora com mudança de tempo", "anemia"]),
    ("Calcarea Sulphurica", "Sulfato de Cálcio", "Mineral (CaSO4)", "Pele / Supurações", "Supurações crônicas, acne, abscessos que não fecham, secreção amarelo-esverdeada.", ["supurações crônicas", "acne", "abscessos", "secreção amarelo-esverdeada"]),
    ("Calendula Officinalis", "Calêndula", "Planta (Calendula officinalis, Asteraceae)", "Pele / Cicatrização", "Cicatrização de feridas, cortes, queimaduras leves, prevenção de infecção, uso tópico.", ["cicatrização", "feridas", "cortes", "queimaduras leves", "uso tópico"]),
    ("Camphora", "Cânfora", "Planta (Cinnamomum camphora)", "Colapso / Febre", "Colapso com extremidades frias, febre com calafrios, choque, sudorese fria.", ["colapso", "extremidades frias", "calafrios", "choque", "sudorese fria"]),
    ("Carcinosinum", "Nosódio de Câncer", "Nosódio (preparado de tecido tumoral)", "Constitucional / Sensível", "Constitucional de pacientes sensíveis, conscienciosos, amantes de música, histórico familiar de câncer.", ["sensibilidade", "consciencioso", "amante de música", "histórico familiar"]),
    ("Caulophyllum", "Blue Cohosh", "Planta (Caulophyllum thalictroides)", "Feminino / Parto", "Dismenorreia, parto difícil, contrações irregulares, problemas de ovulação.", ["dismenorreia", "parto difícil", "contrações irregulares", "ovulação"]),
    ("Causticum Hahnemannii", "Cáustico de Hahnemann", "Preparado (sulfato de potássio e cal)", "Nervoso / Paralisia", "Paralisias, fraqueza muscular, rouquidão, tosse seca, queimaduras, contraturas, medo do escuro.", ["paralisia", "fraqueza muscular", "rouquidão", "tosse seca", "queimaduras"]),
    ("Chelidonium Majus", "Celidônia", "Planta (Chelidonium majus, Papaveraceae)", "Hepático / Digestivo", "Problemas hepáticos, icterícia, dor no ombro direito, constipação, língua amarelada.", ["fígado", "icterícia", "dor no ombro direito", "constipação", "língua amarelada"]),
    ("Cicuta Virosa", "Cicuta (Conium maculatum)", "Planta (Cicuta virosa, Apiaceae)", "Nervoso / Convulsões", "Convulsões, espasmos, rigidez, medo, sensação de estranheza, epilepsia.", ["convulsões", "espasmos", "rigidez", "epilepsia"]),
    ("Cina Maritima", "Semente-de-lombriga", "Planta (Artemisia cina)", "Parasitas / Infantil", "Verminoses, irritabilidade infantil, ranger de dentes, coceira no nariz, apetite voraz.", ["verminoses", "irritabilidade infantil", "ranger de dentes", "coceira no nariz", "apetite voraz"]),
    ("Cocculus Indicus", "Coco-de-Levante", "Planta (Anamirta cocculus)", "Nervoso / Enjoo", "Enjoo de movimento, vertigem, insônia por exaustão, sensibilidade a odores, fraqueza.", ["enjoo de movimento", "vertigem", "insônia por exaustão", "sensibilidade a odores"]),
    ("Coffea Cruda", "Café Cru", "Planta (Coffea arabica, Rubiaceae)", "Nervoso / Insônia", "Insônia por mente acelerada, hipersensibilidade, agitação, dores intoleráveis.", ["insônia", "mente acelerada", "hipersensibilidade", "agitação", "dores intoleráveis"]),
    ("Colocynthis", "Coloquíntida", "Planta (Citrullus colocynthis)", "Digestivo / Cólicas", "Cólicas abdominais intensas que melhoram com pressão forte e flexão, neuralgia, raiva.", ["cólica intensa", "melhora com pressão", "neuralgia", "raiva"]),
    ("Conium Maculatum", "Cicuta-Maior", "Planta (Conium maculatum, Apiaceae)", "Glandular / Idosos", "Endurecimento de glândulas, tontura ao deitar, fraqueza em idosos, problemas prostáticos.", ["glândulas endurecidas", "tontura ao deitar", "fraqueza em idosos", "próstata"]),
    ("Corallium Rubrum", "Coral Vermelho", "Animal (coral vermelho)", "Respiratório / Tosse", "Tosse convulsiva em acessos, coqueluche, espirros em salva.", ["tosse convulsiva", "coqueluche", "espirros em salva"]),
    ("Crataegus Oxyacantha", "Espinheiro-Alvar", "Planta (Crataegus oxyacantha, Rosaceae)", "Cardíaco / Tônico", "Insuficiência cardíaca, arritmias, fraqueza do miocárdio, hipertensão, tônico cardíaco.", ["insuficiência cardíaca", "arritmias", "fraqueza do miocárdio", "hipertensão"]),
    ("Crotalus Horridus", "Veneno de Cascavel", "Animal (veneno de Crotalus horridus)", "Hemorrágico / Séptico", "Hemorragias, septicemia, icterícia, tendência a sangramento, febres hemorrágicas.", ["hemorragia", "septicemia", "icterícia", "febre hemorrágica"]),
    ("Cuprum Metallicum", "Cobre", "Mineral (Cu)", "Nervoso / Espasmos", "Espasmos, cãibras, convulsões, cólicas, asma com espasmo, contrações musculares.", ["espasmos", "cãibras", "convulsões", "asma espasmódica"]),
    ("Cyclamen Europaeum", "Ciclame", "Planta (Cyclamen europaeum, Primulaceae)", "Feminino / Visão", "Distúrbios menstruais, enxaqueca com distúrbios visuais, aversão a gordura, humor mutável.", ["distúrbios menstruais", "enxaqueca", "distúrbios visuais", "aversão a gordura"]),
    ("Dioscorea Villosa", "Inhame Selvagem", "Planta (Dioscorea villosa)", "Digestivo / Cólicas", "Cólicas que irradiam, flatulência, dores que melhoram ao esticar, cólica biliar.", ["cólica irradiante", "flatulência", "melhora ao esticar", "cólica biliar"]),
    ("Drosera Rotundifolia", "Drosera (Orvalhinha)", "Planta (Drosera rotundifolia, Droseraceae)", "Respiratório / Tosse", "Tosse convulsiva, coqueluche, tosse com vômito, rouquidão, piora à noite.", ["tosse convulsiva", "coqueluche", "tosse com vômito", "rouquidão", "piora à noite"]),
    ("Dulcamara", "Doce-Amarga", "Planta (Solanum dulcamara)", "Pele / Reumatismo", "Erupções por frio e umidade, reumatismo por mudança de tempo, urticária, bronquite úmida.", ["erupções por frio", "reumatismo por tempo", "urticária", "bronquite úmida"]),
    ("Echinacea Angustifolia", "Equinácea", "Planta (Echinacea angustifolia, Asteraceae)", "Imunidade / Infeccioso", "Imunoestimulante, septicemia, infecções recorrentes, gânglios inchados, fraqueza.", ["imunoestimulante", "infecções recorrentes", "gânglios inchados", "septicemia"]),
    ("Euphrasia Officinalis", "Eufrásia", "Planta (Euphrasia officinalis)", "Olhos / Nariz", "Conjuntivite, lacrimejamento irritante, coriza com secreção suave, fotofobia.", ["conjuntivite", "lacrimejamento", "coriza", "fotofobia"]),
    ("Eupatorium Perfoliatum", "Eupatório", "Planta (Eupatorium perfoliatum)", "Febre / Gripe", "Gripe com dores ósseas intensas, febre, sede, calafrios, tosse seca.", ["gripe", "dores ósseas", "febre", "calafrios", "tosse seca"]),
    ("Fluoricum Acidum", "Ácido Fluorídrico", "Mineral (HF)", "Tecidos / Destruição", "Varizes, úlceras, problemas dentários, destruição tecidual, tendência a fístulas.", ["varizes", "úlceras", "problemas dentários", "fístulas"]),
    ("Glonoinum", "Nitroglicerina", "Químico (C3H5N3O9)", "Cefaleia / Vascular", "Enxaqueca pulsátil, congestão cefálica, calor na cabeça, hipertensão, piora com sol.", ["enxaqueca pulsátil", "congestão cefálica", "calor na cabeça", "hipertensão", "piora com sol"]),
    ("Graphites Naturalis", "Grafite", "Mineral (C)", "Pele / Digestivo", "Eczema com secreção melosa, pele rachada, cicatrizes, constipação, unhas deformadas.", ["eczema", "secreção melosa", "pele rachada", "constipação", "unhas deformadas"]),
    ("Hamamelis Virginica", "Hamamélis", "Planta (Hamamelis virginiana)", "Venoso / Hemorroidas", "Varizes, hemorroidas, veias dilatadas, hemorragias venosas, flebite.", ["varizes", "hemorroidas", "veias dilatadas", "hemorragia venosa", "flebite"]),
    ("Helonias Dioica", "Helonias (Falso Unicórnio)", "Planta (Chamaelirium luteum)", "Feminino / Útero", "Fraqueza uterina, prolapso, leucorreia, diabetes, exaustão pós-parto.", ["fraqueza uterina", "prolapso", "leucorreia", "exaustão pós-parto"]),
    ("Hydrastis Canadensis", "Selo-de-Ouro", "Planta (Hydrastis canadensis)", "Mucosas / Digestivo", "Inflamação de mucosas, secreção amarela espessa, constipação, úlceras, catarro.", ["inflamação de mucosas", "secreção amarela", "constipação", "úlceras", "catarro"]),
    ("Hyoscyamus Niger", "Meimendro-Negro", "Planta (Hyoscyamus niger)", "Mental / Delírio", "Delírio, alucinações, ciúme, exposição, convulsões, tosse noturna, medo de envenenamento.", ["delírio", "alucinações", "ciúme", "convulsões", "tosse noturna"]),
    ("Hypericum Perforatum", "Erva-de-São-João", "Planta (Hypericum perforatum)", "Nervoso / Traumatismo", "Lesões de nervos, dor neuropática, feridas com pontadas, trauma de dedos e cauda, tétano.", ["lesão de nervos", "dor neuropática", "pontadas", "trauma de dedos", "tétano"]),
    ("Iodium Purum", "Iodo", "Mineral (I2)", "Glandular / Emagrecimento", "Hipertireoidismo, emagrecimento com apetite, glândulas aumentadas, calor, inquietação.", ["hipertireoidismo", "emagrecimento", "glândulas aumentadas", "calor", "inquietação"]),
    ("Iris Versicolor", "Íris (Blue Flag)", "Planta (Iris versicolor)", "Digestivo / Enxaqueca", "Enxaqueca com vômito bilioso, azia, diarreia, problemas de pâncreas, salivação.", ["enxaqueca com vômito", "azia", "diarreia", "pâncreas", "salivação"]),
    ("Kali Bichromicum", "Bicromato de Potássio", "Mineral (K2Cr2O7)", "Mucosas / Secreções", "Secreções espessas e fibrosas, sinusite, bronquite, úlceras, dores que mudam de lugar.", ["secreção espessa", "sinusite", "bronquite", "úlceras", "dores que mudam"]),
    ("Kali Carbonicum", "Carbonato de Potássio", "Mineral (K2CO3)", "Respiratório / Constitucional", "Fraqueza, dores nas costas, edema, bronquite em idosos, sensibilidade ao frio, piora às 2-4h.", ["fraqueza", "dores nas costas", "edema", "bronquite", "piora às 2-4h"]),
    ("Kali Muriaticum", "Cloreto de Potássio", "Mineral (KCl)", "Mucosas / Gânglios", "Secreção branca espessa, gânglios, otite, eczema, língua cinzenta.", ["secreção branca", "gânglios", "otite", "eczema", "língua cinzenta"]),
    ("Kali Phosphoricum", "Fosfato de Potássio", "Mineral (K3PO4)", "Nervoso / Exaustão", "Exaustão nervosa, esgotamento mental, insônia por cansaço, fraqueza, ansiedade.", ["exaustão nervosa", "esgotamento mental", "insônia por cansaço", "fraqueza", "ansiedade"]),
    ("Kalmia Latifolia", "Loureiro-da-Montanha", "Planta (Kalmia latifolia)", "Cardíaco / Neuralgia", "Neuralgia, dor que desce, reumatismo, palpitações, dor cardíaca com pulso lento.", ["neuralgia", "dor descendente", "reumatismo", "palpitações", "pulso lento"]),
    ("Kreosotum", "Creosoto", "Químico (destilado de alcatrão)", "Feminino / Mucosas", "Leucorreia irritante, prurido, hemorragia, problemas dentários, vômito em jato.", ["leucorreia irritante", "prurido", "hemorragia", "problemas dentários", "vômito em jato"]),
    ("Latrodectus Mactans", "Viúva-Negra", "Animal (veneno de Latrodectus mactans)", "Cardíaco / Dor", "Dor cardíaca intensa, constrição torácica, ansiedade de morte, hipertensão.", ["dor cardíaca intensa", "constrição torácica", "ansiedade de morte", "hipertensão"]),
    ("Ledum Palustre", "Ledum (Alecrim-dos-Pântanos)", "Planta (Ledum palustre)", "Traumatologia / Picadas", "Picadas de insetos, feridas perfurantes, contusões, reumatismo que sobe, piora com calor.", ["picadas de insetos", "feridas perfurantes", "contusões", "reumatismo ascendente", "piora com calor"]),
    ("Lilium Tigrinum", "Lírio-Tigre", "Planta (Lilium tigrinum)", "Feminino / Cardíaco", "Sensação de peso pélvico, irritabilidade, palpitações, fluxo menstrual intenso, pressa.", ["peso pélvico", "irritabilidade", "palpitações", "fluxo intenso", "pressa"]),
    ("Magnesia Phosphorica", "Fosfato de Magnésio", "Mineral (Mg3(PO4)2)", "Nervoso / Cólicas", "Cólicas e espasmos que melhoram com pressão e calor, neuralgia, cãibras.", ["cólica", "espasmos", "melhora com pressão e calor", "neuralgia", "cãibras"]),
    ("Medorrhinum", "Nosódio de Gonorreia", "Nosódio (secreção gonocócica)", "Constitucional / Sicótico", "Constitucional sicótico, hiperatividade, medo do escuro, problemas de pele, histórico de gonorreia.", ["sicótico", "hiperatividade", "medo do escuro", "problemas de pele"]),
    ("Mezereum", "Mezereão (Dafne)", "Planta (Daphne mezereum)", "Pele / Nervos", "Eczema com crostas espessas, neuralgia, dor óssea, piora à noite, coceira intensa.", ["eczema com crostas", "neuralgia", "dor óssea", "piora à noite", "coceira intensa"]),
    ("Murex", "Múrice (Caracol)", "Animal (Murex brandaris)", "Feminino / Útero", "Sensação de peso e prolapso uterino, fluxo intenso, desejo sexual aumentado, irritabilidade.", ["peso uterino", "prolapso", "fluxo intenso", "irritabilidade"]),
    ("Naja Tripudians", "Cobra Naja", "Animal (veneno de Naja tripudians)", "Cardíaco / Nervoso", "Problemas cardíacos, palpitações, paralisia, medo de morte, afasia.", ["problemas cardíacos", "palpitações", "paralisia", "medo de morte", "afasia"]),
    ("Nitricum Acidum", "Ácido Nítrico", "Mineral (HNO3)", "Pele / Mucosas", "Fissuras, verrugas, úlceras com bordas irregulares, dores em lascas, mau humor.", ["fissuras", "verrugas", "úlceras irregulares", "dores em lascas", "mau humor"]),
    ("Petroleum", "Petróleo", "Químico (óleo mineral)", "Pele / Digestivo", "Pele seca e rachada, eczema, enjoo, diarreia matinal, piora no inverno.", ["pele seca", "eczema", "enjoo", "diarreia matinal", "piora no inverno"]),
    ("Phytolacca Decandra", "Fitolaça", "Planta (Phytolacca decandra)", "Glandular / Mamário", "Mastite, dores mamárias, gânglios, reumatismo, garganta escura, dores que pioram com frio.", ["mastite", "dores mamárias", "gânglios", "reumatismo", "garganta escura"]),
    ("Plantago Major", "Tanchagem", "Planta (Plantago major)", "Otorrino / Dental", "Dor de ouvido, dor de dente, neuralgia, diarreia, enurese.", ["dor de ouvido", "dor de dente", "neuralgia", "diarreia", "enurese"]),
    ("Platinum Metallicum", "Platina", "Mineral (Pt)", "Mental / Feminino", "Sensação de superioridade, formigamento, menstruação intensa, hipersensibilidade, rigidez.", ["superioridade", "formigamento", "menstruação intensa", "hipersensibilidade", "rigidez"]),
    ("Plumbum Metallicum", "Chumbo", "Mineral (Pb)", "Nervoso / Paralisia", "Paralisia, atrofia muscular, cólicas com abdome retraído, constipação, anemia, neurite.", ["paralisia", "atrofia muscular", "cólica com abdome retraído", "constipação", "neurite"]),
    ("Psorinum", "Nosódio de Sarna", "Nosódio (secreção de sarna)", "Pele / Constitucional", "Prurido intenso, pele oleosa, aversão a frio, desesperança, histórico de sarna, piora no inverno.", ["prurido intenso", "pele oleosa", "aversão a frio", "desesperança", "piora no inverno"]),
    ("Pyrogenium", "Nosódio de Pus", "Nosódio (material séptico)", "Séptico / Febre", "Septicemia, febre alta com pulso rápido, odor fétido, prostração, infecções profundas.", ["septicemia", "febre alta", "odor fétido", "prostração", "infecções profundas"]),
    ("Ranunculus Bulbosus", "Botão-de-Ouro", "Planta (Ranunculus bulbosus)", "Nervoso / Pele", "Neuralgia intercostal, herpes zoster, bolhas, dores que pioram com toque e tempo úmido.", ["neuralgia intercostal", "herpes zoster", "bolhas", "piora com toque", "piora com umidade"]),
    ("Ruta Graveolens", "Arruda", "Planta (Ruta graveolens)", "Traumatologia / Tendões", "Lesões de tendões e ligamentos, entorses, periósteo, esforço ocular, dores como de osso quebrado.", ["lesão de tendões", "entorses", "periósteo", "esforço ocular", "dor como osso quebrado"]),
    ("Sabina", "Sabina (Zimbro)", "Planta (Juniperus sabina)", "Feminino / Hemorrágico", "Hemorragia uterina com coágulos, aborto, menstruação intensa, dor sacral.", ["hemorragia uterina", "coágulos", "aborto", "menstruação intensa", "dor sacral"]),
    ("Sanguinaria Canadensis", "Sanguinária", "Planta (Sanguinaria canadensis)", "Respiratório / Enxaqueca", "Enxaqueca do lado direito, congestão, tosse, problemas respiratórios, ondas de calor.", ["enxaqueca direita", "congestão", "tosse", "ondas de calor"]),
    ("Secale Cornutum", "Ergot (Centeio Espigado)", "Fungo (Claviceps purpurea)", "Circulatório / Contratura", "Contratura, formigamento, hemorragia, extremidades frias, piora com calor, gangrena.", ["contratura", "formigamento", "hemorragia", "extremidades frias", "piora com calor"]),
    ("Sepia Succus", "Tinta de Choco (Sepia)", "Animal (tinta de Sepia officinalis)", "Feminino / Constitucional", "Exaustão, indiferença, problemas hormonais, menopausa, sensação de peso pélvico, piora com responsabilidade.", ["exaustão", "indiferença", "menopausa", "peso pélvico", "piora com responsabilidade"]),
    ("Spigelia Anthelmintica", "Espigélia", "Planta (Spigelia anthelmintica)", "Cardíaco / Neuralgia", "Neuralgia facial, dor cardíaca, palpitações, dor que piora com movimento, verminoses.", ["neuralgia facial", "dor cardíaca", "palpitações", "piora com movimento"]),
    ("Staphysagria", "Estafisagria", "Planta (Delphinium staphisagria)", "Mental / Pós-cirúrgico", "Raiva reprimida, sensibilidade, pós-cirúrgico, cistite, problemas de pele, dentição.", ["raiva reprimida", "pós-cirúrgico", "cistite", "problemas de pele", "dentição"]),
    ("Stramonium", "Estramônio (Figueira-do-Inferno)", "Planta (Datura stramonium)", "Mental / Delírio", "Delírio violento, medo do escuro, alucinações, convulsões, agitação extrema.", ["delírio violento", "medo do escuro", "alucinações", "convulsões", "agitação extrema"]),
    ("Streptococcinum", "Nosódio de Streptococcus", "Nosódio (cultura de estreptococo)", "Infeccioso / Recorrente", "Infecções estreptocócicas recorrentes, amigdalite, faringite, complicações pós-infecciosas.", ["infecções recorrentes", "amigdalite", "faringite", "pós-infeccioso"]),
    ("Sulphuricum Acidum", "Ácido Sulfúrico", "Mineral (H2SO4)", "Digestivo / Fraqueza", "Fraqueza, tremores, azia, diarreia, hematomas fáceis, sede intensa.", ["fraqueza", "tremores", "azia", "diarreia", "hematomas fáceis"]),
    ("Symphytum Officinale", "Consolda (Confrei)", "Planta (Symphytum officinale)", "Traumatologia / Ósseo", "Fraturas, consolidação óssea, dor no periósteo, lesões oculares por trauma, pontadas.", ["fraturas", "consolidação óssea", "periósteo", "trauma ocular", "pontadas"]),
    ("Syphillinum", "Nosódio de Sífilis", "Nosódio (material sifilítico)", "Constitucional / Destrutivo", "Constitucional sifilítico, destruição tecidual, úlceras, dores noturnas, histórico familiar.", ["sifilítico", "destruição tecidual", "úlceras", "dores noturnas"]),
    ("Tarentula Hispanica", "Tarântula", "Animal (Lycosa tarentula)", "Mental / Agitação", "Agitação extrema, inquietação, destruição, ritmo, piora com música, alívio com movimento.", ["agitação extrema", "inquietação", "destruição", "ritmo", "alívio com movimento"]),
    ("Tuberculinum Koch", "Nosódio de Tuberculose", "Nosódio (cultura de tuberculose)", "Constitucional / Instável", "Constitucional tuberculínico, insatisfação, desejo de viajar, problemas respiratórios recorrentes, intolerância a restrição.", ["tuberculínico", "insatisfação", "desejo de viajar", "respiratório recorrente", "intolerância a restrição"]),
    ("Ustilago Maydis", "Carvão do Milho", "Fungo (Ustilago maydis)", "Feminino / Hemorrágico", "Hemorragia uterina, fluxo intenso, ovários, dores em jato, problemas de pele.", ["hemorragia uterina", "fluxo intenso", "ovários", "dores em jato"]),
    ("Veratrum Viride", "Veratro-Verde", "Planta (Veratrum viride)", "Febre / Cardiovascular", "Febre alta com congestão, hipertensão, náusea, pulso cheio, delírio.", ["febre alta", "congestão", "hipertensão", "náusea", "pulso cheio"]),
    ("Vinca Minor", "Vinca (Pervinca)", "Planta (Vinca minor)", "Pele / Couro Cabeludo", "Eczema do couro cabeludo, crostas, prurido, problemas de pele com secreção.", ["eczema do couro cabeludo", "crostas", "prurido"]),
    ("Viscum Album", "Visco", "Planta (Viscum album)", "Circulatório / Tumoral", "Hipertensão, arteriosclerose, tumores (uso adjuvante), epilepsia, dores articulares.", ["hipertensão", "arteriosclerose", "tumores", "epilepsia", "dores articulares"]),
    ("Zincum Metallicum", "Zinco", "Mineral (Zn)", "Nervoso / Exaustão", "Exaustão nervosa, inquietação das pernas, hipersensibilidade, atraso de desenvolvimento, tremores.", ["exaustão nervosa", "inquietação das pernas", "hipersensibilidade", "atraso de desenvolvimento", "tremores"]),
]

def origem_tipo(origem):
    o = origem.lower()
    if "planta" in o: return "Vegetal"
    if "mineral" in o: return "Mineral"
    if "animal" in o or "veneno" in o or "tinta" in o: return "Animal"
    if "nosódio" in o: return "Nosódio"
    if "fungo" in o: return "Fungo"
    if "químico" in o or "preparado" in o: return "Químico/Preparado"
    return "Outro"

adicionados = 0
for nome, popular, origem, categoria, indicacoes, sintomas in NOVOS:
    if nome.lower() in existentes:
        continue
    base["medicamentos"].append({
        "id": nome.upper().replace(" ", "_").replace("(", "").replace(")", "").replace(".", ""),
        "nome": nome,
        "nome_popular": popular,
        "origem": origem,
        "principio_ativo_declarado": f"{nome}, potenciado conforme farmacopeia homeopática",
        "categoria": categoria,
        "potencias_comuns": ["6 CH", "12 CH", "30 CH"],
        "apresentacoes": "Glóbulos, comprimidos, solução oral",
        "conservacao": "Embalagem fechada, ao abrigo de luz, calor, umidade e campos eletromagnéticos.",
        "indicacoes_fabricante": indicacoes,
        "indicacoes_registro_mapa": "Conforme farmacopeia homeopática e matéria médica. Requer registro MAPA desde 2017.",
        "sintomas_homeopaticos": sintomas,
        "contraindicacoes": "Não há contraindicações absolutas documentadas; eficácia não comprovada cientificamente.",
        "precaucoes": "Uso educacional; consulte médico-veterinário.",
        "uso_veterinario": f"Literatura homeopática: {categoria.split(' / ')[0].lower()} — uso conforme indicação clássica adaptada a animais.",
        "fonte_informacao": "AMHB_LISTA_2025",
        "tipo_informacao": "Declaração de fabricantes/literatura homeopática",
        "evidencia_cientifica": "Sem ensaios clínicos controlados robustos em animais. Eficácia não comprovada cientificamente (Bergh et al., 2021).",
        "notas": f"Lista AMHB TEH 2025. Origem: {origem_tipo(origem)}. Policresto/semi-policresto da matéria médica clássica."
    })
    existentes.add(nome.lower())
    adicionados += 1

# Metadata
base["metadata"]["versao"] = "3.0.0"
base["metadata"]["data_atualizacao"] = "2026-09-09"
base["metadata"]["descricao"] = "Base educacional de homeopatia veterinária — 123 medicamentos da lista AMHB TEH 2025, evidências independentes e regulamentação 2024-2026"

novo_json = json.dumps(base, ensure_ascii=False, separators=(",", ":"))
html_novo = html[:m.start(1)] + novo_json + html[m.end(1):]
open(PATH, "w", encoding="utf-8").write(html_novo)

print(f"=== v3.0.0 — {adicionados} medicamentos adicionados ===")
print(f"Total: {len(base['medicamentos'])} medicamentos")
print(f"Evidências: {len(base['evidencias_cientificas'])} | Regulamentação: {len(base['regulamentacao_brasil'])} | Glossário: {len(base['glossario'])}")
print(f"HTML: {len(html_novo)} bytes")
