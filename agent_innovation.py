"""
Agent Innovation — Esteira de Inovação Namu
=============================================
Agente de IA para radar de inovação: mapeamento e triagem de tecnologias.

Configuração (.env):
    ANTHROPIC_API_KEY=sk-ant-...
    MODELO_TRIAGEM=claude-sonnet-4-20250514
    MODELO_MAPEAMENTO=claude-haiku-4-5-20251001
    CACHE_TTL_DIAS=30

Como usar:
    streamlit run app.py
    python agent_innovation.py
"""

import os
import re
import glob
import json
import hashlib
import time
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from dotenv import load_dotenv
import anthropic
from docx import Document

load_dotenv()
client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODELO_MAPEAMENTO = os.getenv("MODELO_MAPEAMENTO", "claude-haiku-4-5-20251001")
MODELO_TRIAGEM = os.getenv("MODELO_TRIAGEM", "claude-sonnet-4-20250514")
CACHE_DIR = os.path.join(BASE_DIR, "cache")
CACHE_TTL_DIAS = int(os.getenv("CACHE_TTL_DIAS", "30"))
DOCS_PATH = r"C:\Users\Arthur Santos\Documents\0. Processo de Inovação"
CUSTO_WEB_SEARCH = 0.10

CUSTOS = {
    "claude-haiku-4-5-20251001":  {"input": 0.80, "output": 4.00},
    "claude-sonnet-4-20250514":   {"input": 3.00, "output": 15.00},
}

REGEX_RACIOCINIO = re.compile(
    r'^(Vou |Agora vou |Deixe-me |Deixa eu |Let me |Now I|'
    r'Com base |Preciso |Vamos |Buscando |Pesquisando )'
)


def _carregar_arquivo(nome_arquivo: str) -> str:
    path = os.path.join(BASE_DIR, nome_arquivo)
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return f.read().strip()
    return ""


CONTEXTO_NAMU = _carregar_arquivo("contexto_namu.txt")
TEMPLATE = _carregar_arquivo("template_triagem.txt")


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
            partes.append(f"--- {os.path.basename(arq)} ---\n{texto[:max_chars_por_doc]}")
        except Exception:
            continue

    return "\n\n".join(partes)


DOCUMENTOS_PROCESSO = carregar_documentos_processo()


# ── Cache ──

def _cache_key(nome: str, url: str) -> str:
    raw = f"{nome.lower().strip()}|{url.strip()}"
    return hashlib.md5(raw.encode()).hexdigest()


def cache_get(nome: str, url: str) -> str | None:
    path = os.path.join(CACHE_DIR, f"{_cache_key(nome, url)}.json")
    if not os.path.exists(path):
        return None
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f).get("resultado")


def cache_set(nome: str, url: str, resultado: str):
    os.makedirs(CACHE_DIR, exist_ok=True)
    path = os.path.join(CACHE_DIR, f"{_cache_key(nome, url)}.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump({"nome": nome, "url": url, "resultado": resultado,
                   "data": datetime.now().isoformat()}, f, ensure_ascii=False)


def limpar_cache_antigo():
    """Remove arquivos de cache com mais de CACHE_TTL_DIAS dias."""
    if not os.path.exists(CACHE_DIR):
        return
    limite = time.time() - (CACHE_TTL_DIAS * 86400)
    removidos = 0
    for arq in glob.glob(os.path.join(CACHE_DIR, "*.json")):
        if os.path.getmtime(arq) < limite:
            os.remove(arq)
            removidos += 1
    if removidos:
        print(f"🗑️ {removidos} cache(s) expirado(s) removido(s) (>{CACHE_TTL_DIAS} dias)")


limpar_cache_antigo()


# ── Utilitários ──

def validar_url(url: str) -> tuple[bool, str]:
    """Testa se a URL é acessível."""
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


def validar_links_resposta(texto: str) -> str:
    """Valida URLs encontradas na resposta e marca as inválidas."""
    urls = re.findall(r'https?://[^\s\)>\]]+', texto)
    urls_unicas = list(dict.fromkeys(urls))

    invalidas = []
    for url in urls_unicas:
        url_limpa = url.rstrip(".,;:|")
        ok, _ = validar_url(url_limpa)
        if not ok:
            invalidas.append(url_limpa)

    if invalidas:
        aviso = "\n\n⚠️ **Links não verificados (podem estar incorretos):**\n"
        for url in invalidas:
            aviso += f"- {url}\n"
        texto += aviso

    return texto


