from __future__ import annotations

import json
import threading
import uuid
from collections.abc import Mapping
from typing import Any

from agent import build_agent
from runtime import invoke_agent

_REQUEST_PROMPT_KEYS = ("prompt", "inputText", "input", "message")
_AGENT = None
_AGENT_LOCK = threading.Lock()


def handle_request(event: Mapping[str, Any] | None) -> dict[str, Any]:
    """AgentCoreリクエストを処理して結果を返す。

    Args:
        event: リクエストイベント。Noneの場合は空のペイロードとして扱う。

    Returns:
        以下のキーを含む辞書。

        - sessionId (str): セッションID。
        - outputText (str): エージェントの出力テキスト。
        - usageSummary (dict, optional): トークン使用量。存在する場合のみ含まれる。
    """

    payload = _normalize_event(event)
    prompt = _extract_prompt(payload)
    session_id = _extract_session_id(payload)

    invocation = invoke_agent(_get_or_create_agent(), prompt)
    response = {
        "sessionId": session_id,
        "outputText": invocation["output_text"],
    }
    if invocation["usage_summary"]:
        response["usageSummary"] = invocation["usage_summary"]
    return response


def _normalize_event(event: Mapping[str, Any] | None) -> dict[str, Any]:
    """イベントを正規化して辞書として返す。

    Args:
        event: 正規化対象のイベント。Noneの場合は空の辞書を返す。

    Returns:
        正規化されたペイロードの辞書。
    """

    if event is None:
        return {}

    payload = dict(event)
    body = payload.get("body")
    if isinstance(body, str) and body.strip():
        try:
            body_payload = json.loads(body)
        except json.JSONDecodeError:
            return payload
        if isinstance(body_payload, dict):
            payload.update(body_payload)
    return payload


def _extract_session_id(payload: Mapping[str, Any]) -> str:
    """ペイロードからセッションIDを抽出して返す。

    Args:
        payload: 抽出元のマッピング。

    Returns:
        セッションID文字列。見つからない場合は新規UUIDを返す。
    """

    for key in ("sessionId", "session_id"):
        value = payload.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return str(uuid.uuid4())


def _extract_prompt(payload: Mapping[str, Any]) -> str:
    """ペイロードからプロンプト文字列を抽出して返す。

    Args:
        payload: 抽出元のマッピング。

    Returns:
        抽出されたプロンプト文字列。

    Raises:
        ValueError: 有効なプロンプトが見つからない場合。
    """

    for key in _REQUEST_PROMPT_KEYS:
        value = payload.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()

    messages = payload.get("messages")
    if isinstance(messages, list):
        for message in reversed(messages):
            if not isinstance(message, Mapping):
                continue
            content = message.get("content")
            if isinstance(content, str) and content.strip():
                return content.strip()

    raise ValueError(
        "Request must include one of: prompt, inputText, input, message, or messages."
    )


def _get_or_create_agent():
    """エージェントを返す。未生成の場合は生成してから返す。

    Returns:
        エージェントインスタンス。
    """

    global _AGENT
    if _AGENT is not None:
        return _AGENT

    with _AGENT_LOCK:
        if _AGENT is None:
            _AGENT = build_agent()
    return _AGENT
