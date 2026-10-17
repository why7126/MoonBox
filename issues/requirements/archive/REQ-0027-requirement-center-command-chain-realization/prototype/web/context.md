---
requirement_id: REQ-0027-requirement-center-command-chain-realization
title: 需求中心卡片全命令产品链路真实化交互原型说明
created_at: 2026-09-30 12:55:45
updated_at: 2026-09-30 12:55:45
---

# 需求中心卡片全命令产品链路真实化交互原型说明

## 定位与事实源

保真模式：局部一致。保持现有需求中心卡片、Chat、Modal、Toast组件族与设计 token，静态 prototype.html 只表达八动作及反馈结构，不替代既有页面视觉，不是产品功能实现。无用户截图/附件，不推定像素级参考。

优先级：PRD业务与权限约束 > 既有需求中心组件和共享 token > 本说明交互契约 > 静态示意。冲突由 Change 明确处置，不牺牲真实持久化、阶段门禁、文档入口和可访问性。

参考入口：src/web/src/pages/catalog/RequirementCenterPage.tsx 的 ActionDialog/confirmActionDialog；src/shared/design-system/tokens/colors.ts；src/web/src/styles/project-governance.css。目标复用卡片、按钮、Modal/Drawer、反馈容器，未在本轮修改这些文件。

## 页面拆解与 UI Contract 种子

页面清单：既有需求中心一页；本地原型为独立动作预览，不新增生产路由。组件层级：页面壳/标题 -> REQ卡片（ID、标题、生命周期、主动作、分析辅助动作）-> 确认或选择浮层 -> 执行反馈 -> 真实产物入口。原型同时列出八动作方便评审；生产仅按阶段展示可用主动作。

数据依赖：授权项目、完整ID、版本、必备文档、生命周期、评审结论、Sprint列表、Change执行事实、操作结果。原型均为示意数据，不调用 API，不改变治理文件。真实接口字段在 Change 设计确定。

状态矩阵：默认/hover/focus；禁用及原因；打开/取消；受理/运行/成功/失败/需补充；空结果/只读/无权限/版本冲突/部分写入/同步失败。所有写动作先走后端门禁；窗口关闭不取消后台任务。

响应式：1440px为主验收宽度，390px检查文本折行与弹窗不溢出；768px作为原型单列断点，最终断点由既有页面对齐。矮视口浮层内部滚动，底部取消与提交可达。

1440px焦点：卡片密度、动作层级、主辅按钮不混淆、反馈不挤动布局、抽屉与弹窗层级、长ID省略及可读全文。PNG本轮暂不要求；实现阶段补真实页面截图与样式证据，readiness 为 Partially Ready。

## 动作按钮与浮层矩阵

参考锚点为既有页面同文案按钮。下列 data-testid 是候选稳定 selector，尚未宣称生产已存在；Change 在 design 中完成到实际组件的映射。均置于按完整 REQ ID 定位的卡片内，避免多卡串对象。

| 动作 | modal类型/组件族 | 按钮selector后缀 | 浮层selector后缀 | 状态与验收证据 |
|---|---|---|---|---|
| 需求分析 | ai-panel / Chat抽屉 | analyze | analysis | 只读、打开、错误、权限；AC-001/009，Chat截图及文件差异 |
| 生成需求 | action-modal / 方式选择+反馈 | generate | generate | AI路径、取消、运行、失败、成功；AC-002/010/011 |
| 完善需求 | action-modal / 方式选择+反馈 | complete | complete | AI路径、材料不足、运行、失败、成功；AC-003 |
| 发起评审 | confirm / 评审Modal | review | review | 通过/拒绝/延后理由、取消、提交中、错误；AC-004 |
| 加入迭代 | dialog / Sprint选择Modal | sprint | sprint | 无/单/多active、容量、取消、冲突；AC-005 |
| 生成 OpenSpec | action-modal / 执行反馈 | opsx | opsx | 门禁、运行、部分写入、成功；AC-006 |
| 开始开发 | action-modal / 执行反馈 | apply | apply | 受理/启动/阻塞/失败/applied；AC-007 |
| 完成归档 | confirm / 归档门禁Modal | archive | archive | 未验收、确认、部分归档、恢复、成功；AC-008/012 |

按钮完整模式为 data-testid="req-action-后缀"；浮层为 data-testid="req-panel-后缀"，内部使用 req-panel-cancel、req-panel-submit、req-operation-status 与 req-artifacts。生产字段后续以实际映射为准；原型采用这些候选按钮选择器。

确认用于评审、Sprint写入和归档的持久化副作用，不采用点击选项即写入；Esc/取消在提交前不写入。内部点击不误关闭，声明外部关闭时采用capture监听或等价机制；Tab焦点限制在Modal，关闭后归还焦点。只读分析不提供写入授权转换。

## 样式采样与分批验收

| 批次 | 组件与采样 | 证据要求 |
|---|---|---|
| 1 | 页面壳、卡片、标题；width/padding/gap/font-family/font-size/line-height | 实际路由、1440px、深浅主题、Skeleton首轮确认 |
| 2 | 八动作按钮与Modal族；height/border/radius/background/color/z-index | hover/focus/disabled/loading/open/error/权限截图及样式对比 |
| 3 | Chat、反馈、Toast、文档入口；position/overflow/width/height | 关闭重开、滚动、外部点击、矮视口、390px与键盘证据 |

期望值来自共享 token 与既有组件；当前实现的分项采样值、截图和视口断言记录于 Change `evidence/acceptance/visual/` 及 AC-PROTOTYPE-003/005 样本，不能用本原型中的期望值代替实测。局部一致的非目标是重设计侧栏、指标、筛选、Capture、导入及会话管理；这些区域的影响按各 AC 证据分别复核。
