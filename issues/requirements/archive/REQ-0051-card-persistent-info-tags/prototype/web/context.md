---
requirement_id: REQ-0051-card-persistent-info-tags
title: 卡片常驻信息标签原型说明
created_at: "2026-10-22 13:44:14"
updated_at: 2026-10-22 19:20:00
---

# 卡片常驻信息标签原型说明

## 原型定位与事实源

局部一致模式，仅设计需求中心现有卡片的标签增量，不复刻整页。业务规则以 requirement.md、business-flow.md 为准；现有 RequirementCenterPage.tsx 的卡片和文档抽屉作为结构基础；prototype.html 仅展示增量布局和交互。全部数据为合成 Mock，不调用 API，不表示产品已实现。

## 页面与组件拆解

页面为 /requirements；原型包含主题切换、四种数据组合、根因抽屉。
组件树：展示容器 → 卡片 → ID/阶段 → 标题 → 等级/负责人/根因按钮/人天 → 文档入口 → 动作区域；抽屉为共享独立层。
不重新设计侧栏、筛选、统计、卡片主动作及真实 Markdown 编辑器。

## 状态与数据矩阵

无值、仅人天、仅根因、两者都有；人天 0/小数/缺失，根因待确认/已确认/冲突；阶段覆盖九阶段及已完成；抽屉 loading/成功/缺失/无权限/错误交由产品验收，原型仅演示成功。
数据依赖：对象身份与阶段、owner、等级、有效 scope estimate、根因状态/有效内容/文档读取权限。

## Selector 与动作映射

| 对象 | 现有锚点 | 目标选择器候选 | 状态/证据 |
|---|---|---|---|
| 卡片/标签 | .rc-card / .rc-card-tags | 保留现有类 | 四种组合及顺序截图 |
| 根因按钮 | 新增 | [data-testid="root-cause-tag"] | 待确认/已确认/冲突；打开共享 Markdown 抽屉 |
| 人天 | 新增 | [data-testid="person-days-tag"] | 只读、零/小数/缺失 |
| 根因抽屉 | 现有文档打开逻辑 | [data-testid="root-cause-document"] 候选 | loading/正文/权限/错误；点击、Esc、外部退出及焦点返回 |

根因动作一次覆盖鼠标、键盘、成功和失败族，无新增确认弹窗。若使用外部点击监听，验证 capture 阶段或等价机制能处理内部 stopPropagation。

## 响应式与样式采样

1440px 检查四卡布局和原看板列宽，390px 检查卡片单列及抽屉自适应；示意断点为 700px，产品维持已有看板滚动策略。标签采用可换行 flex、6px 间距、10px 字号、无描边；最终值与现有 Token 对齐。
采样标签 font-size、line-height、padding、gap、border、background、color、overflow；抽屉 width、position、z-index 与焦点样式。深浅主题均检查文字可读性。

## 门禁与图片策略

原型拆解完成。HTML 为评审事实源，PNG 本轮不要求导出；实际产品 UI Skeleton、1440px 视觉截图与 computed style 在 Change 实现阶段采集，当前均待完成。本原型不构成视觉验收通过，归档前按 AC-PROTOTYPE 完成最终一致性。

## Change冲突决议

add-card-persistent-info-tags保留既有Markdown抽屉桌面420—760px可拖拽和移动全宽；HTML固定560px仅演示，不能用于削减既有行为。以Change设计明确的这一例外实施与验收。

## 实施一致性核对（2026-10-22）

标签顺序、人天只读提示及共享根因抽屉已按Change设计实现，九阶段×双视口×双主题隔离证据已采集。API与OpenAPI/Orval、公开手册已同步；数据规则与本需求子文档一致。本地业务观察及隔离真实服务跨阶段、更新、删除、切换和撤权观察已补齐，逐AC结果由当前验收报告签认；证据入口为 openspec/changes/add-card-persistent-info-tags/evidence/acceptance/implementation-review.md。

## 本次返修原型决议

人天按有效非负值d分档：S为0≤d≤1，M为1<d≤3，L为3<d≤5，XL为5<d≤10，XXL为d>10；显示“档位·数值人天”（如“M·3人天”），不含“开发”前缀。S青、M蓝、L紫、XL橙、XXL玫红，保留精确值和“档位 · 预估开发数值人天”提示；缺失/非法值隐藏。新旧标签共用字体、10px字号、1.2行高、3px 8px内边距、20px圆角且无描边；根因保留状态色、点击与focus-visible提示。旧截图仅为历史参考，以当前HTML和返修computed style为准。

分隔点展示细则：去除两侧普通空格，使用独立分隔点左右各2px固定间距；其余标签样式及根因交互保持不变。
