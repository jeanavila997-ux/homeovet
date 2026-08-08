# 📊 ANÁLISE COMPARATIVA: Agente de Busca vs. Tutor Educacional

## Visão Geral

Este projeto contém **dois agentes distintos** com propósitos complementares:

| Aspecto | Agente de Busca (`agente_homeopatico.py`) | Tutor Educacional (`tutor_homeopatia_vet.py`) |
|---------|-------------------------------------------|-----------------------------------------------|
| **Propósito** | Busca prática por sintomas | Aprendizado teórico-educacional |
| **Público-alvo** | Usuário buscando indicação rápida | Estudante/profissional buscando compreensão |
| **Base de dados** | 24 remédios homeopáticos (humano) | 12 remédios + conceitos + evidências + regulamentação (veterinário) |
| **Memória** | Feedback de eficácia (score dos remédios) | Memória de aprendizado com sessões, tópicos, feedbacks |
| **Fontes** | Não rastreia fontes | Rastreia e classifica 4 tipos de informação |
| **Segurança** | Aviso geral no início | Filtro ativo de bloqueio de diagnóstico + avisos em cada resposta |
| **Ciência** | Não menciona evidências | Destaca limitações e ausência de evidências robustas |

---

## 🤖 Agente 1: Agente de Busca por Sintomas

### O que faz
- Usuário digita sintomas → agente retorna remédios homeopáticos ordenados por relevância
- Sistema de feedback: usuário diz se funcionou → score do remédio aumenta/diminui
- Aprendizado por reforço: remédios mais bem avaliados sobem no ranking

### Pontos Fortes
- ✅ Interface simples e direta
- ✅ Código extremamente leve (Python puro, zero dependências)
- ✅ Sistema de aprendizado funcional e visível
- ✅ Base de dados fácil de expandir

### Limitações
- ⚠️ **Não diferencia tipos de informação** (fabricante vs. ciência vs. conhecimento geral)
- ⚠️ **Não rastreia fontes** das informações
- ⚠️ **Não menciona a controvérsia científica** da homeopatia
- ⚠️ **Aviso de segurança é genérico** (apenas no início)
- ⚠️ Base de dados é para uso humano, não veterinário

---

## 🎓 Agente 2: Tutor Educacional de Homeopatia Veterinária

### O que faz
- Responde perguntas educacionais com formato padronizado:
  1. 📌 Resposta objetiva
  2. 📚 Explicação didática
  3. 📖 Informação da fonte
  4. 🔬 Evidências e limitações
  5. ❓ Perguntas para revisão
  6. ⚠️ Aviso de segurança

- **Sistema de segurança ativo:**
  - Detecta tentativas de diagnóstico/prescrição e BLOQUEIA
  - Detecta sintomas de emergência e avisa para procurar veterinário
  - Em toda resposta sobre medicamento, alerta que eficácia não é comprovada

- **Rastreamento de fontes com 4 categorias:**
  1. **Informações declaradas pelo fabricante** → Indicações de rótulos/bulas
  2. **Evidências científicas encontradas** → Revisões sistemáticas (Bergh 2021, etc.)
  3. **Conhecimento geral** → Princípios teóricos (Lei do Semelhante, etc.)
  4. **Informações não disponíveis** → Mecanismo de ação, eficácia comprovada

- **Memória de aprendizado:**
  - Conta sessões
  - Registra tópicos mais consultados
  - Armazena feedback de utilidade das respostas
  - Identifica conceitos que geram dificuldade

### Pontos Fortes
- ✅ **Segurança ética rigorosa** (filtro ativo de bloqueio)
- ✅ **Transparência epistêmica** (diferencia fontes e evidências)
- ✅ **Honestidade científica** (declara explicitamente que evidências são insuficientes)
- ✅ **Foco veterinário** com regulamentação brasileira (CFMV, MAPA)
- ✅ **Formato pedagógico** com perguntas para revisão
- ✅ **Memória inteligente** que melhora com o uso

### Limitações
- ⚠️ Código mais complexo (~600 linhas vs. ~400)
- ⚠️ Não realiza busca por sintomas (é educacional, não prático)
- ⚠️ Base de dados menor (12 medicamentos vs. 24) — mas mais detalhada

---

## 🔬 Fontes Consultadas e Integradas

