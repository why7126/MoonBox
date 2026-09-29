---
title: 生成文档中文标题门禁规格
created_at: '2026-09-15 23:04:19'
updated_at: '2026-09-15 23:04:19'
---

# 生成文档中文标题门禁规格

## ADDED Requirements

### Requirement: 生成文档中文标题与一致性
所有生成 Markdown 文档 SHALL 包含中文 Frontmatter title 与一致的一级标题，覆盖 capture、trace、user-stories、review、requirement、bug、business-flow、acceptance、root-cause、workaround、proposal、design、tasks、spec 及其他生成文档。业务主文档表达业务目标，辅助文档结合业务主题及用途。注册表每条 SHALL 包含中文业务 title。

#### Scenario: 标题生成与注册表同步
- **WHEN** 创建或重新生成文档
- **THEN** 生成非空中文 title 和一致一级标题，允许英文专名，不接受纯类别或模板标题
- **AND** Issue 主文档业务标题同步注册表，不被 Change 业务标题覆盖；保留 OpenSpec 解析关键字

### Requirement: 标题校验阻止无效生成完成
CLI、技能及产品 Agent 生成入口 SHALL 在应用产物或声明完成之前校验标题，失败不得推进工作流。

#### Scenario: 不合法产物
- **WHEN** 产物缺标题、空白、纯英文或ID、模板/类别标题，或字段与一级标题冲突
- **THEN** 返回文件与字段级错误，不应用部分结果、不声明完成、不推进状态；修正后重验

#### Scenario: 历史资料与聚焦校验
- **WHEN** 校验当前 Issue 或 Change 的生成产物
- **THEN** 当前失败阻断完成，无关历史残留单独报告；不批量改写归档
- **AND** 读取历史缺失标题使用受控回退与提示，不阻断整个看板
