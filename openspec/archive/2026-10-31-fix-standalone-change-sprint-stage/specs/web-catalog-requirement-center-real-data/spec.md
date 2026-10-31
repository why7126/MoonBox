---
title: 独立变更阶段映射修正规格
created_at: '2026-10-31 10:12:35'
updated_at: '2026-10-31 10:12:35'
---
# 独立变更阶段映射修正规格

## MODIFIED Requirements

### Requirement: Change 版本和状态证据
系统 SHALL 精确识别活动与归档完整ID，不以任务完成推断验收或归档。

#### Scenario: 活动与归档冲突
- **WHEN** 活动和归档同ID，或存在多份归档
- **THEN** 系统 SHALL 优先活动并提示冲突，活动缺文档不读旧副本，多份归档禁用含糊入口

#### Scenario: 状态映射与缺失
- **WHEN** 活动trace为proposed/in_progress/applied，或唯一归档，或未知状态
- **THEN** 系统 SHALL 对独立proposed对象仅在唯一有效Sprint归属成立时映射待开发，无归属或冲突/失效时映射迭代规划；其他状态分别映射研发中/验收中、已完成或默认收起的数据异常诊断入口；未知对象不渲染卡片、不计入页面业务统计
- **AND** 缺tasks显示未知，任务全部勾选不自动改为已完成；Sprint信息不覆盖trace

#### Scenario: 稳定快照失败
- **WHEN** registry解析失败、迁移半写入或项目切换发生
- **THEN** 系统 SHALL 保留受控同步失败状态，不能把全部Change判成独立，不能将旧项目迟到响应覆盖新项目

#### Scenario: 规划与归属诊断动作
- **WHEN** 独立提案尚未纳入Sprint
- **THEN** 系统 SHALL 标注待纳入迭代并提供加入迭代入口，不自动执行范围写入
- **WHEN** 归属冲突或失效
- **THEN** 系统 SHALL 保留阻断并提供只读核对归属入口，不自动选择或覆盖Sprint
- **AND** 唯一有效归属成立后才提供开始开发，其他权限和执行门禁继续生效

