---
requirement_id: REQ-0049-sprint-archive-chat-entry
title: 迭代归档会话入口原型与视觉契约
created_at: '2026-10-21 17:59:48'
updated_at: '2026-10-21 17:59:48'
---

# 迭代归档会话入口原型与视觉契约

## 参考事实源与边界

模式：局部一致。业务语义以用户已确认要求和 requirement.md 为先；位置以本会话附件红框标注的容量条右侧归档图标为准；视觉细节沿用既有需求中心与 Chat 组件。附件未复制为持久文件，不记录本机临时路径。prototype.html 是本需求可审阅的交互示意，不是整页像素复刻基线。

页面壳、品牌标题、指标、筛选、看板列、空卡、任务卡与标签沿用现有页面，不在本次重设计；只覆盖归档入口与 Chat 输入保护。原型无网络请求、无真实业务写入，所有 Sprint、容量、会话和状态为 Mock。PNG 暂不要求，真实视觉证据待实现阶段采集，不据原型文件存在宣称产品通过。

## 页面与组件拆解

| 页面 | 组件层级 | 数据依赖 | 1440px 焦点 |
|---|---|---|---|
| 需求中心 | 页面壳 → 标题 → 当前迭代容量条 → Sprint ID/容量/归档按钮/原因 | 完整范围、完成数、权限、Sprint 生命周期、容量显示 | 图标与容量条对齐，提示不挤压布局 |
| Chat | 页面壳 → Sprint 会话身份 → 历史区 → 状态提示 → 草稿选择 → 输入框/发送 | 项目与对象身份、会话、执行保护、现有草稿、一次性预填意图 | 身份可见、输入可读、选择不遮挡输入 |

## 状态与交互矩阵

| 状态 | 入口 | 触发结果 |
|---|---|---|
| 全完成、未签署 | 可用 | 直接 Chat，预填待发送 |
| 未完成/空范围/未知/无权 | 禁用并说明 | 不准备会话 |
| 容量未知、范围已确认完成 | 可用 | 不以容量否决 |
| preparing | 加载且锁定 | 防连点，失败可重试 |
| 有会话/无会话 | 可用 | 复用/新建并关联 |
| 已有不同草稿 | 可用 | Chat inline 选择，默认保留 |
| running/needs-review | 查看既有执行 | 不覆盖输入或启动新执行 |
| 已归档 | 无可执行入口 | 沿用历史入口 |
| 准备失败 | 保留需求中心 | 错误提示与重试 |

## Selector 与动作按钮矩阵

| 动作/组件 | 参考锚点 | 产品 selector | 原型 selector | modal 类型 | 状态/证据 |
|---|---|---|---|---|---|
| 归档 | 附件红框图标 | [data-testid=current-iteration-archive-action] | #archive | N/A，直接导航 | default/hover/focus/disabled/loading/error；截图、DOM |
| 原因提示 | 容量条提示 | [data-testid=current-iteration-archive-summary] | #reason | tooltip 或文本 | 未完成/未知；可访问名称 |
| Chat 输入 | 既有 Composer | [data-testid=chat-prompt] | #prompt | N/A | empty/prefilled/existing/busy；输入与消息计数 |
| 草稿冲突容器 | PRD FR-005 | [data-testid=sprint-archive-draft-conflict] | #conflict | inline-expanded | open/closed；截图与 DOM |
| 填入命令/保留草稿 | FR-005 | [data-testid=sprint-archive-draft-replace] / [data-testid=sprint-archive-draft-keep] | #replace / #keep | N/A | 默认保留，主动替换；键盘证据 |
| 发送 | 既有 Chat 发送 | 沿用 Composer 发送控件，Change 内确认稳定 selector | #send | N/A | 只有主动点击才触发；请求与 turn 证据 |

不新增归档确认 modal；正常动作族复用 Button/Toast，草稿冲突采用 inline 组件，需统一 focus、错误、loading 和关闭语义。原型状态控制器只供审阅，不进入产品。

## Computed style 采样计划

| 区域 | 属性 | 期望/比较基线 |
|---|---|---|
| 归档按钮/图标 | width、height、padding、color、border、border-radius、outline | 实现前既有归档按钮与设计 token，状态差异可识别 |
| 容量条 | display、gap、align-items、overflow、width | 保留同排对齐；窄屏折行而非覆盖 |
| 命令输入 | font-family、font-size、line-height、padding、white-space、overflow-wrap | 复用 Composer，长命令可读且可编辑 |
| 草稿选择/提示 | background、border、gap、position、z-index | inline 占位，不遮挡输入或冒充 modal |

不虚构参考像素数；实现阶段按现有 token 采样确定容差，逐项记录期望/实际/结论。

## 响应式与证据批次

原型在 800px 以下压缩外边距，容量条允许换行；390px 保持按钮可见，命令换行。实现验收以 1440×900 为基准，768×900、390×844 为窄视口。先验证需求中心入口，再验证 Chat 空输入/冲突/执行保护，最后验证真 API 与结果刷新。UI Skeleton 首轮人工确认、真实视觉与 computed style、REQ 最终一致性均为 pending。

## 知识库承接

引用原型驱动门禁、治理恢复证据分层实践及 sprint-010 复盘：模拟交互不替代真实执行，完成提示不替代归档事实，真实归档样本串行隔离，历史失败不被恢复覆盖。

## 本轮验证记录

文档标题、产物完整性、DOM ID 唯一性与引用、无网络调用边界、JavaScript 语法检查通过。本地 HTML 的浏览器预览被 URL 安全策略拒绝，未绕过策略；因此未验证运行态交互、截图或 computed style。此项为非阻断的原型预览缺口，Readiness 保持 Partially Ready，不能将静态检查视为视觉通过。

## 真实页面接入记录

用户已确认容量条右侧入口、Chat Sprint 身份及输入框上方草稿提示的骨架方向。现已复用正式页面壳、Composer 和 Button 接入对象会话 API；原型仍为 Mock，不承担产品执行。正式组件 selector 已回填。

产品截图与 computed style 位于对应 Change 的 evidence/acceptance/ui/，覆盖 1440×900、768×900、390×844；默认/禁用共用容量条截图，草稿冲突独立截图。实际正常归档和未签署拒绝分别保存，不以预填或 Chat 文字推定成功。恢复样本已验证原轮次 stopped 与成果 recovered_valid 分离，未重复同步；30 项 AC 通过，最终共享归档门禁 ready。
