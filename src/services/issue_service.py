from __future__ import annotations

from dataclasses import dataclass

from schemas import IssueQuery, IssueSummary
from services.github_client import GitHubClient

SEARCH_ISSUE_QUERY = """
query SearchIssue($searchQuery: String!) {
  search(query: $searchQuery, type: ISSUE, first: 100) {
    pageInfo {
      hasNextPage
      endCursor
    }
    nodes {
      ... on Issue {
        number
        title
        state
        url
        labels(first: 10) {
          nodes {
            name
            color
          }
        }
        milestone {
          title
          number
          state
          dueOn
        }
        assignees(first: 10) {
          nodes {
            login
            name
          }
        }
        repository {
          name
        }
      }
    }
  }
}
""".strip()

@dataclass(slots=True)
class IssueService:
    """Organization 横断で Issue 一覧を取得するサービス。"""

    client: GitHubClient
    github_org: str

    def list_issues(self, query: IssueQuery) -> list[IssueSummary]:
        """条件に一致する Issue 一覧をページネーション込みで返す。

        Args:
            query: Issue の検索条件。

        Returns:
            条件に一致した Issue 要約一覧。
        """

        search_query = self._build_search_query(query)
        results: list[IssueSummary] = []
        after: str | None = None

        while True:
            data = self.client.execute_graphql(
                SEARCH_ISSUE_QUERY,
                {
                    "searchQuery": search_query,
                },
            )
            results = []
            for node in data["search"]["nodes"]:
                if node is None:
                    continue
                results.append(self._to_summary(node))

            return results


    def _build_search_query(self, query: IssueQuery) -> str:
        """正規化済みの条件から GitHub Search Query 文字列を組み立てる。

        Args:
            query: Issue の検索条件。

        Returns:
            GitHub Search Query 文字列。
        """

        if query.repository:
            terms = [f"repo:{self.github_org}/{query.repository}", "is:issue"]
        else:
            terms = [f"org:{self.github_org}", "is:issue"]
        if query.assignee:
            terms.append(f"assignee:{query.assignee}")
        if query.state:
            terms.append(f"is:{query.state}")
        if query.labels:
            terms.append(f'label:"{query.labels}"')

        return " ".join(terms)

    def _to_summary(self, node: dict) -> IssueSummary:
        """GraphQL の Issue ノードを ``IssueSummary`` に変換する。

        Args:
            node: GraphQL の Issue ノード。

        Returns:
            変換済みの Issue 要約情報。
        """

        repository = node.get("repository") or {}
        return IssueSummary(
            title=node["title"],
            state=node["state"],
            labels=self._extract_labels(node.get("labels")),
            repository=repository["name"],
            url=node["url"],
            milestone=self._extract_milestone(node.get("milestone")),
            assignees=self._extract_assignees(node.get("assignees")),
            number=node["number"],
        )

    def _extract_labels(self, labels_data: dict | None) -> list[str]:
        """GraphQL の labels データからラベル名一覧を抽出する。

        Args:
            labels_data: GraphQL の ``labels`` フィールド。

        Returns:
            ラベル名一覧。
        """

        if not labels_data or not labels_data.get("nodes"):
            return []
        return [
            label["name"]
            for label in labels_data["nodes"]
            if label and label.get("name")
        ]

    def _extract_milestone(self, milestone_data: dict | None) -> str | None:
        """GraphQL の milestone データからタイトルを抽出する。

        Args:
            milestone_data: GraphQL の ``milestone`` フィールド。

        Returns:
            milestone タイトル。存在しない場合は ``None``。
        """

        if not milestone_data:
            return None
        return milestone_data.get("title")

    def _extract_assignees(self, assignees_data: dict | None) -> list[str] | None:
        """GraphQL の assignees データから login 一覧を抽出する。

        Args:
            assignees_data: GraphQL の ``assignees`` フィールド。

        Returns:
            assignee の login 一覧。存在しない場合は ``None``。
        """

        if not assignees_data or not assignees_data.get("nodes"):
            return None

        return [
            assignee["login"]
            for assignee in assignees_data["nodes"]
            if assignee and assignee.get("login")
        ]