def estimar_custo(nome: str, url_ancora: str = "", modelo: str = MODELO_TRIAGEM) -> dict:
    """Estima custo da avaliação antes de rodar."""
    chars_prompt = len(CONTEXTO_NAMU) + len(TEMPLATE) + len(DOCUMENTOS_PROCESSO) + len(nome) + 500
    if url_ancora:
        chars_prompt += 6000
    tokens_input = chars_prompt // 4
    tokens_output = 4000

    custos = CUSTOS.get(modelo, CUSTOS["claude-haiku-4-5-20251001"])
    custo_input = (tokens_input / 1_000_000) * custos["input"]
    custo_output = (tokens_output / 1_000_000) * custos["output"]
    custo_search = CUSTO_WEB_SEARCH * 3

    return {
        "tokens_input": tokens_input,
        "tokens_output": tokens_output,
        "custo_tokens": round(custo_input + custo_output, 4),
        "custo_search": round(custo_search, 2),
        "custo_total": round(custo_input + custo_output + custo_search, 2),
    }


def ler_url(url: str, max_chars: int = 6000) -> str:
    """Extrai texto limpo de uma URL via BeautifulSoup."""
    if not url:
        return ""
    try:
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        resp = requests.get(url, headers=headers, timeout=15)
        resp.raise_for_status()

        soup = BeautifulSoup(resp.text, "html.parser")
        for tag in soup(["script", "style", "nav", "footer", "header", "aside", "form", "iframe"]):
            tag.decompose()

        texto = soup.get_text(separator="\n", strip=True)
        linhas = [l for l in texto.split("\n") if len(l.strip()) > 30]
        return "\n".join(linhas)[:max_chars]
    except Exception as e:
        return f"[Não foi possível acessar {url}: {e}]"


def _extrair_resposta(resposta) -> tuple[str, int]:
    """Extrai texto e conta buscas de uma resposta Claude com web search."""
    partes_texto = []
    buscas = 0

    for bloco in resposta.content:
        if bloco.type == "text":
            partes_texto.append(bloco.text)
        elif bloco.type == "server_tool_use":
            buscas += 1
            query = getattr(bloco.input, "query", "")
            print(f"   🔍 Busca {buscas}: {query}")

    texto = "\n".join(partes_texto)
    linhas = [l for l in texto.split("\n") if not REGEX_RACIOCINIO.match(l.strip())]
    resultado = "\n".join(linhas).strip()
    resultado = re.sub(r'\s+([.,;:!?])', r'\1', resultado)
    return resultado, buscas


# ── Triagem ──

def analisar_tecnologia(nome: str, url_ancora: str = "", modelo: str = MODELO_TRIAGEM) -> str:
    """Triagem completa: URL âncora + web search + template estruturado."""
    cached = cache_get(nome, url_ancora)
    if cached:
        print("\n✅ Resultado encontrado no cache (sem custo)")
        return cached

    print("\n🧠 Claude analisando com busca web + URL âncora...")
    print(f"   🤖 Modelo: {modelo}")

    conteudo_ancora = ""
    if url_ancora:
        print(f"   📖 Lendo URL âncora: {url_ancora}")
        conteudo_ancora = ler_url(url_ancora)
        print("   ✓ URL lida")

    ancora_texto = (
        f"\n\nCONTEÚDO DA URL ÂNCORA ({url_ancora}):\n{conteudo_ancora}"
        if conteudo_ancora else ""
    )

    template_preenchido = TEMPLATE.format(data_hoje=datetime.now().strftime("%d/%m/%Y"))

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
{ancora_texto}

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
{template_preenchido}

Ao final do template preenchido, adicione obrigatoriamente:

---

**Fontes consultadas:**
- [URL 1] — [o que encontrou nesta fonte]
- [URL 2] — [o que encontrou nesta fonte]
- [URL N] — [o que encontrou nesta fonte]

