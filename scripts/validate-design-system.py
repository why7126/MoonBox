#!/usr/bin/env python3
"""
文档用途：校验 Design System 合规性
文档内容：检查 Hex 硬编码、CSS content 非 ASCII、裸原生控件、绕过 shared/ui 等问题
内容来源：build-design-system / initialize-project
更新方式：DS 规则变化时同步更新
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

SCAN_DIRS = [
    ROOT / "src" / "web" / "src",
    ROOT / "src" / "shared",
]

EXTENSIONS = {".tsx", ".ts", ".css"}

# 允许出现 Hex 的路径（Token 定义与生成文件）
ALLOWED_HEX_PATHS = {
    "globals.css",
    "tokens.generated.css",
    "colors.ts",
    "css.ts",
    "tailwind.config.ts",
    "DesignSystemPage.tsx",
    "design-system.test.tsx",
}

HEX_PATTERN = re.compile(r"#[0-9A-Fa-f]{3,8}\b")
ARBITRARY_BG_PATTERN = re.compile(r"bg-\[#[0-9A-Fa-f]+\]")
CSS_CONTENT_STRING_PATTERN = re.compile(r'''(?<![\w-])content\s*:\s*(["'])((?:\\.|(?!\1).)*)\1''')
NATIVE_CONTROL_PATTERN = re.compile(
    r"<(button|input|select|textarea)\b",
)
NATIVE_SKIP_DIRS = ("components/ui/", "shared/ui/")
ALLOWED_NATIVE_CONTROL_FILES = {
    "RequirementCenterPage.tsx",
    "AdminCrudListTemplate.tsx",
    "AdminSidebar.tsx",
    "AdminUserManagementPage.tsx",
    "AdminSpaceManagementPage.tsx",
    "AdminBrandManagementPage.tsx",
    "AdminAuthSettingsPage.tsx",
    "AdminSelect.tsx",
    "Homepage.tsx",
}
REQUIRED_OPS_TOKENS = {
    "--ops-font-body",
    "--ops-font-mono",
    "--ops-radius-md",
    "--ops-shadow-popover",
    "--ops-warning",
    "--ops-danger",
}
REQUIRED_OPS_SELECTORS = {
    ".rc-filter-popover",
    ".rc-stat",
    ".admin-toast",
    ".ds-preview",
}

violations: list[str] = []


def should_skip_hex(path: Path) -> bool:
    return path.name in ALLOWED_HEX_PATHS or "tokens/" in str(path)


def css_content_literal_uses_raw_non_ascii(line: str) -> bool:
    """Return True when a CSS content string contains literal non-ASCII symbols."""
    for match in CSS_CONTENT_STRING_PATTERN.finditer(line):
        value = match.group(2)
        if any(ord(char) > 127 for char in value):
            return True
    return False


def scan_file(path: Path) -> None:
    rel = path.relative_to(ROOT)
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        return

    for i, line in enumerate(text.splitlines(), start=1):
        if not should_skip_hex(path):
            if HEX_PATTERN.search(line) and "var(--" not in line:
                violations.append(f"{rel}:{i} — 硬编码 Hex 颜色")
            if ARBITRARY_BG_PATTERN.search(line):
                violations.append(f"{rel}:{i} — 使用 bg-[#...] 任意值")

        if path.suffix == ".css" and css_content_literal_uses_raw_non_ascii(line):
            violations.append(f"{rel}:{i} — CSS content 中的非 ASCII 符号必须使用 escape 写法")

        if path.suffix in {".tsx", ".ts"} and "pages/dev/" not in str(path):
            if any(skip in str(path) for skip in NATIVE_SKIP_DIRS):
                continue
            if path.name in ALLOWED_NATIVE_CONTROL_FILES:
                continue
            if NATIVE_CONTROL_PATTERN.search(line) and "// ds-ok" not in line:
                violations.append(
                    f"{rel}:{i} — 直接使用原生 HTML 控件，应使用 shadcn/shared/ui（可加 // ds-ok 豁免）"
                )


def scan_ops_contract() -> None:
    globals_css = ROOT / "src" / "web" / "src" / "styles" / "globals.css"
    token_css = ROOT / "src" / "shared" / "design-system" / "tokens" / "css.ts"
    try:
        css_text = globals_css.read_text(encoding="utf-8")
        token_text = token_css.read_text(encoding="utf-8")
    except OSError as exc:
        violations.append(f"Design System Ops 合约读取失败：{exc}")
        return

    combined = f"{css_text}\n{token_text}"
    for token in sorted(REQUIRED_OPS_TOKENS):
        if token not in combined:
            violations.append(f"Design System Ops 合约缺少 token：{token}")
    for selector in sorted(REQUIRED_OPS_SELECTORS):
        if selector not in css_text:
            violations.append(f"Design System Ops 合约缺少选择器：{selector}")


def main() -> int:
    for base in SCAN_DIRS:
        if not base.exists():
            continue
        for path in base.rglob("*"):
            if path.suffix in EXTENSIONS and path.is_file():
                scan_file(path)
    scan_ops_contract()

    if violations:
        print("Design System 校验失败：")
        for v in violations:
            print(f"  - {v}")
        print(f"\n共 {len(violations)} 项违规。修复建议：使用 semantic token class，复用 shared/ui。")
        return 1

    print("Design System 校验通过。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
