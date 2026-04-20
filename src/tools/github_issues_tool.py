from __future__ import annotations

from config import Settings
from schemas import IssueQuery
from services.github_client import GitHubClient
from services.issue_service import IssueService


def github_issues_tool(
    repository: str | None = None,
    assignee: str | None = None,
    state: str | None = None,
    labels: str | None = None,
) -> list[dict]:
    """条件に一致する Issue 一覧を取得する。"""

    settings = Settings.from_env()
    client = GitHubClient(github_token=settings.github_token)
    service = IssueService(client=client, github_org=settings.github_org)
    query = IssueQuery(
        repository=repository,
        assignee=assignee,
        state=state,
        labels=labels,
    )
    try:
        return [item.to_dict() for item in service.list_issues(query)]
    finally:
        client.close()
