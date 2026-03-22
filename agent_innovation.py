"""
Agent Innovation — Radar Tecnológico Namu
==========================================
Agente de IA que avalia tecnologias para o radar de inovação da Namu.

  1. Recebe nome da tecnologia + URL âncora
  2. Lê documentos internos de processo como referência
  3. Claude faz buscas web adicionais via ferramenta nativa
  4. Preenche template estruturado de avaliação

Pré-requisitos:
    pip install -r requirements.txt

Configuração:
    Crie .env com: ANTHROPIC_API_KEY=sk-ant-...

Como usar:
    python agent_innovation.py
"""

import os
import re
import glob
import json
import hashlib
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from dotenv import load_dotenv
import anthropic
from docx import Document

load_dotenv()
client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

# Tavily (optional, additive search provider)
USE_TAVILY = os.getenv("USE_TAVILY", "false").lower() in ("true", "1", "yes")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY", "")

_tavily_client = None


def _get_tavily_client():
    global _tavily_client
    if _tavily_client is None:
        from tavily import TavilyClient
        _tavily_client = TavilyClient(api_key=TAVILY_API_KEY)
    return _tavily_client


def buscar_tavily(query: str, max_results: int = 5) -> str:
    """Pre-fetch search results via Tavily and return formatted snippets."""
    try:
        tavily = _get_tavily_client()
        response = tavily.search(
            query=query,
            max_results=max_results,
            search_depth="advanced",
            topic="general",
        )
        partes = []
        for r in response.get("results", []):
            title = r.get("title", "")
            url = r.get("url", "")
            content = r.get("content", "")
            partes.append(f"- **{title}** ({url})\n  {content}")
        return "\n\n".join(partes) if partes else ""
    except Exception as e:
        print(f"   ⚠ Tavily search failed: {e}")
        return ""

# Modelo: troque para "claude-sonnet-4-20250514" se quiser mais qualidade
MODELO = "claude-haiku-4-5-20251001"

CACHE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cache")

# Custos por 1M tokens (USD)
CUSTOS = {
    "claude-haiku-4-5-20251001":  {"input": 0.80, "output": 4.00},
    "claude-sonnet-4-20250514":   {"input": 3.00, "output": 15.00},
}
CUSTO_WEB_SEARCH = 0.10  # por busca

# ─────────────────────────────────────────
# 0. LEITURA DOS DOCUMENTOS DE PROCESSO
# ─────────────────────────────────────────

DOCS_PATH = r"C:\Users\Arthur Santos\Documents\0. Processo de Inovação"


def carregar_documentos_processo(max_chars_por_doc: int = 3000) -> str:
    """Lê os .docx de processo de inovação como contexto de referência."""
    arquivos = sorted(glob.glob(os.path.join(DOCS_PATH, "*.docx")))
    if not arquivos:
        return ""

    partes = []
    for arq in arquivos:
        try:
            doc = Document(arq)
            texto = "\n".join(p.text for p in doc.paragraphs if p.text.strip())
            nome = os.path.basename(arq)
            partes.append(f"--- {nome} ---\n{texto[:max_chars_por_doc]}")
        except Exception:
            continue

    return "\n\n".join(partes)


# Carrega uma vez na inicialização
DOCUMENTOS_PROCESSO = carregar_documentos_processo()

# ─────────────────────────────────────────
# CONTEXTO DA NAMU
# ─────────────────────────────────────────

CONTEXTO_NAMU = """
A Namu é uma empresa brasileira de health-tech focada em produto digital.
Produtos atuais:
- VitalScan: escaneamento facial para obtenção de dados de saúde
- FoodScan: análise de prato e cálculo de calorias via imagem

Stack e contexto técnico: produto mobile/web, dados de saúde, computer vision, IA aplicada.
Momento estratégico: expansão de capacidades de dados, escalabilidade de plataforma,
criação de ativos proprietários e movimentos de phygital/lifestyle.

Ao analisar tecnologias:
- Seja objetivo e estrategista, não genérico
- Não force conexão com VitalScan ou FoodScan — são apenas referência de contexto
- Foque no potencial estratégico real, não em buzzwords de saúde
- Pense como um analista sênior de inovação, não como um entusiasta de tecnologia
"""

