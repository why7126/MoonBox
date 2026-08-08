---
name: "initialize-project"
description: "根据 project.yaml 完成项目基础设施（DS / API / Test / Docker / Sprint-000）"
---

# initialize-project

Use this skill when the user asks to run the migrated source command `initialize-project`.

## Context Budget Guardrails（MUST）

### Force-proceed Follow-up Guardrails（MUST）

- `force-proceed` 仅允许继续当前命令的非阻断部分，MUST NOT 默认自动创建 follow-up REQ/BUG；除非用户在当前命令中明确授权自动 capture，否则只输出标准 capture 文案，并明确“未自动创建 Issue”。
- 标准 capture 文案 MUST 分条包含：建议命令、类型倾向、标题、背景、影响范围、建议验收或复现要点、来源 Change/Sprint/命令；多个 follow-up 事项 MUST 逐条输出，且每条可独立用于后续 capture。
- 如用户明确授权并实际创建 follow-up Issue，MUST 按 `/req-capture`、`/bug-capture` 或 `/capture` 规则落盘，并运行对应 `req.capture` 或 `bug.capture` Workflow Sync。

- MUST 遵守 `rules/agent-context-budget.md`；同一会话已读且无变更的规则和 Skill 用摘要承接，不重复全量读取。
- 检索先定位再分段读取；大范围 `rg/find` 默认排除 Harness、模板 assets、历史 agent 目录、archive、generated、node_modules、dist、coverage。
- 命令输出优先 `max_output_tokens <= 8000`；大 diff、OpenAPI/Orval 生成物、测试日志、Workflow Sync 输出先给摘要或命中数。


## Command Template

根据 `project.yaml` 与 `rules/*` 完成**一次性**基础设施建设。与业务需求流分离：治理类能力登记为 `REQ-0000-*`，经 **`req-*` → `req-opsx` → `opsx-apply` → `sprint-archive`** 闭环。

**Input**：无，或 `--step design-system|api|test|docker|sprint` 只跑子步骤

**禁止**：跳过 OpenSpec CLI 手写 `openspec/changes/`；业务 REQ 不得用本命令代替 `/req-capture`。

---

## 必须读取

```text
AGENTS.md
openspec/project.md
project.yaml
rules/*
docs/02-deployment.md
```

---

## 前置关系

```text
/initialize-project
    ├─ /build-design-system      → REQ-0000-build-design-system
    ├─ /build-api-standard       → REQ-0000-build-api-standard
    ├─ /build-test-framework     → REQ-0000-build-test-standard
    ├─ Docker / .env.example
    └─ /sprint-propose sprint-000   （登记已交付治理迭代）
```

已归档能力见 `openspec/specs/`（`design-system`、`api-governance`、`testing`）。**扩展**治理规范须新建 REQ + `/req-opsx`，不得直接改本命令重复建仓。

---

## Step 1 — Design System

执行 **`/build-design-system`**（或 `--step design-system`）。

产出：`src/shared/design-system/`、`src/web` 样式与校验脚本、`/design-system` 预览。

---

## Step 2 — API Standard

执行 **`/build-api-standard`**（或 `--step api`）。

产出：`docs/standards/api-governance.md`、`error-codes`、后端分层模板、`validate-api-standard.py`。

---

## Step 3 — Database Standard

读 `rules/database.md`；生成/核对：

```text
src/backend/app/models/
src/backend/app/repositories/
src/backend/app/db/schema.sql
docs/04-database-design.md
```

（无独立 change；随业务 REQ 的 `req-opsx` 演进 schema。）

---

## Step 4 — Test Framework

执行 **`/build-test-framework`**（或 `--step test`）。

产出：`tests/`、`pytest.ini`、Vitest 基线、`validate-test-framework.py`、CI workflow。

---

## Step 5 — Docker 基线

读 `project.yaml`、`docs/02-deployment.md`；核对：

```text
docker-compose.yml
src/backend/Dockerfile
src/web/Dockerfile
.env.example
scripts/docker-up.sh
scripts/docker-down.sh
```

---

## Step 6 — Sprint-000 与 REQ-0000 登记

若 `iterations/archive/sprint-000/` 不存在：

1. **`/sprint-propose sprint-000`** — 纳入（须已 **approved** 或治理 REQ 标记 `done`）：
   - `REQ-0000-build-design-system`
   - `REQ-0000-build-api-standard`
   - `REQ-0000-build-test-standard`
2. 各 REQ 若缺 `review.md`：补评审记录，`status: approved` 或 `done`
3. Change 已归档则 `sprint.yaml` 的 `changes[]` 指向 archive 状态；`sprint.md` 标 **completed**

若 REQ-0000 目录不存在：

```text
/req-capture → /req-generate → /req-complete → /req-review --approve
/req-opsx REQ-0000-build-*
/opsx-apply → /opsx-archive
```

---

## 验收

```text
□ validate-design-system.py 可运行
□ validate-api-standard.py 可运行
□ validate-test-framework.py 可运行
□ docker compose config 通过
□ iterations/archive/sprint-000 四件套存在
□ openspec/specs 含 design-system、api-governance、testing
```

## Next

业务需求走 **`/req-capture`** … **`/sprint-propose sprint-001`**，勿再调用本命令。
## Output Contract（MUST）

- 输出必须包含「下一步」和「待用户决策/处理」两类信息；没有对应事项时写「无」。
- 「下一步」只列可直接执行的命令或验证动作；「待用户决策/处理」只列需要用户选择、授权、提供资料或确认风险的事项。
- 同一事项不得在「下一步」与「待用户决策/处理」中重复；不得重复输出等价事项。

