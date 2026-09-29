---
updated_at: 2026-09-15 00:23:57
name: "bug-opsx"
description: "已评审缺陷 → OpenSpec fix-* Change（CLI）；原 /bug-to-change"
---

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

- BUG 转 Change 时只读取目标 BUG 文档包、父需求 trace 摘要与候选 spec 片段；不得默认读取全部 `openspec/specs/**`。
- MUST 遵守 `rules/agent-context-budget.md`；同一会话已读且无变更的规则和 Skill 用摘要承接，不重复全量读取。
- 关联能力追溯先读取 BUG 包与 `trace.md` 中的 `related_requirement` / `related_change`，再定向读取对应 spec；不要默认在 `openspec/specs` + `openspec/archive` 上做宽泛全文搜索。
- 需要历史证据时先用 `rg -l "<keyword>" openspec/specs issues/requirements` 获取候选文件；只有候选不足时才加入 `openspec/archive/**`。
- 生成 Change artifacts 前只读取目标 capability 的 Requirement 标题和相关场景片段，避免整读大 spec。
- 命令输出优先控制在 `max_output_tokens <= 8000`；大范围命中先给命中数和文件列表。

# bug-opsx

Use this skill when the user asks to run the migrated source command `bug-opsx`.

## Command Template

将已评审且已纳入 Sprint 的 `issues/bugs/BUG-*` 转为 `openspec/changes/fix-*/`。默认 **fix-***；不写 `src/`。

**Input**：完整 `BUG-xxxx-slug`

| Flag | 含义 |
|------|------|
| `--hotfix` | 命名/任务强调紧急发布 |
| `--change-name <id>` | 指定 fix-* id |

---

## Command Order（MUST）

- 推荐顺序遵守 `docs/08-command-execution-order.md`：BUG approved → `/sprint-propose --bug <BUG-full-id>` → BUG `status: in_sprint` → `/bug-opsx <BUG-full-id>` → `/opsx-apply <BUG-full-id>` → `/opsx-modify <BUG-full-id>`（可选）→ `/opsx-archive <BUG-full-id>`。
- `/bug-opsx` 完成后 MUST 通过 Workflow Sync 将 Change 回填到同一 Sprint 的 `changes[]` 和 `scope_estimates[].change`。
- 若后续输出 `/opsx-apply`、`/opsx-modify` 或 `/opsx-archive`，MUST 使用原始完整 `BUG-xxxx-slug`；只有无 REQ/BUG 来源的纯治理 Change 才使用裸 `<change-id>`。
- 写入 `sprint.yaml`、Issue trace、Change trace、Workflow Sync 和 AI Usage 快照的步骤 MUST 严格串行执行。

---

## Step 0 — 读取

```text
AGENTS.md
rules/bug-management.md
rules/testing.md
rules/api.md
openspec/project.md
```

BUG 目录：bug.md、root-cause.md、workaround.md、acceptance.md、trace.md、logs/、screenshots/

```bash
openspec list --json
```

---

## Step 0.5 — 评审门禁（MUST）

读 `trace.md` `status`：

| status | 动作 |
|---|---|
| `approved` | **立即停止** → `/sprint-propose --bug <BUG-full-id>`，纳入 Sprint 并同步为 `in_sprint` 后再执行 `/bug-opsx` |
| `in_sprint` | 可继续（须已完成 `/bug-review` 且已由 `/sprint-propose` 纳入 Sprint） |
| `done` | 可继续（追溯/补建 change） |
| 其他 | **立即停止** → `/bug-review <BUG-full-id> --approve` |

---

## Step 1 — Bug Readiness

Ready / Partially Ready / Not Ready。Not Ready → `/bug-complete`，停止。

---

## Step 2 — 分析

- 现象、复现、影响（Bug Analysis Report）
- 根因分类、严重等级
- 关联 REQ/Change（若有）

---

## Step 3 — 创建 fix-* Change

```bash
openspec new change "fix-<area>-<topic>"
```

命名示例：`fix-minio-upload-timeout`、`fix-admin-login-redirect`

---

## Step 4 — Artifacts

按 CLI 生成 proposal（含回滚方案）、design（根因+修复方案+测试）、specs（MODIFIED/ADDED）、tasks（**含回归测试**）。OpenSpec CLI 返回的英文 instruction 和 template 只作为结构参考，不得原样复制英文脚手架标题到项目文档。

proposal **Why** 链接 `BUG-xxxx`。

### Step 4.1 — OpenSpec CLI 模板标题中文化（MUST）

生成或补齐 Change 文档时，MUST 将 CLI 模板标题替换为项目中文标题：

| 文件 | CLI 标题 | 项目标题 |
|---|---|---|
| `proposal.md` | `Why` | `背景` |
| `proposal.md` | `What Changes` | `变更内容` |
| `proposal.md` | `Capabilities` | `能力影响` |
| `proposal.md` | `New Capabilities` | `新增能力` |
| `proposal.md` | `Modified Capabilities` | `修改能力` |
| `proposal.md` | `Impact` | `影响范围` |
| `design.md` | `Context` | `背景与现状` |
| `design.md` | `Root Cause` / `Proposed Fix` | `根因` / `修复方案` |
| `design.md` | `Test Strategy` | `测试策略` |
| `design.md` | `Risks` / `Rollback Plan` | `风险` / `回滚方案` |
| `tasks.md` | `Implementation` / `Testing` / `Documentation` | `实施任务` / `回归验证` / `文档同步` |

