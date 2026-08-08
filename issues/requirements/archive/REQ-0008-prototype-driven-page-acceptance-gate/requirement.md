---
requirement_id: REQ-0008-prototype-driven-page-acceptance-gate
title: 原型驱动页面开发验收门禁
terminal: multi
version: v1
status: done
owner: product
source: capture.md
priority: P1
parent_requirement:
created_at: 2026-08-08 21:48:39
updated_at: 2026-08-08 23:32:40
---

# 原型驱动页面开发验收门禁

## 背景

MoonBox 当前 Web 前台和管理后台已经存在基于 `prototype.html` 或 `prototype.png` 的页面需求。原型能够表达页面结构、布局密度、组件层级和视觉意图，但如果开发直接进入业务逻辑联调，容易在后期才发现页面骨架、尺寸、间距、弹窗、表格、分页或首屏布局与原型偏离，导致 UI 返工和验收成本升高。

本需求建立原型驱动页面开发验收门禁：当 Web 前台或管理后台页面需求提供 `prototype.html` 或 `prototype.png` 时，开发流程必须先完成原型拆解、UI Skeleton、1440px 截图验收和关键 DOM/CSS 尺寸检查，再进入业务逻辑联调。

## 目标用户

- 页面开发者：需要明确什么时候可以从 UI 骨架进入业务逻辑联调，避免开发顺序倒置。
- 产品与设计协作者：需要基于原型获得可验证的页面还原结果，而不是只依赖主观描述。
- 测试与验收人员：需要稳定的截图证据和 DOM/CSS 检查点，降低 UI 验收歧义。
- Agent 执行者：需要在实现页面型需求时识别原型资产，并按门禁顺序产出可追溯证据。

## 范围

### 包含

- 首期仅覆盖 Web 前台和管理后台页面。
- 仅当页面需求存在 `prototype.html` 或 `prototype.png` 时触发门禁。
- 建立原型拆解要求，明确页面区域、组件层级、布局尺寸、状态占位和交互边界。
- 建立 UI Skeleton 阶段，先完成页面静态骨架、基础响应式布局、关键组件占位和 mock 数据展示。
- 建立 1440px 桌面截图验收，验证 UI Skeleton 与原型在首屏结构、密度和视觉层级上的一致性。
- 建立关键 DOM/CSS 尺寸检查，覆盖容器、表格、分页、弹窗、按钮、间距、字体和滚动区域等高风险元素。
- 明确门禁通过后，才能进入真实 API、权限、状态流转、提交保存等业务逻辑联调。
- 将门禁结论纳入后续需求文档、OpenSpec 任务或验收记录的追溯链路。

### 不包含

- 不覆盖未来微信小程序、移动端、桌面端或其他非 Web 端。
- 不要求没有原型资产的页面补建 `prototype.html` 或 `prototype.png`。
- 不建设通用视觉回归平台或完整截图 diff 服务。
- 不要求对原型进行逐像素 CSS Port；原型用于表达结构、视觉密度和关键尺寸意图。
- 不替代业务功能验收、API 契约验收、安全验收、权限验收或数据库验收。
- 不强制引入新的前端框架、设计工具或第三方 UI 库。

## 功能要求

### FR-001 原型资产识别

页面型需求在进入开发前，系统或 Agent 流程 MUST 检查该需求目录是否存在 `prototype.html` 或 `prototype.png`。

当 Web 前台或管理后台页面存在任一原型资产时，开发任务 MUST 启用原型驱动页面开发验收门禁。

当同一页面同时存在 `prototype.html` 和 `prototype.png` 时，`prototype.html` SHOULD 作为结构、层级和交互意图来源，`prototype.png` SHOULD 作为视觉密度和关键样式对照来源。若两者冲突，需求文档、`prototype/context.md` 或验收文档 MUST 明确优先级。

### FR-002 原型拆解

启用门禁后，开发者或 Agent MUST 先完成原型拆解，再开始页面实现。

原型拆解 MUST 至少识别页面所属端、路由或入口、页面主区域、导航或 Shell 关系、主要组件、数据展示区域、交互控件、弹窗或浮层、加载状态、空状态和错误状态。

原型拆解 SHOULD 记录关键布局尺寸、信息密度、首屏高度、表格或卡片布局、按钮层级、分页位置、弹窗宽度和滚动区域等实现约束。

### FR-003 UI Skeleton 先行

启用门禁的页面 MUST 先完成 UI Skeleton，再进入业务逻辑联调。

UI Skeleton MUST 包含页面静态结构、主要布局区块、关键组件占位、mock 数据或静态样例数据、基础交互占位和必要状态展示。

UI Skeleton 阶段 SHOULD 避免绑定真实 API、复杂权限、持久化写入或不可逆业务操作。若为了渲染页面必须接入少量真实数据，MUST 明确不将其视为完整业务联调完成。

