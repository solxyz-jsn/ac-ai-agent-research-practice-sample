from __future__ import annotations

from config import Settings
from schemas.pull_request_schemas import PullRequestQuery
from services.github_client import GitHubClient
from services.pull_request_service import PullRequestService


def github_pull_requests_tool(
    state: str | None = None,
    repository: str | None = None,
) -> list[dict]:
    """Pull Request一覧を取得する。

    指定された条件に基づいてGitHub組織内のPull Requestを検索し、
    マッチした結果を辞書のリストとして返す。環境変数からの
    設定読み込み、APIクライアントの初期化、リソース管理を自動的に行う。

    Args:
        state: Pull Requestの状態でフィルタリングする値（例: 'open', 'closed'）
        repository: 特定のリポジトリ名でフィルタリングする値

    Returns:
        条件に一致するPull Request情報の辞書リスト。
        各辞書にはtitle, state, url, number, repositoryが含まれる。

    Raises:
        RuntimeError: GitHub API呼び出しでエラーが発生した場合
        ValueError: 設定値が不正な場合
    """

    settings = Settings.from_env()
    client = GitHubClient(github_token=settings.github_token)
    service = PullRequestService(client=client, github_org=settings.github_org)

    query = PullRequestQuery(state=state, repository=repository)

    try:
        return [item.to_dict() for item in service.list_pull_requests(query)]
    finally:
        client.close()
