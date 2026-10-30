---
title: 独立 Change 归档按钮禁用且缺少验收检查入口根因分析
created_at: '2026-10-30 09:48:10'
updated_at: '2026-10-30 09:48:10'
---

# 独立 Change 归档按钮禁用且缺少验收检查入口根因分析

## 根因状态

status: confirmed

## 现象

独立 Change 归档按钮禁用且缺少验收检查入口；详见 bug.md 的复现步骤。

## 证据链

| id | type | source | 摘要 |
|---|---|---|---|
| E1 | reproduction | `capture.md 同会话 Firefox 刷新观察` | 2026-10-30 09:33:58，验收卡片按钮disabled，提示验收待检查，卡片无对象检查入口。 |
| E2 | code_path | `src/web/src/pages/catalog/RequirementCenterPage.tsx loadContext` | 请求context?view=summary，刷新仍使用摘要。 |
| E3 | code_path | `src/backend/app/governance/reader.py ProjectReader._call` | summary+acceptance 设置 checks_deferred，并覆写动作 disabled_reason 为验收待检查。 |
| E4 | code_path | `src/backend/app/governance/change_index.py acceptance_source_reason` | 摘要模式直接返回验收待检查，不运行完整证据判断。 |
| E5 | code_path | `src/web/src/pages/catalog/RequirementCenterPage.tsx renderIssueCard/openIssueDetail` | 隐藏待检查提示正文；tip禁用按钮，独立Change标题只打开文档。 |

## 已排除假设

| 假设 | 排除证据 |
|---|---|
| 缺少Sprint | 本样本有sprint-016，实际禁用提示是验收待检查 |
| 研发7/7即可归档 | 任务完成不等于验收和归档门禁通过 |
| BUG-0054的blocked文案原样复发 | 本次为尚未执行检查的摘要状态，历史问题为检查结果诊断丢失 |

## 已确认根因

已确认摘要延后检查策略与前端交互没有形成闭环：后端将待检查投影为禁用，前端隐藏解释且卡片无触发真实对象检查的路径。反复刷新仍摘要加载，不能退出待检查态。这里确认操作断点，不把历史passed报告当成当前归档ready。

## 修复方向

保持首屏摘要策略，增加卡片级只读验收条件检查，区分待检查/检查中/通过/阻塞/失败并支持重试；按项目、对象、版本绑定结果，写入前再次服务端准入。不得把检查入口当作运行验收计划命令或自动归档的入口。

## 验证闭环

用户授权复用同会话探索证据；本轮补齐可复核源码链，不重新宣称浏览器验收。当前没有修复实现或修复后通过证据。后续按 acceptance.md 执行合成复现、正反例回归和真实浏览器观察，分别记录；文档根因校验仅验证证据结构。