| Fonte | Tipo | O que foi usado |
|-------|------|-----------------|
| **CFMV Resolução 625/95** | Regulatória | Reconhecimento da especialidade |
| **MAPA Ofício-Circular 8/2017** | Regulatória | Registro obrigatório de produtos homeopáticos |
| **CRMV-SP** | Institucional | Informações sobre a prática da especialidade |
| **Bergh et al. (2021) PubMed** | Científica | Revisão sistemática - evidência insuficiente |
| **ScienceDirect Overview** | Científica | Críticas e controvérsias |
| **AMVHB Revista** | Técnica | Casos clínicos publicados (com ressalvas) |
| **MAPA Nota Técnica 13/2026** | Regulatória | Proposta de registro automatizado |

---

## ⚖️ Diferenciação dos 4 Tipos de Informação

### 1. Informações Declaradas pelo Fabricante
```
Exemplo: "Arnica Montana é indicada para traumas físicos, contusões, hematomas"
→ Fonte: Bulas e rótulos de produtos homeopáticos
→ Status: Declaração comercial, não comprovada cientificamente
```

### 2. Evidências Científicas Encontradas
```
Exemplo: "Revisão sistemática Bergh et al. (2021) analisou 982 estudos, 
          encontrou apenas 42 elegíveis, com alto risco de viés"
→ Fonte: PubMed, ScienceDirect
→ Status: Evidência de baixa qualidade, insuficiente para comprovar eficácia
```

### 3. Conhecimento Geral
```
Exemplo: "A Lei do Semelhante (Similia similibus curentur) é o princípio 
          fundador da homeopatia, proposto por Hahnemann"
→ Fonte: História da medicina, literatura homeopática
→ Status: Conhecimento histórico/teórico, não científico
```

### 4. Informações Não Disponíveis
```
Exemplo: "Mecanismo de ação molecular da homeopatia em potências > 12 CH"
→ Status: Não explicado pela ciência atual. Não há moléculas da substância original.
```

---

## 📁 Estrutura Final do Projeto

```
📁 homeovet/
├── PLANO.md                              # Plano original do Agente de Busca
├── ANALISE_COMPARATIVA.md               # Este documento
├── agente_homeopatico.py                # Agente de busca por sintomas (humano)
├── tutor_homeopatia_vet.py              # Tutor educacional (veterinário)
├── testes.py                            # Testes do agente de busca
├── requirements.txt                     # Dependências (zero obrigatórias)
└── data/
    ├── remedios_homeopaticos.json       # Base do agente de busca (24 remédios)
    └── tutor_homeopatia_vet.json        # Base do tutor (12 remédios + conceitos + evidências + regulamentação)
    ├── feedback.json                    # Aprendizado do agente de busca
    ├── memoria_aprendizado.json         # Memória do tutor
    └── historico_conversas.json         # Histórico de conversas do tutor
```

---

## 🚀 Como Usar Cada Agente

### Agente de Busca (uso humano/prático)
```bash
python agente_homeopatico.py
# Digite sintomas: "ansiedade nervosismo"
# Recebe: lista de remédios ordenados por relevância
# Feedback: "Funcionou?" → agente aprende
```

### Tutor Educacional (uso veterinário/educacional)
```bash
python tutor_homeopatia_vet.py
# Escolha [1] para modo conversa
# Pergunte: "O que é a Lei do Semelhante?"
# Ou: "Quais as evidências sobre homeopatia veterinária?"
# Recebe: Resposta estruturada com fontes, evidências e avisos de segurança
```

---

## 🎯 Recomendação de Uso

| Situação | Agente Recomendado | Por quê |
|----------|-------------------|---------|
| Quero saber qual remédio homeopático usar para dor de cabeça | **NENHUM** → vá ao médico | Nenhum agente prescreve |
| Quero estudar para prova de homeopatia | **Tutor** | Didático, com fontes e evidências |
| Quero entender a regulamentação de produtos homeopáticos veterinários no Brasil | **Tutor** | Tem IN MAPA, CFMV, etc. |
| Quero saber o que diz a ciência sobre homeopatia | **Tutor** | Cita revisões sistemáticas |
| Quero experimentar um sistema de busca com aprendizado por feedback | **Agente de Busca** | É mais simples e direto |
| Quero entender como funciona a potenciação homeopática | **Tutor** | Explica CH, DH, limite de Avogadro |

---

*Documento gerado em 08/08/2026. As informações regulatórias refletem o estado da legislação brasileira até esta data.*
