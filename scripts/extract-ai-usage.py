#!/usr/bin/env python3
"""CLI wrapper for AI usage extraction."""

import json
import sys

try:
    from ai_usage import main
except ModuleNotFoundError as error:
    if error.name != "yaml" or "--post-command-hook" not in sys.argv:
        raise
    # A best-effort hook must not fail its parent because the selected interpreter
    # lacks PyYAML. No session content or local absolute path is printed.
    print(json.dumps({
        "status": "warning", "usage_mode": "unavailable", "command_run_count": 0,
        "sprint_snapshot": {"status": "skipped"}, "warning_count": 1,
        "recommended_action": "当前Python缺少PyYAML；使用已有项目环境 src/backend/.venv/bin/python 重跑相同Hook。"
    }, ensure_ascii=False))
    raise SystemExit(0)


if __name__ == "__main__":
    raise SystemExit(main())
