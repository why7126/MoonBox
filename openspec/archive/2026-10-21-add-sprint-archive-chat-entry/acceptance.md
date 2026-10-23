---
title: 迭代归档对象会话变更验收清单
change_id: add-sprint-archive-chat-entry
requirement_id: REQ-0049-sprint-archive-chat-entry
created_at: '2026-10-21 18:34:08'
updated_at: '2026-10-21 18:34:08'
acceptance_status: passed
---

# 迭代归档对象会话变更验收清单

## 验收状态与证据原则

30 项 AC 已通过当前自动验收，逐项证据见 evidence/acceptance/20261021222222616138-ba4f0055/summary.md。真实归档使用隔离 Sprint 099/098；HTML 原型仍只表达意图，产品观察、合成回归和视觉证据分层记录于 verification.md。

## 功能 AC

- [x] AC-001 全范围对象完成、签署缺失，按钮可用；点击进入 Chat，Sprint 状态仍未归档。
- [x] AC-002 存在任一未完成 REQ、BUG 或关联 Change 时禁用；搜索/筛选/分页隐藏该对象不改变结果。
- [x] AC-003 空 Sprint、事实源缺失、未知状态分别给出原因，不将空集合或未知状态当作完成。
- [x] AC-004 容量为零/未知且非空完整范围全部完成时仍可进入；applied 或任务全勾选不能单独当作完成。
- [x] AC-005 同对象已有可用会话时复用同一 ID，无可用会话时创建且主关联为 SPRINT。
- [x] AC-006 多个会话按 business-flow 中确定的服务端排序选择；已删除、已归档会话不复用。
- [x] AC-007 不同空间/仓库同 Sprint ID、不同用户权限的样本不串会话，不泄漏会话标题或消息。
- [x] AC-008 点击正常路径直接进入 Chat，无归档确认弹窗；请求中切换项目时旧结果不跳转、不预填。
- [x] AC-009 空输入精确填入 /sprint-archive 加目标完整编号；输入可编辑，消息数/turn 数与执行请求数均未增加。
- [x] AC-010 输入已是目标命令时只保留一份；无隐藏执行提示词或残留占位编号。
- [x] AC-011 存在不同草稿时原文默认保留；选择填入才替换文本，选择保留关闭意图；附件/Skill 等输入上下文不被无声清除。
- [x] AC-012 预填意图按项目和会话隔离且消费一次；刷新、返回、组件重挂载不重复覆盖或发送。
- [x] AC-013 对象执行中或结果待核对时打开既有执行会话，不替换草稿、不另建会话、不提交新 turn。
- [x] AC-014 连点、并发准备及超时重试返回一致关联结果，不重复新建；关联失败明确反馈且可安全重试。
- [x] AC-015 无权准备或执行时服务端独立拒绝；前端显示原因，无越权写入或敏感响应。
- [x] AC-016 用户主动发送前范围/权限/归档状态变化时重新校验；旧入口就绪结果不绕过最新门禁。
- [x] AC-017 发送后缺签署或文档/同步检查失败时展示具体阻塞，不伪造签署或将 Chat 文本当作归档成功。
- [x] AC-018 真实归档成功后回到需求中心读取最新列表、容量和统计；已归档 Sprint 退出当前迭代区域且历史可追溯。
- [x] AC-019 归档失败、待签署、刷新失败各自反馈，不提前变为成功；已成功副作用不因恢复重复执行。
- [x] AC-020 入口行为、会话准备请求、发送后的任务可用脱敏标识关联；预填不记为归档执行成功，观测失败不阻断主业务。
- [x] AC-021 日志/事件不保存草稿、完整 Prompt、凭证或本机路径；API 契约改变同步 OpenAPI/客户端，DB 改变覆盖双数据库，否则记录具体 N/A。

## 横切 AC（knowledge-base）

本需求为 web-catalog，不命中 admin-list、admin-form、admin-modal、media-upload；对应管理端/上传横切规则 N/A，无新增管理表单或媒体上传。按实际主题补充以下知识库验收：

来源：`docs/knowledge-base/best-practices/governance-recovery-archive-evidence.md`、`docs/knowledge-base/retrospectives/sprint-010-retrospective.md`。

- [x] AC-XCUT-001 分别保留首次正常归档、失败拒绝、原执行恢复的证据；恢复成功不追认原轮次首次成功。
- [x] AC-XCUT-002 会话准备结果的对象/项目/关联身份与消费端一致；业务成果、轮次终态及读取侧展示分别核对。
- [x] AC-XCUT-003 实际归档样本隔离且治理写入串行；回读当前态与证据路径可解析，保留原始历史。

## 原型驱动 UI AC

来源：`docs/knowledge-base/best-practices/prototype-driven-ui-gate.md`。

- [x] AC-PROTOTYPE-001 核对 issues/requirements/review/REQ-0049-sprint-archive-chat-entry/prototype/web/context.md 的页面、组件、状态、触发、数据依赖及断点拆解与实现一致。
- [x] AC-PROTOTYPE-002 实现前完成 UI Skeleton 首轮确认；记录确认事实，不以当前文档齐全替代。
- [x] AC-PROTOTYPE-003 1440×900 检查容量条图标、提示、Chat 身份、命令输入、草稿选择和加载/禁用状态，记录截图及 computed style。
- [x] AC-PROTOTYPE-004 768×900、390×844 验证容量区域折行、无遮挡、提示可访问、长命令与输入区域不溢出；键盘可操作。
- [x] AC-PROTOTYPE-005 按 context 中 selector/动作矩阵逐项核对正常跳转无 modal、草稿 inline 选择、执行保护；采集关键交互证据。
- [x] AC-PROTOTYPE-006 归档前同步 PRD、流程、故事、验收、trace 和原型，声明真实 API/Mock 边界；视觉通过、命令测试通过和真实执行证据分别报告。

## 证据与分批执行

| 批次 | 覆盖项 | 样本/方法 | 证据 |
|---|---|---|---|
| A 准入与身份 | AC-001～007、015～016 | 完成/未完成/未知/空范围、跨项目和权限集成测试 | 测试结果与脱敏请求摘要 |
| B 导航与输入 | AC-008～014 | 浏览器交互、请求计数与会话/turn 回读 | 关键状态截图、DOM 及网络证据 |
| C 归档结果 | AC-017～021、XCUT | 隔离项目真实发送、失败和恢复串行样本 | 实际轮次、成果及同步回读证据 |
| D 视觉一致性 | PROTOTYPE | 1440×900 全状态；768×900 与390×844 默认/禁用/草稿冲突 | 截图与 computed style，逐项结论 |

证据归属本 Change 的 evidence/acceptance/。首次验收计划的前端配置相对路径错误已修正，增量复验复用 23 项、复验 7 项后全部通过。正式归档仍需最终共享门禁及明确授权。
