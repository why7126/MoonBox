---
requirement_id: REQ-0053-chat-scalable-execution-storage
title: Chat 无默认运营配额与大规模工作区持续执行局部交互原型说明
created_at: '2026-10-25 21:59:37'
updated_at: '2026-10-25 21:59:37'
---

# Chat 无默认运营配额与大规模工作区持续执行局部交互原型说明

## 定位与事实源

这是前台 Chat 新增状态的评审线框，不是当前运行截图或一对一复刻请求。业务语义优先级：requirement.md → acceptance.md → 本说明 → prototype.html。既有 Chat 页面壳和规则 token 复用；附件失败截图仅为历史故障证据，不要求复制旧错误表现。保真模式为局部一致，新增反馈区允许按统一组件落实。

## 页面与区域拆解

页面为既有 Chat 对话／轨迹中的执行详情局部区域。组件层级：运行状态容器 → 阶段与持久化摘要 → 已保存结果入口 → 资源原因与可展开详情 → 恢复操作区。页面壳、导航、模型选择器、会话权限均保持既有语义，线框不替代完整工作台。

## 状态与数据依赖

| 状态 | 可见事实 | 动作 |
|---|---|---|
| preparing | 扫描与基线校验进度；尚未启动模型 | 查看进度 |
| running | 执行中；已持久化段与加载状态 | 查看已保存内容 |
| blocked-before-start | 资源不足；尚未执行 | 重新检查资源并续接准备 |
| interrupted | 运行中断；已保存范围与缺口 | 查看已保存内容、核验原轮次 |
| unknown | 原执行终态不明 | 核验；直接重试禁用 |
| recovering | 原轮次核验或准备续接中 | 禁用重复提交 |
| completed | 执行终态与成果完整性分开呈现 | 分段查看结果 |

以上依赖真实轮次阶段、可信终态、持久化游标、完整性、资源诊断与恢复准入；原型全部 Mock，仅演示信息结构，不调用 API，不写业务数据。

## 动作与 selector 矩阵

| 动作 | 浮层类型 | 原型 selector | 状态 | 实现验收 |
|---|---|---|---|---|
| 选择示例状态 | N/A，仅评审控制器 | #scenario | selected | 不进入正式产品 |
| 查看已保存内容 | inline-expanded | #saved、#content | loading／loaded／error | 分页回读、键盘与截图 |
| 查看原因 | inline-expanded | #reason | closed／open | 稳定错误类别与脱敏 |
| 重新检查／核验原轮次 | N/A，原位反馈 | #recover | enabled／busy／disabled／error | 幂等、真实恢复与焦点 |

正式 selector 与组件入口在 Change UI Contract 中映射，不把原型 ID 冒充现有源码 selector。复用现有对话与 ExecutionPanel 组件族，不新增确认弹窗；若设计引入弹窗，先补矩阵和关闭／键盘路径。

## 断点、样式与验收焦点

1440px 局部卡片最大宽度 960px，内容左右留白；1024px 自适应；390px 单列，动作换行，长内容在自身区域滚动。浅色使用 #F4F6FA／#FFFFFF／#202636／#B9832E／#DDE3EE；深色使用规则对应 token。圆角 6px，正文 14px、行高 1.45，间距 12／16／24px。状态文字不单靠颜色传达。

样式采样 selector：#panel、#status、#content、#recover；属性包括字体、字号、行高、padding、gap、border、color、background、overflow、width。正式实现采用项目 token；1440px 重点核对阶段、原因与动作层级；窄视口核对换行、焦点与局部滚动。

## 原型门禁与产物状态

原型拆解、UI Skeleton 首轮确认、局部生产组件截图、computed style 与最终一致性核对已完成，见Change evidence/visual-review.md。本阶段 PNG 暂不要求，HTML 为评审线框；不得将其称为真实产品通过。实现阶段视觉证据已补齐，整体就绪以Change当前验收清单为准。

## 实现一致性核对（2026-10-26）

UI Skeleton 已于2026-10-26获用户确认。生产 selector 为 chat-storage-panel、chat-storage-stage、chat-storage-reason、chat-saved-result、chat-recovery-action、chat-result-page。30组局部组件截图与样式采样在 Change evidence/visual，键盘Esc与恢复拒绝另附；使用生产组件+隔离真实API+合成身份，真实模型轮次独立取证。原型HTML继续作为设计输入，不回写成假生产数据。 验证结论以 Change 当前 acceptance-plan 和证据清单为准。
