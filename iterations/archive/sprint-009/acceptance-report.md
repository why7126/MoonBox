---
note: workflow-sync — 20/20 Change 已 archive；0 applied；待人工 sign-off
sprint_id: sprint-009
title: 本地数据边界与快照轮转迭代验收报告
status: completed
lifecycle_stage: archive
created_at: '2026-10-08 14:40:30'
updated_at: 2026-10-17 17:01:21
---

# 本地数据边界与快照轮转迭代验收报告

## 验收状态

通过；2026-10-17 用户确认 Sprint 总体验收通过。REQ-0043 Change 与 Issue 已归档，真实 Chat Worker、快照轮转、重启、离线恢复及隔离真实 Chat 会话执行验证完成，AC-001 至 AC-019 的实施证据已回填；Sprint 总体验收已签认。

## Scope 验收

| 范围项 | 状态 | 验收入口 |
|---|---|---|
| REQ-0043-unify-data-mount-and-snapshot-rotation | Change 与 Issue 已归档；Sprint 总体验收通过 | `issues/requirements/archive/REQ-0043-unify-data-mount-and-snapshot-rotation/acceptance.md`、`openspec/archive/2026-10-08-add-local-data-mount-and-snapshot-rotation/trace.md` |

## 验收计划

- [x] 数据目录与本地挂载边界符合 REQ-0043 验收条件。
- [x] 自动快照上限默认 2、正整数按上限轮转、0 不创建自动快照；手工备份和删除账本保留。
- [x] 旧快照迁移与清理保护引用中的证据，异常可恢复且不丢数据。
- [x] SQLite/MySQL、部署文档、任务链路观测和相关验证闭环。

## 本轮追加缺陷验收

| 范围项 | 状态 | 验收入口 |
|---|---|---|
| BUG-0030-chat-assistant-output-missing-from-conversation | Change 与 Issue 已归档；Sprint 总体验收通过 | `issues/bugs/archive/BUG-0030-chat-assistant-output-missing-from-conversation/acceptance.md`、`openspec/archive/2026-10-09-fix-chat-assistant-output-missing-from-conversation/trace.md` |
| BUG-0035-requirement-center-acceptance-readiness-projection | 11/11 验收通过；Change 与 Issue 已归档，Sprint 总体验收仍单独判断 | `issues/bugs/archive/BUG-0035-requirement-center-acceptance-readiness-projection/acceptance.md`、`openspec/archive/2026-10-13-fix-requirement-center-acceptance-readiness-projection/trace.md` |

- [x] AC-001至AC-009：停止、未知、恢复、幂等、正常对照、无输出、分页、替代证据、权限与脱敏。
- [x] 合成回归与真实页面观察分别留证；原轮次数据已删除，不认定历史根因已确认。
- [x] BUG-0035 AC-001 至 AC-011：验收事实与卡片进度一致，未完成验收时归档门禁和提示一致；Issue、Change、Sprint 已生成 MD 在后续阶段持续可达且遵守权限与分组。
- [x] BUG-0035：后端/前端回归与真实产品观察分别留证，并核对 1440px、390px 视觉表现；Change 创建后回填实现及验收入口。

BUG-0035 实施取证已完成：`data/visual-evidence/BUG-0035-requirement-center-acceptance-readiness-projection/` 保存桌面、移动卡片和验收文档抽屉截图；Change `trace.md` 记录 computed style、selector、真实 BUG-0025 投影及 4 项权限负向回归。以上是实施验证，Sprint 验收勾选仍等待逐项签认。

BUG-0035 验收返修批次一：卡片来源改为 Issue、Change、Sprint 三组，Sprint 组的 `sprint.md`、`release-note.md`、`acceptance-report.md` 已核对存在性、只读与授权读取；Change trace 按 `trace.md` 显示。Issue `acceptance.md` 的 AC 由验收人依据证据逐项勾选并回填通过结论，未勾选或结论 pending 时继续阻断归档；此处仍待产品侧复验签认。

