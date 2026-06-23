<p align="center">
  <img src="https://img.shields.io/badge/python-3.11+-blue?logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/framework-CrewAI-ff6b35?logo=data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIyNCIgaGVpZ2h0PSIyNCI+PHRleHQgeT0iMjAiIGZvbnQtc2l6ZT0iMjAiPvCfpI88L3RleHQ+PC9zdmc+" alt="CrewAI">
  <img src="https://img.shields.io/badge/LLM-Claude%20(Anthropic)-blueviolet?logo=anthropic&logoColor=white" alt="Claude">
  <img src="https://img.shields.io/badge/output-PDF%20Report-red?logo=adobe&logoColor=white" alt="PDF">
  <img src="https://img.shields.io/badge/license-MIT-green" alt="License">
</p>

<h1 align="center">🔭 Agent Innovation</h1>

<p align="center">
  <strong>Autonomous AI agent for technology viability assessment</strong><br>
  Multi-agent system that researches GitHub repos, analyzes licenses, scrapes documentation,<br>
  evaluates market positioning, and generates structured PDF reports.
</p>

---

## What it does

Give it a technology name (and optionally a GitHub URL), and the agent autonomously:

1. **Researches** — Scrapes the repo, analyzes license (MIT/Apache = ✅, GPL = ⚠️), checks activity, stars, contributors
2. **Analyzes** — Searches for market news, identifies competitors, evaluates adoption and business risk
3. **Reports** — Synthesizes everything into a scored Technical Viability Report exported as PDF

```
Input: "LangGraph" + https://github.com/langchain-ai/langgraph
                           ↓
         ┌─────────────────────────────────────┐
         │  🔬 Researcher Agent                │
         │  GitHub API + Web Scraping          │
         │  License · Stars · Activity · Docs  │
         └──────────────┬──────────────────────┘
                        ↓
         ┌─────────────────────────────────────┐
         │  📊 Market Analyst Agent            │
         │  News · Competitors · Adoption      │
         │  Funding · Risk Assessment          │
         └──────────────┬──────────────────────┘
                        ↓
         ┌─────────────────────────────────────┐
         │  📄 Report Generator Agent          │
         │  Structured scoring (1-5)           │
         │  Recommendation: ADOPT/HOLD/AVOID   │
         │  PDF export                         │
         └──────────────┬──────────────────────┘
                        ↓
              output/report_langgraph_20250401.pdf
```

---

## Architecture

Built with **CrewAI** — a multi-agent orchestration framework. Three specialized agents collaborate sequentially:

| Agent | Role | Tools |
|-------|------|-------|
| 🔬 Researcher | Deep technical analysis of the technology | GitHub API, Web Scraper |
| 📊 Market Analyst | Competitive landscape and business viability | Web Scraper |
| 📄 Reporter | Synthesizes findings into scored PDF report | PDF Generator |

### Custom Tools

| Tool | What it does |
|------|-------------|
| `analyze_github_repo` | Calls GitHub API — extracts stars, license, activity, contributors, topics |
| `scrape_website` | BeautifulSoup — extracts clean text from any URL (max 8K chars) |
| `generate_pdf_report` | FPDF2 — generates structured PDF with headers, sections, and scoring |

---

## Quick Start

### Prerequisites

- Python 3.11+
- [Anthropic API key](https://console.anthropic.com/)

### Installation

```bash
git clone https://github.com/Ninjexxx/agent_innovation.git
cd agent_innovation

python -m venv .venv
.venv\Scripts\activate        # Windows
source .venv/bin/activate     # Linux/Mac

pip install -r requirements.txt
```

### Configuration

```bash
cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY
```

### Usage

```bash
# With GitHub URL (recommended)
python main.py "LangGraph" "https://github.com/langchain-ai/langgraph"

# Without URL (agent will search)
python main.py "CrewAI"
```

---

## Output

### PDF Report Structure

| Section | Content |
|---------|---------|
| Executive Summary | What it is + verdict in 2-3 sentences |
| Technical Assessment | Repo metrics, license analysis, capabilities, risks |
| Market Analysis | Adoption, competitors, funding, market risks |
| Viability Score | 5 criteria scored 1-5 with notes |
| Recommendation | ADOPT / TRIAL / ASSESS / HOLD / AVOID |

Reports are saved to `output/report_{name}_{date}.pdf`

---

## Project Structure

```
agent_innovation/
├── main.py                    # Entry point — orchestrates the crew
├── src/
│   ├── agents/
│   │   └── crew.py            # Agent definitions (roles, goals, backstories)
│   ├── tools/
│   │   ├── github_tool.py     # GitHub API analysis
│   │   ├── scraper_tool.py    # Web content extraction
│   │   └── pdf_tool.py        # PDF report generation
│   └── config/
│       └── settings.py        # Environment and constants
├── output/                    # Generated PDF reports
├── requirements.txt
├── .env.example
└── README.md
```

---

## Viability Scoring Framework

| Criterion | What it measures | 5 = Best |
|-----------|-----------------|----------|
| License Compatibility | Business-friendly license? | MIT/Apache-2.0 |
| Technical Maturity | Production-ready? Active maintenance? | Stable, well-tested |
| Community Health | Contributors, issues response, docs | Large, active community |
| Market Traction | Adoption by real companies | Wide enterprise adoption |
| Business Risk | Vendor lock-in, abandonment risk | Low risk, diverse backing |

**Recommendation scale:**
- **ADOPT** (4.5-5.0) — Use in production now
- **TRIAL** (3.5-4.4) — Worth a proof-of-concept
- **ASSESS** (2.5-3.4) — Monitor and evaluate further
- **HOLD** (1.5-2.4) — Not ready yet, wait
- **AVOID** (1.0-1.4) — Significant risks, do not use

---

## Tech Stack

| Technology | Purpose |
|-----------|---------|
| [CrewAI](https://github.com/crewAIInc/crewAI) | Multi-agent orchestration |
| [Claude](https://docs.anthropic.com/) | LLM backbone (Sonnet 4) |
| [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/) | Web scraping |
| [FPDF2](https://py-pdf.github.io/fpdf2/) | PDF generation |
| GitHub REST API | Repository analysis |

---

## Cost

~$0.30-0.50 per full analysis (3 sequential agent calls with Claude Sonnet 4).

---

## License

MIT

---

<p align="center">
  Made with 🔭 by Arthur Santos
</p>
