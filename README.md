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
  <em>🇧🇷 All generated output and code (variables, comments, prompts) are in Brazilian Portuguese (pt-BR) — internal testing at <a href="https://namu.com.br">Namu</a></em>
</p>

---

## 🧐 What is it?

Agent Innovation is an AI agent that evaluates technologies for Namu's innovation radar. It combines URL scraping, internal document reading (`.docx`), and automatic web searches via Claude to fill structured triage and prioritization templates.

**One call. Full evaluation. No copy-paste.**

```
Technology + Anchor URL
         ↓
  URL Reading (BeautifulSoup)
         ↓
  Process Documents (.docx)
         ↓
  Claude + Web Search (up to 5 searches)
         ↓
  ┌──────────────────────────────────┐
  │  Triage (structured template)    │
  └──────────────────────────────────┘
         ↓
  ┌──────────────────────────────────┐
  │  Prioritization (TAM/SAM/SOM)   │
  └──────────────────────────────────┘
         ↓
  Markdown (.md) + JSON Cache
```

---

## 📊 What it generates

| Stage | Description | Web Search |
|-------|-------------|:----------:|
| 🔍 Triage | Identification, entry criteria, maturity, cost, complexity, decision | ✅ Yes (up to 5) |
| 📊 Prioritization | TAM/SAM/SOM score + business framework (6 categories) | ❌ No |
| 💾 Cache | Results saved as JSON — reprocessing at zero cost | — |

### Triage Template

- Technology identification and category
- Radar entry criteria (strategic impact, data generation, scalability)
- Triage (pain point, maturity, cost estimate, technical complexity)
- Triage decision (advance / observe / discard)

### Prioritization Template

- TAM/SAM/SOM score with weights (30%/40%/30%)
- Business framework: Benchmark, Differentiation, Quality, Productivity, Flexibility, Efficiency
- Strategic conclusion

---

## ✅ Cost per evaluation

| Model | Cost/evaluation | Quality |
|-------|:--------------:|:---------:|
| `claude-haiku-4-5-20251001` (default) | **~$0.05** | Good |
| `claude-sonnet-4-20250514` | ~$0.34 | High |

> Prioritization costs ~$0.01 extra (no web search).

---

## ⚡ Quick start

### Prerequisites

- Python 3.11+
- [Anthropic](https://console.anthropic.com/) API key
- **No GPU required**
- Innovation process `.docx` documents (optional)

### Installation

```bash
# Clone the repository
git clone https://github.com/Ninjexxx/agent_innovation.git
cd agent_innovation

# Create virtual environment
python -m venv .venv

# Activate (Windows)
.venv\Scripts\activate

# Activate (Linux/Mac)
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Configuration

Create a `.env` file in the project root:

```
ANTHROPIC_API_KEY=sk-ant-your-key-here
```

---

## 🎬 How to use

### 1. 🌐 Web interface (Streamlit) — recommended

```bash
streamlit run app.py
```

Opens a dashboard with:
- Name + URL inputs
- Cache indicator and URL validation
- Cost estimate before running
- Triage button → rendered result + `.md` download
- Prioritization button → TAM/SAM/SOM scoring + `.md` download

### 2. 💻 CLI — Interactive mode

```bash
python agent_innovation.py
```

### 3. 🔄 CLI — Batch mode

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

### Generated file

```
radar_technology_name_YYYYMMDD_HHMM.md
```

---

## 🔬 How it works (technical)

### Pipeline

1. **Validation** — HEAD request to check anchor URL accessibility
2. **Scraping** — BeautifulSoup extracts clean text (max 6,000 chars)
3. **Context** — Loads 8 innovation process `.docx` documents (~16,500 chars)
4. **Analysis** — Claude receives everything + performs up to 5 automatic web searches via Tool Use
5. **Filtering** — Regex removes Claude's intermediate reasoning lines
6. **Cache** — Result saved as JSON (MD5 hash of name+url as key)

### Stack

| Technology | Usage |
|-----------|-------|
| Claude API (Anthropic) | LLM + native web search via Tool Use |
| BeautifulSoup | Anchor URL scraping |
| python-docx | Process document reading |
| Streamlit | Web interface |
| python-dotenv | Environment variable management |
| hashlib + JSON | Local cache system |

---

## 📁 Project structure

```
agent_innovation/
├── agent_innovation.py       # Main agent (analysis + prioritization)
├── app.py                    # Streamlit interface
├── requirements.txt          # Dependencies
├── .env                      # API key (not versioned)
├── .gitignore                # Ignores .env, cache/, .venv/, generated *.md
├── cache/                    # JSON cache of evaluations
└── README.md                 # This file
```

---

## 💡 Usage tips

| Tip | Why |
|-----|-----|
| 🔗 Always provide an anchor URL | More context = more accurate evaluation |
| 📄 Keep `.docx` files updated | They are the process criteria reference |
| 💰 Use Haiku for exploration | ~$0.05/eval vs ~$0.34 with Sonnet |
| 🔄 Clear cache to re-evaluate | Delete the corresponding `.json` in `cache/` |
| 📊 Only prioritize what passed triage | Prioritization uses triage as input |

---

## ⚠️ Limitations

- 🤖 **AI-generated results** — review before using in decisions
- 🌐 Web search depends on Anthropic API availability
- 📄 `.docx` documents are read as plain text (no formatting/tables)
- 💰 Each evaluation consumes API credits (~$0.05 with Haiku)
- 🔒 Document path is hardcoded to the local environment

---

## 🏢 About

Project under **internal testing at [Namu](https://namu.com.br)** — a Brazilian health & wellness platform.

- 🤖 **Powered by Claude** — Anthropic API with native web search
- 🇧🇷 **Code and output in Portuguese** — variables, prompts, templates and results in pt-BR
- 💻 **Runs on any computer** — no GPU required
- 📦 **Smart cache** — doesn't reprocess completed evaluations

---

## 📚 References

- [Anthropic API Docs](https://docs.anthropic.com/) — Claude models + Tool Use
- [Streamlit](https://streamlit.io/) — UI framework for data apps
- [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/) — HTML parsing
- [python-docx](https://python-docx.readthedocs.io/) — .docx file reading

---

<p align="center">
  Made with 🔭 by Arthur Santos
</p>
