---
name: "build-api-standard"
updated_at: 2026-10-23 08:31:02
description: "建立 API Governance（统一响应 / 错误码 / OpenAPI / Orval）"
---

# build-api-standard

Use this skill when the user asks to run the migrated source command `build-api-standard`.

## 浏览器自主取证（MUST）

浏览器清单超时、单个工具失败或终端 HTTP 探测失败时，先按 `rules/root-cause-evidence.md` §5.0 检查现有标签页、直接连接浏览器窗口并尝试可行替代入口；区分旧页面展示和当前服务连通性，完成这些检查后才判断是否无法访问。

测试、验收、BUG 补证或问题排查需要产品运行态证据时，Agent 可在已有权限与任务范围内直接通过浏览器访问产品并取证，优先复用 Codex 侧边浏览器中与任务相关的产品标签页，无需人工二次确认；该入口不可用或不能取得所需证据时，使用已提供的其他浏览器或等价自动化工具，Firefox 作为后备。只有无法访问、权限不足、操作超出已授权边界，或自主取证后关键证据仍不足时，才请用户补证，并说明已尝试路径与具体缺口。证据脱敏、不可逆操作和存放边界遵循 `rules/root-cause-evidence.md` 第 5 节。

## Context Budget Guardrails（MUST）

### Force-proceed Follow-up Guardrails（MUST）

- `force-proceed` 仅允许继续当前命令的非阻断部分，MUST NOT 默认自动创建 follow-up REQ/BUG；除非用户在当前命令中明确授权自动 capture，否则只输出标准 capture 文案，并明确“未自动创建 Issue”。
- 标准 capture 文案 MUST 分条包含：建议命令、类型倾向、标题、背景、影响范围、建议验收或复现要点、来源 Change/Sprint/命令；多个 follow-up 事项 MUST 逐条输出，且每条可独立用于后续 capture。
- 如用户明确授权并实际创建 follow-up Issue，MUST 按 `/req-capture`、`/bug-capture` 或 `/capture` 规则落盘，并运行对应 `req.capture` 或 `bug.capture` Workflow Sync。

- MUST 遵守 `rules/agent-context-budget.md`；同一会话已读且无变更的规则和 Skill 用摘要承接，不重复全量读取。
- 检索先定位再分段读取；大范围 `rg/find` 默认排除 Harness、模板 assets、历史 agent 目录、archive、generated、node_modules、dist、coverage。
- 命令输出优先 `max_output_tokens <= 8000`；大 diff、OpenAPI/Orval 生成物、测试日志、Workflow Sync 输出先给摘要或命中数。


## Command Template

将 `rules/api.md` 落地为可执行 API 治理：文档、Schema、校验脚本与 后端分层约定。

**关联 REQ**：`REQ-0000-build-api-standard`（`change_id: build-api-standard`，已归档见 `openspec/specs/api-governance/`）

**Input**：`--verify` 仅校验

---

## 必须读取

```text
AGENTS.md
rules/api.md
rules/security.md
rules/testing.md
rules/coding.md
openspec/specs/api-governance/spec.md
src/backend/app/**
src/web/orval.config.ts
docs/03-api-index.md
```

---

## 与 req / opsx 关系

| 场景 | 做法 |
|------|------|
| 新业务 API | 对应业务 REQ 的 `/req-opsx` → `add-*` |
| 治理规范变更 | 新 REQ + `/req-opsx`（MODIFIED `api-governance`） |
| 接口实现后 | **MUST** 更新 OpenAPI + `scripts/generate-openapi-client.sh` |

---

## Step 1 — 治理文档

核对/更新：

```text
docs/standards/api-governance.md
docs/standards/error-codes.md
docs/standards/openapi-rules.md
docs/standards/authentication.md
docs/standards/file-upload.md
docs/03-api-index.md
```

---

## Step 2 — 统一结构

```text
src/backend/app/schemas/common/     # response, pagination, error
src/backend/app/core/error_codes.py
src/backend/app/api/v1/
```

统一响应：`{ code, message, data }`；分页 `page` / `page_size` / `items` / `total`。

---

## Step 3 — OpenAPI First

- 路由须 `response_model`、`summary`、`tags`
- 导出 `src/web/openapi.json` 为契约
- Orval → `src/web/src/shared/api/generated.ts`

---

## Step 4 — 测试与校验

```text
src/backend/tests/                  # 集成测试
scripts/validate-api-standard.py
```

每接口：成功、失败、权限、边界。

---

## Step 5 — OpenSpec

已归档 **勿重建** `build-api-standard`。新治理需求走 `/req-opsx`。

---

## 验收

```text
□ validate-api-standard.py pass
□ Orval 生成无报错
□ error_codes 与 rules/api.md 一致
```
## Output Contract（MUST）

- 输出必须包含「下一步」和「待用户决策/处理」两类信息；没有对应事项时写「无」。
- 「下一步」只列可直接执行的命令或验证动作；「待用户决策/处理」只列需要用户选择、授权、提供资料或确认风险的事项。
- 同一事项不得在「下一步」与「待用户决策/处理」中重复；不得重复输出等价事项。
## Command Execution Review Hook（MUST）

命令结束前 MUST 遵守 `.agents/skills/workflow-sync/SKILL.md` 的 Command Execution Review Hook，输出「执行链路复盘」：链路状态、问题证据、规范优化建议，并说明默认未自动创建 Issue/Change。

## 面向用户的表达

面向用户的输出遵循 `rules/language.md` 的“产品经理视角沟通”：先讲业务结果和用户影响，优先日常语言，必要技术术语随文解释；决策说明体验、成本、时间和风险。
