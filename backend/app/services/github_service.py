import httpx
from typing import Any

class GitHubService:
    def fetch_repository(self, url: str) -> dict:
        try:
            response = httpx.get(url)
            response.raise_for_status()
            return {"status": "ok", "url": url, "content_length": len(response.text)}
        except httpx.HTTPError as exc:
            return {"status": "error", "message": str(exc)}
