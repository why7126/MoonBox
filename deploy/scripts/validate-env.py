#!/usr/bin/env python3
"""Validate MoonBox deploy environment files without printing secret values."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

EXAMPLE_TOKENS = (
    "change-me",
    "replace-with",
    "example.com",
)

LOCAL_PORT_KEYS = (
    "HOST_PORT_BACKEND",
    "HOST_PORT_WEB",
    "HOST_PORT_MINIO_API",
    "HOST_PORT_MINIO_CONSOLE",
    "HOST_PORT_MINTLIFY_DOCS",
    "HOST_PORT_MYSQL",
)


def parse_env(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        key, value = stripped.split("=", 1)
        values[key.strip()] = value.strip().strip("'\"")
    return values


def is_true(value: str | None) -> bool:
    return str(value or "").strip().lower() in {"1", "true", "yes", "on"}


def has_example_value(value: str | None) -> bool:
    lowered = str(value or "").lower()
    return any(token in lowered for token in EXAMPLE_TOKENS)


def validate_local_ports(env_id: str, values: dict[str, str]) -> list[str]:
    errors: list[str] = []
    seen: dict[int, str] = {}
    for key in LOCAL_PORT_KEYS:
        raw = values.get(key)
        if raw is None:
            continue
        try:
            port = int(raw)
        except ValueError:
            errors.append(f"{env_id}: {key} 必须是数字端口")
            continue
        if port < 18101 or port > 18199:
            errors.append(f"{env_id}: {key} 必须位于 18101-18199")
        if port in seen:
            errors.append(f"{env_id}: {key} 与 {seen[port]} 端口重复")
        seen[port] = key
    return errors


def validate(domain: str, environment: str, env_path: Path, profile: str | None) -> list[str]:
    values = parse_env(env_path)
    errors: list[str] = []
    env_id = f"{domain}-{environment}"
    profile = profile or ""

    storage_mode = values.get("OBJECT_STORAGE_DEPLOYMENT_MODE", "")
    database_mode = values.get("DATABASE_DEPLOYMENT_MODE", "")
    database_type = values.get("DATABASE_TYPE", "")
    database_url = values.get("DATABASE_URL", "")

    if values.get("MOONBOX_DEPLOY_ENV_ID") not in {"", env_id}:
        errors.append(f"{env_id}: MOONBOX_DEPLOY_ENV_ID 必须匹配当前环境")

    if domain == "local":
        errors.extend(validate_local_ports(env_id, values))
        if values.get("TZ", "Asia/Shanghai") != "Asia/Shanghai":
            errors.append(f"{env_id}: TZ 默认必须是 Asia/Shanghai")
        if values.get("DATABASE_TIMEZONE", "+08:00") != "+08:00":
            errors.append(f"{env_id}: DATABASE_TIMEZONE 默认必须是 +08:00")

    if storage_mode == "self-hosted-minio" and "self-hosted-storage" not in profile:
        errors.append(f"{env_id}: 自建 MinIO 环境必须启用 self-hosted-storage profile")
    if storage_mode == "external-minio" and "self-hosted-storage" in profile:
        errors.append(f"{env_id}: 外部对象存储环境不得启用 self-hosted-storage profile")
    if storage_mode not in {"self-hosted-minio", "external-minio"}:
        errors.append(f"{env_id}: OBJECT_STORAGE_DEPLOYMENT_MODE 必须是 self-hosted-minio 或 external-minio")

    if database_mode == "self-hosted-mysql" and "self-hosted-db" not in profile:
        errors.append(f"{env_id}: 自建 MySQL 环境必须启用 self-hosted-db profile")
    if database_mode in {"sqlite", "external-mysql"} and "self-hosted-db" in profile:
        errors.append(f"{env_id}: sqlite/external-mysql 环境不得启用 self-hosted-db profile")
    if database_mode not in {"sqlite", "self-hosted-mysql", "external-mysql"}:
        errors.append(f"{env_id}: DATABASE_DEPLOYMENT_MODE 必须是 sqlite、self-hosted-mysql 或 external-mysql")

    if database_mode == "sqlite" and database_type != "sqlite":
        errors.append(f"{env_id}: SQLite 环境必须设置 DATABASE_TYPE=sqlite")
    if database_mode.endswith("mysql") and database_type != "mysql":
        errors.append(f"{env_id}: MySQL 环境必须设置 DATABASE_TYPE=mysql")
    if database_type == "mysql" and not database_url.startswith(("mysql://", "mysql+pymysql://", "mysql+mysqlconnector://", "mysql+aiomysql://")):
        errors.append(f"{env_id}: DATABASE_TYPE=mysql 时 DATABASE_URL 必须是 MySQL 连接串")
    if database_type == "sqlite" and not database_url.startswith("sqlite:"):
        errors.append(f"{env_id}: DATABASE_TYPE=sqlite 时 DATABASE_URL 必须是 SQLite 连接串")

    for key in ("MINIO_ENDPOINT", "MINIO_ACCESS_KEY", "MINIO_SECRET_KEY", "MINIO_BUCKET"):
        if not values.get(key):
            errors.append(f"{env_id}: {key} 为对象存储必填变量")
    if re.search(r"\s", values.get("MINIO_BUCKET", "")):
        errors.append(f"{env_id}: MINIO_BUCKET 不得包含空白字符")

    if domain == "prod":
        if values.get("APP_ENV") != "production":
            errors.append(f"{env_id}: APP_ENV 必须是 production")
        if is_true(values.get("APP_DEBUG")):
            errors.append(f"{env_id}: 生产环境不允许 APP_DEBUG=true")
        if database_type != "mysql" or database_url.startswith("sqlite:"):
            errors.append(f"{env_id}: 生产环境必须使用外部 MySQL，禁止 SQLite")
        if storage_mode != "external-minio":
            errors.append(f"{env_id}: 生产环境必须使用外部对象存储")
        if not is_true(values.get("MINIO_SECURE")):
            errors.append(f"{env_id}: 生产对象存储必须启用 MINIO_SECURE=true")
        for key in ("APP_SECRET_KEY", "DATABASE_URL", "MINIO_ACCESS_KEY", "MINIO_SECRET_KEY", "MINIO_BUCKET"):
            if has_example_value(values.get(key)):
                errors.append(f"{env_id}: {key} 生产环境不得使用示例值")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate MoonBox deploy env file")
    parser.add_argument("--domain", required=True, choices=("local", "prod"))
    parser.add_argument("--environment", required=True)
    parser.add_argument("--env-file", required=True, type=Path)
    parser.add_argument("--profile", default="")
    args = parser.parse_args()

    if not args.env_file.exists():
        print(f"BLOCKED: env file not found: {args.env_file}", file=sys.stderr)
        return 1

    errors = validate(args.domain, args.environment, args.env_file, args.profile or None)
    if errors:
        print("部署环境校验失败：")
        for error in errors:
            print(f"- {error}")
        print("修复建议：复制对应 *.env.example 为真实 env 后替换占位值，或选择匹配的环境 ID/profile。")
        return 1

    print(f"部署环境校验通过：{args.domain}-{args.environment}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
