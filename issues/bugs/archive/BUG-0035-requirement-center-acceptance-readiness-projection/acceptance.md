---
bug_id: BUG-0035-requirement-center-acceptance-readiness-projection
title: 需求中心验收状态与文档持续展示修复验收标准
acceptance_status: passed
created_at: 2026-10-09 22:41:00
updated_at: 2026-10-17 17:01:21
owner: 产品团队
---

# 需求中心验收状态与文档持续展示修复验收标准

## 回归 AC

- [x] AC-001：研发与测试进度继续按当前 Change `tasks.md` 的对应任务分类统计，返修追加任务进入正确分母；点击研发或测试进度均通过右侧抽屉打开该 Change 的 `tasks.md` 并定位对应章节。Issue 与 Change 文档分组后不得因 Issue 自身没有 `tasks.md` 而使入口失效；关联多个 Change 且无法确定当前来源时不得猜测或借用其他 Change 文档。任务满格不自动代表验收通过。
- [x] AC-002：验收标准、执行结果、人工复验和证据缺口形成独立验收状态；BUG-0025 类样本存在待复验项时，卡片在测试后以“验收 已勾选 AC 数/AC 总数”紧凑显示，点击打开所属 Issue `acceptance.md`，不将 AC 算入 Change `tasks.md` 的研发或测试任务分母。悬浮说明须明确当前数字依据 Issue AC 勾选，自动验收结果尚未计入；已完成的 AC 须依据逐项证据勾选，不得仅凭任务满格代勾。
- [x] AC-003：验收事实变化或刷新后，验收进度与实际归档门禁保持一致；研发、测试、验收任一已知总数且未完成时，仅对应进度数字使用危险色，标签与已完成数字保持常规色，未知总数不误标为未完成。未勾选 AC 时不重复渲染两条相同红色阻断文案，进度按钮可直达 Issue 验收文档，服务端仍独立拒绝归档。所有 AC 已勾选但 `acceptance_status` 仍为 pending 时继续显示待签认，归档前由验收人回填结论与证据。
- [x] AC-004：已生成且可读取的 Issue 治理 MD 从生成阶段起在所有后续阶段持续可达；覆盖 BUG 的 capture、bug、root-cause、workaround、acceptance、review、trace，以及 REQ 对应文档。
- [x] AC-005：关联 Change 后，卡片分为 Issue、Change、Sprint 三组；Issue 组按 BUG/REQ 展示各自主文档及 `trace.md`，Change 组展示当前 Change 已生成文档且 `trace.md` 按文件名显示，Sprint 组展示实际存在的 `sprint.md`、`release-note.md`、`acceptance-report.md`；纯 Change 卡片无 Issue 组。各组在后续阶段持续可达，Sprint 文档不混入 Issue 或 Change 组。验收中卡片不得把 Change 组已显示的 `proposal.md`、`spec.md`、`design.md`、`tasks.md` 再提示为缺失。
- [x] AC-006：Issue 与 Change 出现同名 `trace.md` 等文档时，卡片以组名标注来源并打开各自正确内容；Issue trace 缺失时不借用 Change trace 冒充，Change 组按钮无需重复显示“Change”前缀。
- [x] AC-007：文档不存在、已移动、归档身份不唯一或用户无读取权限时，不显示虚假可读入口或跨对象内容，并给出安全的不可用说明。
- [x] AC-008：已归档对象的已生成 MD 保持可读且只读；修复不扩大阶段编辑、任务勾选、对象授权或跨项目可见范围。
- [x] AC-009：待评审、已评审、Sprint 规划、待开发、研发中、验收中、完成各阶段的 REQ/BUG 卡片，以及独立 Change 卡片，验证三类文档入口、较多文档时的布局与关键交互；记录 1440px 和移动端视觉证据及相关 computed style。
- [x] AC-010：后端文档聚合与权限、前端阶段展示及归档阻断提示均有聚焦回归；自动化结果与真实产品观察分开记录，BUG-0025 样本的 Chat 归档仍在缺证据时被阻断。同轮 Chat `9bffe2e8-bb23-4559-b132-b4feb6856ef6` 的归档脚本退出 1 且返回 `ACCEPTANCE_GATE_BLOCKED`，Change 保持 active；自动验收 AC-010 passed。
- [x] AC-011：未归档 Issue 的表格 AC 按编号迁为独立复选框并保留表格证据，迁移不代签；有验收 AC 而无测试任务分母的验收中卡片仍显示可点击的“验收 已勾选数/总数”，未签认时继续阻断归档。覆盖 BUG-0029、0033、0034 的卡片回归及 BUG-0028 的未来验收入口。

