---
name: "req-opsx"
description: "已评审需求 → OpenSpec Change（CLI 驱动）；原 /requirement-to-opsx"
---

# req-opsx

Use this skill when the user asks to run the migrated source command `req-opsx`.

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

- REQ 转 Change 时只读取目标 REQ 六件套摘要与候选 spec 片段；不得默认读取全部 `openspec/specs/**`。
- MUST 遵守 `rules/agent-context-budget.md`；同一会话已读且无变更的规则和 Skill 用摘要承接，不重复全量读取。
- 检索先定位再分段读取；大范围 `rg/find` 默认排除 Harness、模板 assets、历史 agent 目录、archive、generated、node_modules、dist、coverage。
- 命令输出优先 `max_output_tokens <= 8000`；大 diff、OpenAPI/Orval 生成物、测试日志、Workflow Sync 输出先给摘要或命中数。


## Command Template

将已评审且已纳入 Sprint 的 `issues/requirements/REQ-*` 转为 `openspec/changes/<change-id>/`（proposal / design / specs / tasks）。**不写 `src/`**；实现用 `/opsx-apply`。

**Input**：完整 `REQ-xxxx-slug`

| Flag | 含义 |
|------|------|
| `--type add\|fix\|update` | 强制 change 类型 |
| `--strategy <name>` | css-port、tailwind-ds 等 |
| `--skip-explore` | 跳过 UI 策略探讨 |
| `--change-name <kebab-case>` | 指定 change id |

---

## 前置关系

```text
/req-capture → /req-explore → /req-generate → /req-complete → /req-review (approved)
        │
        └─ /sprint-propose --req REQ-xxxx-slug  →  /req-opsx REQ-xxxx-slug  →  /opsx-apply REQ-xxxx-slug  →  /opsx-modify REQ-xxxx-slug（可选） →  /opsx-archive REQ-xxxx-slug
```

---

## Command Order（MUST）

- 推荐顺序遵守 `docs/08-command-execution-order.md`：REQ approved → `/sprint-propose --req <REQ-full-id>` → REQ `status: in_sprint` → `/req-opsx <REQ-full-id>` → `/opsx-apply <REQ-full-id>` → `/opsx-modify <REQ-full-id>`（可选）→ `/opsx-archive <REQ-full-id>`。
- `/req-opsx` 完成后 MUST 通过 Workflow Sync 将 Change 回填到同一 Sprint 的 `changes[]` 和 `scope_estimates[].change`。
- 若后续输出 `/opsx-apply`、`/opsx-modify` 或 `/opsx-archive`，MUST 使用原始完整 `REQ-xxxx-slug`；只有无 REQ/BUG 来源的纯治理 Change 才使用裸 `<change-id>`。
- 写入 `sprint.yaml`、Issue trace、Change trace、Workflow Sync 和 AI Usage 快照的步骤 MUST 严格串行执行。

---

## Step 0 — 必须读取

```text
AGENTS.md
openspec/project.md
rules/global.md
rules/requirement-management.md
rules/ui-design.md
rules/testing.md
rules/directory-structure.md
```

```bash
openspec list --json
openspec list --specs
```

