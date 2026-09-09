# 🔄 RETOMAR — HomeoVet + Ambiente (atualizado em 2026-09-09, v3.1.0)

Checkpoint do estado real — tudo abaixo foi verificado nesta sessão.

---

## ✅ Concluído

### HomeoVet (github.com/jeanavila997-ux/homeovet)
- Commits `a5eed21` e `db45dcb` em `main`: CLI completa (`homeovet_cli.py` v1.0.0),
  `index.html` standalone (gerado por `scripts/gerar_index.py`), `Modelfile.homeovet`,
  README/.gitignore atualizados
- Correções de segurança: filtro detecta emergências/bloqueios **sem acento**
  ("convulsionando", "vomitando sangue") + radicais na lista de urgência
- CLI: timeout do LLM 300s + `think: false` + contexto RAG 6→4 docs
- Verificação: testes 7/7 ✅, smoke de todos os subcomandos ✅, quiz ✅,
  interface web verificada visualmente (busca com "contusão" → Arnica ✅)
- Commit `e4c1aaa` em `main` (**v3.1.0**): categoria **Cascos e Unhas**
  (Silicea Terra, Antimonium Crudum, Fluoricum Acidum, Graphites,
  Graphites Naturalis — cascos de bovinos/equinos e unhas humanas),
  **índice por sistema** no dashboard (12 categorias maiores consolidando
  as 109 categorias da base AMHB), redesign com identidade "farmacopeia"
  (papel-sálvia, tinta verde, acento âmbar-frasco, serif) e **deploy Node
  zero-dependências para o Hostinger** (`package.json` + `server.js` +
  `scripts/build_web.js`)
- `data/tutor_homeopatia_vet.json` voltou a ser a **fonte única de verdade**
  (125 medicamentos): `scripts/sincronizar_base.py` extrai a BASE do
  index.html de volta ao JSON — regenerar o index.html não perde mais a
  expansão AMHB (armadilha corrigida)
- Verificação v3.1.0: testes 7/7 ✅, `npm run build` ✅, smoke do
  `server.js` (HTTP 200) ✅, screenshots headless revisados ✅
- Backup no Google Drive: `G:\Meu Drive\homeovet-backup-20260909.zip`
  (cliente Google Drive instalado, logado, unidade **G:** ativa)

### Ambiente omp
- Skills oficiais `docx`/`pdf`/`pptx`/`xlsx` instaladas em `~/.claude/skills/`
- `desktop-commander` ativado em `~/.omp/agent/mcp.json`
  (ativar com `/mcp reload` ou nova sessão)
- `modelRoles.default` corrigido → `ollama/glm-5.3:cloud`
  (o antigo apontava para `deepseek-r1:1.5b`, não instalado)
- `~/.omp/agent/.env` criado; `OLLAMA_CLOUD_API_KEY` **preenchida e testada**
  (19 modelos direto em `https://ollama.com/api/tags`, ex.: glm-5.3-flash,
  gpt-oss:120b, nemotron-3-super) — provedor `ollama-cloud` ativa sozinho na
  próxima sessão do omp

---

## 🚀 Deploy no Hostinger (em andamento)

Modal "Alterar configurações de compilação e saída" do assistente Node:
- Comando de construção: `npm run build`
- Gerenciador de pacotes: `npm`
- Diretório de saída: `dist`
- Arquivo de entrada: `server.js` (NÃO `electron/main.js` — o HomeoVet é
  dashboard estático + servidor mínimo, sem Electron)

O commit `e4c1aaa` já está no GitHub com tudo isso.

---

## 📦 Downloads do Google Drive concluídos

- Pasta compartilhada **REAL H - ACRE** baixada 100% para
  `OneDrive/EMPRESAS/02-LOJA/02-REAL H/REAL H - ACRE` — 66 arquivos,
  18 pastas, 0 falhas (cópia do projeto REAL H, VETERINARIO,
  PROJETO_PESSOAL_DE_VIDA, .github com agents/instructions, fichas CMR)
- Comprimida em `02-REAL H/REAL H - ACRE.zip` (66 arquivos, 4.10 MB,
  integridade validada)
- 28 fichas técnicas CMR (PDFs REAL H 2021) também em
  `02-REAL H/FICHAS TECNICAS CMR/`

---

## ⏳ Pendências (acionáveis quando quiser)

1. **`ollama pull nomic-embed-text`** (274 MB) — habilita a busca semântica real
   na CLI HomeoVet (o fallback léxico funciona sem ele; `embeddinggemma`
   já instalado também serve)
2. **Colar as chaves restantes** em `~/.omp/agent/.env`:
   - `NVIDIA_API_KEY` → build.nvidia.com (Login → Get API Key)
   - `OPENROUTER_API_KEY` → openrouter.ai/keys
   - `OPENAI_API_KEY` → platform.openai.com/api-keys
   - `COPILOT_GITHUB_TOKEN` → github.com/settings/tokens (ou `/login github-copilot`)
   Ao colar, avisar o agente para **testar cada provedor** e configurar os papéis
   (`default`/`smol`/`slow`) com eles
3. *(Opcional)* Enviar a pasta `C:/Users/JEANPC/estudos/09-homeopatia` para o
   Google Drive (backup manual ou via cliente)

---

## 🛠️ Comandos úteis

```bash
cd C:/Users/JEANPC/homeovet        # projeto
py testes.py                       # testes (7/7)
py homeovet_cli.py --help          # CLI
py scripts/gerar_index.py          # regenera index.html após mudar data/
py scripts/sincronizar_base.py     # puxa a BASE do index.html para o JSON
npm run build && npm start         # build + servidor local (deploy Hostinger)
ollama list                        # modelos locais
omp models                         # provedores/modelos disponíveis no omp
```

Git: identidade dos commits → `-c user.name="jeanavila997-ux" -c user.email="jeanavila997@gmail.com"`

**Contexto de negócio:** Real H = nutrição animal (OneDrive/EMPRESAS/02-LOJA/02-REAL H,
catálogos e projeções ROI). HomeoVet = educacional, sem diagnóstico/prescrição;
segurança por regras ANTES de qualquer LLM. Hardware: RTX 3050 4GB → modelos
locais 3-4B (nemotron-3-nano:4b OK; evitar 7B+ local).