## 验收记录要求

本文件定义人工验收标准，当前未给出最终验收结论。每项通过前记录部署版本、角色、对象类型、阶段、文档来源、预期与实际、响应摘要及脱敏证据入口；UI 项记录视口、选择器、截图与关键 computed style。涉及验收状态的项同时对照服务端归档门禁，不以卡片文案或合成测试单独宣布通过。

返修批次一补充：验收人完成每项 AC 的复核后，依据证据将本文件对应 `- [ ]` 改为 `- [x]`，并在验收结果中回填通过结论、签认人、时间和证据入口。未复核、失败或缺证据的 AC 保持未勾选；本次返修执行不代签 AC-001 至 AC-010，也不改变验收阶段的页面写权限。

## 实施取证进展

- 自动化：后端需求中心聚焦测试 79 项通过，前端需求中心 116 项通过；OpenSpec 严格、中文和标题校验通过。
- 本地标准部署：`self-storage-sqlite --chat-platform` 配对重启并全部健康。Firefox 观察到 BUG-0025 卡片研发 41/41、测试 37/37，同时显示验收待办 52 项且不提供归档入口；Issue 的 acceptance.md、Change 的 acceptance-fixes.md、Sprint 文档各有入口。
- 52 项来自当前 BUG-0025 `acceptance.md` 仍未勾选的 AC。Chat 归档复盘点名 AC-051/052 及交付证据缺口；其余 AC 尚未逐项回填结论，不能自动视为通过。
- Firefox 响应式模式保存了 `data/visual-evidence/BUG-0035-requirement-center-acceptance-readiness-projection/card-1440.png`、`card-390.png` 和 `acceptance-drawer-1440.png`。双视口卡片均显示 Issue/Change/Sprint 文档来源、52 项验收待办与任务进度；Issue acceptance.md 抽屉可读且当前阶段只读。卡片宽 300px，来源文档组与验收提示宽 264px；部署后的 390px 页面 `innerWidth` 和 `body.scrollWidth` 均为 390px。修复了 Web 入口缺少 viewport 元标签导致移动端按 980px 布局的问题。
- 权限负向聚焦回归 4 项通过：未登录 401、非法文档 400、无权读取与写入 403、归档身份冲突 404；合成权限断言与管理员真实页面观察分开记录。实施证据已完成，AC-001 至 AC-010 仍等待产品侧逐项验收签认。
- 返修批次二实施证据：后端 102 项、前端 117 项聚焦回归及 TypeScript 通过；Firefox 1440px/390px 的 BUG-0035 卡片显示“人工验收 0/10”，无重复验收红字，点击后打开只读 Issue `acceptance.md`。截图见 `data/visual-evidence/BUG-0035-requirement-center-acceptance-readiness-projection/modify2-card-1440.png`、`modify2-card-390.png`、`modify2-acceptance-drawer-390.png`。以上仍是实施验证，AC 勾选与最终验收结论等待产品侧签认。
- 返修批次三实施证据：前端需求中心 117 项与 TypeScript 通过；Firefox 实际页面 1440px/390px 均核对 BUG-0035 仅“人工验收 0/10”数字为红色，已完成的研发、测试数字仍为灰色，390px 页面无新增横向溢出。对照和 computed style 见当前 Change `acceptance-fixes.md`；AC 勾选与最终验收结论仍待产品侧签认。
- 返修批次四实施证据：研发与测试按钮改用关联 Change `tasks.md` 的真实读取入口；前端 119 项需求中心测试与 TypeScript 已通过。Firefox 双视口的真实点击与抽屉定位证据见当前 Change `acceptance-fixes.md`；本条仍待验收人复验签认。
- 返修批次五实施证据：卡片“验收 0/10”及口径说明在 Firefox 390px、1440px 视口可见，点击仍打开 Issue `acceptance.md`；前端 119 项测试与 TypeScript 通过。自动验收结果尚未计入当前数字，AC 勾选及最终验收结论仍待产品侧签认。

## 2026-10-11 逐项复验与签认

