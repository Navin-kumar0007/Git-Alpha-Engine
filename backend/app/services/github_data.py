import logging
import os
from typing import Dict, Any

import httpx

logger = logging.getLogger(__name__)

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")  # optional, but helps avoid rate limiting


async def fetch_repo_metrics(owner_repo: str) -> Dict[str, Any]:
  """
  Fetch basic stats + recent commit count from GitHub.

  owner_repo: e.g. "bitcoin/bitcoin"
  """
  headers = {
      "Accept": "application/vnd.github+json",
      "X-GitHub-Api-Version": "2022-11-28",
  }
  if GITHUB_TOKEN:
      headers["Authorization"] = f"Bearer {GITHUB_TOKEN}"

  async with httpx.AsyncClient(timeout=15.0) as client:
      try:
          repo_resp = await client.get(
              f"https://api.github.com/repos/{owner_repo}",
              headers=headers,
          )
          repo_resp.raise_for_status()
          repo = repo_resp.json()
      except Exception as exc:
          logger.warning("Failed to fetch repo %s: %s", owner_repo, exc)
          return {}

      # recent commits (last ~30)
      try:
          commits_resp = await client.get(
              f"https://api.github.com/repos/{owner_repo}/commits",
              params={"per_page": 30},
              headers=headers,
          )
          commits_resp.raise_for_status()
          commits = commits_resp.json()
          recent_commits = len(commits)
      except Exception as exc:
          logger.warning("Failed to fetch commits for %s: %s", owner_repo, exc)
          recent_commits = 0

  # you can plug this text into your NLTK/TextBlob AI later if you want
  commit_messages = " ".join(
      c.get("commit", {}).get("message", "") for c in commits[:20]
  ) if recent_commits else ""

  # for now, simple sentiment placeholder
  sentiment = "Bullish" if recent_commits > 10 else "Neutral"

  return {
      "stargazers_count": repo.get("stargazers_count", 0),
      "forks_count": repo.get("forks_count", 0),
      "open_issues_count": repo.get("open_issues_count", 0),
      "recent_commits": recent_commits,
      "sentiment": sentiment,
      "sample_commit_text": commit_messages[:2000],
  }