BUG-0035 验收返修批次二：验收中卡片的测试进度后显示“人工验收 已勾选 AC 数/AC 总数”，点击打开所属 Issue `acceptance.md`；进度取自 Issue AC，研发与测试任务仍取自 Change `tasks.md`。未勾选 AC 的重复红色阻断文案合并，服务端归档门禁及全部勾选后仍待签认的提示保持有效。后端 102 项、前端 117 项聚焦回归与双视口产品观察见 Change `acceptance-fixes.md`，人工签认未代办。

BUG-0035 验收返修批次三：三个进度中已知且未完成的数字使用危险色，标签与已完成数字保持常规色；未知总数不显示虚假未完成。视觉对照与验证记录见 Change `acceptance-fixes.md`，人工签认仍待产品侧完成。

BUG-0035 验收返修批次四：研发与测试进度点击入口对齐关联 Change `tasks.md`，分别定位研发与自动化测试章节；Issue 自身不含 `tasks.md` 时仍可打开右侧抽屉。多 Change 来源不唯一时不借用其他 Change 文档。前端 119 项测试通过，真实页面双视口复测记录见 Change `acceptance-fixes.md`，人工签认仍待产品侧完成。

BUG-0035 验收返修批次五：卡片第三个进度名称改为“验收”，数字仍由 Issue `acceptance.md` 中已勾选 AC/总 AC 得出，点击仍打开该文档；悬浮说明自动验收结果尚未计入。验收结论与归档门禁不变，前端验证及真实页面观察见 Change `acceptance-fixes.md`，人工签认仍待产品侧完成。

BUG-0035 验收返修批次六：四份未归档的表格 AC 文档已补同编号未勾选清单，保留表格证据和原验收状态；无测试任务分母的验收中卡片独立展示验收进度。BUG-0033 原先提示“验收结论待核实”，文档迁移后解析为 0/11；真实页面刷新发现测试分母依赖并纳入前端修复。实施与回归见 Change `acceptance-fixes.md`，验收签认仍待逐项复核。

product_data_collection_observability：applicable；affected_layers：DB、chat_messages、execution_events、request_logs、task_traces、task_trace_spans、Web、治理上下文 API、授权文档读取 API；validation：BUG-0030 的消息链路和 BUG-0035 的验收投影、文档权限、双视口与真实产品观察待执行，仅保留脱敏状态、计数和请求关联，不保存文档正文或凭证。新增 usage_events、DB schema、客户端请求封装和请求协议目前为 N/A，Change 定案时复核。

BUG-0035 2026-10-11 逐项技术复验：Codex 已在 linked Issue `acceptance.md` 勾选 AC-001～008、AC-011，并逐项记录预期/实际、响应摘要、证据入口与签认身份。本轮后端 88 项、前端 120 项聚焦回归通过，Firefox 实际卡片与测试结果分开记录。AC-009 尚缺全阶段双视口真实视觉矩阵，AC-010 尚缺当前 BUG-0025 Chat 归档阻断响应；两项未勾选，Sprint 此聚合验收项保持未完成，Change 不可 archive。历史“人工签认未代办”段落属于各实施批次当时状态，以本段为本轮最新结论。

BUG-0035 2026-10-12 `/opsx-accept`：证据包 `openspec/archive/2026-10-13-fix-requirement-center-acceptance-readiness-projection/evidence/acceptance/20261012154349001165-323fcebd/` 记录 9 passed、AC-009 因全阶段双视口视觉矩阵缺失为 failed、AC-010 因未取得获授权的当前 BUG-0025 Chat 归档轮次为 blocked。既有 9 项技术签认不变，最终验收 pending；不能归档。旧 Chat 阻断回复只作历史背景，当前需求中心卡片和自动化分别留证。

