---
purpose: 原型驱动 UI 开发门禁治理优化提案
content: 建立带 prototype 页面从需求完善到归档的原型拆解、UI Skeleton、1440px 视觉验收和 REQ 最终一致性回填机制
created_at: 2026-08-08 21:08:00
updated_at: 2026-08-08 22:01:14
owner: MoonBox 产品团队
source_requirement: REQ-0008-prototype-driven-page-acceptance-gate
---

# 原型驱动 UI 开发门禁治理优化

## 背景

当前 UI 类需求已经要求读取知识库并写入横切 AC，但带 `prototype/` 的页面在进入实现时仍缺少连续门禁：原型意图没有被结构化拆解为实现骨架，1440px 桌面视觉验收不够明确，验收返修后的 REQ 文档与实际实现也缺少最终一致性检查。

## 目标

- 将带 prototype 的页面纳入统一的 Prototype-driven UI Gate。
- 在 `/req-complete` 阶段沉淀原型拆解与 UI Skeleton 要求。
- 在 `/req-opsx` 阶段把原型冲突、Skeleton 和 1440px 验收写入 Change。
- 在 `/opsx-apply` / `/opsx-modify` 阶段先完成 Skeleton 与 1440px 视觉验收，再标记任务完成。
- 在 `/opsx-archive` 和 Workflow Sync 阶段完成 REQ 文档最终一致性回填检查。

## 非目标

- 不修改 `src/` 业务实现。
- 不引入新的前端框架或视觉风格。
- 不归档正式 `openspec/specs/`，本 Change 仅新增 active delta。

## 影响范围

- `issues/requirements/review/REQ-0008-prototype-driven-page-acceptance-gate/`
- `.agents/skills/req-complete/SKILL.md`
- `.agents/skills/req-opsx/SKILL.md`
- `.agents/skills/opsx-apply/SKILL.md`
- `.agents/skills/opsx-modify/SKILL.md`
- `.agents/skills/opsx-archive/SKILL.md`
- `.agents/skills/workflow-sync/SKILL.md`
- `rules/ui-design.md`
- `docs/knowledge-base/README.md`
- `docs/knowledge-base/best-practices/prototype-driven-ui-gate.md`

## 关联需求

- `REQ-0008-prototype-driven-page-acceptance-gate`：原型驱动页面开发验收门禁，首期限定 Web 前台和管理后台页面，要求存在 `prototype.html` 或 `prototype.png` 的页面先完成原型拆解、UI Skeleton、1440px 截图验收和关键 DOM/CSS 尺寸检查，再进入业务逻辑联调。