REGRA: NÃO faça perguntas ao usuário — este é um relatório final."""

    resposta = client.messages.create(
        model=modelo,
        max_tokens=16000,
        tools=[{"type": "web_search_20250305", "name": "web_search", "max_uses": 5}],
        messages=[{"role": "user", "content": prompt}]
    )

    resultado, buscas = _extrair_resposta(resposta)
    print(f"   ✓ {buscas} buscas realizadas pelo Claude")
    print("   ✓ Template preenchido")
    print("   🔗 Validando links...")

    resultado = validar_links_resposta(resultado)

    cache_set(nome, url_ancora, resultado)
    return resultado


# ── Mapeamento ──

def mapear_tecnologias(categoria: str) -> str:
    """Busca tecnologias open-source testáveis por categoria via Haiku + web search."""
    cache_key_map = f"map|{categoria}"
    cached = cache_get(cache_key_map, "")
    if cached:
        print("\n✅ Mapeamento encontrado no cache (sem custo)")
        return cached

    print(f"\n🗺️ Claude mapeando tecnologias open-source em '{categoria}'...")
    print(f"   🤖 Modelo: {MODELO_MAPEAMENTO}")

    prompt = f"""Você é um analista sênior de inovação tecnológica em uma empresa de health-tech brasileira.

CONTEXTO DA EMPRESA:
{CONTEXTO_NAMU}

SUA TAREFA:
Busque e liste tecnologias OPEN-SOURCE relevantes na categoria: "{categoria}"

REGRAS OBRIGATÓRIAS:
- SOMENTE tecnologias open-source (GitHub, HuggingFace, GitLab, etc.)
- SOMENTE projetos que podem ser clonados, testados e avaliados localmente
- NÃO inclua SaaS, APIs pagas, produtos comerciais ou empresas
- Foque em: bibliotecas, frameworks, SDKs, modelos, ferramentas de linha de comando
- Priorize projetos com boa documentação, stars e atividade recente
- Inclua datasets open-source relevantes se existirem na categoria

FORMATO OBRIGATÓRIO (não altere a estrutura):

Preencha a tabela abaixo com TODOS os projetos encontrados. Cada linha DEVE ter o link real do repositório:

| # | Nome | Repo/Link | Descrição (1 linha) | Stars | Última atividade | Linguagem | Por que avaliar |
|---|------|-----------|---------------------|-------|-----------------|-----------|----------------|
| 1 | [nome] | [URL real do repo] | [descrição] | [número ou ~estimativa] | [ano] | [lang] | [1 linha] |

Após a tabela:

**Top 3 para triagem imediata:**
1. [nome] — [justificativa em 1 linha]
2. [nome] — [justificativa em 1 linha]
3. [nome] — [justificativa em 1 linha]

---

**Fontes consultadas:**
- [URL 1] — [o que encontrou]
- [URL 2] — [o que encontrou]
- [URL N] — [o que encontrou]

REGRAS DE FORMATO:
- SEMPRE use a tabela markdown acima, mesmo que os dados sejam parciais
- SEMPRE inclua links reais (URLs completas) — nunca omita
- Se não encontrar stars exatas, escreva "~estimativa" ou "N/D"
- NÃO faça perguntas ao usuário — este é um relatório final
- NÃO mude o formato da tabela nem substitua por texto corrido
- Seja objetivo. Dados reais. Sem inventar repos ou stars."""

    resposta = client.messages.create(
        model=MODELO_MAPEAMENTO,
        max_tokens=4000,
        tools=[{"type": "web_search_20250305", "name": "web_search", "max_uses": 5}],
        messages=[{"role": "user", "content": prompt}]
    )

    resultado, buscas = _extrair_resposta(resposta)
    print(f"   ✓ {buscas} buscas realizadas")
    print("   🔗 Validando links...")

    resultado = validar_links_resposta(resultado)
    print("   ✓ Mapeamento concluído")

    cache_set(cache_key_map, "", resultado)
    return resultado


# ── Descoberta ──

def descobrir_novidades() -> str:
    """Busca novidades open-source recentes nas áreas de interesse da Namu."""
    cache_key_desc = "descoberta|semanal"
    cached = cache_get(cache_key_desc, "")
    if cached:
        print("\n✅ Descoberta encontrada no cache (sem custo)")
        return cached

    print("\n🔥 Claude buscando novidades open-source...")
    print(f"   🤖 Modelo: {MODELO_MAPEAMENTO}")

    prompt = f"""Você é um analista sênior de inovação tecnológica.

CONTEXTO DA EMPRESA:
{CONTEXTO_NAMU}

SUA TAREFA:
Busque tecnologias, bibliotecas, modelos e ferramentas OPEN-SOURCE que surgiram ou ganharam tração RECENTEMENTE (últimos 30 dias) e que sejam relevantes para o contexto da empresa acima.