TEMPLATE = """
## IDENTIFICAÇÃO DA TECNOLOGIA

**Nome da Tecnologia:** [preencher]
**Categoria:** [IA / Infra / Automação / Data / HealthTech / outro]
**Fonte:** [Open source / Proprietária / Startup / Big Tech]
**Link oficial/Repo:** [preencher]
**Data de entrada no Radar:** {data_hoje}

---

## CRITÉRIO DE ENTRADA NO RADAR

⬜ Potencial de Impacto Estratégico
⬜ Capacidade de Geração ou Estruturação de Dados
⬜ Criação de Ativo Proprietário
⬜ Aumento de Escalabilidade ou Eficiência
⬜ Movimento Relevante no Mercado

**Por que entrou no Radar no contexto da Namu:**
[preencher — objetivo, estratégico, sem ser genérico]

---

## TRIAGEM

### Possível Problema Resolvido

**Qual dor potencial ela ataca?**
[preencher]

**É dor interna (Operação/Tech) ou externa (Usuário)?**
[preencher]

**Atua mais em:**
⬜ Plataforma
⬜ Massificação
⬜ Dados & Impacto
⬜ Lifestyle & Phygital
⬜ Educação

---

### Maturidade Tecnológica

**Nível de maturidade:**
⬜ Experimental
⬜ Early Adoption
⬜ Consolidado

**Está sendo usada por players relevantes?**
[sim/não + quem, se sim]

**Possui documentação sólida?**
[sim/não + observação breve]

**Tem comunidade ativa?**
[sim/não + observação breve]

---

### Estimativa Financeira Inicial

**Estimativa qualitativa de custo:**
⬜ Muito Baixo  ⬜ Baixo  ⬜ Moderado  ⬜ Alto  ⬜ Muito Alto

**Modelo de custo:**
⬜ Open-source  ⬜ SaaS por usuário  ⬜ API por requisição  ⬜ Infra própria  ⬜ Licença enterprise

**Observação:**
[preencher]

---

### Complexidade Técnica Inicial

**Avaliação preliminar (qualitativa):**
[preencher]

**Integração com stack atual:**
⬜ Simples
⬜ Moderada
⬜ Complexo

**Exige infraestrutura própria?**
[sim/não + detalhes]

**Exige especialização específica?**
[sim/não + qual]

**Risco regulatório aparente?**
[sim/não + contexto LGPD/ANVISA se aplicável]

---

### Decisão de Triagem

⬜ Avança na Priorização (TAM/SAM/SOM)
⬜ Mantém Observação em Radar
⬜ Descartado

**Justificativa:**
[objetivo, estratégico, específico para a Namu]
"""


TEMPLATE_PRIORIZACAO = """
## SCORE TAM/SAM/SOM

| Critério | Peso | Nota (1-5) |
|---|---|---|
| TAM Tecnológico | 30% | [nota] |
| SAM (Fit de Mercado) | 40% | [nota] |
| SOM (Viabilidade) | 30% | [nota] |

**Prioridade Namu = (TAM x 0.3) + (SAM x 0.4) + (SOM x 0.3) = [calcular]**

**TAM:** Transformacional para a empresa.
[Explique]

**SAM:** Alta aderência à demanda do mercado.
[Explique]

**SOM:** Tecnologicamente viável de integrar e escalar.
[Explique]

---

## FRAMEWORK DE NEGÓCIOS

⬜ Benchmark (Iniciativas de Mercado)
⬜ Diferenciação (Vendas)
⬜ Qualidade (Evolução do que já existe)
⬜ Produtividade (Eficiência Operacional)
⬜ Flexibilidade (Integração e Evolução)
⬜ Eficiência (Otimização de Custos)

**Benchmark (Iniciativas de Mercado)**
[Explique]

**Diferenciação (Vendas)**
[Explique]

**Qualidade (Evolução do que já existe)**
[Explique]

**Produtividade (Eficiência Operacional)**
[Explique]

**Flexibilidade (Integração e Evolução)**
[Explique]

**Eficiência (Otimização de Custos)**
[Explique]

---

## CONCLUSÃO

[Conclusão estratégica objetiva para a Namu]
"""


# ─────────────────────────────────────────
# 1. CACHE
# ─────────────────────────────────────────

def _cache_key(nome: str, url: str) -> str:
    raw = f"{nome.lower().strip()}|{url.strip()}"
    return hashlib.md5(raw.encode()).hexdigest()


def cache_get(nome: str, url: str) -> str | None:
    path = os.path.join(CACHE_DIR, f"{_cache_key(nome, url)}.json")
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data.get("resultado")
    return None


