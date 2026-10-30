---
requirement_id: REQ-0055-sprint-authorized-worktree-merge
owner: 产品团队
created_at: '2026-10-29 00:02:50'
updated_at: '2026-10-29 00:02:50'
title: 继承迭代操作权限的工作区成果确认合入原型上下文
---
# 继承迭代操作权限的工作区成果确认合入原型上下文

## 定位与事实源

此为新方案的需求评审交互原型，不是既有页面一对一复刻，不声明产品已实现。业务优先级：requirement.md 与 acceptance.md > 本 context.md > HTML 示例。布局与 token 参照 rules/ui-design.md、src/shared/design-system/tokens/colors.ts；全部数据 Mock，无网络调用、无真实写入、无真实鉴权。页面挂在现有空间/工作区或执行详情入口，最终路由由 Change 设计确定。

## 页面与组件拆解

单个详情页：空间导航 -> 标题及主题切换 -> 状态容器 -> 摘要面板 -> 操作栏 -> 浮层族。关键区域为 summary、status、actions；浮层内为 header/body/footer。具体业务字段与动作见 business-flow.md 动作矩阵。静态 HTML 为便于评审统一用 dialog 演示浮层内容；popover/drawer 的最终形态、轻量选择即生效、权限与 API 行为以业务矩阵为准，不能照搬演示按钮逻辑上线。

## 状态矩阵与数据依赖

| 状态 | 页面与动作 | 依赖 |
|---|---|---|
| 正常 | 展示身份、版本、业务状态与可用操作 | 服务端详情与能力结果 |
| 加载中 / 执行中 | 显示进度，禁止重复提交 | 请求/操作身份与阶段 |
| 空态 | 说明未有工作区/恢复点/候选，合法时提供创建入口 | 当前范围内结果集合 |
| 无权限 | 说明缺少操作权限，禁写但不泄漏隐藏对象详情 | 服务端能力与可见性 |
| 版本过期 | 保留旧结果提示已过期，重新预检/验证 | 前后版本和候选身份 |
| 操作失败 | 可读错误与恢复入口，不宣称回滚 | 持久操作结果 |

HTML 状态选择器用于评审，不作为真实接口实现。每个动作保留稳定 data-testid，浮层根加 -dialog；实现映射到正式 selector 时保留测试映射。对拒绝、迟到响应、重复提交、部分成功按 acceptance 验证。

## 断点与视觉焦点

1440×900：216px 导航、32px 内容边距、14px 正文、24px 标题、16px 面板间距，摘要和状态可扫读；1024×600：浮层内容滚动，footer 可达；390×844：导航折叠、16px 内容边距、按钮换行、文字不溢出。浮层宽度 min(880px, viewport - 32px)，圆角6px，边框1px。采样字体、字号、行高、宽高、gap、padding、border、颜色、overflow、position、z-index；深浅主题均验证。原型未使用外部字体下载，生产沿用项目字体资源。

## 交互与证据计划

关闭按钮、取消与 Esc 均可退出；关闭不撤销已接受业务操作。正式实现采用共享组件并覆盖 focus、loading、disabled、error。工作区轻量选择使用即时应用并关闭的 popover，若声明外部关闭需 capture 阶段与内部 stopPropagation 联合验证。高风险确认弹窗只以显式确认提交。

decomposition 已完成；UI Skeleton、1440px 及其他视口真实视觉和 computed style 证据留待后续 Change 实现。PNG 本阶段暂不要求，Readiness 为 Partially Ready（视觉证据待实现），不影响需求提交评审，不代表功能可上线。

## 实际组件与原型对照

实际承载为 Chat 工作台打开的共享工作区详情，复用 ChatDialog 及设计 Token，不新增独立导航页。原型中的工作区轻量选择落为原生 select，选择只改变查看范围；创建会话是单独显式动作。浮层统一 header/body/footer，父浮层在子浮层打开时暂停外部点击和键盘关闭。正常、无权限、错误、恢复冲突、候选失败及返修均走真实 API；静态 prototype.html 继续只用于评审。

固定来源和目标后创建双父组合候选，由部署批准的隔离模板检查 SQLite/MySQL 8.4、应用和浏览器。未配置模板或检查未通过时不能确认。当前具有迭代操作权限且可访问相应对象的人确认，执行前再次核验权限与版本。同仓库串行合入，主线变化使后续确认失效。Git 完成后独立同步主目录注册表的 workspace_integration 与 Sprint 合入记录；同步失败可续接且不重复合并。治理修改保持可审阅的未提交状态，不自动提交人工修改；正式规格仍只在归档合并时生效。

视觉材料位于关联 Change 的 evidence/ui，验收汇总将记录到 evidence/acceptance；尚未签署的检查保持待验。

## 最终原型一致性签认

采用既有ChatDialog统一浮层族与原生select，保留原型动作和权限意图。全部三视口深浅主题、错误/拒绝、恢复/确认/返修动作均有真实API界面证据；Skeleton仅作为结构样本。实际映射和差异处置见Change design.md与implementation-verification.md。上述历史Readiness说明已由本次验收材料替代。
