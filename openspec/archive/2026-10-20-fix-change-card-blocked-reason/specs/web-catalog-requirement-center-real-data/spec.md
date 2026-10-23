---
title: 纯 Change 卡片阻塞诊断修复规格增量
created_at: '2026-10-20 19:09:48'
updated_at: '2026-10-20 19:09:48'
---

# 纯 Change 卡片阻塞诊断修复规格增量

## ADDED Requirements

### Requirement: 纯 Change 验收阻塞诊断可操作

系统 SHALL 将纯 Change 验收阻塞的安全诊断从 readiness 传递至归档准入和需求中心卡片，保持动作准入与提示一致。

#### Scenario: 已知输入问题
- **WHEN** 验收因输入缺失或内容变化而阻塞
- **THEN** 系统 SHALL 显示对应中文原因、受影响 AC、必要的安全相对路径与下一步提示，不仅显示 blocked

#### Scenario: 未执行或未知错误
- **WHEN** 验收尚未执行或具体原因不可分类
- **THEN** 系统 SHALL 分别提示补充验收或待核查，并提供证据定位入口，不虚构缺失原因

#### Scenario: 诊断与准入一致
- **WHEN** 卡片读取 blocked 或 ready 状态
- **THEN** 系统 SHALL 保持既有门禁，阻塞时禁用动作，ready 时清除旧原因；卡片与动作提示语义一致

#### Scenario: 敏感诊断被过滤
- **WHEN** 原始诊断包含本机绝对路径、绑定配置、密钥或堆栈
- **THEN** 系统 SHALL 只展示安全摘要，不泄漏敏感字段
