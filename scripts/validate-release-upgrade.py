#!/usr/bin/env python3
"""Generate and validate public-safe release upgrade plans."""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
RELEASES_DIR = ROOT / "releases"

SUPPORT_LEVELS = {
    "fresh-install-supported",
    "adjacent-upgrade-supported",
    "cross-version-upgrade-requires-manual-review",
    "unsupported",
}
SENSITIVE_PATTERNS = (
    re.compile(r"\bAuthorization\s*:", re.I),
    re.compile(r"\bBearer\s+[A-Za-z0-9._-]+", re.I),
    re.compile(r"\bCookie\s*:", re.I),
    re.compile(r"\bDATABASE_URL\s*=\s*(?!<)", re.I),
    re.compile(r"mysql(?:\+\w+)?://", re.I),
    re.compile(r"/Users/[^\\s\"']+", re.I),
    re.compile(r"/home/[^\\s\"']+", re.I),
)
ENV_EXAMPLE_PATTERNS = (
    ".env.example",
    "src/backend/.env.example",
    "deploy/**/*.env.example",
    "scripts/build-images.env.example",
)


class UpgradePlanError(ValueError):
    """User-facing validation error."""


def now_text() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def rel(path: Path) -> str:
    return os.path.relpath(path.resolve(), ROOT)