- MODIFIED spec 的 `Requirement:` 标题必须与 `openspec/specs/` 既有能力标题一致；OpenSpec 关键字、命令、路径、API 字段和代码标识可保留英文。
- 若 CLI template 中出现 HTML 注释、尖括号占位符或英文说明，写入项目前必须改写为当前 BUG 的中文事实，不得保留占位解释。
- 生成后必须运行 `python scripts/validate-openspec-language.py --change <change-id> --residual-report`，确保当前 Change 不残留英文脚手架标题。

---

## Step 5 — 追溯

更新 BUG `trace.md`：

```yaml
openspec_changes:
  - change_id: fix-…
    type: fix
    status: proposed
```

tasks 末项提醒：`docs/knowledge-base/incidents/`（若适用）

创建 `openspec/changes/<id>/trace.md` 时，新建 trace frontmatter MUST 固化 execution schema v1，最小模板如下：

```yaml
execution:
  schema_version: 1
  started_at: null
  completed_at: null
  last_event: bug.opsx
```

- `schema_version` MUST 为数字 `1`，不得写成字符串或省略。
- `/bug-opsx` 创建 Change 时只声明 schema 与创建事件，不把 `started_at` 伪造为实施启动时间；后续 `/opsx-apply` 的 Workflow Sync 会在 `opsx.start` / `opsx.apply` 中维护实际启动、完成与最后事件。
- 已存在 `execution` frontmatter 时，MUST 保留有效 `started_at`、`completed_at` 和 `last_event`，只补齐缺失的 `schema_version: 1`；不得批量重写历史终态。

---

## Step 5.5 — 当前 Change 中文校验与残留分离报告（MUST）

成功生成或确认 Change 文档后，MUST 运行当前 Change 聚焦中文优先校验，并输出全仓残留分离报告：

```bash
python scripts/validate-openspec-language.py --change <change-id> --residual-report
```

- 当前 Change 校验失败时，MUST 修复当前 Change 文档并重跑，退出码为失败时不得结束 `/bug-opsx`。
- 其他 active Change 的中文残留只作为“全仓残留分离报告”输出，不得混入当前 BUG → Change 链路的失败结论。
- 若残留报告存在非当前 Change 问题，最终「执行链路复盘」可标记为 warning，并给出聚焦治理建议；默认不得自动修改无关 Change 或创建 follow-up Issue/Change。

---

## Step 6 — 输出

```text
## Bug → OpenSpec 完成
**BUG:** …
**Change:** fix-…
**Next:** `/opsx-apply <BUG-full-id>`
```

---

## Guardrails

- 仅 in_sprint；已评审但未纳入 Sprint 时先 `/sprint-propose --bug <BUG-full-id>`
- 默认 fix-*，非 add
- 不跳过 CLI
- 不写 src

## 参考

- `.agents/skills/req-opsx/SKILL.md`（结构对照）
- `.agents/skills/opsx-apply/SKILL.md`

---

## 当前态看板索引（MUST）

成功创建或确认 BUG 对应 OpenSpec Change 后，MUST 在 `issues/bugs/CHANGELOG.md` 更新对应 BUG 当前态行，并记录关联 Sprint、Change、下一步和事实源路径。看板索引不替代 BUG `trace.md`、Change trace、父需求反向追溯索引或 Sprint scope。

## Output Contract（MUST）

- 输出必须包含「下一步」和「待用户决策/处理」两类信息；没有对应事项时写「无」。
- 「下一步」只列可直接执行的命令或验证动作；「待用户决策/处理」只列需要用户选择、授权、提供资料或确认风险的事项。
- 同一事项不得在「下一步」与「待用户决策/处理」中重复；不得重复输出等价事项。

## Command Execution Review Hook（MUST）

命令结束前 MUST 遵守 `.agents/skills/workflow-sync/SKILL.md` 的 Command Execution Review Hook，输出「执行链路复盘」：链路状态、问题证据、规范优化建议，并说明默认未自动创建 Issue/Change。

## Final Step — Workflow Sync (MUST)

Read `.agents/skills/workflow-sync/SKILL.md` and run:

```bash
python scripts/sync-workflow-status.py --event bug.opsx --bug <BUG-id> --change <change-id> --sprint auto
```

- Exit code **MUST** be `0` before ending this command.
- Print the summary **Workflow Sync Report** to the user; use `--output detail` only for debugging.
- Do **not** hand-edit `sprint.md` Scope marker blocks (`<!-- workflow-sync:* -->`).
- Workflow Sync 成功后仍 MUST 确认 Step 5.5 的当前 Change 聚焦中文校验已通过；全仓残留分离报告只影响复盘 warning 与后续治理建议，不阻断当前 Change。

## Change 身份门禁

遵循 `rules/document-governance.md` 的“Change 身份唯一性”：新建前运行 `python scripts/validate-change-identity.py --new-id <change-id>`；复用活动 Change 或归档前运行 `python scripts/validate-change-identity.py`。失败时先处理冲突，不得复用已归档 ID 或按日期自动取最新。

## 中文标题生成门禁

本次生成或重生成的所有 Markdown 必须包含中文业务 Frontmatter `title` 与一致的唯一一级标题，辅助文档标题包含业务主题及用途；不得只有 ID、英文模板或文档类别。Issue 主文档的业务 title 同步注册表，Change proposal 标题不得覆盖 Issue 标题。保留 OpenSpec 解析关键字。

在完成态 Workflow Sync 之前，对本次产物执行 `python scripts/validate-document-titles.py` 并传入明确文件路径或当前 `--req` / `--bug` / `--change`；失败先修正，不宣称完成、不推进状态。不批量修复无关历史文档。