def cache_set(nome: str, url: str, resultado: str):
    os.makedirs(CACHE_DIR, exist_ok=True)
    path = os.path.join(CACHE_DIR, f"{_cache_key(nome, url)}.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump({"nome": nome, "url": url, "resultado": resultado,
                   "data": datetime.now().isoformat()}, f, ensure_ascii=False)


# ─────────────────────────────────────────
# 2. VALIDAÇÃO DE URL
# ─────────────────────────────────────────

def validar_url(url: str) -> tuple[bool, str]:
    """Testa se a URL é acessível. Retorna (ok, mensagem)."""
    if not url:
        return True, ""
    try:
        resp = requests.head(url, timeout=10, allow_redirects=True,
                             headers={"User-Agent": "Mozilla/5.0"})
        if resp.status_code < 400:
            return True, f"URL acessível ({resp.status_code})"
        return False, f"URL retornou status {resp.status_code}"
    except requests.RequestException as e:
        return False, f"URL inacessível: {e}"


# ─────────────────────────────────────────
# 3. ESTIMATIVA DE CUSTO
# ─────────────────────────────────────────

def estimar_custo(nome: str, url_ancora: str = "") -> dict:
    """Estima custo da avaliação antes de rodar."""
    # Estima tokens de input
    chars_prompt = (
        len(CONTEXTO_NAMU) + len(TEMPLATE) + len(DOCUMENTOS_PROCESSO)
        + len(nome) + 500  # instruções fixas
    )
    if url_ancora:
        chars_prompt += 6000  # max_chars da URL
    tokens_input = chars_prompt // 4  # ~4 chars por token
    tokens_output = 4000  # estimativa do template preenchido

    custos = CUSTOS.get(MODELO, CUSTOS["claude-haiku-4-5-20251001"])
    custo_input = (tokens_input / 1_000_000) * custos["input"]
    custo_output = (tokens_output / 1_000_000) * custos["output"]
    custo_search = CUSTO_WEB_SEARCH * 3  # média de 3 buscas

    total = custo_input + custo_output + custo_search

    return {
        "tokens_input": tokens_input,
        "tokens_output": tokens_output,
        "custo_tokens": round(custo_input + custo_output, 4),
        "custo_search": round(custo_search, 2),
        "custo_total": round(total, 2),
    }


# ─────────────────────────────────────────
# 4. LEITURA DA URL ÂNCORA
# ─────────────────────────────────────────

def ler_url(url: str, max_chars: int = 6000) -> str:
    """Lê o conteúdo principal de uma URL."""
    if not url:
        return ""

    try:
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            )
        }
        resp = requests.get(url, headers=headers, timeout=15)
        resp.raise_for_status()

        soup = BeautifulSoup(resp.text, "html.parser")

        for tag in soup(["script", "style", "nav", "footer",
                          "header", "aside", "form", "iframe"]):
            tag.decompose()

        texto = soup.get_text(separator="\n", strip=True)
        linhas = [l for l in texto.split("\n") if len(l.strip()) > 30]

        return "\n".join(linhas)[:max_chars]

    except Exception as e:
        return f"[Não foi possível acessar {url}: {e}]"


# ─────────────────────────────────────────
# 5. ANÁLISE HÍBRIDA VIA CLAUDE
# ─────────────────────────────────────────

