#!/usr/bin/env python3
"""Validate MoonBox Mintlify public docs safety and navigation."""

from __future__ import annotations

import json
import re
import sys
import hashlib
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
MINTLIFY_DIR = ROOT / "mintlify"

SENSITIVE_PATTERNS = (
    re.compile(r"\bAPP_SECRET_KEY\s*=", re.I),
    re.compile(r"\bDATABASE_URL\s*=", re.I),
    re.compile(r"mysql(\+\w+)?://[^`\s<>()]+:[^`\s<>()]+@", re.I),
    re.compile(r"\bMINIO_SECRET_KEY\s*=", re.I),
    re.compile(r"\bAuthorization\s*:", re.I),
    re.compile(r"\bBearer\s+[A-Za-z0-9._-]+", re.I),
    re.compile(r"\bCookie\s*:", re.I),
)

FORBIDDEN_NAMES = {".env", ".env.local", ".DS_Store"}
FORBIDDEN_DIRS = {"node_modules", "dist", "build", ".mintlify"}
MARKDOWN_IMAGE_PATTERN = re.compile(r"!\[[^\]]*\]\(([^)]+)\)")
MARKDOWN_LINK_PATTERN = re.compile(r"(?<!!)\[[^\]]+\]\(([^)]+)\)")


def load_json(path: Path, errors: list[str]) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        errors.append(f"缺少文件: {path}")
        return {}
    except json.JSONDecodeError as exc:
        errors.append(f"JSON 格式无效: {path}: {exc}")
        return {}
    if not isinstance(data, dict):
        errors.append(f"{path} 必须是 JSON object")
        return {}
    return data


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def mintlify_config_path() -> Path:
    docs_json = MINTLIFY_DIR / "docs.json"
    if docs_json.exists():
        return docs_json
    return MINTLIFY_DIR / "mint.json"


def collect_pages(value: Any, pages: set[str]) -> None:
    if isinstance(value, dict):
        for key, nested in value.items():
            if key == "pages" and isinstance(nested, list):
                for item in nested:
                    if isinstance(item, str):
                        pages.add(item)
                    else:
                        collect_pages(item, pages)
            else:
                collect_pages(nested, pages)
    elif isinstance(value, list):
        for item in value:
            collect_pages(item, pages)


def validate_site_manifest(manifest: dict[str, Any], errors: list[str]) -> None:
    latest_version = str(manifest.get("latest_version", "")).strip()
    versions = manifest.get("versions", [])
    if latest_version and isinstance(versions, list) and latest_version not in versions:
        errors.append("site-manifest.latest_version 必须出现在 versions 中")
    if versions is not None and not isinstance(versions, list):
        errors.append("site-manifest.versions 必须是数组")

    projections = manifest.get("projections", [])
    if projections is not None and not isinstance(projections, list):
        errors.append("site-manifest.projections 必须是数组")
    for index, item in enumerate(projections if isinstance(projections, list) else []):
        if not isinstance(item, dict):
            errors.append(f"site-manifest.projections[{index}] 必须是对象")
            continue
        for key in ("status", "target_site_root", "mode"):
            if not item.get(key):
                errors.append(f"site-manifest.projections[{index}] 缺少字段: {key}")
        target_root = str(item.get("target_site_root", "")).strip()
        if target_root:
            target = ROOT / target_root
            if not target.exists() or not target.is_dir():
                errors.append(f"site-manifest.projections[{index}] target_site_root 不存在: {target_root}")

    overrides = manifest.get("manual_overrides", [])
    if overrides is not None and not isinstance(overrides, list):
        errors.append("site-manifest.manual_overrides 必须是数组")
    for index, item in enumerate(overrides if isinstance(overrides, list) else []):
        if not isinstance(item, dict):
            errors.append(f"site-manifest.manual_overrides[{index}] 必须是对象")
            continue
        for key in ("reason", "confirmed_by", "confirmed_at", "files", "summary"):
            if not item.get(key):
                errors.append(f"site-manifest.manual_overrides[{index}] 缺少字段: {key}")

    assets = manifest.get("assets", [])
    if assets is not None and not isinstance(assets, list):
        errors.append("site-manifest.assets 必须是数组")
    for index, item in enumerate(assets if isinstance(assets, list) else []):
        if not isinstance(item, dict):
            errors.append(f"site-manifest.assets[{index}] 必须是对象")
            continue
        path_value = str(item.get("path") or item.get("site_asset") or "").strip()
        if not path_value:
            errors.append(f"site-manifest.assets[{index}] 缺少 path/site_asset")
            continue
        asset_path = ROOT / path_value
        if path_value.startswith("/assets/"):
            asset_path = MINTLIFY_DIR / path_value.lstrip("/")
        elif path_value.startswith("assets/"):
            asset_path = MINTLIFY_DIR / path_value
        if not asset_path.exists() or asset_path.is_dir():
            errors.append(f"site-manifest.assets[{index}] 引用不存在资产: {path_value}")
            continue
        expected_hash = str(item.get("sha256") or item.get("content_hash") or "").strip()
        if expected_hash and file_sha256(asset_path) != expected_hash:
            errors.append(f"site-manifest.assets[{index}] hash 不匹配: {path_value}")


