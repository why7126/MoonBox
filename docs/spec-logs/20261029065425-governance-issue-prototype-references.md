---
title: Issue 迁移原型引用保护
created_at: 2026-10-29 06:54:25
updated_at: 2026-10-29 06:54:25
---

# Issue 迁移原型引用保护

## 迭代目标与变更
用户明确授权由 explore 切换 spec-opt，实现 Issue 原型引用预检与后检。Change 为 guard-issue-prototype-references；用户选择 sprint-014，估算1人天，容量34/30，保留超容量风险。

共享模块识别有效、历史和示例引用，检查本地原型资源与关联 Change/Sprint，迁移前模拟、迁移后复核。直接入口与归档包装入口在写入前检查；dry-run 零写入，部分阻断隔离，后检失败可重试。

## 更新文件与影响范围
- scripts/workflow_sync/prototype_references.py
- scripts/promote-issue-stage.py、scripts/promote-issues-for-archive.py
- scripts/test_prototype_references.py
- scripts/README.md、rules/issues-lifecycle.md、.agents/skills/workflow-sync/SKILL.md
- 当前 Change 与 sprint-014 派生文档、本日志及索引

API、DB、Web、客户端、管理端、Orval、Docker Compose 和产品权限均不变，无需生成客户端或执行数据库迁移。只修改治理行为，不改正式规格。

## 验证结果
隔离回归及原有生命周期/评审迁移测试通过，最终计数和治理门禁见当前 Change trace 与自动验收证据。真实 REQ-0042 当前目录只读检查零阻断；首次探针暴露 prototype.html 路径截断，已修复提取边界并新增回归，未改动该需求目录。Docker reap 因 daemon 不可用受阻，未创建或删除资源，不是静态验证依赖。

## 边界与后续建议
仅覆盖明确静态引用，远程 URL、动态 JS、根路径、HTML base 和页面渲染不属于完整性通过证明。交付效果待后续真实迁移观察，未宣称耗时或 Token 收益。未自动创建后续 Issue/Change；正式归档须另行授权。