def read_json(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise UpgradePlanError(f"missing file: {rel(path)}") from None
    except json.JSONDecodeError as exc:
        raise UpgradePlanError(f"invalid JSON {rel(path)}: {exc}") from None
    if not isinstance(data, dict):
        raise UpgradePlanError(f"{rel(path)} must contain a JSON object")
    return data


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def semver_key(version: str) -> tuple[int, int, int]:
    match = re.fullmatch(r"v(\d+)\.(\d+)\.(\d+)", version)
    if not match:
        raise UpgradePlanError(f"unsupported version format: {version}")
    return tuple(int(part) for part in match.groups())


def release_versions() -> list[str]:
    if not RELEASES_DIR.exists():
        return []
    versions = [path.name for path in RELEASES_DIR.iterdir() if path.is_dir() and re.fullmatch(r"v\d+\.\d+\.\d+", path.name)]
    return sorted(versions, key=semver_key)


def previous_version(to_version: str) -> str | None:
    versions = [version for version in release_versions() if semver_key(version) < semver_key(to_version)]
    return versions[-1] if versions else None


def versions_between(from_version: str, to_version: str) -> list[str]:
    start = semver_key(from_version)
    end = semver_key(to_version)
    return [version for version in release_versions() if start < semver_key(version) <= end]


def release_dir(version: str) -> Path:
    return RELEASES_DIR / version


def release_fact(version: str) -> dict[str, Any] | None:
    path = release_dir(version) / "release.json"
    return read_json(path) if path.exists() else None


def parse_env_text(text: str) -> dict[str, str]:
    values: dict[str, str] = {}
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        key, value = stripped.split("=", 1)
        values[key.strip()] = value.strip().strip("'\"")
    return values


def env_example_files() -> list[Path]:
    files: list[Path] = []
    for pattern in ENV_EXAMPLE_PATTERNS:
        files.extend(path for path in ROOT.glob(pattern) if path.is_file())
    return sorted(set(files), key=rel)


def env_review() -> dict[str, Any]:
    files = env_example_files()
    keys = sorted({key for path in files for key in parse_env_text(path.read_text(encoding="utf-8"))})
    return {
        "status": "manual_review",
        "source": "env-example-files",
        "files": [rel(path) for path in files],
        "key_count": len(keys),
        "keys": keys,
        "notes": [
            "仅读取可提交 env 示例文件，不读取真实 .env。",
            "跨版本 env diff 需要结合 Git tag、release 归档或人工快照复核。",
        ],
    }


def support_level(from_version: str, to_version: str) -> str:
    if from_version == "fresh":
        return "fresh-install-supported"
    if release_fact(from_version) is None:
        return "unsupported"
    previous = previous_version(to_version)
    if previous == from_version:
        return "adjacent-upgrade-supported"
    return "cross-version-upgrade-requires-manual-review"


def source_confidence(version: str) -> str:
    if version == "fresh":
        return "fresh"
    data = release_fact(version)
    if not data:
        return "missing"
    return "verified" if data.get("version") == version else "partial"


def impact_requires_database(data: dict[str, Any] | None) -> bool:
    if not data:
        return False
    impact = data.get("impact_scope")
    if not isinstance(impact, dict):
        return False
    value = str(impact.get("database", "")).strip().lower()
    return value not in {"", "none", "na", "n/a", "not_applicable", "不涉及", "无"}


def build_plan(from_version: str, to_version: str) -> dict[str, Any]:
    if from_version != "fresh":
        semver_key(from_version)
    semver_key(to_version)
    target_release = release_fact(to_version)
    if target_release is None:
        raise UpgradePlanError(f"missing target release: releases/{to_version}/release.json")

    level = support_level(from_version, to_version)
    blockers: list[str] = []
    warnings: list[str] = []
    if level == "unsupported":
        blockers.append("source-release-missing")
    if level == "cross-version-upgrade-requires-manual-review":
        warnings.append("cross-version-upgrade-requires-manual-review")

    db_review = {
        "status": "manual_review" if impact_requires_database(target_release) else "not_applicable",
        "notes": ["数据库影响非空时，必须补充 MySQL drift/smoke、备份和回滚证据。"],
    }
    object_storage_review = {
        "status": "manual_review",
        "notes": ["如 release 影响对象存储、上传或媒体路径，必须补充对象存储影响和回滚说明。"],
    }
    rollback_review = {
        "status": "manual_review",
        "notes": ["生产实施前必须确认备份、回滚窗口、回滚责任人和验证方式。"],
    }

    return {
        "schema_version": 1,
        "created_at": now_text(),
        "from_version": from_version,
        "to_version": to_version,
        "support_level": level,
        "source_confidence": {
            "from": source_confidence(from_version),
            "to": source_confidence(to_version),
        },
        "versions_in_path": [] if from_version == "fresh" else versions_between(from_version, to_version),
        "target_release": f"releases/{to_version}/release.json",
        "image_manifest": f"releases/{to_version}/image-manifest.json",
        "env_review": env_review(),
        "database_review": db_review,
        "object_storage_review": object_storage_review,
        "rollback_review": rollback_review,
        "blockers": blockers,
        "warnings": warnings,
        "boundaries": [
            "不自动执行生产升级。",
            "不自动修改真实 env。",
            "不自动执行 DB restore、写入型 migration 或对象存储维护任务。",
        ],
    }


def validate_sensitive_text(path: Path, text: str) -> list[str]:
    issues: list[str] = []
    for pattern in SENSITIVE_PATTERNS:
        if pattern.search(text):
            issues.append(f"sensitive-pattern:{pattern.pattern}")
    return issues


def validate_plan(path: Path) -> tuple[bool, list[str], dict[str, Any]]:
    data = read_json(path)
    messages: list[str] = []
    for key in ("from_version", "to_version", "support_level", "env_review", "database_review", "rollback_review"):
        if key not in data:
            messages.append(f"missing-key:{key}")
    if data.get("support_level") not in SUPPORT_LEVELS:
        messages.append(f"invalid-support-level:{data.get('support_level')}")
    messages.extend(validate_sensitive_text(path, path.read_text(encoding="utf-8")))
    if data.get("support_level") == "cross-version-upgrade-requires-manual-review":
        messages.append("manual-review-required:cross-version-upgrade")
    messages.extend(f"blocker:{item}" for item in data.get("blockers") or [])
    ok = not any(message.startswith(("missing-key", "invalid-support-level", "sensitive-pattern", "blocker")) for message in messages)
    return ok, messages, data


def command_plan(args: argparse.Namespace) -> int:
    plan = build_plan(args.from_version, args.to_version)
    path = release_dir(args.to_version) / "upgrade-plans" / f"{args.from_version}-to-{args.to_version}.json"
    write_json(path, plan)
    ok, messages, _ = validate_plan(path)
    print("## Release Upgrade Plan")
    print()
    print(f"Status: {'PASS' if ok else 'BLOCKED'}")
    print(f"Plan: {rel(path)}")
    print(f"From: {args.from_version}")
    print(f"To: {args.to_version}")
    print(f"Support Level: {plan['support_level']}")
    print(f"Messages: {', '.join(messages) if messages else 'none'}")
    return 0 if ok else 1


def command_validate_plan(args: argparse.Namespace) -> int:
    path = (ROOT / args.plan).resolve() if not Path(args.plan).is_absolute() else Path(args.plan)
    ok, messages, data = validate_plan(path)
    print("## Release Upgrade Plan Validation")
    print()
    print(f"Status: {'PASS' if ok else 'BLOCKED'}")
    print(f"Plan: {rel(path)}")
    print(f"From: {data.get('from_version', '')}")
    print(f"To: {data.get('to_version', '')}")
    print(f"Support Level: {data.get('support_level', '')}")
    print(f"Messages: {', '.join(messages) if messages else 'none'}")
    return 0 if ok else 1


def command_env_diff(_: argparse.Namespace) -> int:
    review = env_review()
    print(json.dumps(review, ensure_ascii=False, indent=2))
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    plan_parser = subparsers.add_parser("plan", help="Generate an upgrade plan.")
    plan_parser.add_argument("--from", dest="from_version", required=True)
    plan_parser.add_argument("--to", dest="to_version", required=True)
    plan_parser.set_defaults(func=command_plan)

    validate_parser = subparsers.add_parser("validate-plan", help="Validate an upgrade plan.")
    validate_parser.add_argument("--plan", required=True)
    validate_parser.set_defaults(func=command_validate_plan)

    env_parser = subparsers.add_parser("env-diff", help="Print public-safe env example summary.")
    env_parser.set_defaults(func=command_env_diff)

    args = parser.parse_args()
    try:
        return int(args.func(args))
    except UpgradePlanError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
