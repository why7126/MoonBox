---
bug_id: BUG-0018-standalone-change-acceptance-source-unverified
title: 独立 Change 卡片误报验收来源待核实
created_at: 2026-09-14 10:23:16
updated_at: 2026-09-14 15:40:08
owner: 产品团队
severity: medium
---

# 根因分析

## 根因状态

status: confirmed

## 现象

需求中心“验收中 / 测试与人工验收”分组内，独立 Change 卡片 `refresh-issue-index-after-archive-promotion` 展示“验收来源待核实：未找到交付验证记录”。后续 `enhance-workflow-sync-current-status-block` 也出现同类提示。该提示与目标 Change trace 中已存在的验证摘要或 Validation Log 不一致。

## 证据链

| id | type | source | 摘要 | 支持的判断 |
|---|---|---|---|---|
| E1 | screenshot | `issues/bugs/review/BUG-0018-standalone-change-acceptance-source-unverified/screenshots/user-evidence-acceptance-source-unverified.png` | 用户截图显示 `refresh-issue-index-after-archive-promotion` 卡片在验收中阶段展示“未找到交付验证记录”。 | 证明实际页面存在误报现象。 |
| E2 | data_sample | `openspec/archive/2026-09-14-refresh-issue-index-after-archive-promotion/trace.md:25` | 目标 Change trace 存在非空 `## 验证摘要` 章节，并列出 pytest、OpenSpec、Sprint scope、Workflow Sync 等验证记录。 | 证明目标 Change 有交付验证摘要，不应被简单判定为“未找到”。 |
| E3 | code_path | `src/backend/app/governance/change_index.py:236` | 验收来源识别只接受 `验证记录`、`验收记录`、`验收结果`、`验证结果` 四类章节标题，未覆盖 `验证摘要`。 | 证明当前识别逻辑会漏掉目标 trace 的验证摘要标题。 |
| E4 | test_failure | `src/backend/tests/test_change_visibility.py:273` | 现有测试覆盖 `验证记录`、`verification.md` 与显式引用边界，但未覆盖 `验证摘要`。 | 证明回归测试对白名单标题变体覆盖不足，允许该漏判存续。 |
| E5 | screenshot | 用户 2026-09-14 后续截图 | `enhance-workflow-sync-current-status-block` 卡片展示“验收来源待核实：未找到交付验证记录”。 | 证明同类误报影响新的独立 Change。 |
| E6 | data_sample | `openspec/archive/2026-09-14-enhance-workflow-sync-current-status-block/trace.md:37` | 目标 Change trace 存在非空 `## Validation Log` 章节，并列出 pytest、py_compile、OpenSpec、Sprint scope、Workflow Sync 等验证记录。 | 证明英文验证日志章节同样会被当前白名单漏判。 |

## 已排除假设

| 假设 | 排除证据 |
|---|---|
| 目标 Change 完全没有验证记录 | E2 与 E6 显示目标 Change trace 存在非空 `## 验证摘要` 或 `## Validation Log`，包含多条验证命令和结果。 |
| 这是 Issue `acceptance.md` 缺失导致的合理提示 | 已生效规格要求独立 Change 按自身交付证据定位验收来源，不套用 Issue 固定 `acceptance.md` 要求；E2 提供自身 trace 验证摘要。 |
| 仅为前端文案问题 | E3 显示后端验收来源识别逻辑存在标题白名单漏判，前端只是展示后端 `disabled_reason` 或阻塞提示。 |

## 已确认根因

独立 Change 验收来源识别逻辑对 trace 章节标题采用固定白名单，只接受 `验证记录`、`验收记录`、`验收结果`、`验证结果`，未接受项目中实际使用的 `验证摘要` 与 `Validation Log`。当目标 Change 没有 `acceptance.md` 或 `verification.md`，但 trace 中存在这些非白名单验证章节时，后端仍会返回“验收来源待核实：未找到交付验证记录”，导致需求中心卡片误报。

## 修复方向

- 扩展独立 Change trace 验收来源标题识别，至少覆盖 `验证摘要` 与 `Validation Log`；可同时评估是否纳入 `实施与验证记录` 等项目已有表达。
- 增加后端回归测试：构造已完成独立 Change，trace 中仅含非空 `## 验证摘要` 或 `## Validation Log`，期望 `action.disabled_reason` 为空。
- 保留安全边界：证据存在只表示找到验收来源，不等于自动判定验收通过；显式 `acceptance_refs` 无效、越界、缺失或空文件仍应返回具体待核实原因。

## 验证闭环

- 后端单元测试覆盖 `验证摘要` 与 `Validation Log` 标题。
- 需求中心上下文中，`refresh-issue-index-after-archive-promotion`、`enhance-workflow-sync-current-status-block` 或等价合成独立 Change 不再展示“未找到交付验证记录”。
- 对无验收来源的独立 Change 仍展示待核实提示，避免误放行。
