from __future__ import annotations
from dataclasses import dataclass

from schemas.pull_request_schemas import PullRequestQuery, PullRequestSummary
from services.github_client import GitHubClient

SEARCH_QUERY = """
query SearchPullRequests($searchQuery: String!) {
  search(query: $searchQuery, type: ISSUE, first: 20) {
    nodes {
      ... on PullRequest {
        number
        title
        state
        url
        repository {
          name
        }
      }
    }
  }
}
""".strip()


@dataclass(slots=True)
class PullRequestService:
    """Pull Request検索サービス。

    GitHub組織内のPull Requestを検索し、条件に一致する
    Pull Request情報を取得する機能を提供する。

    Attributes:
        client: GitHub APIクライアント
        github_org: 検索対象のGitHub組織名
    """

    client: GitHubClient
    github_org: str

    def list_pull_requests(self, query: PullRequestQuery) -> list[PullRequestSummary]:
        """条件に一致するPull Request一覧を取得する。

        指定された検索条件に基づいてGitHub Search APIを実行し、
        マッチしたPull Requestの要約情報をリストで返す。

        Args:
            query: Pull Request検索条件

        Returns:
            条件に一致するPull Request要約情報のリスト

        Raises:
            RuntimeError: GitHub API呼び出しでエラーが発生した場合
        """
        search_query = self._build_search_query(query)

        data = self.client.execute_graphql(SEARCH_QUERY, {"searchQuery": search_query})

        results = []
        for node in data["search"]["nodes"]:
            if node is None:
                continue
            results.append(self._to_summary(node))

        return results

    def _build_search_query(self, query: PullRequestQuery) -> str:
        """GitHub Search Query文字列を構築する。

        検索条件からGitHub Search APIで使用するクエリ文字列を生成する。
        組織全体または特定リポジトリ、状態による絞り込みに対応する。

        Args:
            query: Pull Request検索条件

        Returns:
            GitHub Search APIで使用可能なクエリ文字列
        """

        if query.repository:
            terms = [f"repo:{self.github_org}/{query.repository}", "is:pr"]
        else:
            terms = [f"org:{self.github_org}", "is:pr"]
        if query.state:
            terms.append(f"is:{query.state}")

        return " ".join(terms)

    def _to_summary(self, node: dict) -> PullRequestSummary:
        """GraphQLレスポンスをPullRequestSummaryオブジェクトに変換する。

        GitHub GraphQL APIから取得したPull Request情報を
        アプリケーション内で扱いやすい形式に変換する。

        Args:
            node: GraphQL APIレスポンスのPull Requestノード

        Returns:
            変換されたPull Request要約情報
        """
        repository = node.get("repository") or {}
        return PullRequestSummary(
            title=node["title"],
            state=node["state"],
            url=node["url"],
            number=node["number"],
            repository=repository["name"],
        )
