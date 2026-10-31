---
bug_id: BUG-0072-standalone-change-ready-dev-without-sprint
title: 独立变更排期阶段与动作缺陷评审
status: done
severity: medium
created_at: '2026-10-31 09:01:53'
updated_at: 2026-10-31 10:53:17
reviewer: 用户明确批准，AI执行复核
---
# 独立变更排期阶段与动作缺陷评审

## 评审结论
approved：用户执行bug-review --approve，确认修复独立Change未排期提前进入待开发的问题。维持medium，不采用hotfix。

## 检查结果
- [x] 根因充分：既有真实截图/刷新观察、代码分支和四类隔离样本相互印证；根因证据门禁通过。
- [x] 分级合理：规划语义和操作入口问题，现有执行阻断仍有效，无越权证据。
- [x] 验收明确：acceptance.md八项覆盖分列、动作、权限、状态刷新与真实产品观察；修复验收尚未执行。
- [x] 修复范围明确：未开始的独立proposed Change，保留canonical状态、历史执行事实、REQ/BUG既有流程与开发准入。

## 批准的细化方案
无归属显示迭代规划和待纳入迭代，主动作为加入迭代；唯一有效归属显示待开发和开始开发。冲突/失效留在迭代规划并明确阻塞，提供只读核对归属入口；不自动选择或修复Sprint。加入迭代复用现有治理入口，不以点击代替容量、权限及同步门禁。

## 关联与风险
BUG-0039仍独立处理有效归属误报，本次不得替代其评审或扩大修复。产品API投影、Web主动作及Agent Workflow需在Change设计复核契约与观测影响；无证据不得宣称新增字段或DB迁移必要。

## 后续门禁
先sprint-propose正式纳入并同步in_sprint，再bug-opsx生成修复Change。本评审不等于已排期、已开发或验收通过。