REQ 目录：requirement.md、user-stories.md、business-flow.md、acceptance.md、trace.md、prototype/**

---

## Step 0.5 — 评审门禁（MUST — 无例外）

读 `trace.md`（或 requirement.md frontmatter）`status`：

| status | 动作 |
|--------|------|
| `approved` | **立即停止** → `/sprint-propose --req <REQ-full-id>`，纳入 Sprint 并同步为 `in_sprint` 后再执行 `/req-opsx` |
| `in_sprint` | 可继续（须已完成 `/req-review` 且已由 `/sprint-propose` 纳入 Sprint） |
| `done` | 可继续（追溯/补建 change） |
| `pending_review` / `draft` / `captured` / `enriching` / … | **立即停止** → `/req-review <REQ-full-id> --approve` |

未评审或未纳入 Sprint **不得** opsx；**不得**因口头确认、Change 名称已确定或用户急于开发而 bypass（见 `rules/requirement-management.md` §4.1）。

---

## Step 1 — Readiness

输出 **Requirement Readiness Report**（ready / partially ready / not ready）。

**Not Ready** → `/req-complete <REQ-full-id>`，**停止**，不创建 change。

---

## Step 2 — 影响分析与 Change 分类

```yaml
impact: { backend, web, miniapp, admin, database, storage, api }
capabilities: { new: [], modified: [] }
```

| 条件 | change_type | 示例 |
|------|-------------|------|
| 无相关 spec | add | add-user-login |
| 已有实现，验收/视觉未过 | fix | fix-login-css-port |
| 仅规范文案 | update | update-login-acceptance-sync |

---

## Step 3 — 原型与验收冲突（MUST）

`prototype/web/` 存在时输出 Conflict Report；优先级：

```text
HTML > PNG > *-context.md > acceptance.md > ui-design.md > openspec/specs
```

design.md **MUST** 含 Conflict Resolution；delta spec 用 MODIFIED/REMOVED 消化。

### Step 3.1 — 原型拆解承接（MUST — 存在 prototype 时）

`prototype/**` 存在时，`/req-opsx` MUST 读取并承接 `/req-complete` 产出的原型拆解、`AC-PROTOTYPE-*`、`trace.md prototype_gate` 和 `docs/standards/prototype-ui-acceptance.md`：

- 若缺原型拆解、`prototype_refs`、`prototype_gate` 或 `AC-PROTOTYPE-*`，Requirement Readiness MUST 为 `Not Ready`，停止并输出 `/req-complete <REQ-full-id>`。
- Change `design.md` MUST 先新增 `UI Contract`，明确事实源优先级、前后台一致性 checklist、关键尺寸/字体/颜色/图标/文案、权限规则、Mock/API 边界和 computed style 验收点。
- Change `design.md` MUST 新增 `UI Skeleton` 章节，包含页面结构、区域边界、组件层级、状态容器、数据依赖、可测选择器和 1440px 验收焦点。
- Change `tasks.md` MUST 将 `UI Skeleton` 作为先行任务，并在任何细节实现任务前完成。
- Change `trace.md` MUST 记录 prototype 来源、Conflict Resolution、UI Contract、Skeleton 状态、1440px/关键交互截图、computed style、Mock/API 边界和最终一致性状态。
- Delta spec MUST 写明 prototype 是设计输入，最终验收以 Change design、acceptance、1440px/关键交互视觉证据、computed style、Mock/API 边界和 REQ 最终一致性回填共同为准。

---

## Step 4 — UI Explore Gate

`impact.web` 且有 prototype 时，无 `--strategy` 且非 `--skip-explore`：选 CSS Port / DS / Asset，写入 design.md D1。

---

## Step 5 — 创建 Change（CLI）

```bash
openspec new change "<change-id>"
openspec status --change "<change-id>" --json
```

---

## Step 6 — 生成 Artifacts

```bash
openspec instructions <artifact-id> --change "<change-id>" --json
```

按 schema 顺序写 proposal、design、specs、tasks。MODIFIED 标题 **MUST** 与 `openspec/specs/` 一致。

---

## Step 7 — 追溯

更新 REQ `trace.md`：

```yaml
openspec_changes:
  - change_id: …
    type: fix
    status: proposed
```

创建 `openspec/changes/<id>/trace.md`（UI 类含 PNG checklist）。

---

## Step 8 — 输出

```text
## Req → OpenSpec 完成
**REQ:** …
**Change:** …
**Next:** `/opsx-apply <REQ-full-id>` 或 `/sprint-apply sprint-xxx`
```

---

## Guardrails

| 规则 | 说明 |
|------|------|
| 仅 in_sprint | 已评审但未纳入 Sprint 时先 `/sprint-propose --req <REQ-full-id>` |
| 不替代 req-complete | 文档不全先 complete |
| 不跳过 CLI | 禁止手写 change 目录 |
| 不写 src | 实现用 opsx-apply |

---

## 参考

- `.agents/skills/req-complete/SKILL.md`
- `.agents/skills/opsx-apply/SKILL.md`、`opsx-archive.md`、`opsx-explore.md`
- 归档样例：`openspec/archive/`

---

## 当前态看板索引（MUST）

成功创建或确认 REQ 对应 OpenSpec Change 后，MUST 在 `issues/requirements/CHANGELOG.md` 更新对应 REQ 当前态行，并记录关联 Sprint、Change、下一步和事实源路径。看板索引不替代 REQ `trace.md`、Change trace 或 Sprint scope。

## Output Contract（MUST）

- 输出必须包含「下一步」和「待用户决策/处理」两类信息；没有对应事项时写「无」。
- 「下一步」只列可直接执行的命令或验证动作；「待用户决策/处理」只列需要用户选择、授权、提供资料或确认风险的事项。
- 同一事项不得在「下一步」与「待用户决策/处理」中重复；不得重复输出等价事项。

## Command Execution Review Hook（MUST）

命令结束前 MUST 遵守 `.agents/skills/workflow-sync/SKILL.md` 的 Command Execution Review Hook，输出「执行链路复盘」：链路状态、问题证据、规范优化建议，并说明默认未自动创建 Issue/Change。

## Final Step — Workflow Sync (MUST)

Read `.agents/skills/workflow-sync/SKILL.md` and run:

```bash
python scripts/sync-workflow-status.py --event req.opsx --req <REQ-id> --change <change-id> --sprint auto
```

- Exit code **MUST** be `0` before ending this command.
- Print the summary **Workflow Sync Report** to the user; use `--output detail` only for debugging.
- Do **not** hand-edit `sprint.md` Scope marker blocks (`<!-- workflow-sync:* -->`).
