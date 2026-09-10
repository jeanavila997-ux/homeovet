# 🐾 HomeoVet — Agentes de IA para Homeopatia

Conjunto de agentes inteligentes em **Python puro** (zero dependências obrigatórias) para busca e educação em homeopatia, com foco em **homeopatia veterinária**, segurança ética ativa e transparência científica.

- 🔍 **Agente de busca por sintomas** com aprendizado por feedback (24 remédios)
- 🎓 **Tutor educacional veterinário** com filtro de segurança e rastreamento de fontes
- 💻 **CLI completa** (v1.0.0): fichas, evidências, regulamentação, quiz e memória
- 🌐 **Interface web standalone** (HTML/CSS/JS, sem backend)
- 🤖 **Modo IA local opcional** (Ollama) com fallback 100% offline

> ⚠️ **Aviso importante**: este projeto tem fins **estritamente educacionais**. Não diagnostica, não prescreve, não recomenda doses e não substitui a consulta com um médico-veterinário ou médico. A eficácia da homeopatia **não é sustentada por evidências científicas robustas** segundo revisões sistemáticas (Bergh et al., 2021).

---

## 📦 Componentes

| Arquivo | O que é | Público |
|---------|---------|---------|
| `agente_homeopatico.py` | 🔍 Agente de **busca por sintomas** com aprendizado por feedback (24 remédios, uso humano) | Prática/demonstração |
| `tutor_homeopatia_vet.py` | 🎓 **Tutor educacional** veterinário com filtro de segurança, fontes e memória | Estudantes e profissionais |
| `homeovet_cli.py` | 💻 **CLI completa** (v1.0.0): fichas, evidências, regulamentação, glossário, quiz e progresso | Profissional veterinário |
| `index.html` | 🌐 **Interface web standalone** com busca, filtros, fichas e evidências | Qualquer usuário |
| `testes.py` | ✅ Testes automatizados do agente de busca | Desenvolvedores |
| `Modelfile.homeovet` | 🧠 **Modelfile do tutor local** (Ollama) → modelo `homeovet-tutor` | Uso com IA local |
| `scripts/gerar_index.py` | 🔧 Regenera o `index.html` a partir da base JSON | Manutenção |

## 🧠 Funcionalidades

### Agente de Busca (`agente_homeopatico.py`)
- Matching por similaridade de texto nos sintomas (`difflib.SequenceMatcher`)
- Ranking por relevância + score de aprendizado
- Feedback do usuário (funcionou / não funcionou) ajusta o ranking
- Base JSON expansível (24 remédios pré-cadastrados)

### Tutor Educacional (`tutor_homeopatia_vet.py`)
- Respostas no formato pedagógico: 📌 objetiva → 📚 didática → 📖 fonte → 🔬 evidências → ❓ revisão → ⚠️ aviso
- **Filtro de segurança ativo**: bloqueia diagnóstico/prescrição e detecta sintomas de emergência
- **Rastreamento de fontes em 4 categorias**: declarações de fabricante, evidências científicas, conhecimento geral e informação indisponível
- Memória persistente: sessões, tópicos mais consultados, feedbacks

### CLI HomeoVet (`homeovet_cli.py`)
- Fichas técnicas completas (indicações, sintomas, contraindicações, conservação, uso veterinário)
- Evidências científicas com nível de evidência e links
- Regulamentação brasileira (CFMV, MAPA)
- Quiz de 15 perguntas, memória local (favoritos, anotações, histórico, progresso) e exportação

### Interface Web (`index.html`)
- 100% standalone — nenhum servidor necessário
- Busca com normalização de acentos, filtros por categoria, modal com ficha completa
- Abas: Medicamentos, Evidências Científicas, Regulamentação, Glossário

---

## 🚀 Como Usar

> **Windows**: se o comando `python` abrir a Microsoft Store, use o lançador `py`.

```bash
# Agente de busca por sintomas
py agente_homeopatico.py                 # (linux/macOS: python3)

# Tutor educacional veterinário
py tutor_homeopatia_vet.py

# CLI completa (opcional: pip install rich para interface colorida)
py homeovet_cli.py ficha "Arnica Montana"
py homeovet_cli.py buscar "contusão queda dor muscular"
py homeovet_cli.py perguntar "O que é a Lei do Semelhante?"
py homeovet_cli.py quiz
py homeovet_cli.py exportar --formato md

# Interface web — basta abrir no navegador
start index.html   # Windows
open index.html    # macOS
```

## 🤖 Modo IA Local (Opcional)

Todo o projeto funciona em **Python puro, 100% offline**. Se o [Ollama](https://ollama.com) estiver rodando em `http://localhost:11434`, a CLI e a interface web ganham automaticamente (com **fallback completo** quando desligado):

- **Busca semântica** no comando `buscar` — embeddings `nomic-embed-text` (274 MB) combinados com busca léxica por fusão de rankings (RRF)
- **Tutor RAG** no comando `perguntar` e no painel "Tutor IA local" — respostas LLM **ancoradas exclusivamente na base educacional**, no formato 📌→📚→📖→🔬→⚠️

```bash
ollama pull nomic-embed-text                        # embeddings (busca semântica)
ollama create homeovet-tutor -f Modelfile.homeovet  # tutor (base: nemotron-3-nano:4b)
```

- Sem o `homeovet-tutor`, a CLI usa automaticamente o `nemotron-3-nano:4b` local.
- Use `--sem-ia` para forçar o modo Python puro.
- A web conversa com o Ollama direto do navegador. Se o navegador bloquear (CORS ao abrir arquivo local), inicie o Ollama com `OLLAMA_ORIGINS=* ollama serve`.
- **Segurança em camadas**: bloqueio de diagnóstico/prescrição e detecção de emergências rodam por REGRAS, antes de qualquer LLM.

---

## 📁 Estrutura

```
homeovet/
├── agente_homeopatico.py          # Agente de busca por sintomas
├── tutor_homeopatia_vet.py        # Tutor educacional veterinário
├── homeovet_cli.py                # CLI completa v1.0.0
├── index.html                     # Interface web standalone
├── Modelfile.homeovet             # Modelfile do tutor local (Ollama)
├── testes.py                      # Testes automatizados
├── requirements.txt               # Zero dependências obrigatórias
├── PLANO.md                       # Plano original do agente de busca
├── ANALISE_COMPARATIVA.md         # Análise comparativa dos agentes
├── scripts/
│   └── gerar_index.py             # Regenera o index.html a partir da base JSON
└── data/
    ├── remedios_homeopaticos.json # Base do agente de busca (24 remédios)
    └── tutor_homeopatia_vet.json  # Base do tutor (12 remédios + conceitos + evidências + regulamentação)
```

Arquivos de runtime (feedback, memória, histórico e a pasta `runtime/` da CLI) são gerados localmente e ignorados pelo `.gitignore`. Reexecute `py scripts/gerar_index.py` após alterar qualquer base JSON.

---

## 📦 Dependências

- **Python 3.7+** — única exigência
- Opcional: `rich>=13.0.0` para interface colorida (`pip install rich`)

## 🔬 Fontes e Regulamentação

A base educacional rastreia fontes como: Resolução CFMV nº 625/95, Ofício-Circular MAPA nº 8/2017, CRMV-SP, revisão sistemática Bergh et al. (2021, PubMed), ScienceDirect Veterinary Homeopathy Overview e literatura da AMVHB — sempre diferenciando **declaração comercial** de **evidência científica**.

---

## 📄 Licença

Uso educacional. Consulte um médico-veterinário para qualquer decisão clínica.