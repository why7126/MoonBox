---
title: 交付卡片来源估算归属排查
created_at: '2026-10-31 23:48:00'
updated_at: '2026-10-31 23:48:00'
source: BUG-0073-change-source-issue-estimate-missing
---

# 交付卡片来源估算归属排查

## 现象与机制
Sprint来源Issue已估算而Change显示待估算时，先检查scope行身份与投影入口。BUG-0070真实输入为3人天，旧函数因id属于Issue而排除，即使change明确关联。

## 修复原则
Change自身值及错误优先。回退前使用完整项目关系（含隐藏、归档和缺失目录关联），不能使用当前可见卡数证明一对一。双方须属于有效Sprint，来源scope行须明确绑定目标；相同值去重，冲突不猜测，0有效。来源可见性先校验，提示是引用估算而非实际耗时。展示回退不改Sprint容量或源文档。

## 回归入口
src/backend/tests/test_change_source_estimate.py与src/web/src/card-info-tags.test.tsx。产品观察与合成夹具分开记录；证据入口为对应Change的verification.md及evidence/acceptance。本文不修改其他历史交付或全局规则。
