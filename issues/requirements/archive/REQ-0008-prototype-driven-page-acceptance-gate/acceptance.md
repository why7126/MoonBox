---
requirement_id: REQ-0008-prototype-driven-page-acceptance-gate
acceptance_status: passed
created_at: 2026-08-08 21:51:55
updated_at: 2026-08-08 23:37:38
---

# 验收清单

## 功能 AC

- [ ] AC-001 Web 前台或管理后台页面需求存在 `prototype.html` 或 `prototype.png` 时，后续开发任务必须标记启用原型驱动页面开发验收门禁。
- [ ] AC-002 小程序、移动端、桌面端或其他非 Web 端需求不得被本门禁阻断；若未来纳入，必须另行评审需求范围。
- [ ] AC-003 无原型资产的页面需求不得被要求临时补建原型作为本门禁前置条件，但必须记录“门禁不适用：无 prototype.html/prototype.png”。
- [ ] AC-004 同时存在 `prototype.html` 与 `prototype.png` 时，验收记录必须说明 HTML 用于结构/交互意图、PNG 用于视觉/密度对照；冲突时必须记录优先级。
- [ ] AC-005 启用门禁的页面必须完成原型拆解，拆解内容至少覆盖页面入口、端类型、布局区块、主要组件、状态占位、关键交互和高风险尺寸点。
- [ ] AC-006 启用门禁的页面必须先完成 UI Skeleton，且 UI Skeleton 至少包含静态结构、关键组件占位、mock 数据或静态样例、基础状态展示。
- [ ] AC-007 UI Skeleton 通过前，不得进入真实 API、权限、状态变更、提交保存、删除冻结等业务逻辑联调。
- [ ] AC-008 启用门禁的页面必须在 1440px 桌面宽度下生成截图并记录截图位置、验收结论和未覆盖区域。
- [ ] AC-009 1440px 截图中不得出现明显文本重叠、控件遮挡、首屏关键内容缺失、布局漂移或与原型结构明显不一致。
- [ ] AC-010 启用门禁的页面必须完成关键 DOM/CSS 尺寸检查；检查项必须按页面类型覆盖主容器、表格、分页、按钮、弹窗、toast、字体、间距和滚动区域中的适用项。
- [ ] AC-011 可稳定自动化的 DOM/CSS 检查必须优先使用浏览器自动化、computed style 读取、DOM 查询或等价断言沉淀；无法自动化的项必须保留人工验收说明。
- [ ] AC-012 门禁未通过时必须默认阻断业务逻辑联调；若用户或产品负责人确认带风险继续，必须记录未通过项、继续原因、风险影响、补验计划和确认人。
- [ ] AC-013 业务逻辑联调后若改变已验收 UI 区域，必须重新执行受影响范围的 1440px 截图验收和 DOM/CSS 尺寸检查。
- [ ] AC-014 后续 `/req-opsx` 生成 Change 时，design 或 tasks 必须引用本 REQ 的门禁顺序，并把原型拆解、UI Skeleton、截图验收和 DOM/CSS 检查转化为可执行任务。

## 横切 AC（knowledge-base）

> 来源：`docs/knowledge-base/best-practices/admin-list-page-consistency.md`、`docs/knowledge-base/best-practices/admin-modal-width-css-cascade.md` — 预防管理后台页面 UI 复发类缺陷

- [ ] AC-XCUT-001 启用门禁的管理后台 CRUD 列表页必须检查分页 DOM：总数位于左侧，翻页、页码、“每页显示”文案和条数下拉位于右侧。
- [ ] AC-XCUT-002 启用门禁的管理后台页面必须检查成功和失败反馈使用 fixed toast，且不得引发布局位移或挤压列表、分页、弹窗内容。
- [ ] AC-XCUT-003 启用门禁的管理后台状态变更页面必须使用设计系统确认弹窗，不得以浏览器原生确认框替代。
- [ ] AC-XCUT-004 启用门禁的管理后台状态变更页面必须检查无 `window.confirm` 调用。
- [ ] AC-XCUT-005 启用门禁的管理后台列表页必须检查行内操作列在横向滚动或列较多时仍可访问。
- [ ] AC-XCUT-006 启用门禁的管理后台弹窗页面必须检查 TSX 或模板实现中不存在通用 `modal-card` 与专属宽度类并存导致的宽度覆盖风险。
- [ ] AC-XCUT-007 启用门禁的管理后台弹窗页面必须通过浏览器 computed style 验收最终宽度与设计预期一致。
- [ ] AC-XCUT-008 启用门禁的管理后台弹窗页面必须检查低视口下弹窗 body 可滚动，底部主操作和取消操作可访问。
- [ ] AC-XCUT-009 启用门禁的管理后台弹窗页面必须检查遮罩不吞掉内部滚动，也不导致页面主体误滚动。
- [ ] AC-XCUT-010 启用门禁的管理后台弹窗页面必须检查必填字段、错误提示和底部操作区不得互相遮挡。

## 验收结果回填

```yaml
acceptance_status: passed
accepted_at: 2026-08-08 23:37:38
accepted_by: workflow-sync
source_change: enforce-prototype-driven-ui-gate
source_sprint: sprint-001
evidence: []
failed_items: []
source_event: sprint.archive
notes: 由 Workflow Sync 根据 Change/Sprint 状态回填。
```

