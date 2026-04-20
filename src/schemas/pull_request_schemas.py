from __future__ import annotations
from dataclasses import dataclass


@dataclass(slots=True)
class PullRequestQuery:
    """Pull Request検索条件を表現するデータクラス。

    Attributes:
        state: Pull Requestの状態でフィルタリング（例: 'open', 'closed'）
        repository: 特定のリポジトリ名でフィルタリング
    """
    state: str | None = None
    repository: str | None = None


@dataclass(slots=True)
class PullRequestSummary:
    """Pull Request要約情報を格納するデータクラス。

    GitHub APIから取得したPull Requestの基本情報を保持します。

    Attributes:
        title: Pull Requestのタイトル
        state: Pull Requestの状態（OPEN, CLOSED, MERGED等）
        url: Pull RequestのURL
        number: Pull Request番号
        repository: リポジトリ名
    """
    title: str
    state: str
    url: str
    number: int
    repository: str

    def to_dict(self) -> dict:
        """オブジェクトを辞書形式に変換します。

        Returns:
            Pull Request情報を含む辞書
        """
        return {
            "title": self.title,
            "state": self.state,
            "url": self.url,
            "number": self.number,
            "repository": self.repository,
        }