ONDE BUSCAR:
- GitHub Trending e repos com crescimento recente de stars
- HuggingFace (modelos e datasets novos)
- Blogs técnicos, Hacker News, dev.to, Reddit (r/MachineLearning, r/opensource)
- Papers With Code (implementações recentes)

REGRAS:
- SOMENTE open-source (clonável, testável localmente)
- NÃO inclua SaaS, APIs pagas ou produtos comerciais
- Foque no que é NOVO ou ganhou tração recente, não em projetos antigos
- Priorize relevância para as áreas da empresa

FORMATO OBRIGATÓRIO:

| # | Nome | Repo/Link | O que faz (1 linha) | Por que é relevante | Quando surgiu/cresceu |
|---|------|-----------|---------------------|--------------------|-----------------------|
| 1 | [nome] | [URL real] | [descrição] | [relevância para a empresa] | [data/período] |

Após a tabela:

**🎯 Top 3 para avaliar esta semana:**
1. [nome] — [por que agora]
2. [nome] — [por que agora]
3. [nome] — [por que agora]

---

**Fontes consultadas:**
- [URL 1] — [o que encontrou]
- [URL 2] — [o que encontrou]

REGRAS DE FORMATO:
- SEMPRE use a tabela markdown acima
- SEMPRE inclua links reais (URLs completas)
- NÃO faça perguntas ao usuário — este é um relatório final
- NÃO inclua projetos com mais de 6 meses sem novidade
- Seja objetivo. Dados reais. Sem inventar repos."""

    resposta = client.messages.create(
        model=MODELO_MAPEAMENTO,
        max_tokens=4000,
        tools=[{"type": "web_search_20250305", "name": "web_search", "max_uses": 5}],
        messages=[{"role": "user", "content": prompt}]
    )

    resultado, buscas = _extrair_resposta(resposta)
    print(f"   ✓ {buscas} buscas realizadas")
    print("   🔗 Validando links...")

    resultado = validar_links_resposta(resultado)
    print("   ✓ Descoberta concluída")

    cache_set(cache_key_desc, "", resultado)
    return resultado


# ── Salvar documento ──

def salvar_documento(nome: str, conteudo: str, modelo: str = MODELO_TRIAGEM) -> str:
    nome_arquivo = (
        f"radar_{nome.lower().replace(' ', '_')}_"
        f"{datetime.now().strftime('%Y%m%d_%H%M')}.md"
    )
    cabecalho = (
        f"# Radar Tecnológico — {nome}\n"
        f"*Gerado em {datetime.now().strftime('%d/%m/%Y às %H:%M')} "
        f"via {modelo} + Web Search*\n"
        f"*Revisar antes de usar*\n\n---\n\n"
    )
    with open(nome_arquivo, "w", encoding="utf-8") as f:
        f.write(cabecalho + conteudo)
    return nome_arquivo


# ── CLI ──

def avaliar_tecnologia(nome: str = "", url_ancora: str = ""):
    if not nome:
        print("\n" + "="*52)
        print("  ESTEIRA DE INOVAÇÃO — NAMU")
        print(f"  {MODELO_TRIAGEM} + Web Search nativo")
        print("="*52)
        nome = input("\nNome da tecnologia: ").strip()
        url_ancora = input("URL âncora (site/doc que te fez colocar no radar): ").strip()

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

    return documento, arquivo


def mapear_cli():
    print("\n" + "="*52)
    print("  MAPEAMENTO DE TECNOLOGIAS OPEN-SOURCE")
    print("="*52)
    categoria = input("\nCategoria (ex: rPPG, facial analysis, food recognition): ").strip()
    if not categoria:
        print("❌ Categoria é obrigatória.")
        return
    resultado = mapear_tecnologias(categoria)
    print("\n" + resultado)


def avaliar_lista(tecnologias: list):
    """Avalia várias tecnologias em sequência."""
    for item in tecnologias:
        print(f"\n{'='*52}\nAvaliando: {item['nome']}\n{'='*52}")
        avaliar_tecnologia(nome=item["nome"], url_ancora=item.get("url_ancora", ""))
    print(f"\n✅ {len(tecnologias)} tecnologias avaliadas.")


if __name__ == "__main__":
    avaliar_tecnologia()
