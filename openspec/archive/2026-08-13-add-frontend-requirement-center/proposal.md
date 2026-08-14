---
change_id: add-frontend-requirement-center
status: proposed
type: add
source_requirement: REQ-0012-frontend-requirement-center
source_sprint: sprint-002
created_at: 2026-08-10 13:10:06
updated_at: 2026-08-10 13:10:06
---

# 新增 MoonBox 前台需求中心

## 背景

MoonBox 已具备需求、BUG、Sprint、OpenSpec 和 Workflow Sync 治理链路，但前台用户尚缺少一个统一查看与操作 Requirement/Bug 全生命周期的产品化工作台。REQ-0012 已完成评审并纳入 sprint-002，需要将既有产品原型转为 OpenSpec Change，作为后续实现和验收的契约。

## 变更内容

- 新增 MoonBox 前台需求中心页面，提供 9 阶段 Requirement/Bug 生命周期看板。
- 新增看板统计、搜索、对象类型筛选、负责人/优先级/Sprint 筛选和横向滚动看板交互。
- 新增 Requirement/Bug 卡片信息展示、阶段主动作映射、文档缺失阻断和验收中归档入口门禁。
- 新增前台侧边栏、用户菜单、主题切换、Hover 切换空间浮层和空间设置弹窗。
- 承接 REQ-0012 目录中的 `prototype.html`、`prototype.png`、`prototype-context.md`，要求实现阶段先完成 UI Skeleton，再执行 1440px 视觉验收。
- 承接 knowledge-base 横切门禁：prototype-driven UI Gate 与空间设置弹窗宽度/滚动验收。

## 能力范围

### 新增能力

- `web-catalog-requirement-center`: MoonBox 前台需求中心，包括 Requirement/Bug 生命周期看板、空间上下文交互、阶段动作门禁、原型驱动 UI 验收和前台视觉约束。

### 修改能力

- 无。

## 影响范围

```yaml
impact:
  backend: false
  web: true
  miniapp: false
  admin: false
  database: false
  storage: false
  api: false
capabilities:
  new:
    - web-catalog-requirement-center
  modified: []
source:
  requirement: REQ-0012-frontend-requirement-center
  sprint: sprint-002
  prototype:
    - issues/requirements/review/REQ-0012-frontend-requirement-center/prototype/prototype.html
    - issues/requirements/review/REQ-0012-frontend-requirement-center/prototype/prototype.png
    - issues/requirements/review/REQ-0012-frontend-requirement-center/prototype/prototype-context.md
```