BUG-0035 授权补证：隔离环境三个临时 BUG 对象覆盖迭代规划、待开发、研发中阶段，文档分组由 Firefox 页面核对；完整双视口截图及 computed style 未取得，AC-009 仍未签认。正式 BUG-0025 Chat 归档已尝试，但任务 80/81 与规格合并校验先于验收门禁阻断，不能证明验收门禁，AC-010 仍未签认。新证据包 `openspec/archive/2026-10-13-fix-requirement-center-acceptance-readiness-projection/evidence/acceptance/20261012162428424904-79c14fde/` 为 9 passed、2 failed，Sprint 聚合验收保持 pending。

BUG-0035 后续阶段视觉补证：Firefox 在 1440×900 与 390×900 取得七个 Issue 阶段及独立 Change 共 16 张完整截图，矩阵见当前 Change `evidence/acceptance/phase-matrix-1440-390.md`。AC-009 已技术签认；最新自动验收 `20261012164826724067-559511d7` 为 10 passed、AC-010 failed。前段“截图未取得”是首次尝试的历史状态；BUG-0025 正式归档未触达验收门禁，故 Sprint 聚合验收仍 pending。

BUG-0034 2026-10-13 验收返修：隔离产品 `source` 工作区的纯治理 Change 首次归档轮次完成，目标命令退出码 0，事实源仅保留唯一 canonical archive；归档续接的 Issue 验收门禁缺口已修复，产品 `--finalize` 轮次完成且 Workflow Sync 0 errors。逐项脱敏证据见 `openspec/archive/2026-10-13-fix-chat-standalone-archive-scope-tool-path/evidence/acceptance/samples/AC-005.md`；Sprint 整体关闭仍以其他范围项门禁为准。

BUG-0035 AC-010 后续复验：BUG-0025 的 AF-041 与 delta 规格合并问题已修复；正式关联 Chat 同轮归档命令返回 `ACCEPTANCE_GATE_BLOCKED`、退出码 1，BUG-0025 仍为 24/52 且未归档。BUG-0035 完整增量验收包 `20261012174521381442-836220d3` 为 11/11 passed，`--readiness` ready，Workflow Sync 将其 Issue 验收同步为 passed；Change 保持 applied，Sprint 是否可关闭仍以全迭代门禁为准。此前 10/11 记录为历史状态。

BUG-0035 验收返修批次七：用户截图确认验收卡片已列出 Change 的四份计划文档却同时提示缺少。Web 已修正验收阶段的缺文档来源判断并补正反向回归；此前 11/11 ready 结论须按变更输入指纹增量复验，不能仅凭旧证据包直接归档。详细对照与验证见 Change `acceptance-fixes.md`。

本批次增量复验：最终证据包 `openspec/archive/2026-10-13-fix-requirement-center-acceptance-readiness-projection/evidence/acceptance/20261013082531057132-a6e693ef/` 为 11/11 passed，readiness ready、stale 为空；Workflow Sync `opsx.accept` 将 linked Issue 验收同步为 passed。合成 API 双视口预览确认误报消失；2026-10-13 08:24:00 常驻 Firefox 刷新后，BUG-0035 卡片无 Change 文档缺失误报，`proposal.md` 抽屉读取成功，见归档 Change 返修台账。2026-10-13 `/opsx-archive` 已完成 Change 规格合并、归档与 Issue 迁移；Sprint 整体验收仍以各范围项为准。

## Sprint 关闭签认

2026-10-17 16:53:49，用户确认 Sprint 总体验收通过并授权关闭。`sprint.archive` Workflow Sync 因归档 Change 的 AC-005 样本状态值不符合当前 schema 而失败；受控兼容 Change 已归档，`sprint.archive` 同步完成后关闭生效。AI 用量本地自动发现无可归属会话，使用 estimated_fallback。

2026-10-17 17:00:07 关闭复核：20/20 Change 已归档、152/152 任务完成；归档就绪、Issue 子文档、环境文件忽略策略与陈旧扫描均通过，用户总体验收签认继续有效。历史 AC-005 兼容修复见 `openspec/archive/2026-10-17-accept-legacy-archive-sample-status/trace.md`。
