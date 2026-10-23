---
title: 需求中心卡片扩宽与迭代标签布局设计
created_at: "2026-10-19 09:31:29"
updated_at: "2026-10-19 09:31:29"
---

# 需求中心卡片扩宽与迭代标签布局设计

## 背景与现状

来源：BUG-0043，Sprint：sprint-010，父需求 REQ-0012-frontend-requirement-center。截图和 computed style 见 BUG capture/root-cause。当前九列为 320px；顶部为 flex，标签 white-space: normal、flex-shrink: 1。

## 根因与修复方案

标签与长 ID 竞争有限宽度且允许折行。共用网格改为 repeat(9, 380px)；标签 nowrap、flex-shrink: 0；ID 设置 min-width: 0 并允许 overflow-wrap: anywhere，使其在剩余宽度折行。优先使用共用样式，无需新增依赖或修改数据模型。

只扩宽仍不能保证超长 ID 的稳定性；只禁止标签换行不能满足用户要求的阅读宽度。因此两项一起实现。不得按阶段逐列复制样式。

## UI Reference Replication Contract

模式为局部一致。事实源优先级：用户确认的 380px 与单行目标 > BUG 附件中的缺陷事实 > 现有页面其余视觉与行为。附件不是 320px 目标稿。

| 组件 | 文本锚点 / selector | 现状 | 目标与采样 |
|---|---|---|---|
| 九阶段网格 | .rc-board | repeat(9, 320px) | repeat(9, 380px)，采样 grid-template-columns、gap、overflow |
| 列头与列体 | .rc-column-head / .rc-column | 九列统一 320px | 统一 380px，对齐，采样 width 与边界 |
| 卡片 | .rc-card | 随列布局 | 随列扩宽，保留 padding、字体、颜色、边框 |
| ID | .rc-card-top strong | 与标签同排竞争宽度 | 在剩余宽度可收缩与折行，采样 min-width、overflow-wrap、边界 |
| Sprint 标签 | .rc-sprint-tag | 可压缩、可换行 | nowrap、flex-shrink: 0，文本单行且不溢出 |

## UI Skeleton 与分批门禁

页面壳 → 横向滚动容器 → 九列网格 → 列头/列体 → 卡片 → ID 与 Sprint 顶部行。已有骨架不新增组件或改变信息层级。实施前用 1440px 基准采样核对本合同；第一批完成共用宽度与顶部行，第二批完成九阶段×1440×900/768×900 双视口及交互回归。

本次不新增或调整动作按钮、FAB、footer、工具栏或 modal；既有动作族仅回归打开/关闭，不执行真实状态迁移。若实施发现必须改变动作布局，先补齐动作到 modal/selector/状态/证据矩阵。

## 测试策略与证据

采用 BUG acceptance.md 的 AC-001 至 AC-005：九列宽度、长 ID 标签单行、超长 80 字符无空格 ID、有无标签、三类对象、空列、首末列横向滚动与既有入口。真实产品观察与合成极端样本分别记录，不将 DOM 静态或单元测试当作视觉通过。

截图、computed style 和回归结果存入本 Change evidence/acceptance/。执行 apply 时预检环境并建立自动验收计划，逐 AC 映射证据；本次只定义计划，不声明通过。Mock/API 边界：真实页面用于运行态观察；极端 ID 用隔离夹具，不写持久业务数据；无 API 替换与契约变更。

## 风险与回滚方案

380px 增加横向滚动距离，需检查末列可达。标签禁止收缩后要验证长 ID 不覆盖标签。样式回滚无需数据库操作；回滚后原缺陷仍存在。

## 文档与观测边界

同步 BUG、Sprint 和父需求中实际受影响的 UI 契约及验收口径；不重开父需求归档状态，不直接改 openspec/specs。原型存在时按最终一致性清单核对。

product_data_collection_observability:
- status: N/A
- affected_layers: web_ui
- reason: 仅 CSS 布局，不改变 usage_events、request_logs、Task Trace、请求封装、API 或存储。
- validation: 五项 UI AC 验证布局及既有交互；API/DB/OpenAPI/客户端生成与链路字段测试不适用。
