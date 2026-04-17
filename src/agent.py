import importlib.resources
import json
import os

from config import Settings

from tools.github_pull_requests_tool import github_pull_requests_tool as github_pull_requests_tool_impl
from tools.github_issues_tool import github_issues_tool as github_issues_tool_impl


def build_agent() -> "Agent":
    """Strands Agents を構築して返す。"""

    try:
        from strands import Agent, tool
    except ImportError as exc:
        raise RuntimeError(
            "Strands Agents SDK is not installed. Run `uv sync` to install dependencies."
        ) from exc

    settings = Settings.from_env()

    if settings.aws_bearer_token_bedrock:
        os.environ["AWS_BEARER_TOKEN_BEDROCK"] = settings.aws_bearer_token_bedrock

    @tool
    def github_pull_requests_tool(
        repository: str | None = None,
        state: str | None = None,
    ) -> str:
        """GitHub Organization 配下の PR 一覧を JSON で取得する。"""

        return json.dumps(
            github_pull_requests_tool_impl(
                repository=repository,
                state=state,
            ),
            ensure_ascii=False,
        )

    @tool
    def github_issues_tool(
        repository: str | None = None,
        assignee: str | None = None,
        state: str | None = None,
        labels: str | None = None,
    ) -> str:
        """GitHub Organization 配下の Issue 一覧を JSON で取得する。

        Args:
            repository: repo 名のみ。未指定なら Organization 全体を対象にする。
            assignee: GitHub ユーザー名。
            state: `open`, `closed` のいずれか。
            labels: ラベル名。
        """

        items = github_issues_tool_impl(
            repository=repository,
            assignee=assignee,
            state=state,
            labels=labels,
        )
        return json.dumps(items, ensure_ascii=False)



    return Agent(
        model=settings.bedrock_inference_profile_arn,
        system_prompt=_load_system_prompt(),
        tools=[github_pull_requests_tool, github_issues_tool],
        callback_handler=None,
    )

def _load_system_prompt() -> str:
    """システムプロンプトをファイルから読み込む。"""

    prompt_file = importlib.resources.files("prompts").joinpath(
        "system_prompt.md"
    )

    return prompt_file.read_text(encoding="utf-8").strip()
