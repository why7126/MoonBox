---
title: 当前迭代归档入口交互规格
change_id: add-sprint-archive-chat-entry
requirement_id: REQ-0049-sprint-archive-chat-entry
created_at: '2026-10-21 18:32:37'
updated_at: '2026-10-21 18:32:37'
---

# 当前迭代归档入口交互规格

## MODIFIED Requirements

### Requirement: 当前迭代归档入口

系统 SHALL 在当前迭代容量区域保留明确绑定目标 Sprint 的归档入口。非空完整范围全部对象已完成、Sprint未归档且用户有权限时允许准备会话；点击直接进入Chat工作台，预填命令但不发送。最终签署及归档检查在用户发送后的执行阶段完成。

#### Scenario: 全部对象完成后允许进入
- **WHEN** Sprint非空完整范围的REQ、BUG和全部关联Change均已完成且尚未归档
- **THEN** 入口 SHALL 可用并明确绑定该Sprint
- **AND** 容量为零或待核实、验收尚未sign-off MUST NOT 单独阻止准备会话
- **AND** 入口 SHALL 保留在容量区域，不分散到每张对象卡片

#### Scenario: 不完整或未知范围拒绝
- **WHEN** 存在未完成对象、空范围、事实源缺失、状态未知或当前迭代不可解析
- **THEN** 系统 MUST 禁用可执行入口并区分安全原因
- **AND** 当前搜索、筛选及分页 MUST NOT 掩盖未完成或关联Change
- **AND** applied状态或任务勾选率 MUST NOT 单独视为已完成

#### Scenario: 多迭代与异步响应
- **WHEN** 页面有多个当前Sprint或请求期间切换项目
- **THEN** 点击 SHALL 仅准备所选Sprint，不按编号或更新时间替用户选择
- **AND** 迟到响应 MUST NOT 导航或预填到其他项目、Sprint或会话

#### Scenario: 直接进入对象会话
- **WHEN** 用户点击可用归档入口
- **THEN** 系统 SHALL 显示准备状态并复用或创建对应SPRINT会话后直接进入Chat
- **AND** 正常路径 MUST NOT 打开旧归档确认modal，也不得仅提示手动复制命令
- **AND** 系统 MUST NOT 因点击或导航直接归档；退出Chat或放弃草稿不改变归档事实

#### Scenario: 准备或权限失败
- **WHEN** 准备失败、关联失败或用户无权限
- **THEN** 系统 MUST 安全反馈并允许适用的重试，不打开无关联空会话
- **AND** 系统 MUST NOT 泄漏不可见对象、会话、内部路径、堆栈、密钥或环境内容
- **AND** 系统 MUST NOT 提供强制归档绕过按钮

#### Scenario: 最终归档与刷新
- **WHEN** 用户发送后的归档流程执行完成
- **THEN** 系统 MUST 依据最新权限、范围、验收签署、文档及Workflow Sync真实结果判断成功
- **AND** 成功后 SHALL 重新读取当前迭代、容量、Scope、卡片及统计，已归档Sprint不再显示为当前迭代
- **AND** 检查、执行或刷新失败 SHALL 保留上下文并显示失败或过期提示，不能提前展示归档成功

#### Scenario: 原型与真实验收
- **WHEN** 本入口和Chat输入保护完成实现并准备验收
- **THEN** 系统 SHALL 按Change设计、验收清单、1440px及关键交互视觉证据、computed style、Mock/API边界和REQ最终一致性共同验收
- **AND** 原型 SHALL 仅作为设计输入，模拟数据和静态检查不得替代真实产品证据
