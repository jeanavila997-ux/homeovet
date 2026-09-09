# 🔄 RETOMAR — Sessão HomeoVet + Ambiente (2026-09-09)

Checkpoint completo para retomar o trabalho de onde parou, com contexto limpo.

---

## ✅ Concluído e enviado ao GitHub

- Repo **https://github.com/jeanavila997-ux/homeovet** clonado em `C:/Users/JEANPC/homeovet`
- Commit `a5eed21` enviado para `main` (push OK) com:
  - **`homeovet_cli.py`** — CLI v1.0.0: `ficha`, `buscar`, `medicamentos`, `evidencias`,
    `regulamentacao`, `glossario`, `perguntar`, `quiz` (15 perguntas), `progresso`,
    `favoritos`, `anotacoes`, `historico`, `exportar`. Flag `--sem-ia`. Modo IA local
    opcional: embeddings (`nomic-embed-text`) + fusão RRF na busca + RAG/LLM no
    `perguntar` (fallback automático para o motor de regras do tutor)
  - **`index.html`** — interface web standalone gerada por `scripts/gerar_index.py`
    (4 abas, busca sem acentos, filtro por categoria, modal com ficha completa,
    painel "Tutor IA local" falando direto com o Ollama pelo navegador)
  - **`Modelfile.homeovet`** — `ollama create homeovet-tutor -f Modelfile.homeovet`
  - README e .gitignore atualizados (seção "Modo IA Local", `py` no Windows, `runtime/`)
- Testes originais: **7/7 passando** (`py testes.py`)
- Smoke tests da CLI: todos OK (busca, fichas, quiz, favoritos, anotações, exportação,
  histórico, bloqueio de prescrição)
- API do Ollama testada direto: `nemotron-3-nano:4b` responde OK via `/api/chat` (1.8s)

---

## ⚠️ Pendências do HomeoVet (nesta ordem)

1. **BUG do filtro de acentos** (segurança): "meu cachorro esta convulsionando" (sem
   acento) NÃO dispara o aviso de emergência — a lista do tutor tem "convulsão" com acento.
   Correção planejada:
   - `tutor_homeopatia_vet.py`: adicionar `import unicodedata` (imports, linhas 16-21) +
     função `sem_acentos()` após `similaridade()` (linha ~46) + aplicar em
     `FiltroSeguranca.detectar_tentativa_diagnostico` e `verificar_sintomas_urgentes`
     (comparar `sem_acentos(texto)` com `sem_acentos(palavra)`)
   - `scripts/gerar_index.py` (template): usar `norm()` nas comparações de
     `PALAVRAS_BLOQUEIO` e `SINTOMAS_URGENTES` no JS
   - Regenerar: `py scripts/gerar_index.py`
   - Testar: `py homeovet_cli.py perguntar "meu cachorro esta convulsionando"` → deve dar 🚨 emergência
   - Commitar + push
2. **LLM local — RESOLVIDO PARCIALMENTE pelo debug (bg_14)**: a chamada via urllib
   FUNCIONA — `nemotron-3-nano:4b` respondeu no formato pedagógico correto
   (📌→📚→📖→🔬), porém levou **~150 s** (o modelo gera "thinking" antes da resposta).
   Causa provável da falha anterior: geração lenta estourando timeout/contexto.
   Ações recomendadas: subir `timeout` do `chat_llm` em `homeovet_cli.py` de 180 → 300 s,
   reduzir contexto RAG (n=6 → 4 documentos) e, se o Ollama suportar, desligar
   thinking no payload (ex.: `"think": false`). Depois: testar
   `py homeovet_cli.py perguntar "O que e a Lei do Semelhante?"` (sem --sem-ia),
   **deletar `scripts/_debug_llm.py`** e commitar.
3. **Verificar index.html no navegador** (ainda não feito): abrir
   `file:///C:/Users/JEANPC/homeovet/index.html`, conferir abas, busca, modal e painel
   do tutor com evidência visual (screenshot)
4. **`ollama pull nomic-embed-text`** (274MB, não instalado) — busca semântica da CLI
   ainda não foi exercitada de verdade (fallback léxico funciona)

---

## 🆕 Pedido novo em andamento: configurar o ambiente

Pedido do usuário: **"instale skills, ferramentas, troca de modelos llm provedores, api, mcp"**

Plano (não iniciado — leituras foram canceladas pela compactação):
1. Ler docs do harness: `omp://models.md`, `omp://providers.md`, `omp://skills.md`,
   `omp://mcp-config.md`, `omp://settings.md`, `omp://secrets.md`
2. Levantar estado atual: skills instaladas, modelos Ollama
   (locais: `nemotron-3-nano:4b`, `qwen2.5-coder:3b`, `tinydolphin`, `assistente-glm`;
   clouds: `glm-5.3`, `kimi-k2.6/k2.7-code`, `mistral-large-3`, `qwen3.5`, `gpt-oss:120b`,
   `gemma4:31b`, `nemotron-3-ultra/super`), MCPs montados
3. Confirmar com o usuário o que exatamente instalar/configurar
   (quais provedores padrão, quais chaves API ele tem, quais skills, quais MCPs)

---

## 🛠️ Comandos úteis

```bash
cd C:/Users/JEANPC/homeovet
py testes.py                      # testes (7/7)
py homeovet_cli.py --help         # ajuda da CLI
py homeovet_cli.py quiz           # quiz interativo
py scripts/gerar_index.py         # regenera index.html após mudar data/
ollama list                       # modelos instalados
```

Git: identidade usada nos commits → `-c user.name="jeanavila997-ux" -c user.email="jeanavila997@gmail.com"`

---

## 📌 Contexto do negócio (para não perder)

- **Real H** (loja do usuário, OneDrive/EMPRESAS/02-LOJA/02-REAL H): nutrição animal,
  catálogos PDF, projeções ROI (PESOMAX, RECRIMAX, COMBO ÁGUAS, MÚLTIPLO 20)
- HomeoVet é **educacional**: não diagnostica, não prescreve; filtro de segurança
  por regras ANTES de qualquer LLM (nunca delegada ao modelo)
- Hardware: RTX 3050 Laptop 4GB VRAM → modelos locais de 3-4B (nemotron-3-nano:4b OK;
  evitar 7B+ local)