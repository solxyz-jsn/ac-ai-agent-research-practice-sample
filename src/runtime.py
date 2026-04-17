from __future__ import annotations


def invoke_agent(agent, prompt: str) -> dict[str, str | None]:
    """エージェントを実行し、レスポンスを正規化する。

    Args:
        agent: 呼び出し可能なエージェントオブジェクト。
        prompt: エージェントに渡す入力テキスト。

    Returns:
        以下のキーを持つ辞書。

        - ``output_text``: エージェントの出力テキスト。
        - ``usage_summary``: 使用量サマリー（現在は常に ``None``）。
    """

    result = agent(prompt)
    return {
        "output_text": str(result).strip(),
        "usage_summary": None,
    }
