# Agent Innovation — Namu

AI agent that evaluates technologies for Namu's innovation radar. It scrapes web sources, reads internal process documents, and uses Claude (Anthropic) with web search to fill a structured evaluation template.

> **Note:** All generated output is in Brazilian Portuguese (pt-BR), as this tool is designed for internal use at Namu.

## What it does

1. Takes a technology name + anchor URL as input
2. Loads internal innovation process documents (`.docx`) as reference
3. Scrapes the anchor URL content
4. Claude performs additional web searches automatically
5. Generates a complete radar evaluation in Markdown (`.md`)

## Setup

```bash
pip install -r requirements.txt
```

Create a `.env` file:

```
ANTHROPIC_API_KEY=sk-ant-your-key-here
```

## Usage

### Web interface (Streamlit)

```bash
streamlit run app.py
```

### CLI — Interactive mode

```bash
python agent_innovation.py
```

### CLI — Batch mode

```python
from agent_innovation import avaliar_lista

avaliar_lista([
    {"nome": "Ada Health API", "url_ancora": "https://ada.com"},
    {"nome": "Multimodal RAG", "url_ancora": ""},
])
```

## Model

Default: `claude-haiku-4-5-20251001` (cost-effective).
Change the `MODELO` constant in the script to `claude-sonnet-4-20250514` for higher quality.

## Output

```
radar_technology_name_20250101_1200.md
```

## Template fields

- Technology identification and category
- Radar entry criteria (strategic impact, data generation, scalability)
- Triage (pain point, maturity, cost estimate, technical complexity)
- Triage decision (advance / observe / discard)
