---
title: 归档规格空行补证设计
created_at: 2026-10-26 11:01:27
updated_at: 2026-10-26 11:01:27
---

# 归档规格空行补证设计

## 证据与约束

证据存于 openspec/archive/.spec-normalizations/。保存完整目录文件哈希清单以及受影响规格前后文本；以源 Change expected hash 和已完成后继 baseline hash 双向锚定。两端目录哈希由清单按现有算法重新计算，变更仅允许 spec.md 末尾 LF 差异；拒绝增删文件、路径逃逸、符号链接、非正文变更和未知结构。

## 读取与并发

只读共享恢复门禁将验证后的转换作为链中独立边；正常归档边的身份、交付、delta、后继验收及最终条文效果保护不变。完整读取前后复核证明目录及恢复记录，不重写旧记录。无证明仍拒绝。

## 验证

测试空行正向链、正文差异、缺失文件、哈希篡改、符号链接、错误锚点与链末并发复核。Sprint 真实链 readiness 作为最终检查。

## 产品数据采集

product_data_collection_observability: not_applicable；affected_layers: []。仅归档静态证明读取，不新增请求、日志、事件、Task Trace 或业务存储；validation: 定向归档门禁回归与 Sprint readiness。
