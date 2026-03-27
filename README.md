<p align="center">
  <img src="https://img.shields.io/badge/python-3.11+-blue?logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/LLM-Claude%20(Anthropic)-blueviolet?logo=anthropic&logoColor=white" alt="Claude">
  <img src="https://img.shields.io/badge/GPU-not%20required-brightgreen" alt="No GPU">
  <img src="https://img.shields.io/badge/license-MIT-blue" alt="License">
  <img src="https://img.shields.io/badge/status-internal%20testing-orange" alt="Status">
</p>

<h1 align="center">🔭 Agent Innovation</h1>

<p align="center">
  <strong>AI agent for technology radar evaluation</strong><br>
  Scrapes web sources, reads internal process documents, and uses Claude + Web Search<br>
  to fill a structured evaluation template. Includes TAM/SAM/SOM scoring.
</p>

<p align="center">
  <em>🇧🇷 Output e código em português — projeto em testes internos na <a href="https://namu.com.br">Namu</a></em>
</p>

---

## 🧐 O que é?

Agent Innovation é um agente de IA que avalia tecnologias para o radar de inovação da Namu. Ele combina scraping de URLs, leitura de documentos internos (`.docx`) e buscas web automáticas via Claude para preencher templates estruturados de triagem e priorização.

**Uma chamada. Avaliação completa. Sem copiar e colar.**

```
Tecnologia + URL âncora
         ↓
  Leitura da URL (BeautifulSoup)
         ↓
  Documentos de processo (.docx)
         ↓
  Claude + Web Search (até 5 buscas)
         ↓
  ┌──────────────────────────────────┐
  │  Triagem (template estruturado)  │
  └──────────────────────────────────┘
         ↓
  ┌──────────────────────────────────┐
  │  Priorização (TAM/SAM/SOM)      │
  └──────────────────────────────────┘
         ↓
  Markdown (.md) + Cache JSON
```

---

## 📊 O que gera

| Etapa | Descrição | Web Search |
|-------|-----------|:----------:|
| 🔍 Triagem | Identificação, critérios de entrada, maturidade, custo, complexidade, decisão | ✅ Sim (até 5) |
| 📊 Priorização | Score TAM/SAM/SOM + framework de negócios (6 categorias) | ❌ Não |
| 💾 Cache | Resultados salvos em JSON — reprocessamento sem custo | — |

### Template de Triagem

- Identificação da tecnologia e categoria
- Critérios de entrada no radar (impacto estratégico, geração de dados, escalabilidade)
- Triagem (dor resolvida, maturidade, estimativa financeira, complexidade técnica)
- Decisão de triagem (avança / observa / descarta)

### Template de Priorização

- Score TAM/SAM/SOM com pesos (30%/40%/30%)
- Framework de negócios: Benchmark, Diferenciação, Qualidade, Produtividade, Flexibilidade, Eficiência
- Conclusão estratégica

---

## ✅ Custos por avaliação

| Modelo | Custo/avaliação | Qualidade |
|--------|:--------------:|:---------:|
| `claude-haiku-4-5-20251001` (padrão) | **~$0.05** | Boa |
| `claude-sonnet-4-20250514` | ~$0.34 | Alta |

> Priorização custa ~$0.01 adicional (sem web search).

---

## ⚡ Início rápido

### Pré-requisitos