复验人：Codex（按用户本轮指令执行技术复验）；产品团队的最终验收结论尚未代签。部署：本地 `self-storage-sqlite --chat-platform`，Web v0.1.0；角色：平台超级管理员。对象：BUG/REQ Issue、关联或独立 Change、Sprint；实际观察以 BUG-0035、BUG-0033、BUG-0029、BUG-0034、BUG-0025 验收中卡片为主。证据分层：本轮 Firefox 实际页面 AX 观察，仓库内既有 1440px/390px 截图与 computed style 记录，以及本轮后端 88 项和前端 120 项聚焦回归；合成测试不充当真实产品观察。

| AC | 本轮结论 | 预期、实际与响应摘要 | 脱敏证据入口 / 缺口 |
|---|---|---|---|
| 001 | 技术复验通过，Codex 签认 | 研发/测试仍由关联 Change `tasks.md` 计数；BUG-0035 实际为 14/14、13/13，验收独立为 0/11。研发按钮实际打开 `BUG-0035 · tasks.md` 抽屉；测试章节定位与多 Change 歧义由聚焦回归覆盖。 | 本轮 Firefox `/requirements` AX；`src/web/src/requirement-center.test.tsx` 的任务抽屉及多 Change 用例；Change `acceptance-fixes.md` 批次四双视口观察。 |
| 002 | 技术复验通过，Codex 签认 | BUG-0025 实际为研发 41/41、测试 38/39、验收 18/52；BUG-0035 为 0/11。验收按钮的无障碍说明写明数字来自 Issue AC、自动验收未计入；抽屉目标与分母隔离由回归覆盖。 | 本轮 Firefox AX；前端验收进度与文档点击用例；后端 `test_acceptance_readiness_is_separate_from_task_progress`。 |
| 003 | 技术复验通过，Codex 签认 | 未完成验收数字使用危险色，任务满格不解锁归档；未勾选与全部勾选但结论 pending 均被服务端投影阻断。按钮可达文档，重复红字被前端回归排除。 | Change `acceptance-fixes.md` 批次二、三的双视口及 RGB computed style；本轮 Firefox 卡片；后端状态矩阵及前端阻断回归。真实归档命令本轮未执行，AC-010 单列待验。 |
| 004 | 技术复验通过，Codex 签认 | BUG-0035 实际保留 7 份 Issue 文档入口；已生成文档在后续阶段持续显示，REQ 和 BUG 的阶段矩阵由聚焦回归覆盖。 | 本轮 Firefox BUG-0035 AX；`test_generated_issue_documents_remain_issue_owned_after_change`、阶段/文档聚焦回归。 |
| 005 | 技术复验通过，Codex 签认 | BUG-0035 实际显示 Issue 7 份、Change 6 份、Sprint 3 份；Sprint 文档独立分组，Change `trace.md` 无前缀。纯 Change 的无 Issue 组由前端用例覆盖。 | 本轮 Firefox AX；`src/web/src/requirement-center.test.tsx` 文档分组用例；Change `acceptance-fixes.md` 批次一双视口截图。 |
| 006 | 技术复验通过，Codex 签认 | Issue 与 Change 各有 `trace.md` 独立入口，实际卡片按来源分组；缺失 Issue trace 不借用 Change 内容。 | 本轮 Firefox BUG-0035 AX；后端 `test_change_index_keeps_same_named_issue_and_change_documents`、`test_trace_always_targets_issue_in_every_stage`。 |
| 007 | 技术复验通过，Codex 签认 | 缺失、错误身份与越权读取在服务端保守拒绝；前端读取失败显示不可用，未跨对象回退。 | 本轮后端 `test_governance_board.py`、`test_governance_scope.py` 共 88 项；前端文档读取失败用例；Change trace 的未登录 401、非法文档 400、越权 403、身份冲突 404 实施取证。 |
| 008 | 技术复验通过，Codex 签认 | 归档文档可读、不可编辑或勾任务；项目隔离与对象授权未放宽。 | 后端 `test_archived_issue_and_sprint_do_not_reopen_or_block`、`test_sprint_documents_are_readonly_and_separate_from_issue_and_change`、`test_scope_document_and_no_cross_project_leak`。 |
| 009 | 待验收，未签认 | 自动化覆盖 9 阶段与文档状态，既有验收中卡片有 1440px/390px 截图、selector 与 computed style。尚缺待评审至完成各阶段的真实页面双视口逐项视觉矩阵，以及独立 Change 当前页面观察。 | `data/visual-evidence/BUG-0035-requirement-center-acceptance-readiness-projection/`；Change `acceptance-fixes.md`；需补完整阶段/视口矩阵。 |
| 010 | 待验收，未签认 | 本轮后端 88 项、前端 120 项通过，真实 BUG-0025 卡片显示验收 18/52，与自动化证据已分开。尚未在当前产品中执行并观察 BUG-0025 Chat 归档拒绝结果；历史截图不能替代本轮服务端响应。 | 本轮 Firefox AX；两组聚焦测试；需补当前 Chat 归档命令的脱敏阻断响应和时间。 |
| 011 | 技术复验通过，Codex 签认 | 四份未归档表格 AC 文档分别迁为 8、6、11、5 条同编号未勾选清单，原表格及状态保留；实际 BUG-0033 为验收 0/11 且无测试分母，BUG-0029、0034 也显示 0/6、0/5。无测试分母点击、未来入口和未签认阻断由回归覆盖。 | 本轮文档逐项计数、Firefox 卡片 AX；前端 `shows Issue acceptance progress when a card has no test task denominator`；后端验收状态矩阵。BUG-0028 尚未进入验收阶段，未来入口按合成回归验。 |

