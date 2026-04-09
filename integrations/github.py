import os
import requests


class GitHubClient:
    BASE_URL = "https://api.github.com"

    def __init__(self):
        self.token = os.environ["GH_TOKEN"]
        self.repo = os.environ["GH_REPO"]  # format: "owner/repo"
        self.base_branch = os.environ.get("BASE_BRANCH", "main")
        self._headers = {
            "Authorization": f"Bearer {self.token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }

    def create_pull_request(self, title: str, description: str, branch: str) -> str:
        url = f"{self.BASE_URL}/repos/{self.repo}/pulls"
        payload = {
            "title": title,
            "body": description,
            "head": branch,
            "base": self.base_branch,
        }
        response = requests.post(url, json=payload, headers=self._headers)
        if not response.ok:
            raise requests.HTTPError(
                f"{response.status_code} {response.reason}: {response.text}",
                response=response,
            )
        return response.json().get("html_url", "")
