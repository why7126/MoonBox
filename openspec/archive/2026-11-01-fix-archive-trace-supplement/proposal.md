---
title: 归档来源追溯补充证明
created_at: 2026-11-01 08:03:00
updated_at: 2026-11-01 08:03:00
---

# 归档来源追溯补充证明

## 背景
BUG-0073归档后给REQ-0056追加关联缺陷表与更新时间，导致原恢复证明绑定漂移。逆向两处差异后哈希精确匹配。

## 变更内容
保留原证明及当前文档，以独立补证绑定原文和当前来源；仅接受末尾追加的已关闭缺陷索引与更新时间变化，其他差异阻断。

## 能力
### 修改能力
- archive-finalization-consistency：来源追溯追加证明。

## 影响
共享归档校验及CLI、回归和治理文档。不改变API、DB、UI、权限或客户端生成。

product_data_collection_observability: not_applicable
affected_layers: []
reason: 仅本地归档证据验证，不改变请求、事件、日志或Task Trace采集。
validation: 聚焦证明正反例与真实归档复验。
