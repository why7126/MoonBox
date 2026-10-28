---
title: Issue 生命周期阶段同步与校验补齐
created_at: 2026-10-27 09:21:37
updated_at: 2026-10-27 09:21:37
---

# Issue 生命周期阶段同步与校验补齐

## 迭代目标与证据
BUG-0068 归档后主文档及 capture 的生命周期仍为 plan，trace/注册表已为 archive；旧扫描返回零残留。归因为阶段投影与校验覆盖遗漏，非原归档失败。

## 变更摘要与更新文件
共享脚本 scripts/workflow_sync/issue_stage.py；接入 promote-issue-stage.py、issue_subdocuments.py、issue_status_residuals.py、engine.py、promote-issues-for-archive.py。同步 rules/issues-lifecycle.md、scripts/README.md 和 workflow-sync 技能引用，新增 tests/unit/test_issue_lifecycle_stage.py。

## 定向维护
先预览两字段 plan→archive，再运行仅 reconcile 分支修正 BUG-0068 的 bug.md、capture.md，同时刷新 updated_at。原 Issue 与原 Change 共41个文件快照中，39个文件哈希保持一致；两份目标文档除此之外不扩展修复。未重跑归档，未改原 trace、验收、manifest、归档日志或正式规格。

## 验证结果
17项新增回归与31项相关回归合计48项通过；覆盖REQ/BUG各阶段、迁移、预览、非法值阻断、历史正文保护及幂等。静态门禁结果见本次 Change trace 验证记录。真实维护为两字段补正，不作为产品运行态行为改善证据。

## 影响与边界
纯治理 Change fix-issue-lifecycle-stage-sync，sprint-014新增估算1人天，总28/30人天，缓冲2人天。API、数据库、Web、客户端、管理端、Orval、Docker Compose、安全及运行态观测均不涉及。未重启服务。临时Docker到期扫描受 daemon 连通限制，无新建资源，不宣称全局零残留。

## 授权与后续建议
本次为用户明确单次授权，不以自动优化候选预算替代授权。反馈分类为治理方法缺陷及项目元数据残留；规则已有迁移要求但未覆盖镜像。新实现自后续脚本调用生效，收益状态 observing，未获得精确Token，不宣称收益确认。没有额外创建 follow-up Issue/Change。
