import requests
from bs4 import BeautifulSoup
from crewai.tools import tool


@tool("Scrape Website Content")
def scrape_website(url: str) -> str:
    """Extracts the main text content from a website URL.
    Removes navigation, scripts, and boilerplate. Returns clean text (max 8000 chars)."""

    try:
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        resp = requests.get(url, headers=headers, timeout=15)
        resp.raise_for_status()

        soup = BeautifulSoup(resp.text, "html.parser")
        for tag in soup(["script", "style", "nav", "footer", "header", "aside", "form", "iframe", "noscript"]):
            tag.decompose()

        text = soup.get_text(separator="\n", strip=True)
        lines = [line for line in text.split("\n") if len(line.strip()) > 20]
        content = "\n".join(lines)[:8000]

        return f"## Content from {url}\n\n{content}"
    except requests.RequestException as e:
        return f"Failed to scrape {url}: {e}"
