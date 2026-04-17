from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from bedrock_agentcore.runtime import BedrockAgentCoreApp

from agentcore import handle_request

app = BedrockAgentCoreApp()


@app.entrypoint
def invoke(request: Mapping[str, Any]) -> dict[str, Any]:
    """AgentCore Runtimeから呼び出されるエントリーポイント。

    Args:
        request: Runtimeから受け取るリクエストデータ。

    Returns:
        処理結果を格納した辞書。
    """

    return handle_request(request)


if __name__ == "__main__":
    app.run()
