---
title: Git 隐私上下文扫描规格
created_at: 2026-10-30 08:49:30
updated_at: 2026-10-30 08:49:30
---

# Git 隐私上下文扫描规格

## ADDED Requirements

### Requirement: 有限上下文排除隐私误报

扫描器 MUST 仅在明确摘要、数值、代码语法或合成身份上下文排除已核实误报，不按整个文件或目录豁免。

#### Scenario: 哈希与测量数字

- **WHEN** 手机号形态出现在完整摘要或JSON小数数值内部
- **THEN** 不产生手机号告警，其他独立手机号继续告警

### Requirement: 占位符和链接不掩盖真实敏感值

扫描器 MUST 按完整值与具体规则识别占位符，链接存在不跳过同排扫描。

#### Scenario: 链接旁出现邮箱

- **WHEN** URL同排包含非合成邮箱
- **THEN** 仍产生邮箱告警

#### Scenario: 密钥含示例字样

- **WHEN** 非占位密钥或连接串包含example、localhost或问号
- **THEN** 仍报告错误并脱敏
