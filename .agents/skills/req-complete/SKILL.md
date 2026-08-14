---
name: "req-complete"
description: "需求完善 - 基于 requirement.md 补齐六件套（不含 OpenSpec）"
---

# req-complete

Use this skill when the user asks to run the migrated source command `req-complete`.

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
- 检索先定位再分段读取；大范围 `rg/find` 默认排除 Harness、模板 assets、历史 agent 目录、archive、generated、node_modules、dist、coverage。
- 命令输出优先 `max_output_tokens <= 8000`；大 diff、OpenAPI/Orval 生成物、测试日志、Workflow Sync 输出先给摘要或命中数。


## Command Template

替代原 `/requirement-to-change` 的**文档部分**。不创建 `openspec/changes/`。

**Input**：完整 `REQ-xxxx-slug`（须存在 `requirement.md`）

**Output**：user-stories、business-flow、acceptance、trace（扩写）、prototype（UI 类）；Readiness Report + Knowledge-base Cross-cutting Report

---

## Step 0 — 读取

```text
AGENTS.md
rules/requirement-management.md
rules/ui-design.md          # UI 类
docs/knowledge-base/README.md
issues/requirements/<REQ-ID>/requirement.md
issues/requirements/<REQ-ID>/capture.md
```

### Step 0.1 — 知识库读库与 REQ 类型判定（MUST）

1. 根据 `requirement.md` / `capture.md` 判定本 REQ 涉及的 **UI 场景标签**（可多选）：

| 标签 | 触发条件（任一命中即选） |
|------|--------------------------|
| `admin-list` | 管理端 CRUD **列表页**、表格 + 分页 + 行内操作 |
| `admin-form` | 管理端**表单页/设置页**（非弹窗）、Tab 面板、页内保存 |
| `admin-modal` | 管理端**弹窗**新建/编辑（含宽弹窗 880px 类） |
| `media-upload` | 图片/视频/头像/Logo **上传**与回显 |

2. 按标签 **MUST** 读取对应 best-practices（路径均相对 `docs/knowledge-base/`）：

| 标签 | 文档 |
|------|------|
| `admin-list` | `best-practices/admin-list-page-consistency.md` |
| `admin-form` | `best-practices/admin-form-page-consistency.md` |
| `admin-modal` | `best-practices/admin-modal-width-css-cascade.md` |
| `media-upload` | `best-practices/admin-media-upload-chain.md` |

3. **SHOULD** 读取最近一期 `retrospectives/*-retrospective.md`，检索与本 REQ 同域的复发模式（列表/confirm/toast/上传等），写入 trace 变更记录摘要。

4. 输出 **Knowledge-base Cross-cutting Report**（表格：标签 / 引用文档 / 将写入 acceptance 的 AC 条数）。

5. **无匹配标签**（纯 API/后端/非 UI）：在 Report 注明「无横切 AC」；跳过 Step 1.1。

---

## Step 1 — 生成/补齐文档

| 文件 | 内容要点 |
|------|----------|
| `user-stories.md` | US-xxx、验收要点 |
| `business-flow.md` | 流程 ASCII、与父 REQ 差异 |
| `acceptance.md` | AC-xxx 可勾选清单 + **§横切 AC（knowledge-base）**（见 Step 1.1） |
| `trace.md` | 扩写 yaml、关联、变更记录；**MUST** 含 `knowledge_base_refs:` 列表；带 prototype 时 MUST 含 `prototype_refs:` 与 `prototype_gate:` |
| `prototype/web/*` | UI 类：html、context.md；PNG 可标待导出；带 prototype 页面 MUST 完成原型拆解 |

`status` → `enriching`（补齐中）→ 文档齐后 `pending_review`

### Step 1.1 — 横切 AC 嵌入 acceptance.md（MUST — 有 UI 标签时）

在 `acceptance.md` 末尾追加固定章节（不得与功能 AC 混编号，使用 **AC-XCUT-xxx**）：

```markdown
## 横切 AC（knowledge-base）

> 来源：`docs/knowledge-base/best-practices/<doc>.md` — 预防 Sprint 002/003 复发类缺陷

- [ ] AC-XCUT-001 …（从 best-practices「验收 gate」逐条转化，措辞 MUST 可测试）
- [ ] AC-XCUT-002 …
```

**转化规则**：

| 来源文档 | MUST 写入的横切 AC 要点（至少） |
|----------|--------------------------------|
| `admin-list-page-consistency.md` | 分页 DOM 对齐用户管理基准；fixed toast 无 layout shift；状态变更 DS confirm；无 `window.confirm` |
| `admin-form-page-consistency.md` | 全页单保存 CTA（footer）；无页头重复保存；恢复默认/dirty 切换 DS modal；成功反馈 fixed toast |
| `admin-modal-width-css-cascade.md` | TSX 禁止 `modal-card` 与专属类并存；Computed width 验收；矮视口 body scroll |
| `admin-media-upload-chain.md` | 上传状态机 idle→uploading→done/failed；同会话即时回显；Docker 实际 Web 端口上传读取回显；脚本准备测试身份且不依赖默认管理员密码 |

