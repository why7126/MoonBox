#!/usr/bin/env python3
"""
文档用途：校验 API 标准合规性
文档内容：检查路由 OpenAPI 元数据、错误码引用等
内容来源：build-api-standard / initialize-project
"""

from __future__ import annotations

import ast
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
API_DIR = ROOT / "src" / "backend" / "app" / "api"

violations: list[str] = []


def collect_router_tags(tree: ast.AST) -> set[str]:
    routers_with_tags: set[str] = set()
    for node in ast.walk(tree):
        if not isinstance(node, ast.Assign):
            continue
        if not isinstance(node.value, ast.Call):
            continue
        func = node.value.func
        if not isinstance(func, ast.Name) or func.id != "APIRouter":
            continue
        if not any(keyword.arg == "tags" for keyword in node.value.keywords):
            continue
        for target in node.targets:
            if isinstance(target, ast.Name):
                routers_with_tags.add(target.id)
    return routers_with_tags


def route_router_name(decorator: ast.AST) -> str | None:
    if not isinstance(decorator, ast.Call):
        return None
    func = decorator.func
    if not isinstance(func, ast.Attribute):
        return None
    value = func.value
    if isinstance(value, ast.Name):
        return value.id
    return None


def check_router_file(path: Path) -> None:
    rel = path.relative_to(ROOT)
    text = path.read_text(encoding="utf-8")
    tree = ast.parse(text)
    routers_with_tags = collect_router_tags(tree)

    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        # Heuristic: route handlers often have router decorator
        for dec in node.decorator_list:
            src = ast.get_source_segment(text, dec) or ""
            if "router." not in src and "app." not in src:
                continue
            if "get(" in src or "post(" in src or "put(" in src or "patch(" in src or "delete(" in src:
                body = ast.get_source_segment(text, node) or ""
                if "response_model" not in src and "response_model" not in body:
                    violations.append(
                        f"{rel}:{node.lineno} — 路由 {node.name} 缺少 response_model"
                    )
                router_name = route_router_name(dec)
                if "tags=" not in src and router_name not in routers_with_tags:
                    violations.append(f"{rel}:{node.lineno} — 路由 {node.name} 缺少 tags")
                if "summary=" not in src:
                    violations.append(f"{rel}:{node.lineno} — 路由 {node.name} 缺少 summary")
                break


def main() -> int:
    if not API_DIR.exists():
        print("API 目录不存在，跳过校验。")
        return 0

    for path in API_DIR.rglob("*.py"):
        if path.name.startswith("_"):
            continue
        try:
            check_router_file(path)
        except SyntaxError as e:
            violations.append(f"{path.relative_to(ROOT)} — 语法错误: {e}")

    required_docs = [
        "docs/standards/api-governance.md",
        "docs/standards/error-codes.md",
        "src/backend/app/core/error_codes.py",
        "src/backend/app/schemas/common.py",
    ]

    for doc in required_docs:
        if not (ROOT / doc).exists():
            violations.append(f"缺少必需文件: {doc}")

    check_openapi_client_generator()

    if violations:
        print("API 标准校验失败：")
        for v in violations:
            print(f"  - {v}")
        return 1

    print("API 标准校验通过。")
    return 0


def check_openapi_client_generator() -> None:
    script = ROOT / "scripts" / "generate-openapi-client.sh"
    if not script.exists():
        violations.append("缺少 OpenAPI 客户端生成脚本: scripts/generate-openapi-client.sh")
        return

    text = script.read_text(encoding="utf-8")
    required_markers = [
        ("pnpm is not available", "缺少 pnpm 缺失时的明确提示"),
        ("pnpm version check failed", "缺少 pnpm 版本错配时的明确提示"),
        ("corepack prepare pnpm@11.2.2 --activate", "缺少 pnpm 版本对齐修复命令"),
        ("Orval is not declared", "缺少 Orval 未声明时的明确提示"),
        ("local Orval binary is missing", "缺少本地 Orval 二进制缺失时的明确提示"),
        ("OpenAPI contract exported to", "缺少 OpenAPI 已导出后的 fallback 状态说明"),
        ("does not implicitly download Orval", "缺少不隐式联网安装 Orval 的说明"),
    ]
    for marker, message in required_markers:
        if marker not in text:
            violations.append(f"scripts/generate-openapi-client.sh — {message}")


if __name__ == "__main__":
    sys.exit(main())
