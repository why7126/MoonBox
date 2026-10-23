---
title: 需求评审追溯身份兼容规格
---

# 需求评审追溯身份兼容规格

## ADDED Requirements

### Requirement: 评审识别既有需求追溯身份
需求评审校验 MUST 接受 trace 中既有的 req_id 或 requirement_id，并保持主文档及评审记录原身份要求；存在多个身份字段时 MUST 全部匹配目标对象，缺失或冲突不得通过。

#### Scenario: 需求追溯使用既有简写身份
- **WHEN** trace 的 req_id 与目标一致且其他评审门禁通过
- **THEN** 不因缺少 requirement_id 拒绝成果

#### Scenario: 追溯包含冲突身份
- **WHEN** req_id 与 requirement_id 不一致或任一显式字段无效
- **THEN** 拒绝应用并保留原事实

### Requirement: 评审收尾同步验收来源事件
系统 MUST 在完整评审校验通过后，将验收文档中既有 complete 来源事件同步为对应 review 事件，再次校验后进入正式同步回读，不改变验收状态或验收内容。

#### Scenario: 模型保留验收子文档原文
- **WHEN** 有效评审成果仍保留 req.complete 或 bug.complete 来源事件
- **THEN** 收尾同步对应 review 事件，重复收尾无额外变化

### Requirement: 源码执行使用可信源码根目录同步
源码模式 MUST 从已授权 source_root 执行 Workflow Sync；治理 root 只挂载文档时不得要求其包含脚本。同步前后 MUST 同时校验源码与治理投影文件一致，禁止客户端指定执行路径。

#### Scenario: 治理投影与源码根分离
- **WHEN** 治理投影只有文档而可信源码根包含同步脚本
- **THEN** 在源码根运行同步并核对两处治理事实，任一漂移则阻断
