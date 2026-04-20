from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


@dataclass(slots=True)
class Settings:
    """環境変数から読み込むアプリケーション設定。

    Attributes:
        aws_region: 利用するAWSリージョン。
        bedrock_inference_profile_arn: Amazon Bedrockの推論プロファイルARN。
        aws_bearer_token_bedrock: ローカル実行で利用するAmazon Bedrock API key。
        github_org: 検索対象のGitHub Organization名。
        github_token: GitHub APIを呼び出すためのToken。
        log_level: アプリケーションのログレベル。
    """

    aws_region: str
    bedrock_inference_profile_arn: str
    aws_bearer_token_bedrock: str
    github_org: str
    github_token: str
    log_level: str = "INFO"

    @classmethod
    def from_env(cls) -> "Settings":
        """現在の環境変数から設定を生成する。

        Returns:
            現在の環境変数から生成した設定オブジェクト。

        Raises:
            ValueError: 必須の環境変数が未設定の場合。
        """
        return cls(
            aws_region=os.getenv("AWS_REGION", "ap-northeast-1"),
            bedrock_inference_profile_arn=_require_env(
                "BEDROCK_INFERENCE_PROFILE_ARN"
            ),
            aws_bearer_token_bedrock=_require_env("AWS_BEARER_TOKEN_BEDROCK"),
            github_org=_require_env("GITHUB_ORG"),
            github_token=_require_env("GITHUB_TOKEN"),
            log_level=os.getenv("LOG_LEVEL", "INFO"),
        )


def _require_env(name: str) -> str:
    """必須の環境変数を取得する。

    Args:
        name: 取得する環境変数名。

    Returns:
        環境変数の値。

    Raises:
        ValueError: 環境変数が未設定または空文字の場合。
    """
    value = os.getenv(name)
    if not value:
        raise ValueError(f"Missing required environment variable: {name}")
    return value