def validate_local_refs(path: Path, text: str, errors: list[str]) -> None:
    for pattern in (MARKDOWN_IMAGE_PATTERN, MARKDOWN_LINK_PATTERN):
        for match in pattern.finditer(text):
            raw_ref = match.group(1).strip().split()[0].strip("<>")
            if not raw_ref or raw_ref.startswith(("http://", "https://", "mailto:", "#")):
                continue
            if raw_ref.startswith("/assets/screenshots/"):
                target = MINTLIFY_DIR / raw_ref.lstrip("/")
            elif raw_ref.startswith("/"):
                target = MINTLIFY_DIR / raw_ref.lstrip("/")
            else:
                target = (path.parent / raw_ref).resolve()
            if target.suffix == "":
                mdx_target = target.with_suffix(".mdx")
                if mdx_target.exists():
                    continue
            if not target.exists():
                errors.append(f"Mintlify 页面引用不存在资源: {path} -> {raw_ref}")


def validate() -> list[str]:
    errors: list[str] = []
    if not MINTLIFY_DIR.exists():
        return [f"缺少 Mintlify 目录: {MINTLIFY_DIR}"]

    mint = load_json(mintlify_config_path(), errors)
    manifest = load_json(MINTLIFY_DIR / "site-manifest.json", errors)
    validate_site_manifest(manifest, errors)

    pages: set[str] = set()
    collect_pages(mint, pages)
    if not pages:
        errors.append("Mintlify navigation.pages 不能为空")
    for page in sorted(pages):
        path = MINTLIFY_DIR / f"{page}.mdx"
        if not path.exists():
            errors.append(f"Mintlify 导航引用不存在页面: {page}")

    for path in MINTLIFY_DIR.rglob("*"):
        if path.name in FORBIDDEN_NAMES:
            errors.append(f"Mintlify 目录禁止提交文件: {path}")
        if path.is_dir() and path.name in FORBIDDEN_DIRS:
            errors.append(f"Mintlify 目录禁止提交构建产物目录: {path}")
        if path.is_file() and path.suffix in {".md", ".mdx", ".json"}:
            text = path.read_text(encoding="utf-8", errors="ignore")
            for pattern in SENSITIVE_PATTERNS:
                if pattern.search(text):
                    errors.append(f"公开产品手册包含敏感配置模式 {pattern.pattern}: {path}")
            if path.suffix in {".md", ".mdx"}:
                validate_local_refs(path, text, errors)

    return errors


def main() -> int:
    errors = validate()
    if errors:
        print("Mintlify 产品手册校验失败：")
        for error in errors:
            print(f"- {error}")
        return 1
    print("Mintlify 产品手册校验通过。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
