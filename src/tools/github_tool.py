import re
import requests
from crewai.tools import tool


@tool("Analyze GitHub Repository")
def analyze_github_repo(repo_url: str) -> str:
    """Analyzes a GitHub repository extracting metadata, license, activity and tech stack.
    Input should be a GitHub URL like https://github.com/owner/repo"""

    match = re.match(r'https?://github\.com/([^/]+)/([^/]+)', repo_url.rstrip('/'))
    if not match:
        return f"Invalid GitHub URL: {repo_url}"

    owner, repo = match.groups()
    headers = {"Accept": "application/vnd.github.v3+json"}

    try:
        resp = requests.get(f"https://api.github.com/repos/{owner}/{repo}", headers=headers, timeout=15)
        if resp.status_code != 200:
            return f"GitHub API returned status {resp.status_code} for {owner}/{repo}"
        data = resp.json()
    except requests.RequestException as e:
        return f"Failed to reach GitHub API: {e}"

    license_info = data.get("license")
    license_name = license_info.get("spdx_id", "Unknown") if license_info else "No license detected"

    business_friendly = license_name in ("MIT", "Apache-2.0", "BSD-2-Clause", "BSD-3-Clause", "ISC", "Unlicense")

    contributors = "Unknown"
    try:
        contrib_resp = requests.get(f"https://api.github.com/repos/{owner}/{repo}/contributors?per_page=1&anon=true", headers=headers, timeout=10)
        if "Link" in contrib_resp.headers:
            last_page = re.search(r'page=(\d+)>; rel="last"', contrib_resp.headers["Link"])
            contributors = last_page.group(1) if last_page else "1"
        else:
            contributors = str(len(contrib_resp.json()))
    except Exception:
        pass

    return f"""## GitHub Repository Analysis: {data.get('full_name')}

**Description:** {data.get('description', 'N/A')}
**Stars:** {data.get('stargazers_count', 0):,}
**Forks:** {data.get('forks_count', 0):,}
**Open Issues:** {data.get('open_issues_count', 0):,}
**Contributors:** {contributors}
**Primary Language:** {data.get('language', 'N/A')}
**Created:** {data.get('created_at', 'N/A')[:10]}
**Last Push:** {data.get('pushed_at', 'N/A')[:10]}
**Default Branch:** {data.get('default_branch', 'main')}

### License Analysis
**License:** {license_name}
**Business-Friendly:** {'✅ Yes' if business_friendly else '❌ No — may restrict commercial use'}

### Activity Indicators
**Archived:** {'Yes ⚠️' if data.get('archived') else 'No'}
**Topics:** {', '.join(data.get('topics', [])) or 'None'}
**Has Wiki:** {'Yes' if data.get('has_wiki') else 'No'}
**Has Discussions:** {'Yes' if data.get('has_discussions') else 'No'}
"""
