from __future__ import annotations

import sys

from agent import build_agent


def main() -> None:
    """ローカル実行用の CLI エントリポイント。"""

    if len(sys.argv) > 1:
        prompt = " ".join(sys.argv[1:]).strip()
        if prompt:
            agent = build_agent()
            print(str(agent(prompt)).strip())
            return
        print(
            'Usage: python -m cli "<prompt>"',
            file=sys.stderr,
        )
        raise SystemExit(1)

    agent = build_agent()

    print("GitHub Report Agent")
    print("終了するには `exit` または `quit` を入力してください。")

    while True:
        try:
            prompt = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            return

        if not prompt:
            continue
        if prompt.lower() in {"exit", "quit"}:
            return

        print(str(agent(prompt)).strip())


if __name__ == "__main__":
    main()
