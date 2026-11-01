---
title: 知识库使用说明
purpose: 规定 docs/knowledge-base 如何被后续 Sprint、需求完善和 OpenSpec 实现流程复用
content: 知识库入口、行动项状态、命令读取门禁和落地要求
source: workflow governance
update_method: Sprint 复盘、best-practice 或命令门禁变化时更新
owner: 项目负责人
status: active
updated_at: 2026-11-01 08:10:00
---

# 知识库使用说明

- [会话准备延迟的证据边界与安全优化](incidents/20261030-object-session-preparation-latency.md)
- [受控规则替代的验证与恢复经验](best-practices/20261022-controlled-rule-replacement.md)

`docs/knowledge-base/` 保存跨 Sprint 可复用的经验、复盘、事故和最佳实践。它不是事后报告库；后续规划、需求完善和实现命令必须把这里的内容作为输入。

## 目录职责

| 路径 | 职责 | 使用时机 |
|---|---|---|
| `sprints/` | Sprint 复盘、行动项、容量与流程经验 | `/sprint-propose` 必读上一 Sprint 和未关闭行动项 |
| `retrospectives/` | 迁移命令生成的 Sprint 复盘与行动项沉淀 | `/sprint-propose`、`/sprint-exps` 读取最近复盘和 open 行动项 |
| `incidents/` | 故障、事故、线上问题复盘 | `/bug-opsx`、`/opsx-apply`、`/sprint-apply` 处理相关能力时必读 |
| `best-practices/` | 可复用设计、组件、测试、验收模式 | `/req-complete`、`/opsx-apply`、`/sprint-apply` 按主题匹配读取 |

## 行动项状态

复盘行动项必须使用以下状态之一：

| 状态 | 含义 |
|---|---|
| `open` | 已提出，尚未进入 Sprint 或 Change |
| `in_sprint` | 已被当前或未来 Sprint 承接 |
| `done` | 已通过 REQ/BUG/Change 或规则更新落地 |
| `deferred` | 明确延期，并记录原因 |
| `rejected` | 明确不做，并记录原因 |

## 命令门禁

| 命令 | 必须读取 | 必须落地 |
|---|---|---|
| `/sprint-propose` | 最近一次 Sprint 复盘、所有 `open`/`in_sprint` 行动项、相关 best-practices | 在 `sprint.md` 写「知识库承接项」，在 `sprint.yaml` 记录承接的 action id |
| `/req-complete` | 与需求领域、UI 模式、数据流、上传、权限、测试相关的 best-practices | 在 `acceptance.md` 增加知识库 checklist，无法适用时写明原因 |
| `/req-opsx` | 带 prototype 的 UI REQ 必读 `best-practices/prototype-driven-ui-gate.md` | 在 Change `design.md` 写 UI Skeleton，在 `tasks.md` 写 1440px 视觉验收任务 |
| `/opsx-apply` | 当前 Change 关联领域的 best-practices 与 incidents；带 prototype UI 必读原型驱动 gate | 实现前输出 Knowledge Gate；带 prototype 页面先完成 UI Skeleton 和 1440px 视觉验收 |
| `/opsx-modify` | 验收反馈涉及 UI/visual/prototype 时读取原型驱动 gate | 返修后重新跑 1440px 视觉验收并回填 Change/REQ 文档 |
| `/opsx-archive` | 带 prototype UI 的 Change 读取原型驱动 gate 与最终验收证据 | 归档前确认 REQ 最终一致性，不一致则阻断 |
| `/sprint-apply` | Sprint 承接项、相关 best-practices、相关 incidents | Queue Report 中列出 Knowledge Gate 状态 |

## 禁止事项

- 禁止只在 `/sprint-exps` 写入知识库，而在下一 Sprint 规划中不读取。
- 禁止将 `open` 行动项长期保留而不标记 `in_sprint`、`done`、`deferred` 或 `rejected`。
- 禁止 add-* Change 忽略已存在的同类 best-practice，等 Bug 出现后才引用。

## Sprint 复盘索引

