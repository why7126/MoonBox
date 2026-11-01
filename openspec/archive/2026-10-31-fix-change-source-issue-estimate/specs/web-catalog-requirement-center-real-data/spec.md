---
title: Change 来源估算投影规格变更
created_at: '2026-10-31 23:29:25'
updated_at: '2026-10-31 23:29:25'
---

# Change 来源估算投影规格变更

## MODIFIED Requirements

### Requirement: 单卡预估人天投影
系统 MUST 使用授权项目内对象有效Sprint归属的scope_estimates估算，支持已归档源；不得用总容量、优先级或story_points替代。

#### Scenario: 总量分项与异常值
- **WHEN** 存在Issue总量、关联Change分项或重复记录
- **THEN** 前期 Issue 维持唯一总量优先；交付卡优先使用自身明确分项；缺少自身记录时，仅在授权项目完整关系证明来源与交付唯一且估算明确绑定目标时引用来源Issue估算并说明来源，其他缺失显示待估算，不向多个Change复制Issue总量或平均分摊。相同记录去重，冲突不得猜测；Sprint 容量沿用原 scope 口径，不按卡片重新累计
- **AND** 仅有限非负数有效，0和小数展示，字符串、布尔、负数和非有限数不输出数值

#### Scenario: 来源权限与冲突保护
- **WHEN** 存在不可见来源、多个来源、多个未分配交付或自身估算冲突
- **THEN** 系统 SHALL 不推断唯一归属、不泄漏来源，不使用来源值掩盖自身错误；Sprint容量不因展示回退改变。
