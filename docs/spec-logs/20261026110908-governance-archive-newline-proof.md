---
title: 归档规格末尾空行差异补证与迭代关闭修复
created_at: 2026-10-26 11:09:08
updated_at: 2026-10-26 11:09:08
---

# 归档规格末尾空行差异补证与迭代关闭修复

## 目标与根因

用户授权修复 sprint-013 基线证明与失效引用并继续归档。临时重放精确匹配原归档 expected，历史 Git 版本与后继 baseline 只相差规格末尾一个 LF。

## 变更与边界

Change repair-archive-newline-proof 纳入 sprint-013，估算1人天，总量33/30人天，未变更容量。共享恢复读取独立完整目录补证，两端哈希锚定历史记录；仅允许末尾 LF 数量差异，原 journal/manifest 不改写。补证存于 openspec/archive/.spec-normalizations/；修复REQ-0050/0053验收文档四处归档链接，保留历史结论。

## 更新与验证

更新 src/backend/app/governance/archive_recovery.py、spec_normalization.py、定向测试、docs/standards/opsx-acceptance.md、rules/directory-structure.md 和相关 Change/Sprint 文档。189项联合回归通过，最终验收与归档事实以 Change trace 和 Sprint 最终报告为准。目录校验仅既有legacy SQLite警告，运行数据保持不变。

## 影响与后续建议

无API、DB、Web、客户端、管理端、Orval、Docker Compose契约变化。未部署运行容器；本地共享读取与CLI验证。后续可改进范围脚本的无缩进YAML列表支持；本次仅纠正其生成条目，未新增跟进Issue。