本轮前端首次运行受 Node 25 实验性 Web Storage 影响，120 项均在 `localStorage.clear` 初始化处失败；使用 `NODE_OPTIONS=--no-experimental-webstorage` 复跑后 120/120 通过，属于测试环境差异。Firefox 当前窗口在抽屉加载后切回另一 Chat 页面，因此本轮仅签认可由既有双视口证据与聚焦回归共同覆盖的项目，不把短暂加载状态记作文档正文成功读取。

本轮签认 9/11 项；AC-009、AC-010 保持未勾选，整体 `acceptance_status` 保持 `pending`，不满足 `/opsx-archive` 门禁。需要补齐上述真实产品证据后再回填最终结论。

## 2026-10-12 自动验收证据包

`/opsx-accept` 建立了与本文件 AC-001～011 一一对应的 `acceptance-plan.json`，在本地 MoonBox Web v0.1.0、Firefox 管理员会话下先观察当前卡片，再运行逐项检查。证据包：`openspec/archive/2026-10-13-fix-requirement-center-acceptance-readiness-projection/evidence/acceptance/20261012154349001165-323fcebd/manifest.json` 与同目录 `summary.md`。结果为 9 项 passed、1 项 failed（AC-009 缺全阶段 1440px/390px 视觉矩阵产物）、1 项 blocked（AC-010 缺获授权的当前 BUG-0025 Chat 归档轮次及可读产品数据源）。AC-009 的命令回归退出码为 0，失败仅指必需视觉证据缺失；不得表述为产品功能已证实失败。 当前可见阶段的只读盘点记录在 `openspec/archive/2026-10-13-fix-requirement-center-acceptance-readiness-projection/evidence/acceptance/phase-matrix-partial.md`；迭代规划、待开发、研发中暂无真实对象，未造正式对象补样本。

Firefox 当前刷新页面显示 BUG-0035 研发 14/14、测试 14/14、验收 9/11，Issue/Change/Sprint 三组入口仍在，且无归档动作；BUG-0025 显示 42/42、38/39、验收 24/52。Chat 历史先出现 504，恢复后只读查看到 2026-10-09 的 BUG-0025 归档阻断回复；它不是本轮归档响应。本轮没有执行正式 BUG-0025 首次归档，以免在门禁意外失效时推进其真实生命周期。

此前 Codex 技术签认的 9 项已由新计划命令检查再次通过，AC-009/010 仍未勾选；`acceptance_status: pending`，最终产品验收与归档就绪未达成。

## 2026-10-12 授权补证结果

用户授权在隔离环境建立可清理样本，并授权正式 BUG-0025 Chat 归档尝试。隔离样本 BUG-9101、BUG-9102、BUG-9103 分别投影到迭代规划、待开发、研发中；Firefox 页面确认三类文档分组与研发进度。响应式截图导出整窗且目标卡片被裁切，未取得完整双视口视觉矩阵和 computed style，AC-009 保持未勾选。

