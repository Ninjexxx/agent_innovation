from crewai import Agent
from src.tools.github_tool import analyze_github_repo
from src.tools.scraper_tool import scrape_website
from src.tools.pdf_tool import generate_pdf_report
from src.config.settings import MODEL


def create_researcher() -> Agent:
    return Agent(
        role="Senior Technology Researcher",
        goal="Conduct deep technical research on a given technology, analyzing its GitHub repository, documentation, license, and technical capabilities.",
        backstory="""You are a senior technology researcher with 10+ years of experience 
        evaluating open-source projects. You specialize in assessing code quality, 
        community health, license implications, and technical architecture. You are 
        methodical and always back your findings with data.""",
        tools=[analyze_github_repo, scrape_website],
        llm=MODEL,
        verbose=True,
    )


def create_market_analyst() -> Agent:
    return Agent(
        role="Market Intelligence Analyst",
        goal="Analyze market positioning, competitive landscape, adoption trends, and business viability of the technology.",
        backstory="""You are a market intelligence analyst who tracks emerging technologies 
        and their commercial potential. You evaluate market traction by analyzing news, 
        funding, partnerships, competitor moves, and adoption patterns. You think 
        strategically about business implications.""",
        tools=[scrape_website],
        llm=MODEL,
        verbose=True,
    )


def create_report_generator() -> Agent:
    return Agent(
        role="Technical Report Specialist",
        goal="Synthesize research and market analysis into a clear, structured Technical Viability Report with a final recommendation.",
        backstory="""You are a technical writer who specializes in executive-level technology 
        assessments. You transform complex research into actionable reports with clear 
        structure, scoring frameworks, and strategic recommendations. Your reports are 
        used by CTOs and VP Engineering to make build-vs-buy decisions.""",
        tools=[generate_pdf_report],
        llm=MODEL,
        verbose=True,
    )
