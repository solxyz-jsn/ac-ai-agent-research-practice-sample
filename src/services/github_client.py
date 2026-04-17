from dataclasses import dataclass
import httpx


@dataclass
class GitHubClient:
    """GitHub API呼び出しを集約するクライアント。

    Personal Access Tokenを使用してGitHub GraphQL APIと通信する。
    HTTPクライアントの初期化、認証、リクエストの実行を担当する。

    Attributes:
        github_token: GitHub Personal Access Token
    """

    github_token: str

    def __post_init__(self) -> None:
        """HTTPクライアントを初期化する。"""
        self._client = httpx.Client(
            headers={"Authorization": f"Bearer {self.github_token}"}
        )

    def execute_graphql(self, query: str, variables: dict | None = None) -> dict:
        """GraphQL APIを実行してレスポンスのdata部分を返す。

        Args:
            query: 実行するGraphQLクエリ文字列
            variables: クエリで使用する変数（オプション）

        Returns:
            GraphQLレスポンスのdataフィールド

        Raises:
            RuntimeError: GraphQLエラーが発生した場合
            httpx.HTTPStatusError: HTTP通信エラーが発生した場合
        """
        response = self._client.post(
            "https://api.github.com/graphql",
            json={"query": query, "variables": variables or {}},
        )
        response.raise_for_status()

        payload = response.json()
        if payload.get("errors"):
            raise RuntimeError(f"GitHub GraphQL errors: {payload['errors']}")

        return payload["data"]

    def close(self) -> None:
        """HTTPクライアントを閉じてリソースを解放する。"""
        self._client.close()