def analisar_tecnologia(nome: str, url_ancora: str = "") -> str:
    """
    Claude recebe a URL âncora + faz buscas web adicionais automaticamente.
    Ao final preenche o template completo.
    """
    # Verifica cache
    cached = cache_get(nome, url_ancora)
    if cached:
        print("\n✅ Resultado encontrado no cache (sem custo)")
        return cached

    print("\n🧠 Claude analisando com busca web + URL âncora...")

    # Lê a URL âncora se fornecida
    conteudo_ancora = ""
    if url_ancora:
        print(f"   📖 Lendo URL âncora: {url_ancora}")
        conteudo_ancora = ler_url(url_ancora)
        print("   ✓ URL lida")

    # Tavily pre-fetch (additive — runs before Claude call when enabled)
    tavily_texto = ""
    if USE_TAVILY and TAVILY_API_KEY:
        print(f"   🔎 Buscando via Tavily: {nome}")
        tavily_resultado = buscar_tavily(nome)
        if tavily_resultado:
            tavily_texto = (
                f"\n\nRESULTADOS DE BUSCA (TAVILY):\n"
                f"(Resultados pré-buscados via Tavily para contexto adicional)\n\n"
                f"{tavily_resultado}"
            )
            print("   ✓ Resultados Tavily obtidos")

    # Monta o prompt
    ancora_texto = (
        f"\n\nCONTEÚDO DA URL ÂNCORA ({url_ancora}):\n{conteudo_ancora}"
        if conteudo_ancora else ""
    )

    template_preenchido = TEMPLATE.format(
        data_hoje=datetime.now().strftime("%d/%m/%Y")
    )

    # Monta bloco de documentos de processo (se disponível)
    docs_texto = ""
    if DOCUMENTOS_PROCESSO:
        docs_texto = (
            f"\n\nDOCUMENTOS DE REFERÊNCIA DO PROCESSO DE INOVAÇÃO DA NAMU:\n"
            f"(Use APENAS como referência de critérios e etapas do processo. "
            f"NÃO invente dados — use só o que encontrar nas buscas web e na URL âncora.)\n\n"
            f"{DOCUMENTOS_PROCESSO}"
        )
        print(f"   📄 {len(DOCUMENTOS_PROCESSO):,} chars de documentos de processo carregados")

    prompt = f"""Você é um analista sênior de inovação tecnológica em uma empresa de health-tech brasileira.

CONTEXTO DA EMPRESA:
{CONTEXTO_NAMU}
{docs_texto}

TECNOLOGIA A AVALIAR: {nome}
{tavily_texto}{ancora_texto}

SUA TAREFA:
1. Use a ferramenta de busca web para pesquisar sobre "{nome}" — busque:
   - Documentação oficial e casos de uso
   - Players e empresas que já adotam
   - Modelo de precificação
   - Nível de maturidade no mercado
   - Riscos regulatórios se aplicável

2. Com base na URL âncora (se fornecida) E nas buscas que fizer, preencha 
   COMPLETAMENTE o template abaixo em português.

INSTRUÇÕES DE PREENCHIMENTO:
- Seja direto, objetivo e estrategista — sem linguagem genérica
- Para checkboxes (⬜), marque com ✅ os que se aplicam
- Foque no contexto estratégico da Namu especificamente
- Não mencione bem-estar e saúde de forma genérica
- Use os documentos de processo como referência de critérios, NÃO invente dados
- Baseie-se SOMENTE em fatos encontrados nas buscas web e na URL âncora

TEMPLATE:
{template_preenchido}"""

    # Chama Claude com web search nativo
    resposta = client.messages.create(
        model=MODELO,
        max_tokens=16000,
        tools=[{
            "type": "web_search_20250305",
            "name": "web_search",
            "max_uses": 5  # até 5 buscas automáticas por análise
        }],
        messages=[{"role": "user", "content": prompt}]
    )

    # Extrai todos os blocos de texto e filtra raciocínio intermediário
    partes_texto = []
    buscas_feitas = 0

    for bloco in resposta.content:
        if bloco.type == "text":
            partes_texto.append(bloco.text)
        elif bloco.type == "server_tool_use":
            buscas_feitas += 1
            query = getattr(bloco.input, "query", "")
            print(f"   🔍 Busca {buscas_feitas}: {query}")

    print(f"   ✓ {buscas_feitas} buscas realizadas pelo Claude")
    print("   ✓ Template preenchido")

    # Junta tudo e remove linhas de raciocínio do Claude
    texto_completo = "\n".join(partes_texto)
    linhas = texto_completo.split("\n")
    linhas_filtradas = [
        l for l in linhas
        if not re.match(
            r'^(Vou |Agora vou |Deixe-me |Deixa eu |Let me |Now I|'
            r'Com base |Preciso |Vamos |Buscando |Pesquisando )',
            l.strip()
        )
    ]

    resultado = "\n".join(linhas_filtradas).strip()

    # Salva no cache
    cache_set(nome, url_ancora, resultado)

    return resultado


# ─────────────────────────────────────────
# 5b. PRIORIZAÇÃO (SCORING)
# ─────────────────────────────────────────

