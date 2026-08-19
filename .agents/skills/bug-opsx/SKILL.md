---
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

按 CLI 生成 proposal（含 Rollback Plan）、design（根因+修复方案+测试）、specs（MODIFIED/ADDED）、tasks（**含回归测试**）。

proposal **Why** 链接 `BUG-xxxx`。

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
