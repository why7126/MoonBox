---
requirement_id: REQ-0021-markdown-editor-vditor-enhancement
status: in_sprint
priority: P1
created_at: 2026-08-19 11:30:07
updated_at: 2026-08-19 12:23:54
lifecycle:
  captured: 2026-08-19 11:30:07
  generated: 2026-08-19 11:32:02
  completed: 2026-08-19 11:36:10
  reviewed: 2026-08-19 11:41:07
  approved: 2026-08-19 11:41:07
iteration: sprint-003
openspec_changes:
  - change_id: update-markdown-editor-vditor-enhancement
    type: update
    status: applied
related_requirements:
  - REQ-0020-requirement-center-card-document-actions-ai-chat
lifecycle_stage: review
knowledge_base_refs:
  - docs/knowledge-base/best-practices/admin-media-upload-chain.md
  - docs/knowledge-base/retrospectives/sprint-002-retrospective.md
cross_cutting_tags:
  - media-upload
prototype_refs:
  - path: issues/requirements/review/REQ-0021-markdown-editor-vditor-enhancement/prototype/web/context.md
    role: ui-decomposition
prototype_gate:
  decomposition: done
  ui_skeleton: done
  visual_acceptance_1440: done
  req_final_consistency: done
related_change: update-markdown-editor-vditor-enhancement
---

# REQ-0021-markdown-editor-vditor-enhancement Trace

## 当前状态

- 状态：in_sprint
- 优先级：P1
- 阶段：review
- 关联 Sprint：sprint-003
- 关联 Change：update-markdown-editor-vditor-enhancement
- 父级/关联需求：REQ-0020-requirement-center-card-document-actions-ai-chat
- Knowledge-base 标签：media-upload
- Prototype Gate：decomposition done；UI Skeleton / 1440px 视觉验收 / 最终一致性已由 Change 实现证据完成

## Knowledge-base Cross-cutting Report

| 标签 | 引用文档 | 写入 acceptance 的 AC 条数 |
|---|---|---:|
| media-upload | `docs/knowledge-base/best-practices/admin-media-upload-chain.md` | 7 |

最近复盘参考：`docs/knowledge-base/retrospectives/sprint-002-retrospective.md` 提醒 Docker/media-upload 验收必须使用动态端口、脚本化测试身份和隔离证据，已转化为 AC-XCUT-005 与 AC-XCUT-006。

## Readiness Report

| 项 | 结果 | 说明 |
|---|---|---|
| Readiness | Ready | requirement、user-stories、business-flow、acceptance、trace 与 prototype context 已补齐 |
| Knowledge-base gate | Pass | media-upload best-practice 已读并转化为横切 AC |
| Cross-cutting tags | media-upload | 上传状态机、即时回显、Docker 端口和测试身份已覆盖 |
| Prototype Gate | Ready | 已完成原型拆解、UI Skeleton、1440px 视觉截图和 computed style 证据 |

## Apply Evidence

| 项 | 证据 |
|---|---|
| 实现 Change | `openspec/changes/update-markdown-editor-vditor-enhancement` |
| 视觉截图 | `openspec/changes/update-markdown-editor-vditor-enhancement/evidence/20260819-vditor-editor-visual/01-capture-vditor-editor-1440.png`、`02-image-upload-controlled-failure-1440.png` |
| 样式证据 | `openspec/changes/update-markdown-editor-vditor-enhancement/evidence/20260819-vditor-editor-visual/computed-vditor-editor-1440.json` |
| API 边界 | 当前无认可需求文档图片上传接口，图片入口受控失败，不写入本机路径、私有对象地址或凭据 |

## 变更记录

| 时间 | 事件 | 说明 |
|---|---|---|
| 2026-08-19 12:23:54 | /opsx-apply | Change `update-markdown-editor-vditor-enhancement` apply 完成，待 archive。 |
| 2026-08-19 11:30:07 | req.capture | 记录需求：为需求中心 `capture.md` 引入 Vditor 增强编辑体验，MVP 限定为采集阶段可编辑文档。 |
| 2026-08-19 11:32:02 | req.generate | 生成 `requirement.md`，需求进入 draft 状态。 |
| 2026-08-19 11:36:10 | req.complete | 补齐 user-stories、business-flow、acceptance 与 prototype context，嵌入 media-upload 横切 AC，需求进入 pending_review。 |
| 2026-08-19 11:41:07 | req.review | 评审通过，需求进入 approved，下一步纳入 Sprint。 |
| 2026-08-19 12:01:07 | req.opsx | 创建 OpenSpec Change `update-markdown-editor-vditor-enhancement`，状态为 proposed。 |
| 2026-08-19 12:22:00 | opsx.apply | Change 已实现并验证，等待人工验收或归档。 |

- 阶段迁移：plan → review（/req-review --approve）