- Python 3.11+
- Chave de API da [Anthropic](https://console.anthropic.com/)
- **Não precisa de GPU**
- Documentos `.docx` do processo de inovação (opcional)

### Instalação

```bash
# Clone o repositório
git clone https://github.com/Ninjexxx/agent_innovation.git
cd agent_innovation

# Crie o ambiente virtual
python -m venv .venv

# Ative (Windows)
.venv\Scripts\activate

# Ative (Linux/Mac)
source .venv/bin/activate

# Instale as dependências
pip install -r requirements.txt
```

### Configuração

Crie um arquivo `.env` na raiz:

```
ANTHROPIC_API_KEY=sk-ant-your-key-here
```

---

## 🎬 Como usar

### 1. 🌐 Interface web (Streamlit) — recomendado

```bash
streamlit run app.py
```

Abre o dashboard com:
- Inputs de nome + URL
- Indicador de cache e validação de URL
- Estimativa de custo antes de rodar
- Botão de triagem → resultado renderizado + download `.md`
- Botão de priorização → scoring TAM/SAM/SOM + download `.md`

### 2. 💻 CLI — Modo interativo

```bash
python agent_innovation.py
```

### 3. 🔄 CLI — Modo batch

```python
from agent_innovation import avaliar_lista

avaliar_lista([
    {"nome": "Ada Health API", "url_ancora": "https://ada.com"},
    {"nome": "Multimodal RAG", "url_ancora": ""},
])
```

---

## 📤 Output

### Terminal

```
🚀 Avaliando 'QuickPose.ai'...

🧠 Claude analisando com busca web + URL âncora...
   📖 Lendo URL âncora: https://quickpose.ai
   ✓ URL lida
   📄 16,500 chars de documentos de processo carregados
   🔍 Busca 1: QuickPose.ai SDK documentation pricing
   🔍 Busca 2: QuickPose.ai health tech use cases
   🔍 Busca 3: rPPG pose estimation SDK comparison
   ✓ 3 buscas realizadas pelo Claude
   ✓ Template preenchido

✅ Arquivo salvo: radar_quickpose.ai_20250627_1430.md
```

### Arquivo gerado

```
radar_technology_name_YYYYMMDD_HHMM.md
```

---

## 🔬 Como funciona (técnico)

### Pipeline

1. **Validação** — HEAD request na URL âncora para verificar acessibilidade
2. **Scraping** — BeautifulSoup extrai texto limpo (max 6.000 chars)
3. **Contexto** — Carrega 8 documentos `.docx` do processo de inovação (~16.500 chars)
4. **Análise** — Claude recebe tudo + faz até 5 buscas web automáticas via Tool Use
5. **Filtragem** — Regex remove linhas de raciocínio intermediário do Claude
6. **Cache** — Resultado salvo em JSON (hash MD5 de nome+url como chave)

### Stack

| Tecnologia | Uso |
|-----------|-----|
| Claude API (Anthropic) | LLM + web search nativo via Tool Use |
| BeautifulSoup | Scraping da URL âncora |
| python-docx | Leitura dos documentos de processo |
| Streamlit | Interface web |
| python-dotenv | Gerenciamento de variáveis de ambiente |
| hashlib + JSON | Sistema de cache local |

---

## 📁 Estrutura do projeto

```
agent_innovation/
├── agent_innovation.py       # Agente principal (análise + priorização)
├── app.py                    # Interface Streamlit
├── requirements.txt          # Dependências
├── .env                      # API key (não versionado)
├── .gitignore                # Ignora .env, cache/, .venv/, *.md gerados
├── cache/                    # Cache JSON das avaliações
└── README.md                 # Este arquivo
```

---

## 💡 Dicas de uso

| Dica | Por quê |
|------|---------|
| 🔗 Sempre forneça URL âncora | Mais contexto = avaliação mais precisa |
| 📄 Mantenha os `.docx` atualizados | São a referência de critérios do processo |
| 💰 Use Haiku para exploração | ~$0.05/avaliação vs ~$0.34 com Sonnet |
| 🔄 Limpe o cache se precisar reavaliar | Delete o `.json` correspondente em `cache/` |
| 📊 Só priorize o que passou na triagem | Priorização usa a triagem como input |

---

## ⚠️ Limitações

- 🤖 **Resultados gerados por IA** — revisar antes de usar em decisões
- 🌐 Web search depende da disponibilidade da API da Anthropic
- 📄 Documentos `.docx` são lidos como texto puro (sem formatação/tabelas)
- 💰 Cada avaliação consome créditos da API (~$0.05 com Haiku)
- 🔒 Path dos documentos está hardcoded para o ambiente local

---

## 🏢 Sobre

Projeto em **testes internos na [Namu](https://namu.com.br)** — plataforma brasileira de saúde e bem-estar.

- 🤖 **Powered by Claude** — Anthropic API com web search nativo
- 🇧🇷 **Código e output em português** — variáveis, prompts, templates e resultados em pt-BR
- 💻 **Roda em qualquer computador** — sem necessidade de GPU
- 📦 **Cache inteligente** — não reprocessa avaliações já feitas

---

## 📚 Referências

- [Anthropic API Docs](https://docs.anthropic.com/) — Claude models + Tool Use
- [Streamlit](https://streamlit.io/) — Framework de UI para data apps
- [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/) — HTML parsing
- [python-docx](https://python-docx.readthedocs.io/) — Leitura de arquivos .docx

---

<p align="center">
  Feito com 🔭 por <a href="https://namu.com.br">Namu</a>
</p>