| Sprint | 复盘 | 状态 | Open 行动项 |
|---|---|---|---:|
| sprint-018 | [Sprint-018 经验复盘](retrospectives/sprint-018-retrospective.md) | active | 6（含5项前序承接） |
| sprint-017 | [Sprint-017 经验复盘](retrospectives/sprint-017-retrospective.md) | active | 5（含3项前序承接） |
| sprint-016 | [Sprint-016 经验复盘](retrospectives/sprint-016-retrospective.md) | active | 4 |
| sprint-015 | [Sprint-015 经验复盘](retrospectives/sprint-015-retrospective.md) | active | 8（另1项已纳入sprint-016） |
| sprint-014 | [Sprint-014 经验复盘](retrospectives/sprint-014-retrospective.md) | active | 8（含7项前序承接） |
| sprint-013 | [Sprint-013 经验复盘](retrospectives/sprint-013-retrospective.md) | active | 8（含6项前序承接） |
| sprint-012 | [Sprint-012 经验复盘](retrospectives/sprint-012-retrospective.md) | active | 6（含5项前序承接） |
| sprint-011 | [Sprint-011 经验复盘](retrospectives/sprint-011-retrospective.md) | active | 5（含4项前序承接） |
| sprint-010 | [Sprint-010 经验复盘](retrospectives/sprint-010-retrospective.md) | active | 4 |
| sprint-009 | [Sprint-009 经验复盘](retrospectives/sprint-009-retrospective.md) | active | 5 |
| sprint-008 | [Sprint-008 经验复盘](retrospectives/sprint-008-retrospective.md) | active | 5 |
| sprint-007 | [Sprint-007 经验复盘](retrospectives/sprint-007-retrospective.md) | active | 6 |
| sprint-006 | [Sprint-006 经验复盘](retrospectives/sprint-006-retrospective.md) | active | 6 |
| sprint-005 | [Sprint-005 经验复盘](retrospectives/sprint-005-retrospective.md) | active | 6 |
| sprint-004 | [Sprint-004 经验复盘](retrospectives/sprint-004-retrospective.md) | active | 7 |
| sprint-003 | [Sprint-003 经验复盘](retrospectives/sprint-003-retrospective.md) | active | 6 |
| sprint-002 | [Sprint-002 经验复盘](retrospectives/sprint-002-retrospective.md) | active | 5 |
| sprint-001 | [Sprint-001 经验复盘](retrospectives/sprint-001-retrospective.md) | active | 4 |

- [Capture假成功与多文件持久化](incidents/20260912-capture-persistence.md)：BUG-0014，终态反馈、锁内编号、幂等与恢复证据。

## 研发启动状态经验

[启动事实与任务进度分离](incidents/20260912-apply-start-stage.md)：BUG-0015已通过Change实现与验证，无新增未承接行动项。

- [需求中心读取失败与重复解析](incidents/20260912-requirement-center-read-performance.md)：BUG-0016后端阶段证据，UI与部署验收仍待完成。

## 治理恢复与归档验收

- [需求中心快照读取性能与安全复用](incidents/requirement-context-read-cost.md)：BUG-0056，请求内索引、完整字节验证、有界缓存及冷暖测量边界。

- [治理恢复与归档验收证据分层实践](best-practices/governance-recovery-archive-evidence.md)：生产消费契约、首次成功与恢复分层、串行样本及历史证据保留。

- [完成证明与执行保护交接故障](incidents/20261020-completion-proof-guard-convergence.md)：BUG-0052，历史证明与当前准入分离、持久交接和有界核验。

- [直接治理命令完成证明与安全核验](incidents/20261021-direct-command-completion-proof.md)：BUG-0060，相关依赖、最终签认、持久核验队列及历史缺证边界。

- [Chat 跨秒消息倒置的排序与时间分离实践](incidents/20261021-chat-message-causal-order.md)：BUG-0055，运行验收待补。

- [跨入口续接证明与执行保护收敛](incidents/cross-entry-successor-proof-convergence.md)：BUG-0061，正式同步收据、独立后继证明、保守冲突判断与实际归档验收。

- [归档条文冲突与验收进度](incidents/20261021-archive-requirement-scope-conflict.md)：BUG-0062，条文级冲突、有效验收进度与恢复准入分离；sprint-012修复解除sprint-011关闭阻塞。

- [同条文兼容追加与显式替代边界](incidents/20261022-compatible-requirement-successor.md)：BUG-0063，独立证明、逐边完整链、候选预检及原约束保留。

- [规格末尾空行与归档断链补证](incidents/20261026-archive-newline-proof.md)：完整目录双端锚定、末尾LF限定、原记录保留及当前引用修复。

- [Chat 最终答案身份与自动核验状态经验](incidents/chat-answer-identity-and-verification.md)：BUG-0065/0066，跨路径幂等、历史投影与有界状态跟进。

- [Chat 流式片段不等于正文长度](incidents/chat-stream-preview-budget.md)：BUG-0067 读取预算与证据边界。

- [Chat 数据库锁竞争与核验事务隔离](incidents/chat-database-lock-verification.md)：BUG-0068，线程证据、零行更新及提交未知边界。

- [无旧成功证明的中断接续复发](incidents/20261027-interrupted-successor-proof.md)：BUG-0069，可信启动基线、独立后继收据、完整差异覆盖与历史保留。

- [依赖子交付与迭代承接实践](best-practices/partial-delivery-sprint-handoff.md)：父需求partial、历史交付保留、当前归属及重放限制。

- [历史归档证明与后续同步经验](incidents/20261101-archive-proof-and-later-sync.md)：合法追加补证、同步副作用和关闭后复核。
