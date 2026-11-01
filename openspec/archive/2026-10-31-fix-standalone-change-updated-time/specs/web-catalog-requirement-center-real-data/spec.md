---
title: 独立 Change 卡片可信时间增量规格
created_at: "2026-10-31 22:33:14"
updated_at: "2026-10-31 22:33:14"
---

# 独立 Change 卡片可信时间增量规格

## ADDED Requirements

### Requirement: 独立 Change 可信时间来源

系统 SHALL 在独立 Change 卡片上显示经过校验的时间及其真实业务来源，摘要和完整投影一致，不改变 REQ/BUG 卡片时间契约。

#### Scenario: 按来源展示有效时间
- **WHEN** 独立 Change 含有效 updated_at、created_at 或执行时间
- **THEN** 系统 SHALL 依次选择 updated_at、created_at、execution.completed_at、execution.started_at 的首个合法值，并分别显示更新、创建、执行完成或执行开始标签
- **AND** 系统 SHALL 通过独立 card_time/card_time_source 投影，不将执行时间冒充 updated_at，不修改源 trace

#### Scenario: 非法或完全缺失时间
- **WHEN** 高优先级时间非法或所有时间均缺失
- **THEN** 系统 SHALL 跳过非法候选；无合法候选时显示“时间未记录”，不得使用查询时刻、文件 mtime 或复制时间补齐

#### Scenario: 时区与卡片兼容
- **WHEN** 活动或归档独立 Change 在深浅主题及桌面或窄屏展示
- **THEN** 系统 SHALL 以 Asia/Shanghai 显示 YY/MM/DD HH:mm，不拆分时间文本或挤压动作，必要时 footer 换行，保留权限、优先级和验收入口行为

### Requirement: Change 业务时间幂等维护

系统 SHALL 在新建及有效业务变更时维护真实时间，并保持历史事实和无变化重放稳定。

#### Scenario: 新建及有效变更
- **WHEN** 创建 Change 或 start/apply/modify/归档发生有效内容或状态变化
- **THEN** 系统 SHALL 在新建时记录合法 created_at/updated_at，在有效变更时维护 updated_at，保留合法 created_at 和首次 execution.completed_at
- **AND** 旧对象缺 created_at 时 SHALL 不补造历史创建时间，缺 updated_at 时可记录本次真实变更时间

#### Scenario: 无变化重放与历史只读
- **WHEN** 重复同一事件没有实际变化、读取卡片或重放已完成对象
- **THEN** 系统 SHALL 不刷新业务时间、不覆盖首次执行完成事实、不批量改写归档历史证据

