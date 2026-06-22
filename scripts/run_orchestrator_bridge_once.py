from __future__ import annotations

from deli_autoresearch.cli import main


if __name__ == "__main__":
    raise SystemExit(
        main(
            [
                "--workspace",
                ".",
                "--backend",
                "codex-bridge",
                "--backend-timeout-seconds",
                "60",
                "run-orchestrator-once",
            ]
        )
    )
