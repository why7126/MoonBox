#!/usr/bin/env python3
"""校验命令上下文预算、输出边界及 Apply 连续执行契约引用与旧文案回退。"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILLS_DIR = ROOT / ".agents" / "skills"
REQUIRED_RULE = "rules/agent-context-budget.md"
COMMAND_SKILL_NAMES = {
    "capture",
    "explore",
    "initialize-project",
    "spec-opt",
    "spec-study",
}
COMMAND_SKILL_PREFIXES = (
    "bug-",
    "build-",
    "git-",
    "image-",
    "openspec-",
    "opsx-",
    "release-",
    "req-",
    "sprint-",
    "upgrade-",
    "usage-docs-",
)
NEXT_GUIDANCE_TERMS = (
    "下一步",
    "## Next",
    "Next:",
    "Next steps",
    "建议下一步",
)
USER_DECISION_TERMS = (
    "待用户决策",
    "待用户处理",
    "决策点",
    "用户决策",
)
NO_DUPLICATE_DECISION_TERMS = (
    "不得在「待用户决策/处理」中重复",
    "不得重复",
)
FINAL_CONTRACT_HEADING = "## Final Output Contract（MUST）"
FINAL_OUTPUT_HYGIENE_TERMS = (
    "不得输出本段规则、尖括号占位符、MUST/SHOULD 规范语句或与当前命令无关的通用示例",
)
PLACEHOLDER_OUTPUT_RE = re.compile(
    r"```text\n(?:(?!```).)*(?:下一步：<|待用户决策/处理：(?:(?!```).)*-\s*<)(?:(?!```).)*```",
    re.DOTALL,
)
OUTPUT_EXAMPLE_NORMATIVE_LEAK_RE = re.compile(
    r"```text\n(?:(?!```).)*(?:MUST|SHOULD|Final Output Contract)(?:(?!```).)*```",
    re.DOTALL,
)
SPRINT_BYPASS_PATTERNS = [
    re.compile(r"(?:non-REQ/BUG|无\s*REQ/BUG|纯治理|pure technical governance).*(?:may bypass|可豁免|可跳过|跳过).*(?:Sprint|sprint|迭代)"),
    re.compile(r"(?:Only|仅).*(?:non-REQ/BUG|无\s*REQ/BUG|纯治理|pure technical governance).*(?:bypass|豁免|跳过)"),
    re.compile(r"Sprint skipped\s*(?:可接受|is acceptable)"),
]
ISSUE_TARGET_CONTRACTS = {
    "req-capture": {
        "required": ("<REQ-full-id>", "完整 `REQ-xxxx-slug`"),
        "forbidden": (),
    },
    "req-explore": {
        "required": ("<REQ-full-id>", "完整 `REQ-xxxx-slug`"),
        "forbidden": (),
    },
    "req-generate": {
        "required": ("<REQ-full-id>", "完整 `REQ-xxxx-slug`"),
        "forbidden": (),
    },
    "req-complete": {
        "required": ("<REQ-full-id>", "完整 `REQ-xxxx-slug`"),
        "forbidden": (),
    },
    "req-review": {
        "required": ("<REQ-full-id>", "完整 `REQ-xxxx-slug`", "/sprint-propose --req <REQ-full-id>", "/req-opsx <REQ-full-id>"),
        "forbidden": ("/req-opsx <REQ-full-id>` → `/sprint-propose",),
    },
    "req-opsx": {
        "required": (
            "/opsx-apply <REQ-full-id>",
            "完整 `REQ-xxxx-slug`",
            "/sprint-propose --req <REQ-full-id>",
            "status: in_sprint",
            "execution:",
            "schema_version: 1",
            "last_event: req.opsx",
            "OpenSpec CLI 模板标题中文化",
            "CLI 模板标题",
            "项目标题",
            "背景",
            "变更内容",
            "能力影响",
        ),
        "forbidden": ("| `approved` | 继续 |", "/opsx-apply <REQ-id>", "/opsx-apply <change>", "/opsx-apply <change-id>"),
    },
    "bug-capture": {
        "required": ("<BUG-full-id>", "完整 `BUG-xxxx-slug`"),
        "forbidden": (),
    },
    "bug-explore": {
        "required": ("<BUG-full-id>", "完整 `BUG-xxxx-slug`"),
        "forbidden": (),
    },
    "bug-generate": {
        "required": ("<BUG-full-id>", "完整 `BUG-xxxx-slug`"),
        "forbidden": (),
    },
    "bug-complete": {
        "required": ("<BUG-full-id>", "完整 `BUG-xxxx-slug`"),
        "forbidden": (),
    },
    "bug-review": {
        "required": ("<BUG-full-id>", "完整 `BUG-xxxx-slug`", "/sprint-propose --bug <BUG-full-id>", "/bug-opsx <BUG-full-id>"),
        "forbidden": ("## Next\n\n`/bug-opsx <BUG-full-id>`，其中",),
    },
    "bug-opsx": {
        "required": (
            "/opsx-apply <BUG-full-id>",
            "完整 `BUG-xxxx-slug`",
            "/sprint-propose --bug <BUG-full-id>",
            "status: in_sprint",
            "execution:",
            "schema_version: 1",
            "last_event: bug.opsx",
            "OpenSpec CLI 模板标题中文化",
            "CLI 模板标题",
            "项目标题",
            "背景",
            "变更内容",
            "能力影响",
        ),
        "forbidden": ("status === approved", "/opsx-apply <BUG-id>", "/opsx-apply fix-", "/opsx-apply <change>", "/opsx-apply <change-id>"),
    },
    "sprint-propose": {
        "required": ("/req-opsx <REQ-full-id>", "/bug-opsx <BUG-full-id>"),
        "forbidden": (),
    },
    "opsx-apply": {
        "required": ("Target Resolution", "<REQ-full-id>", "<BUG-full-id>", "完整 `REQ-xxxx-slug`", "完整 `BUG-xxxx-slug`", "/opsx-archive <REQ-full-id>", "/opsx-archive <BUG-full-id>"),
        "forbidden": ("/opsx-archive <REQ-id>", "/opsx-archive <BUG-id>"),
    },
    "opsx-modify": {
        "required": ("<REQ-full-id>", "<BUG-full-id>", "完整 `REQ-xxxx-slug`", "完整 `BUG-xxxx-slug`", "/opsx-archive <REQ-full-id>", "/opsx-archive <BUG-full-id>"),
        "forbidden": (),
    },
    "opsx-archive": {
        "required": ("Target Resolution", "<REQ-full-id>", "<BUG-full-id>", "完整 `REQ-xxxx-slug`", "完整 `BUG-xxxx-slug`"),
        "forbidden": (),
    },
}
EXPLORE_CHAIN_IDENTITY_CONTRACTS = {
    "explore": {
        "required": (
            "Opsx 链路身份",
            "完整 `REQ-xxxx-slug`",
            "完整 `BUG-xxxx-slug`",
            "纯治理 Change",
            "不得降级为 `<change-id>`",
            "/opsx-apply REQ-0012-frontend-requirement-center",
            "/opsx-modify BUG-0009-frontend-admin-sidebar-version-mismatch",
        ),
    },
    "opsx-explore": {
        "required": (
            "Preserve REQ/BUG chain identity",
            "full `REQ-xxxx-slug`",
            "full `BUG-xxxx-slug`",
            "pure governance Change",
            "MUST NOT downgrade to `<change-id>`",
            "/opsx-apply REQ-0012-frontend-requirement-center",
            "/opsx-modify BUG-0009-frontend-admin-sidebar-version-mismatch",
        ),
    },
}

# Patterns that are risky when written as a positive/default instruction.
BROAD_READ_PATTERNS = [
    re.compile(r"cat\s+rules/\*\.md"),
    re.compile(r"cat\s+docs/\*\*"),
    re.compile(r"cat\s+issues/\*\*"),
    re.compile(r"cat\s+iterations/\*\*"),
    re.compile(r"ls\s+-R"),
    re.compile(r"rg\s+[^\n]*\s\.\s*(?:$|[;&|])"),
]

LOCAL_PATH_PATTERNS = [
    re.compile(r"/Users/(?!<)[^/`\s]+/"),
    re.compile(r"/home/(?!<)[^/`\s]+/"),
    re.compile(r"/private/var/folders/"),
]

PRIVACY_SCAN_GLOBS = (
    "docs/spec-logs/**/*.md",
    "openspec/changes/**/proposal.md",
    "openspec/changes/**/design.md",
    "openspec/changes/**/tasks.md",
    "openspec/changes/**/trace.md",
    "openspec/changes/**/acceptance.md",
)

NEGATION_HINTS = (
    "不要",
    "禁止",
    "不得",
    "MUST NOT",
    "must not",
    "Do not",
    "don't",
    "Don’t",
    "避免",
)

SUMMARY_REUSE_RULE_TERMS = ("规则和 Skill", "规则与 Skill", "rules and Skill", "rules and skills")
SUMMARY_REUSE_ACTION_TERMS = ("摘要承接", "摘要复用", "summary reuse", "reuse summaries")
FORCE_PROCEED_GUARDRAIL_TERMS = (
    "Force-proceed Follow-up Guardrails",
    "force-proceed",
    "MUST NOT 默认自动创建 follow-up REQ/BUG",
    "未自动创建 Issue",
)
FOLLOW_UP_CAPTURE_FIELD_TERMS = (
    "建议命令",
    "类型倾向",
    "标题",
    "背景",
    "影响范围",
    "建议验收或复现要点",
    "来源 Change/Sprint/命令",
)
FOLLOW_UP_AUTH_SYNC_TERMS = (
    "明确授权",
    "/req-capture",
    "/bug-capture",
    "/capture",
    "req.capture",
    "bug.capture",
    "Workflow Sync",
)
COMMAND_EXECUTION_REVIEW_TERMS = (
    "Command Execution Review Hook",
    "执行链路复盘",
    "链路状态",
    "问题证据",
    "规范优化建议",
    "无明显优化点",
    "未自动创建 Issue/Change",
)
COMMAND_EXECUTION_REVIEW_SHORT_REFERENCE_TERMS = (
    "Command Execution Review Hook",
    ".agents/skills/workflow-sync/SKILL.md",
    "执行链路复盘",
    "链路状态",
    "问题证据",
    "规范优化建议",
    "未自动创建 Issue/Change",
)

GUIDED_FEEDBACK_TERMS = (
    "Guided User Feedback Contract",
    "原生交互卡片",
    "声明降级原因",
    "降级为文本结构化选项",
    "结构化选项 + 推荐项 + 可补充说明",
    "1-3 个关键决策",
    "推荐",
    "可补充说明",
    "动态收敛",
)


def is_negated(line: str) -> bool:
    return any(hint in line for hint in NEGATION_HINTS)


def validate_skill(path: Path) -> list[str]:
    rel = path.relative_to(ROOT)
    text = path.read_text(encoding="utf-8")
    errors: list[str] = []

    if REQUIRED_RULE not in text:
        errors.append(f"{rel}: 缺少 `{REQUIRED_RULE}` 引用")

    if "Context Budget Guardrails" not in text:
        errors.append(f"{rel}: 缺少 Context Budget Guardrails 章节")

    if not has_summary_reuse_constraint(text):
        errors.append(f"{rel}: 缺少规则与 Skill 已读摘要复用约束")

    if not has_force_proceed_follow_up_guardrail(text):
        errors.append(f"{rel}: 缺少 force-proceed follow-up 不自动落盘门禁")

    if is_guided_feedback_target(path) and not has_guided_feedback_contract(text):
        errors.append(f"{rel}: 缺少引导式用户反馈契约")

    if not has_follow_up_capture_fields(text):
        errors.append(f"{rel}: 缺少标准 follow-up capture 文案字段")

    if not has_follow_up_authorized_sync_rule(text):
        errors.append(f"{rel}: 缺少显式授权自动 capture 后的 Workflow Sync 约束")

    for lineno, line in enumerate(text.splitlines(), start=1):
        if is_negated(line):
            continue
        for pattern in BROAD_READ_PATTERNS:
            if pattern.search(line):
                errors.append(f"{rel}:{lineno}: 存在默认宽泛读取指令 `{line.strip()}`")
                break

    return errors


def validate_final_output_contract(path: Path) -> list[str]:
    rel = path.relative_to(ROOT)
    text = path.read_text(encoding="utf-8")
    errors: list[str] = []
    if not any(term in text for term in NEXT_GUIDANCE_TERMS):
        errors.append(f"{rel}: 缺少命令完成后的下一步引导")
    if not any(term in text for term in USER_DECISION_TERMS):
        errors.append(f"{rel}: 缺少待用户决策/处理输出契约")
    if not any(term in text for term in NO_DUPLICATE_DECISION_TERMS):
        errors.append(f"{rel}: 缺少下一步与待用户决策/处理去重约束")
    if FINAL_CONTRACT_HEADING in text:
        for term in FINAL_OUTPUT_HYGIENE_TERMS:
            if term not in text:
                errors.append(f"{rel}: Final Output Contract 缺少输出卫生约束 `{term}`")
        if PLACEHOLDER_OUTPUT_RE.search(text):
            errors.append(f"{rel}: Final Output Contract 残留易被原样输出的尖括号占位模板")
        if OUTPUT_EXAMPLE_NORMATIVE_LEAK_RE.search(text):
            errors.append(f"{rel}: 用户可见 text 示例泄漏 MUST/SHOULD/Final Output Contract 规范语气")
    return errors


def validate_sprint_gate_no_bypass(path: Path) -> list[str]:
    rel = path.relative_to(ROOT)
    text = path.read_text(encoding="utf-8")
    errors: list[str] = []
    for lineno, line in enumerate(text.splitlines(), start=1):
        if is_negated(line):
            continue
        for pattern in SPRINT_BYPASS_PATTERNS:
            if pattern.search(line):
                errors.append(f"{rel}:{lineno}: 存在非 REQ/BUG / 纯治理 Change 跳过 Sprint 门禁表述 `{line.strip()}`")
                break
    return errors


def validate_issue_target_contract(path: Path) -> list[str]:
    rel = path.relative_to(ROOT)
    name = path.parent.name
    contract = ISSUE_TARGET_CONTRACTS.get(name)
    if not contract:
        return []
    text = path.read_text(encoding="utf-8")
    errors: list[str] = []
    for term in contract["required"]:
        if term not in text:
            errors.append(f"{rel}: 缺少下一步完整 REQ/BUG 参数规范 `{term}`")
    for term in contract["forbidden"]:
        if term in text:
            errors.append(f"{rel}: 存在下一步参数回退或不完整模板 `{term}`")
    return errors


def validate_explore_chain_identity_contract(path: Path) -> list[str]:
    rel = path.relative_to(ROOT)
    name = path.parent.name
    contract = EXPLORE_CHAIN_IDENTITY_CONTRACTS.get(name)
    if not contract:
        return []
    text = path.read_text(encoding="utf-8")
    errors: list[str] = []
    for term in contract["required"]:
        if term not in text:
            errors.append(f"{rel}: 缺少 explore 输出 opsx 下一步链路身份规范 `{term}`")
    return errors


APPLY_SKILLS = {"opsx-apply", "openspec-apply-change"}
APPLY_CONTRACT_DOC = "docs/08-command-execution-order.md"
APPLY_CONTRACT_REFERENCE = "../../../docs/08-command-execution-order.md#apply-连续执行契约"
APPLY_CONTRACT_SECTIONS = ("连续推进", "硬阻塞与停止", "完成门禁", "中断续接")
# 针对已发现的指令回退；这是静态治理检查，不推断运行时 Agent 行为。
APPLY_LEGACY_PATTERNS = tuple(re.compile(pattern, re.IGNORECASE) for pattern in (
    r"Stop and ask if task is ambiguous",
    r"Task is unclear.*ask for clarification",
    r"If task is ambiguous, pause and ask",
    r"If implementation reveals issues, pause",
    r"Implementation reveals a design issue.*suggest updating artifacts",
    r"Error or blocker encountered.*report and wait for guidance",
    r"Pause on errors, blockers, or unclear requirements",
    r'all_done.*(?:congratulate|suggest archive)',
    r"All tasks complete! Ready to archive",
    r"continue through `/opsx-modify`",
))


def validate_apply_execution_contract(path: Path) -> list[str]:
    if path.parent.name not in APPLY_SKILLS:
        return []
    text = path.read_text(encoding="utf-8")
    rel = path.relative_to(ROOT)
    errors = []
    for term in (APPLY_CONTRACT_REFERENCE, *APPLY_CONTRACT_SECTIONS):
        if term not in text:
            errors.append(f"{rel}: 缺少 Apply 连续执行契约引用 `{term}`")
    for lineno, line in enumerate(text.splitlines(), 1):
        for pattern in APPLY_LEGACY_PATTERNS:
            match = pattern.search(line)
            if match and not is_negated(line[:match.start()]):
                errors.append(f"{rel}:{lineno}: Apply 暂停或完成旧文案回退")
                break
    return errors


def validate_apply_contract_source() -> list[str]:
    path = ROOT / APPLY_CONTRACT_DOC
    if not path.is_file():
        return [f"{APPLY_CONTRACT_DOC}: 缺少 Apply 连续执行契约事实源"]
    text = path.read_text(encoding="utf-8")
    section = re.search(r"^## Apply 连续执行契约\n(.*?)(?=^## |\Z)", text, re.M | re.S)
    if not section:
        return [f"{APPLY_CONTRACT_DOC}: 缺少 Apply 连续执行契约章节"]
    errors = []
    for heading in APPLY_CONTRACT_SECTIONS:
        body = re.search(r"^### " + heading + r"\n(.*?)(?=^### |\Z)", section[1], re.M | re.S)
        if not body or not body[1].strip():
            errors.append(f"{APPLY_CONTRACT_DOC}: 缺少或空白子契约 `{heading}`")
    for term in ("### 停止前决策", "### 行为验收", "validate-apply-behavior.py", "无可执行任务"):
        if term not in section[1]:
            errors.append(f"{APPLY_CONTRACT_DOC}: 缺少停止决策或行为验收 `{term}`")
    if not (ROOT / "scripts/validate-apply-behavior.py").is_file():
        errors.append("缺少apply行为轨迹校验器")
    return errors


def validate_governance_privacy_boundaries() -> list[str]:
    errors: list[str] = []
    paths: set[Path] = set()
    for pattern in PRIVACY_SCAN_GLOBS:
        paths.update(ROOT.glob(pattern))

    for path in sorted(paths):
        if not path.is_file():
            continue
        rel = path.relative_to(ROOT)
        text = path.read_text(encoding="utf-8")
        for lineno, line in enumerate(text.splitlines(), start=1):
            for pattern in LOCAL_PATH_PATTERNS:
                if pattern.search(line):
                    errors.append(f"{rel}:{lineno}: 存在未脱敏本机路径 `{line.strip()}`")
                    break
    return errors


def validate_command_execution_review_hook() -> list[str]:
    errors: list[str] = []
    targets = (
        ROOT / "rules" / "agent-context-budget.md",
        SKILLS_DIR / "workflow-sync" / "SKILL.md",
        ROOT / "docs" / "08-command-execution-order.md",
    )
    for path in targets:
        rel = path.relative_to(ROOT)
        text = path.read_text(encoding="utf-8")
        for term in COMMAND_EXECUTION_REVIEW_TERMS:
            if term not in text:
                errors.append(f"{rel}: 缺少命令执行复盘 Hook 契约 `{term}`")
    return errors


def validate_command_skill_review_hook_reference(path: Path) -> list[str]:
    rel = path.relative_to(ROOT)
    text = path.read_text(encoding="utf-8")
    errors: list[str] = []
    if path.parent.name == "workflow-sync":
        return errors
    for term in COMMAND_EXECUTION_REVIEW_SHORT_REFERENCE_TERMS:
        if term not in text:
            errors.append(f"{rel}: 缺少命令执行复盘 Hook 短引用 `{term}`")
    return errors


def has_summary_reuse_constraint(text: str) -> bool:
    has_scope = any(term in text for term in SUMMARY_REUSE_RULE_TERMS)
    has_action = any(term in text for term in SUMMARY_REUSE_ACTION_TERMS)
    return has_scope and has_action


def has_force_proceed_follow_up_guardrail(text: str) -> bool:
    return all(term in text for term in FORCE_PROCEED_GUARDRAIL_TERMS)


def has_follow_up_capture_fields(text: str) -> bool:
    return all(term in text for term in FOLLOW_UP_CAPTURE_FIELD_TERMS)


def has_follow_up_authorized_sync_rule(text: str) -> bool:
    return all(term in text for term in FOLLOW_UP_AUTH_SYNC_TERMS)


def has_guided_feedback_contract(text: str) -> bool:
    return all(term in text for term in GUIDED_FEEDBACK_TERMS)


def is_command_skill(path: Path) -> bool:
    name = path.parent.name
    return name in COMMAND_SKILL_NAMES or name.startswith(COMMAND_SKILL_PREFIXES)


def is_guided_feedback_target(path: Path) -> bool:
    name = path.parent.name
    return name in {"capture", "explore", "git-check"} or name.startswith(
        ("bug-", "opsx-", "release-", "req-", "sprint-")
    )


def main() -> int:
    all_skill_paths = sorted(SKILLS_DIR.glob("*/SKILL.md"))
    skill_paths = [path for path in all_skill_paths if is_command_skill(path)]
    if not all_skill_paths:
        print("未找到命令技能文件。", file=sys.stderr)
        return 1

    errors: list[str] = []
    for path in skill_paths:
        errors.extend(validate_skill(path))
        errors.extend(validate_command_skill_review_hook_reference(path))
    for path in all_skill_paths:
        errors.extend(validate_final_output_contract(path))
        errors.extend(validate_sprint_gate_no_bypass(path))
        errors.extend(validate_issue_target_contract(path))
        errors.extend(validate_explore_chain_identity_contract(path))
        errors.extend(validate_apply_execution_contract(path))
    errors.extend(validate_apply_contract_source())
    errors.extend(validate_governance_privacy_boundaries())
    errors.extend(validate_command_execution_review_hook())

    if errors:
        print("Agent 上下文预算校验失败：")
        for error in errors:
            print(f"- {error}")
        return 1

    print(
        f"Agent 上下文预算校验通过：{len(skill_paths)} 个命令技能均已接入预算规则、"
        "摘要复用约束、引导式用户反馈契约与 force-proceed follow-up 门禁；"
        "且均已接入命令执行复盘 Hook 短引用；"
        f"{len(all_skill_paths)} 个技能均已接入下一步与待用户决策/处理输出契约及去重约束，"
        "未发现最终输出占位模板、通用示例或规范语气泄漏风险，"
        "且未发现非 REQ/BUG / 纯治理 Change 跳过 Sprint 门禁表述、"
        "REQ/BUG 下一步参数回退、explore 链路身份契约缺失、不完整 Issue ID、"
        "Apply 连续执行契约缺失或旧暂停/完成文案回退、命令执行复盘 Hook 中央契约缺失或治理文档本机路径泄露。"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