def priorizar_tecnologia(nome: str, resultado_triagem: str) -> str:
    """
    Etapa 2: Recebe o resultado da triagem e gera o scoring TAM/SAM/SOM
    + framework de negócios. Sem web search (usa só a triagem como input).
    """
    # Cache separado pra priorização
    cache_key_prio = f"prio|{nome}"
    cached = cache_get(cache_key_prio, "")
    if cached:
        print("\n✅ Priorização encontrada no cache (sem custo)")
        return cached

    print("\n📊 Claude gerando scoring de priorização...")

    prompt = f"""Você é um analista sênior de inovação tecnológica.

CONTEXTO DA EMPRESA:
{CONTEXTO_NAMU}

RESULTADO DA TRIAGEM (já realizada):
{resultado_triagem}

SUA TAREFA:
Com base EXCLUSIVAMENTE na triagem acima, preencha o template de priorização abaixo.

REGRAS DE SCORING:
- TAM (peso 30%): 5 = muda o jogo da empresa / 1 = melhoria mínima
- SAM (peso 40%): 5 = desejo direto do cliente / 1 = pouco interesse
- SOM (peso 30%): 5 = fácil de empacotar (API/Doc) / 1 = muito complexo
- Calcule: (TAM x 0.3) + (SAM x 0.4) + (SOM x 0.3) = Prioridade Namu
- Para checkboxes (⬜), marque com ✅ os que se aplicam
- Seja objetivo e estratégico, baseado nos dados da triagem
- NÃO invente dados que não estão na triagem

TEMPLATE:
{TEMPLATE_PRIORIZACAO}"""

    resposta = client.messages.create(
        model=MODELO,
        max_tokens=4000,
        messages=[{"role": "user", "content": prompt}]
    )

    resultado = resposta.content[0].text.strip()

    # Salva no cache
    cache_set(cache_key_prio, "", resultado)

    print("   ✓ Scoring preenchido")
    return resultado


# ─────────────────────────────────────────
# 6. SALVAR DOCUMENTO
# ─────────────────────────────────────────

def salvar_documento(nome: str, conteudo: str) -> str:
    nome_arquivo = (
        f"radar_{nome.lower().replace(' ', '_')}_"
        f"{datetime.now().strftime('%Y%m%d_%H%M')}.md"
    )
    cabecalho = (
        f"# Radar Tecnológico — {nome}\n"
        f"*Gerado em {datetime.now().strftime('%d/%m/%Y às %H:%M')} "
        f"via Claude Sonnet 4 + Web Search*\n"
        f"*Revisar antes de usar*\n\n---\n\n"
    )
    with open(nome_arquivo, "w", encoding="utf-8") as f:
        f.write(cabecalho + conteudo)

    return nome_arquivo


# ─────────────────────────────────────────
# 7. EXECUÇÃO PRINCIPAL
# ─────────────────────────────────────────

def avaliar_tecnologia(nome: str = "", url_ancora: str = ""):
    if not nome:
        print("\n" + "="*52)
        print("  RADAR TECNOLÓGICO — NAMU")
        print(f"  {MODELO} + Web Search nativo")
        print("="*52)
        nome = input("\nNome da tecnologia: ").strip()
        url_ancora = input(
            "URL âncora (site/doc que te fez colocar no radar): "
        ).strip()

    if not nome:
        print("❌ Nome é obrigatório.")
        return

    print(f"\n🚀 Avaliando '{nome}'...\n")

    documento = analisar_tecnologia(nome, url_ancora)
    arquivo = salvar_documento(nome, documento)

    print("\n" + "="*52)
    print(f"✅ Arquivo salvo: {arquivo}")
    print("="*52)
    print("\n📄 RESULTADO:\n")
    print(documento)
    print("\n📋 Próximos passos:")
    print("   1. Abra o arquivo .md gerado nesta pasta")
    print("   2. Revise os campos que precisar")
    print("   3. Cole no seu Google Doc")

    return documento, arquivo


# ─────────────────────────────────────────
# MODO BATCH
# ─────────────────────────────────────────

def avaliar_lista(tecnologias: list):
    """
    Avalia várias tecnologias em sequência.

    Exemplo:
        avaliar_lista([
            {
                "nome": "Ada Health API",
                "url_ancora": "https://ada.com"
            },
            {
                "nome": "Multimodal RAG",
                "url_ancora": ""  # sem âncora — só busca web
            },
        ])
    """
    for item in tecnologias:
        print(f"\n{'='*52}\nAvaliando: {item['nome']}\n{'='*52}")
        avaliar_tecnologia(
            nome=item["nome"],
            url_ancora=item.get("url_ancora", "")
        )
    print(f"\n✅ {len(tecnologias)} tecnologias avaliadas.")


if __name__ == "__main__":
    avaliar_tecnologia()