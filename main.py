"""
Agent Innovation - Tech Viability Agent
========================================
Autonomous AI agent that evaluates emerging technologies.
Uses CrewAI to orchestrate multiple specialized agents that research,
analyze, and generate structured PDF reports.

Usage:
    python main.py "technology name" "https://github.com/owner/repo"
"""

import sys
from crewai import Crew, Task, Process
from src.agents.crew import create_researcher, create_market_analyst, create_report_generator
from src.config.settings import ANTHROPIC_API_KEY

import litellm
litellm.drop_params = True


def run(technology: str, repo_url: str = "") -> str:
    if not ANTHROPIC_API_KEY:
        raise RuntimeError("ANTHROPIC_API_KEY is not set. Copy .env.example to .env and add your API key.")

    researcher = create_researcher()
    analyst = create_market_analyst()
    reporter = create_report_generator()

    research_task = Task(
        description=f"""Research the technology: "{technology}"
        
        {'GitHub Repository: ' + repo_url if repo_url else 'Find the official repository if possible.'}
        
        You MUST:
        1. Analyze the GitHub repository (stars, license, activity, contributors, language)
        2. Scrape the official website/documentation for capabilities and use cases
        3. Assess the license for business-friendliness (MIT, Apache-2.0 = good; GPL, AGPL = restrictive)
        4. Evaluate code maturity (age, commit frequency, open issues vs closed)
        
        Deliver a structured technical summary with all findings.""",
        expected_output="A detailed technical research report with repository metrics, license analysis, and capability assessment.",
        agent=researcher,
    )

    market_task = Task(
        description=f"""Analyze the market positioning of: "{technology}"
        
        You MUST:
        1. Search for recent news, blog posts, or announcements about this technology
        2. Identify competitors and alternatives in the same space
        3. Assess adoption level (who uses it, production-ready or experimental?)
        4. Evaluate business viability (funding, backing, enterprise support)
        5. Identify risks (vendor lock-in, abandonment, regulatory concerns)
        
        Deliver a market intelligence summary with competitive positioning.""",
        expected_output="A market analysis with competitive landscape, adoption status, and business risk assessment.",
        agent=analyst,
    )

    report_task = Task(
        description=f"""Generate a Technical Viability Report for: "{technology}"
        
        Using the research and market analysis provided by your colleagues, create a 
        comprehensive report with the following EXACT structure:
        
        ## Executive Summary
        [2-3 sentences on what this technology is and the verdict]
        
        ## Technical Assessment
        **Repository:** [GitHub URL]
        **License:** [license name and business-friendliness verdict]
        **Maturity:** [Experimental / Early Adoption / Production-Ready]
        **Primary Language:** [language]
        **Stars:** [count]
        **Last Activity:** [date]
        **Contributors:** [count]
        
        ### Capabilities
        [bullet list of what it does]
        
        ### Technical Risks
        [bullet list of concerns]
        
        ## Market Analysis
        **Adoption Level:** [Low / Medium / High]
        **Key Users:** [who uses it]
        **Competitors:** [alternatives]
        **Funding/Backing:** [if any]
        
        ### Market Risks
        [bullet list]
        
        ## Viability Score
        
        | Criterion | Score (1-5) | Notes |
        |-----------|:-----------:|-------|
        | License Compatibility | [score] | [note] |
        | Technical Maturity | [score] | [note] |
        | Community Health | [score] | [note] |
        | Market Traction | [score] | [note] |
        | Business Risk | [score] | [note] |
        
        **Overall Score:** [average]/5
        
        ## Recommendation
        [ADOPT / TRIAL / ASSESS / HOLD / AVOID] - [justification in 2-3 sentences]
        
        After writing the report content, use the PDF generation tool to save it.
        Pass the full report text as 'content' and "{technology}" as 'technology_name'.""",
        expected_output="A complete Technical Viability Report generated as PDF.",
        agent=reporter,
        context=[research_task, market_task],
    )

    crew = Crew(
        agents=[researcher, analyst, reporter],
        tasks=[research_task, market_task, report_task],
        process=Process.sequential,
        verbose=True,
    )

    result = crew.kickoff()
    return str(result)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("\nUsage: python main.py <technology_name> [github_url]")
        print("Example: python main.py 'LangGraph' 'https://github.com/langchain-ai/langgraph'")
        sys.exit(1)

    tech_name = sys.argv[1]
    github_url = sys.argv[2] if len(sys.argv) > 2 else ""

    print(f"\n{'='*60}")
    print(f"  AGENT INNOVATION - Tech Viability Agent")
    print(f"  Analyzing: {tech_name}")
    print(f"{'='*60}\n")

    output = run(tech_name, github_url)
    print(f"\n{'='*60}")
    print("  DONE")
    print(f"{'='*60}")
    print(f"\n{output}")
