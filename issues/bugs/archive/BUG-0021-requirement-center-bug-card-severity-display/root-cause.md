---
bug_id: BUG-0021-requirement-center-bug-card-severity-display
title: 需求中心 BUG 卡片显示优先级 P 值而非严重性
status: confirmed
created_at: 2026-09-14 14:01:07
updated_at: 2026-09-14 14:01:07
severity: medium
---

# 根因分析

## 根因状态

status: confirmed

## 现象

需求中心 BUG 类型卡片显示 REQ 优先级格式 `P2`，而不是 BUG 严重性 `severity`。用户截图中的 BUG-0020 卡片显示 `P2`；但 BUG-0020 的 `trace.md`、`bug.md` 和 `issues/bugs/_registry.yaml` 均记录 `severity: medium`。

## 证据链

| id | type | source | 摘要 | 支持的判断 |
|---|---|---|---|---|
| E1 | screenshot | 用户截图 | BUG-0020 卡片元信息标签显示 `P2` | 证明实际 UI 展示为优先级 P 值 |
| E2 | data_sample | `issues/bugs/archive/BUG-0020-req-complete-status-projection-drift/trace.md`、`bug.md`、`issues/bugs/_registry.yaml` | BUG-0020 分级事实源均为 `severity: medium` | 证明事实源不是 `priority: P2`，展示与事实源不一致 |
| E3 | code_path | `rules/document-governance.md:250` | 规则明确 REQ 使用 `priority`，BUG 使用 `severity`，不得互相映射或把 BUG 严重度称为优先级 | 证明当前展示违反分级契约 |
| E4 | code_path | `src/backend/app/schemas/requirement_center.py:36-43` | `RequirementCenterIssue` 响应模型只有 `priority: str = "P2"`，没有 `severity` 字段 | 证明 API 卡片模型无法表达 BUG 严重性 |
| E5 | code_path | `src/backend/app/services/requirement_center.py:161-166` | 后端构卡统一写入 `priority=str(entry.get("priority") or "P2")` | 证明 BUG 缺少 `priority` 时会被默认投影为 `P2` |
| E6 | code_path | `src/web/src/pages/catalog/RequirementCenterPage.tsx:75-83`、`2402-2403` | 前端 `IssueCard` 类型只定义 `priority`，卡片标签只渲染 `issue.priority` | 证明前端只会展示优先级字段 |
| E7 | code_path | `src/web/src/requirement-center.test.tsx:333-356` | 测试 fixture 中 BUG 样本仍传 `priority: "P1"` | 证明现有测试固化了 BUG 使用优先级字段的错误契约 |

## 已排除假设

| 假设 | 排除证据 |
|---|---|
| BUG-0020 事实源本身记录了 `priority: P2` | E2 显示 BUG-0020 当前 trace、主文档和 registry 均为 `severity: medium` |
| 只是前端样式文案问题 | E4、E5、E6 显示后端响应模型、构卡逻辑和前端类型/渲染均围绕 `priority`，不是单纯 CSS 或文案问题 |
| Capture 创建阶段没有区分 REQ/BUG 分级字段 | 现有 Capture 表单与后端创建契约已经区分 `priority` / `severity`；问题发生在需求中心卡片投影与展示链路 |

## 已确认根因

需求中心卡片数据模型和展示链路沿用了 REQ 的 `priority` 字段作为通用分级字段：后端 `RequirementCenterIssue` schema 没有 `severity`，构卡函数对所有 Issue 统一读取 `entry.priority` 并在缺失时默认 `P2`，前端 `IssueCard` 类型与卡片标签渲染也只消费 `issue.priority`。因此 BUG 类型即使事实源保存的是 `severity: medium`，也会在卡片中被投影并展示为优先级 P 值。

## 修复方向

1. 后端 `RequirementCenterIssue` 增加或等价暴露 BUG `severity` 字段，并按 Issue 类型分别从 registry / trace 读取分级。
2. 后端构卡逻辑保持 REQ 输出 `priority`，BUG 输出 `severity`，避免对 BUG 默认填充 `P2`。
3. 前端 `IssueCard` 类型和卡片标签渲染按 `issue.type` 分流：REQ 显示 P0-P3，BUG 显示 `blocker|critical|high|medium|low` 或产品确认的中文映射。
4. 更新前端 fixture、后端 API 测试和回归测试，覆盖 REQ/BUG 分级字段不混用。

## 验证闭环

- 根因门禁：`python scripts/validate-root-cause-evidence.py --bug BUG-0021-requirement-center-bug-card-severity-display`。
- 后续修复验证：后端 API 响应中 BUG-0021 或等价 BUG 卡片提供 `severity: medium` 且不提供错误的 `priority: P2`。
- 前端验证：BUG 卡片显示严重性，REQ 卡片仍显示 P0-P3。
- 回归测试：覆盖现有九阶段卡片 fixture、BUG 卡片分级标签、独立 Change 卡片不受影响。
