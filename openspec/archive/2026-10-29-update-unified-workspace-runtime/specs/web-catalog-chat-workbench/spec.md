---
title: 工作台主目录与隔离交付规格变更
created_at: '2026-10-29 06:50:53'
updated_at: '2026-10-29 06:50:53'
---

# 工作台主目录与隔离交付规格变更

## MODIFIED Requirements

### Requirement: 治理候选与事实源完成边界

Chat 工作台 SHALL 将执行工作区、assistant 输出和治理 candidate 作为候选或执行证据；卡片阶段、文档入口和完成态 SHALL 以治理事实源、Workflow Sync 结果和事实源重读投影为准。

#### Scenario: candidate 应用前版本校验

- **WHEN** 用户或后端自动应用治理 candidate
- **THEN** 系统 SHALL 校验 candidate manifest、revision、binding revision 和当前事实源版本
- **AND** 校验失败时 SHALL 返回 conflict、stale 或等价待恢复状态
- **AND** 不得把候选差异、assistant 回复或工作区文件直接展示为完成事实

#### Scenario: 应用后刷新事实源投影

- **WHEN** candidate 文件写入完成
- **THEN** 系统 SHALL 执行对应 Workflow Sync
- **AND** 同步成功后 SHALL 重读治理事实源并刷新需求中心卡片投影
- **AND** 同步失败或重读失败时 SHALL 保留操作身份和安全错误摘要
- **AND** 前端不得刷新卡片阶段为成功态

#### Scenario: 本地部署默认真实仓库工作区

- **WHEN** 本地常驻部署生成仓库绑定
- **THEN** 系统 SHALL 默认声明 `workspace_mode: source`
- **AND** 执行器 SHALL 直接使用 `source_root` 当前工作树作为工作区
- **AND** 系统 SHALL 不创建 `<workspace_root>/<conversation_id>` 会话副本、不执行副本同步、不要求候选二次应用
- **AND** 隔离或并行交付 SHALL 按交付链路创建真正 Git worktree，不新建 copy 会话副本
- **AND** 历史 copy SHALL 标为 legacy 并保留隔离副本、候选应用与未应用成果保护，完成核验迁移前不得删除；任务树成果通过受控合入，正式规格经归档生效
