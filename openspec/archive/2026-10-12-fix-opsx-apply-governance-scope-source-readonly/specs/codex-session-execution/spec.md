---
title: 实现写权限兼容与观测增量规格
created_at: 2026-10-07 15:16:20
updated_at: 2026-10-07 15:16:20
---

# 实现写权限兼容与观测增量规格

## ADDED Requirements

### Requirement: 实现授权治理字段归一化

系统 MUST 从服务端可信治理文件归一化来源与 Sprint：BUG 支持 bug、bug_id、source_bug、related_bug，REQ 支持 requirement、requirement_id、req_id、source_requirement，Sprint 支持 sprint、iteration。系统 MUST 校验多字段一致性、合法类型、主对象匹配、成员权限、Issue in_sprint、活动 Change proposed/in_progress 及 Sprint 双向包含；不因字段兼容放开其他阶段或直接 Change 主对象授权。

#### Scenario: 已纳入迭代的缺陷使用别名字段
- **WHEN** 满足全部授权门禁的 BUG Change 使用 bug_id 与 iteration
- **THEN** 实现任务获得 implementation_write 并映射 moonbox-write，不因别名回退治理权限

#### Scenario: 需求来源字段兼容
- **WHEN** 已满足实现门禁的 REQ 使用一致的来源与 Sprint 别名
- **THEN** 获得与规范字段相同的实现权限

#### Scenario: 冲突或缺失事实
- **WHEN** 同义字段冲突、类型非法、来源不匹配或 Sprint 未同时包含 Issue 和 Change
- **THEN** 不授予源码实现权限，并保留可辨识的安全诊断原因

#### Scenario: 其他权限边界保持
- **WHEN** 用户无写权限、处于治理候选、Change 已 applied/archived 或执行中撤权
- **THEN** 继续遵守相应拒绝、治理只写或停止执行规则，不因兼容解析扩权

### Requirement: 同轮次权限决策与实际执行配置留痕

系统 MUST 关联同一 turn 的服务端 scope、reason_code、时间、治理输入版本摘要和执行器实际选用 profile，区分计划配置与已核验启动结果；记录 MUST 脱敏，不存原始会话、凭证或完整治理文件。系统 MUST 不以当前重建值冒充历史日志，不以 UI 标签或会话 completed 代替实现成功。

#### Scenario: 原缺陷场景修复后执行
- **WHEN** 测试环境用原 BUG-0029 字段形态启动合法实现任务
- **THEN** 可核验该 turn 的实现决策、moonbox-write、实际源码写入及一致的治理输入版本摘要

#### Scenario: 配置不一致或观测不可用
- **WHEN** profile 与授权不符，或观测写入失败
- **THEN** 配置不符时阻断启动；观测失败明确记录降级且不扩权，不声称取得缺失证据