- 若 best-practices 某 gate 与本 REQ 无关（如无上传），**MUST** 在 AC 行注释 `N/A — <理由>`，不得删除整节。
- `design.md` 尚未创建时：在 `trace.md` `knowledge_base_refs` 列出文档路径，供后续 `/req-opsx` 写入 change design。

### Step 1.2 — Prototype-driven UI Gate（MUST — 存在 prototype 时）

当 REQ 存在 `prototype/web/`、`prototype/admin/` 或等价页面原型目录时，`/req-complete` MUST 先完成原型拆解，再输出 Ready：

1. 读取 `prototype/**/context.md`、`prototype/**/prototype.html` 和已有 PNG/截图清单；不得只凭文件存在判断完成。
2. 在 `prototype/**/context.md` 或 `acceptance.md` 补齐：页面清单、关键区域、组件层级、状态矩阵、交互触发、数据依赖、响应式断点和 1440px 验收焦点。
3. 在 `acceptance.md` 增加 `## 原型驱动 UI AC`，至少包含原型拆解、UI Skeleton、1440px 视觉验收、REQ 最终一致性检查四项 `AC-PROTOTYPE-*`。
4. 在 `trace.md` 增加：

```yaml
prototype_refs:
  - path: issues/requirements/<stage>/<REQ-full-id>/prototype/web/prototype.html
    role: html-structure
prototype_gate:
  decomposition: required|done
  ui_skeleton: pending
  visual_acceptance_1440: pending
  req_final_consistency: pending
```

缺少拆解或 AC-PROTOTYPE 时，Readiness MUST 为 `Not Ready`；只有 PNG 缺失但 `context.md` 明确 PNG 暂不要求时 MAY 为 `Partially Ready`。

### trace.md 扩展字段示例

```yaml
knowledge_base_refs:
  - docs/knowledge-base/best-practices/admin-list-page-consistency.md
cross_cutting_tags:
  - admin-list
  - admin-modal
```

---

## Step 2 — Readiness Report

| readiness | 条件 |
|-------------|------|
| Ready | 五件套齐（+ UI 有 prototype 策略）+ **有 UI 标签时 §横切 AC 已写入** |
| Partially Ready | 缺 PNG 等非阻塞；或横切 AC 已写但 best-practices 为 draft；prototype 已拆解但视觉截图待实现阶段产出 |
| Not Ready | 缺 acceptance 等；或有 UI 标签但缺 §横切 AC；或存在 prototype 但缺原型拆解 / AC-PROTOTYPE / prototype_gate |

| knowledge-base gate | 条件 |
|---------------------|------|
| Pass | 所有命中标签的 best-practices 已读且 AC-XCUT 已转化 |
| N/A | 纯后端/API REQ |
| Fail | 有 UI 标签但未读库或未写 §横切 AC |

---

## Step 3 — 输出

```text
## Req Complete

**REQ:** <REQ-full-id>
**Readiness:** Ready | Partially Ready | Not Ready
**Knowledge-base gate:** Pass | N/A | Fail
**Cross-cutting tags:** admin-list, admin-modal, …
**Refs:** docs/knowledge-base/best-practices/…
**Prototype Gate:** Pass | Partially Ready | Fail

**Added AC-XCUT:** N 条（见 acceptance.md §横切 AC）

**Next:**
1. `/req-review <REQ-full-id> --approve`
2. 通过后 `/req-opsx <REQ-full-id>`（design.md MUST 引用 knowledge_base_refs）

`<REQ-full-id>` MUST 使用完整 `REQ-xxxx-slug`。
3. 纳入 Sprint 前确认 sprint.md §横切预防清单 已覆盖本 REQ
```

## Guardrails

- 不写 `src/`、不 `openspec new change`
- 不替代 `/req-generate`（若无 requirement.md 先 generate）
- **不得跳过 Step 0.1**（UI 类 REQ）；不得省略 §横切 AC 仅写功能 AC
- 横切 AC **MUST NOT** 复制整份 best-practices 正文，只写可勾选、可测试条目 + 来源链接

---

## 当前态看板索引（MUST）

成功补齐需求六件套或关键验收资料后，MUST 在 `issues/requirements/CHANGELOG.md` 更新对应 REQ 当前态行。该索引只做目录级当前快照，不替代单条 REQ `trace.md`。

## Output Contract（MUST）

- 输出必须包含「下一步」和「待用户决策/处理」两类信息；没有对应事项时写「无」。
- 「下一步」只列可直接执行的命令或验证动作；「待用户决策/处理」只列需要用户选择、授权、提供资料或确认风险的事项。
- 同一事项不得在「下一步」与「待用户决策/处理」中重复；不得重复输出等价事项。

## Final Step — Workflow Sync (MUST)

Read `.agents/skills/workflow-sync/SKILL.md` and run:

```bash
python scripts/sync-workflow-status.py --event req.complete --req <REQ-id> --sprint auto
```

- Exit code **MUST** be `0` before ending this command.
- Print the summary **Workflow Sync Report** to the user; use `--output detail` only for debugging.
- Do **not** hand-edit `sprint.md` Scope marker blocks (`<!-- workflow-sync:* -->`).
