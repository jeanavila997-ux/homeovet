# 🤖 Agente de Aprendizagem - Medicamentos Homeopáticos

## 📋 Visão Geral

Agente inteligente em Python puro que auxilia na busca e indicação de medicamentos homeopáticos baseado em sintomas informados pelo usuário. O sistema aprende com o feedback dos usuários, melhorando suas recomendações ao longo do tempo.

## 🎯 Objetivos

1. **Busca Inteligente por Sintomas**: Encontrar medicamentos homeopáticos que correspondam aos sintomas descritos
2. **Sistema de Aprendizado**: Melhorar recomendações com base no feedback de eficácia
3. **Base de Dados Expansível**: JSON simples, fácil de editar e expandir
4. **Interface Amigável**: CLI interativa e intuitiva

## 🏗️ Arquitetura

```
agente_homeopatico/
├── agente_homeopatico.py       # Código principal
├── data/
│   └── remedios_homeopaticos.json  # Base de dados
├── feedback.json               # Histórico de aprendizado
└── requirements.txt            # Dependências
```

## 📦 Dependências

- **Python 3.7+** (único requisito!)
- Zero bibliotecas externas obrigatórias
- Opcional: `rich` para interface colorida no terminal

## 🔧 Funcionalidades

### 1. Motor de Busca
- Matching por similaridade de texto nos sintomas
- Suporte a múltiplos sintomas simultâneos
- Ranking por relevância

### 2. Sistema de Aprendizado
- Registra feedback do usuário (funcionou / não funcionou)
- Ajusta pontuação dos remédios baseado no histórico
- Salva aprendizado em arquivo JSON local

### 3. Base de Dados
- 20+ medicamentos homeopáticos pré-cadastrados
- Campos: nome, princípio ativo, indicações, sintomas, dosagem, contraindicações
- Formato JSON editável em qualquer editor de texto

## 🚀 Como Usar

```bash
# 1. Executar o agente
python agente_homeopatico.py

# 2. No menu interativo, escolher:
#    [1] Buscar por sintomas
#    [2] Listar todos os remédios
#    [3] Ver estatísticas de aprendizado
#    [4] Adicionar novo remédio
#    [0] Sair
```

## 🧠 Lógica de Aprendizado

```
Score Inicial: baseado no matching de sintomas

Feedback Positivo (+1):
  → Score aumenta → Remédio sobe no ranking

Feedback Negativo (-1):
  → Score diminui → Remédio desce no ranking

Fator de Confiança:
  → Mais feedback = maior confiança na recomendação
```

## 📈 Expansões Futuras

- Exportar relatórios de uso
- Filtros por gravidade dos sintomas
- Integração com web (Flask/Streamlit)
- Backup na nuvem
