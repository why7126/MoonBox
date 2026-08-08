#!/usr/bin/env python3
"""Validate that real env files are ignored while examples remain trackable."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

MUST_BE_IGNORED = [
    ".env",
    ".env.local",
    ".env.production",
    "deploy/local/self-storage-sqlite.env",
    "deploy/prod/external-storage-external-mysql.env",
    "scripts/build-images.env",
]

MUST_BE_TRACKABLE = [
    ".env.example",
    "deploy/local/self-storage-sqlite.env.example",
    "deploy/prod/external-storage-external-mysql.env.example",
    "scripts/build-images.env.example",
]


def git_check_ignore(path: str) -> bool:
    result = subprocess.run(
        ["git", "check-ignore", "--quiet", path],
        cwd=ROOT,
        check=False,
    )
    return result.returncode == 0


def main() -> int:
    errors: list[str] = []

    for path in MUST_BE_IGNORED:
        if not git_check_ignore(path):
            errors.append(f"真实环境文件未被 Git ignore 覆盖: {path}")

    for path in MUST_BE_TRACKABLE:
        if git_check_ignore(path):
            errors.append(f"示例环境文件被 Git ignore 误覆盖: {path}")

    if errors:
        print("环境文件 ignore 策略校验失败：")
        for error in errors:
            print(f"- {error}")
        return 1

    print("环境文件 ignore 策略校验通过。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
