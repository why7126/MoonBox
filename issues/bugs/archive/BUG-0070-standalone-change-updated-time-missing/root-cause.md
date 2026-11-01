---
title: 独立 Change 卡片更新时间缺失根因分析
created_at: '2026-10-30 09:48:10'
updated_at: "2026-10-31 22:56:40"
---

# 独立 Change 卡片更新时间缺失根因分析

## 根因状态

status: confirmed

## 现象

独立 Change 卡片更新时间缺失；详见 bug.md 的复现步骤。

## 证据链

| id | type | source | 摘要 |
|---|---|---|---|
| E1 | data_sample | `openspec/archive/2026-10-30-fix-archive-finalization-consistency/trace.md` | 源 trace 缺 created_at/updated_at，但 execution 时间存在。导航随 Change 归档更新，保留采证时的事实结论。 |
| E2 | code_path | `src/backend/app/governance/change_index.py cards` | 仅用 updated_at 或 created_at 投影卡片时间，没有执行时间回退。 |
| E3 | code_path | `src/web/src/pages/catalog/RequirementCenterPage.tsx rc-updated` | 投影不满足显示格式时显示更新时间未知。 |
| E4 | code_path | `scripts/workflow_sync/execution.py transition` | 执行事实更新时仅用正则替换已存在 updated_at，不插入缺字段；applied/archived 可提前返回，不能据此补时间。 |
| E5 | reproduction | `capture.md 同会话 Firefox 刷新观察` | 2026-10-30 09:33:58，/requirements 目标卡片仍显示未知；截图为会话附件，未落盘为新附件。 |

## 已排除假设

| 假设 | 排除证据 |
|---|---|
| 时区偏移 | 源字段不存在，未进入合法时间转换；不是本样本根因 |
| 优先级为空导致时间缺失 | cards 中两个字段独立读取 |
| 任务未完成导致未知 | 任务7/7且execution完成时间存在，显示仍只依赖两个顶层字段 |

## 已确认根因

已确认数据缺失与读取契约不完整：源文件缺少卡片需要的时间，执行状态同步不补缺字段，投影只能返回空值。这个分支足以解释为何有执行完成时间却仍显示未知。最初由谁或哪个创建入口漏写无法从现有证据归责，不扩大为已确认历史原因。

## 修复方向

规范化新建及有效变更时的业务时间维护；同步时补缺字段策略需有真实来源，不伪造历史 created_at。旧数据若只有执行完成时间，应明确标注“执行完成于”或“更新时间未记录”，不能把它冒充最后更新时间。保留首次执行完成事实、原创建时间及幂等无变更不更新时间语义。

## 验证闭环

用户授权复用同会话探索证据；本轮补齐可复核源码链，不重新宣称浏览器验收。修复已按 acceptance.md 完成合成回归、真实浏览器刷新与四组合视觉验证；实现与当前证据见关联 Change verification.md。历史 E1–E5 保留为故障事实，文档根因校验仅验证证据结构。