### FR-004 1440px 截图验收

启用门禁的页面 MUST 在 1440px 桌面宽度下完成截图验收。

1440px 截图验收 SHOULD 使用 Playwright 或等价浏览器自动化方式生成。截图必须能够展示页面关键区域，并用于对照原型的布局结构、视觉密度、文本层级、主操作位置和首屏可见内容。

若页面首屏无法覆盖全部关键区域，验收记录 SHOULD 补充滚动区域截图或局部截图，但不得用局部截图替代首屏 1440px 验收。

### FR-005 关键 DOM/CSS 尺寸检查

启用门禁的页面 MUST 完成关键 DOM/CSS 尺寸检查。

关键检查项 SHOULD 根据页面类型选择，至少覆盖以下高风险类别中的适用项：主容器宽度与高度、页面 Shell 内边距、表格列宽、分页 DOM 结构、按钮尺寸、表单控件高度、弹窗宽度、toast 或确认弹窗定位、字体大小、行高、间距、滚动容器和首屏遮挡情况。

检查方式 MAY 使用浏览器自动化断言、computed style 读取、DOM 查询、截图人工复核或组合方式。对于可稳定自动化的尺寸，SHOULD 优先沉淀为测试或脚本断言。

### FR-006 门禁阻断策略

当原型拆解、UI Skeleton、1440px 截图验收或关键 DOM/CSS 尺寸检查未完成时，页面开发 MUST NOT 进入业务逻辑联调。

若存在紧急交付场景需要带风险继续，MUST 在需求或 Change 验收记录中说明未通过项、继续原因、风险影响和补验计划，并由用户或产品负责人确认。

### FR-007 业务逻辑联调准入

只有在 UI Skeleton 门禁通过后，页面开发才 SHOULD 进入真实业务逻辑联调。

业务逻辑联调包括真实 API 调用、鉴权权限、状态变更、提交保存、删除冻结等破坏性操作、错误处理、审计追溯或与后端数据结构强绑定的交互。

进入业务逻辑联调后，后续实现不得破坏已验收的页面骨架和关键尺寸；如业务逻辑导致 UI 明显变化，MUST 重新执行受影响范围的截图与 DOM/CSS 检查。

### FR-008 追溯与报告

启用门禁的页面需求 MUST 在后续文档或任务中记录门禁证据。

门禁证据 SHOULD 包括原型资产路径、原型拆解摘要、UI Skeleton 验收结论、1440px 截图位置、DOM/CSS 检查项和是否允许进入业务逻辑联调。

若门禁不适用，文档 SHOULD 说明原因，例如该需求不是页面型需求，或不存在 `prototype.html` / `prototype.png`。

## UI 约束

- UI Skeleton 必须优先还原原型的页面结构、信息密度、主要视觉层级和操作位置。
- Web 前台页面应尊重品牌、首屏叙事、响应式布局和可访问性要求。
- 管理后台页面应保持高信息密度、清晰表格、稳定分页、克制视觉风格和重复操作效率。
- 原型不得被机械复制为不符合现有 Design System 的孤立 CSS；实现必须兼容当前 Web 前端样式体系。
- 1440px 验收截图中不得出现明显文本重叠、控件遮挡、首屏关键内容缺失或布局漂移。
- 弹窗、toast、表格、分页和主要按钮的尺寸与位置应纳入关键检查，避免后续业务联调时被 CSS 级联破坏。

## 关联需求

- REQ-0004-admin-user-management：历史存在 `prototype.html` 与 `prototype.png`，可作为原型驱动页面验收门禁的既有页面参考。
- REQ-0005-admin-auth-system：已提供后台登录页 `prototype.html`，后续类似页面应先完成 UI Skeleton 验收。
- REQ-0006-admin-crud-list-template：后台 CRUD 列表页模板体系可承接管理后台列表页的 DOM/CSS 尺寸检查项。
- REQ-0007-admin-user-first-login-activation：存在 Web 原型页面，后续开发应先通过 UI Skeleton 与 1440px 验收，再联调激活与冻结业务逻辑。

## 状态块

```yaml
status: archived
generated_at: 2026-08-08 21:48:39
completed_at: 2026-08-08 21:51:55
reviewed_at: 2026-08-08 21:54:56
approved_at: 2026-08-08 21:54:56
source_material:
  - capture.md
  - req-explore: REQ-0008 保持为独立流程门禁需求，不作为后台 CRUD 模板子需求
  - user-decision: 门禁先限定 Web 前台和管理后台，暂不覆盖未来小程序或移动端
next: /req-opsx REQ-0008-prototype-driven-page-acceptance-gate
iteration: sprint-001
```
