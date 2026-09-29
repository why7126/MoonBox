---
bug_id: BUG-0022-requirement-center-html-preview-auth-lost
title: 需求中心卡片 HTML 预览直开受保护接口导致认证失败
status: done
created_at: '2026-09-14 15:10:06'
updated_at: 2026-09-14 18:20:41
related_requirement: REQ-0012-frontend-requirement-center
related_bug: null
owner: 产品团队
source: explore
lifecycle_stage: archive
iteration: sprint-006
openspec_changes:
  - change_id: fix-requirement-center-html-preview-auth-lost
    status: archived
lifecycle:
  captured: '2026-09-14 15:10:06'
  generated: '2026-09-14 15:12:25'
  completed: '2026-09-14 15:18:00'
  reviewed: '2026-09-14 15:22:33'
  approved: '2026-09-14 15:22:33'
related_change: fix-requirement-center-html-preview-auth-lost
severity: medium
---

# BUG-0022-requirement-center-html-preview-auth-lost Trace

## 来源与范围

用户授权 `/bug-capture`；承接前序 `/explore` 对需求中心 HTML 预览失败的只读分析。范围限定为需求中心卡片 HTML / prototype 文档预览链路，不包含 Markdown 抽屉读取、文档保存、对象存储头像读取或 Chat 会话权限。

## 证据入口

- capture.md：用户现象、复现步骤、期望/实际、代码路径证据和初步修复方向。
- `src/backend/app/api/v1/requirement_center.py`：HTML 预览接口和 `get_reader` 项目作用域/鉴权依赖。
- `src/backend/app/chat/api.py`：401/403 脱敏错误响应映射。
- `src/web/src/components/workbench/governanceApi.ts`：`scopedUrl()` 项目作用域参数拼接。
- `src/web/src/pages/catalog/RequirementCenterPage.tsx`：HTML / `new-tab` 分支直接 `window.open(document.url)`。
- `src/web/src/requirement-center.test.tsx`：现有测试仍断言裸 preview URL 打开。

## 变更记录

| 时间 | 命令 | 说明 |
|---|---|---|
| 2026-09-14 18:20:41 | /opsx-archive | Change `fix-requirement-center-html-preview-auth-lost` 已归档，状态同步完成。 |
| 2026-09-14 15:56:44 | /opsx-apply | Change `fix-requirement-center-html-preview-auth-lost` apply 完成，待 archive。 |
| 2026-09-14 15:56:24 | /opsx-apply | Change `fix-requirement-center-html-preview-auth-lost` opsx.progress 已同步；研发中，未宣告完成。 |
| 2026-09-14 15:52:38 | /opsx-apply | Change `fix-requirement-center-html-preview-auth-lost` opsx.start 已同步；研发中，未宣告完成。 |
| 2026-09-14 15:39:22 | /bug-opsx | 创建 OpenSpec Change `fix-requirement-center-html-preview-auth-lost`，纳入 sprint-006 修复执行链路。 |
| 2026-09-14 15:22:33 | /bug-review --approve | 评审通过，批准修复；后续先纳入 Sprint，再创建修复 Change。 |
| 2026-09-14 15:19:10 | /bug-complete | BUG-0022-requirement-center-html-preview-auth-lost 已完成文档补齐，状态同步为 pending_review。 |
| 2026-09-14 15:13:00 | /bug-generate | BUG-0022-requirement-center-html-preview-auth-lost 已生成 bug.md，状态同步为 draft。 |
| 2026-09-14 15:10:06 | /bug-capture | 创建单条采集记录，严重度 medium，关联 REQ-0012-frontend-requirement-center，记录 HTML 预览 Bearer 丢失与项目作用域缺失风险。 |

- 阶段迁移：plan → review（/bug-review --approve）
- 2026-09-14 18:20:41 workflow-sync：状态同步为 done（Change archived）
- 归档同步：/opsx-archive fix-requirement-center-html-preview-auth-lost