正式 BUG-0025 Chat 归档轮次 `f3d624c6-2422-4eee-9a49-3181af97d5fd` 已完成，但归档脚本退出码 1，先因任务 80/81 与规格合并校验失败停止，尚未触达验收证据门禁；Change/Issue 未归档。故不能以“归档未发生”替代“验收门禁已阻断”的证明，AC-010 保持未勾选。本轮自动验收包 `20261012162428424904-79c14fde` 为 9 passed、2 failed。脱敏观察见 Change `evidence/acceptance/isolation-stage-and-archive-observation.md`；总体 `acceptance_status: pending`，尚不可归档。

## 2026-10-12 阶段矩阵补证与技术签认

复验人：Codex；角色：隔离环境管理员；版本：当前本地 Web v0.1.0。Firefox 在 1440×900 与 390×900 两个视口，对待评审 BUG-0037、已评审 REQ-0045、隔离样本 BUG-9101/9102/9103、验收中 BUG-0035、完成 BUG-0026 及独立 Change 各保存完整卡片截图，共 16 张。隔离样本仅写入临时治理源及 SQLite；Issue、Change、Sprint 分组、文档密集布局和卡片点击已逐项记录。390px 布局与关键 computed style 沿用本 Change `acceptance-fixes.md` 中 Firefox 采样；本轮截图没有冒充新的样式采样。逐行对象、视口、选择器、观察与图片入口见 Change `evidence/acceptance/phase-matrix-1440-390.md`。据此 AC-009 技术复验通过并勾选；此前“截图缺失”的段落是补证前记录。

最新自动验收包 `evidence/acceptance/20261012164826724067-559511d7/summary.md` 为 10 passed、1 failed。AC-010 仍未勾选：正式 BUG-0025 Chat 归档先被其任务 80/81 与规格合并校验阻断，没有触达待验证的验收门禁。整体 `acceptance_status: pending`，不签署最终验收或归档就绪结论。

续验预检：`--readiness` 仅报告 AC-010 stale。其自动计划当前要求归档命令成功退出，而 AC-010 要验证的是缺证据时拒绝归档；两种判定相矛盾。BUG-0025 的 AF-041 未完成及规格合并问题也未消除。本次未重复执行正式归档，AC-010 保持未签认；详见 Change `trace.md` 的 AC-010 续验预检。

## 2026-10-12 AC-010 负向门禁复验

BUG-0025 的 AF-041 在独立真实产品副本取得卡片候选 `applied` 与 application `applied/verified`；九条 delta Requirement 分类修正后，OpenSpec 严格校验与临时副本合并通过。正式项目新增归档前 Issue 验收检查后，同轮 Chat `9bffe2e8-bb23-4559-b132-b4feb6856ef6` 实际运行归档脚本，`execution.tool` 序号 38 以 1 退出，结果为 `ACCEPTANCE_GATE_BLOCKED issue_acceptance_pending checked=24 total=52`。Change 未迁移，BUG-0025 Issue 仍 pending。自动验收 AC-010 单项通过；此前旧轮次及旧判定是历史记录。完整增量验收包 `20261012174521381442-836220d3` 为 11/11 passed，readiness ready；Workflow Sync `opsx.accept` 将本 Issue 验收结论同步为 passed。复验人：Codex；签认依据为逐 AC 证据包，未执行归档。

## 数据采集与链路观测

product_data_collection_observability: applicable

affected_layers: Web 需求中心、治理上下文 API、文档读取与权限、归档动作提示。

validation: 本轮新增治理上下文 API 验收字段，已同步 OpenAPI、Orval 客户端、API 索引与聚焦测试；沿用授权文档读取和脱敏请求日志。DB、对象存储、新行为事件、Task Trace 协议、Web 请求封装、部署配置和安全策略无结构变化。

## 验收结果回填

```yaml
acceptance_status: passed
accepted_at: 2026-10-17 17:01:21
accepted_by: workflow-sync
source_change: fix-requirement-center-acceptance-readiness-projection
source_sprint: sprint-009
evidence: [openspec/archive/2026-10-13-fix-requirement-center-acceptance-readiness-projection/evidence/acceptance/20261013082531057132-a6e693ef/summary.md]
failed_items: []
source_event: sprint.archive
notes: 由 Workflow Sync 根据 Change/Sprint 状态回填。
```
