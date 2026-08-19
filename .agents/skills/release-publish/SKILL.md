---
name: "release-publish"
description: "记录产品版本发布确认结果和最终公告位置"
---

# release-publish

Use this skill when the user asks `/release-publish <version>` or wants to record the final release confirmation.

## Context Budget Guardrails（MUST）

### Guided User Feedback Contract（MUST）

当命令需要用户选择、确认、补充信息或处理阻塞时，MUST 采用引导式反馈：

- 优先使用原生交互卡片组织问题；当客户端或工具层不支持原生交互卡片时，MUST 先声明降级原因，再降级为文本结构化选项。
- 两种形态都必须包含「结构化选项 + 推荐项 + 可补充说明」，不用大段开放式追问替代。
- 每轮只聚焦 1-3 个关键决策；每个决策点 SHOULD 给出 2-4 个互斥选项。
- 至少一个选项 MUST 标注「推荐」，并用一句话说明推荐理由或适用前提。
- 默认提供「可补充说明」入口，允许用户用自然语言覆盖选项、补充约束或给出例外。
- 用户已回答的决策 MUST 在后续输出中被承接并动态收敛，只追问剩余阻塞点或新增风险点，避免重复询问已确认事项。
- 无需用户反馈的成功路径 SHOULD 保持紧凑，不为了套用格式而追加无意义问卷。

### Force-proceed Follow-up Guardrails（MUST）

- `force-proceed` 仅允许继续当前命令的非阻断部分，MUST NOT 默认自动创建 follow-up REQ/BUG；除非用户在当前命令中明确授权自动 capture，否则只输出标准 capture 文案，并明确“未自动创建 Issue”。
- 标准 capture 文案 MUST 分条包含：建议命令、类型倾向、标题、背景、影响范围、建议验收或复现要点、来源 Change/Sprint/命令；多个 follow-up 事项 MUST 逐条输出，且每条可独立用于后续 capture。
- 如用户明确授权并实际创建 follow-up Issue，MUST 按 `/req-capture`、`/bug-capture` 或 `/capture` 规则落盘，并运行对应 `req.capture` 或 `bug.capture` Workflow Sync。

- MUST 遵守 `rules/agent-context-budget.md`；同一会话已读且无变更的规则和 Skill 用摘要承接，不重复全量读取。
- 从 `releases/<version>/release.json` 和 `announcement.mdx` 开始，按 validator/gate 报告定位问题。
- 不为发布确认全量展开关联 Sprint、Issue、Change；只有门禁证据缺失时读取对应片段。
- 输出聚焦发布结论、公告位置、门禁结果和回滚提醒。

## Input

- `<version>`：必填，例如 `v0.1.0`。
- Flags：`--announcement-url <url>`、`--published-at <YYYY-MM-DD HH:mm:ss>`、`--dry-run`、`--force`（仅用户明确确认时可用）。

## Must Read

```text
AGENTS.md
rules/document-governance.md
rules/directory-structure.md
rules/release.md
rules/security.md
rules/agent-context-budget.md
releases/<version>/release.json
releases/<version>/announcement.mdx
src/shared/product-version.ts
```

## Gates

Publish MUST be blocked unless:

- `python scripts/validate-release.py --release-dir releases/<version> --stage publish` exits `0`.
- Every required gate is `pass` or correctly justified as `na`.
- Formal-scope Changes are archived.
- Public announcement is safe for external publication.
- Product version mismatch has explicit rationale, or `PRODUCT_VERSION` equals `<version>`.
- If `image_required=true` or offline image delivery is in scope, `releases/<version>/image-manifest.json` validates, or approved external build evidence is present.
- Manifest version, image tag, source plan, and input hashes still match current release inputs.
- User has supplied or confirmed the final announcement location if there is an external URL.

`--force` MUST NOT bypass public-safety failures, missing `release.json` / `announcement.mdx`, missing image manifest for image-required releases, or stale image input hashes.

## Steps

1. Validate release metadata and announcement safety.
2. Validate image manifest when `image_required=true`:
   - `python scripts/validate-image-build.py validate-manifest --release <version>`
   - Confirm manifest `version`, `image_tag`, `source_plan` and `input_hashes` match current inputs.
   - If external build evidence is used, confirm evidence source, platform, digest or tarball sha256, validation method, owner confirmation and risk statement.
3. Confirm publish-time fields:
   - `release_time` / published time in `YYYY-MM-DD HH:mm:ss`
   - final announcement path or URL
   - rollback and known issues are present
4. Update `releases/<version>/release.json` with publish confirmation fields if the existing schema already contains them, or append a conservative `publish_confirmation` object:

```json
{
  "published_at": "YYYY-MM-DD HH:mm:ss",
  "announcement_url": "https://example.com/releases/vX.Y.Z",
  "confirmed_by": "operator",
  "notes": "发布确认说明"
}
```

5. Re-run validation.

## Output Contract（MUST）

- 输出必须包含「下一步」和「待用户决策/处理」两类信息；没有对应事项时写「无」。
- 「下一步」只列可直接执行的命令或验证动作；「待用户决策/处理」只列需要用户选择、授权、提供资料或确认风险的事项。
- 同一事项不得在「下一步」与「待用户决策/处理」中重复；不得重复输出等价事项。

## Output

Report version, publish status, announcement file/URL, validation command result, gate summary, updated files, and rollback reminder.

## Command Execution Review Hook（MUST）

命令结束前 MUST 遵守 `.agents/skills/workflow-sync/SKILL.md` 的 Command Execution Review Hook，输出「执行链路复盘」：链路状态、问题证据、规范优化建议，并说明默认未自动创建 Issue/Change。

## Final Step — AI Usage Post-command Hook (MUST)

After publish confirmation is recorded or publish is blocked with a documented reason, run:

```bash
python scripts/extract-ai-usage.py \
  --post-command-hook \
  --workflow-event release.publish \
  --release <version> \
  [--release-sprint <sprint-id>] \
  [--sprint <sprint-id>] \
  [--req <REQ-id>] \
  [--bug <BUG-id>] \
  [--change <change-id>] \
  --json
```

- Pass Sprint / REQ / BUG / Change ids from `releases/<version>/release.json`.
- Pass `--release <version>` so the hook writes `data/ai-usage/command-runs/releases/<version>/release.publish.json`.
- Pass each release-scope Sprint with repeated `--release-sprint <sprint-id>`.
- If no Sprint is associated, omit `--sprint`; Sprint snapshot output MUST be `skipped`.
- Print only the compact hook summary: `status`, `usage_mode`, `command_run_count`, `session_input`, `release_artifact`, `sprint_snapshot`, `warning_count`, and `recommended_action`.
- If local session input is unavailable, report `usage_mode: unavailable` and the recommended action; do not treat that as parent command failure.
