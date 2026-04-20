from __future__ import annotations

from dataclasses import dataclass

@dataclass(slots=True)
class IssueQuery:
    """Issue 一覧取得に使う検索条件。"""

    repository: str | None = None
    assignee: str | None = None
    state: str | None = None
    labels: str | None = None

@dataclass(slots=True)
class IssueSummary:
    """Issue 一覧で返す要約情報。"""

    title: str
    state: str
    labels: list[str]
    repository: str
    url: str
    milestone: str | None
    assignees: list[str] | None
    number: int

    def to_dict(self) -> dict:
        """外部仕様に合わせて camelCase の辞書へ変換する。

        Returns:
            camelCase キーの辞書。
        """

        return {
            "title": self.title,
            "state": self.state,
            "labels": self.labels,
            "repository": self.repository,
            "url": self.url,
            "milestone": self.milestone,
            "assignees": self.assignees,
            "number": self.number,
        }
