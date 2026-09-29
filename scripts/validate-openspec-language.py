#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
from pathlib import Path


CHANGE_DOCS = {
    "proposal.md",
    "design.md",
    "tasks.md",
    "trace.md",
    "acceptance.md",
    "test-plan.md",
}

ENGLISH_SCAFFOLD_WORDS = {
    "bug analysis report",
    "capabilities",
    "context",
    "data and api",
    "documentation",
    "implementation",
    "impact",
    "knowledge base decision",
    "non-goals",
    "proposed design",
    "proposed fix",
    "risks",
    "rollback plan",
    "root cause",
    "test strategy",
    "testing",
    "validation",
    "what",
    "what changes",
    "why",
}

CJK_RE = re.compile(r"[\u4e00-\u9fff]")
ALPHA_RE = re.compile(r"[A-Za-z]")
CHECKBOX_RE = re.compile(r"^\s*-\s+\[[ xX]\]\s+")
HEADING_RE = re.compile(r"^\s{0,3}#{1,6}\s+(.+?)\s*$")


def has_cjk(text: str) -> bool:
    return bool(CJK_RE.search(text))


def strip_inline_code(text: str) -> str:
    return re.sub(r"`[^`]*`", "", text)


def is_english_scaffold_heading(text: str) -> bool:
    title = strip_inline_code(text).strip().strip("#").strip()
    if has_cjk(title) or not ALPHA_RE.search(title):
        return False
    normalized = re.sub(r"[^a-zA-Z -]", "", title).strip().lower()
    return normalized in ENGLISH_SCAFFOLD_WORDS


def is_english_task(text: str) -> bool:
    if not CHECKBOX_RE.match(text):
        return False
    task_text = strip_inline_code(CHECKBOX_RE.sub("", text).strip())
    return bool(ALPHA_RE.search(task_text)) and not has_cjk(task_text)


def iter_change_docs(root: Path, include_archive: bool, changes: list[str] | None = None) -> list[Path]:
    paths: list[Path] = []
    change_ids = sorted(set(changes or []))
    if change_ids:
        for change_id in change_ids:
            found = False
            change_dir = root / "openspec" / "changes" / change_id
            if change_dir.exists():
                found = True
                paths.extend(path for path in change_dir.glob("*.md") if path.name in CHANGE_DOCS)

            if include_archive:
                archive_root = root / "openspec" / "archive"
                if archive_root.exists():
                    for archived_dir in archive_root.glob(f"*-{change_id}"):
                        if archived_dir.is_dir():
                            found = True
                            paths.extend(path for path in archived_dir.glob("*.md") if path.name in CHANGE_DOCS)

            if not found:
                location = "openspec/changes 或 openspec/archive" if include_archive else "openspec/changes"
                raise ValueError(f"未找到 Change：{change_id}（搜索范围：{location}）")
        return sorted(paths)

    change_root = root / "openspec" / "changes"
    if change_root.exists():
        for path in change_root.glob("*/*.md"):
            if path.name in CHANGE_DOCS:
                paths.append(path)

    if include_archive:
        archive_root = root / "openspec" / "archive"
        if archive_root.exists():
            for path in archive_root.glob("*/*.md"):
                if path.name in CHANGE_DOCS:
                    paths.append(path)

    return sorted(paths)


def iter_residual_docs(root: Path, include_archive: bool, focus_paths: list[Path]) -> list[Path]:
    focus = {path.resolve() for path in focus_paths}
    return [path for path in iter_change_docs(root, include_archive) if path.resolve() not in focus]


def validate_file(path: Path, root: Path) -> list[str]:
    errors: list[str] = []
    in_fence = False

    for line_no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        stripped = line.strip()
        if stripped.startswith("```"):
            in_fence = not in_fence
            continue
        if in_fence:
            continue

        heading = HEADING_RE.match(line)
        if heading and is_english_scaffold_heading(heading.group(1)):
            errors.append(
                f"{path.relative_to(root)}:{line_no}: OpenSpec 文档标题必须中文优先，避免英文脚手架标题：{stripped}"
            )
            continue

        if is_english_task(line):
            errors.append(
                f"{path.relative_to(root)}:{line_no}: tasks.md 任务项必须中文优先，命令/路径可保留英文：{stripped}"
            )

    return errors


def collect_errors(paths: list[Path], root: Path) -> list[str]:
    errors: list[str] = []
    for path in paths:
        errors.extend(validate_file(path, root))
    return errors


def print_errors(title: str, errors: list[str]) -> None:
    print(title)
    for error in errors:
        print(f"- {error}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate Chinese-first OpenSpec change documents.")
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--include-archive", action="store_true")
    parser.add_argument(
        "--change",
        action="append",
        default=[],
        help="只校验指定 Change，可重复传入；默认校验全部 active Change。",
    )
    parser.add_argument(
        "--residual-report",
        action="store_true",
        help="与 --change 配合输出非当前 Change 中文残留报告；残留不影响当前 Change 退出码。",
    )
    args = parser.parse_args()

    root = args.root.resolve()
    if args.residual_report and not args.change:
        parser.error("--residual-report requires --change")

    try:
        paths = iter_change_docs(root, args.include_archive, args.change)
    except ValueError as exc:
        print(f"OpenSpec 文档语言校验失败：{exc}")
        return 2

    errors = collect_errors(paths, root)

    if errors:
        title = "OpenSpec 当前 Change 中文校验失败：" if args.change else "OpenSpec 文档语言校验失败："
        print_errors(title, errors)
        print("\n修复建议：标题和任务描述使用中文优先；OpenSpec 关键字、命令、路径、代码标识符可保留英文。")
        return 1

    if args.change:
        print(f"OpenSpec 当前 Change 中文校验通过：{', '.join(args.change)}")
    else:
        print("OpenSpec 文档语言校验通过")

    if args.change and args.residual_report:
        residual_errors = collect_errors(iter_residual_docs(root, args.include_archive, paths), root)
        print("\n全仓残留分离报告：")
        if residual_errors:
            print(f"- 非当前 Change 中文残留：{len(residual_errors)} 项")
            for error in residual_errors[:20]:
                print(f"  - {error}")
            if len(residual_errors) > 20:
                print(f"  - ... 另有 {len(residual_errors) - 20} 项未展开")
        else:
            print("- 未发现非当前 Change 中文残留")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
