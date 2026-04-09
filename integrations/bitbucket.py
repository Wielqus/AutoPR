import os
import requests


class BitbucketClient:
    BASE_URL = "https://api.bitbucket.org/2.0"

    def __init__(self):
        self.workspace = os.environ["WORKSPACE"]
        self.repo = os.environ["REPO"]
        self.base_branch = os.environ.get("BASE_BRANCH", "main")
        self._auth = (os.environ["BB_USER"], os.environ["BB_TOKEN"])
        self._headers = {"Content-Type": "application/json"}

    def _repo_url(self, path: str) -> str:
        return f"{self.BASE_URL}/repositories/{self.workspace}/{self.repo}/{path}"

    def create_branch(self, branch_name: str) -> dict:
        url = self._repo_url("refs/branches")
        payload = {
            "name": branch_name,
            "target": {"hash": self.base_branch},
        }
        response = requests.post(url, json=payload, auth=self._auth, headers=self._headers)
        response.raise_for_status()
        return response.json()

    def create_pull_request(self, title: str, description: str, branch: str) -> str:
        url = self._repo_url("pullrequests")
        payload = {
            "title": title,
            "description": description,
            "source": {"branch": {"name": branch}},
            "destination": {"branch": {"name": self.base_branch}},
            "close_source_branch": True,
        }
        response = requests.post(url, json=payload, auth=self._auth, headers=self._headers)
        if not response.ok:
            raise requests.HTTPError(
                f"{response.status_code} {response.reason}: {response.text}",
                response=response,
            )
        pr_data = response.json()
        return pr_data.get("links", {}).get("html", {}).get("href", "")
