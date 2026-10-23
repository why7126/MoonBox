---
title: 验收编排与证据复用治理设计
created_at: 2026-10-20 18:07:02
updated_at: 2026-10-20 18:07:02
---

# 验收编排与证据复用治理设计

## 方案
以 docs/standards/opsx-acceptance.md 为唯一详细契约，技能和入口使用短引用。先建立入口与真实样本矩阵，再稳定实现和文档，完成集中验证；发生修改仅失效受影响项及其依赖闭包，无法界定则扩大验证。

## 边界
不新增跨运行命令缓存，不缓存失败为通过，不豁免真实产品、视觉、权限、指纹、归档门禁。仅复用当前验收器已支持的有效逐 AC 证据。

## 验证
静态契约检查与删除关键条款、技能引用的负向测试；OpenSpec、中文、标题、目录及 Sprint 校验。静态测试不证明实际任务提速。

## 数据与部署
product_data_collection_observability: N/A；affected_layers: []；原因：仅规范与静态校验，不采集产品数据、不改事件链路。validation：检查无业务 src、API、DB、Web、管理端、Orval、Docker Compose 修改。
