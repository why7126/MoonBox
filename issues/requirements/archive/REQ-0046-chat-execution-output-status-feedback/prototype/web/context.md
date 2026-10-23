---
requirement_id: REQ-0046-chat-execution-output-status-feedback
title: Chat 状态反馈局部原型与交互契约
created_at: '2026-10-19 11:14:18'
updated_at: '2026-10-20 16:26:38'
---

# Chat 状态反馈局部原型与交互契约

## 原型策略与事实源

局部一致模式：保留现有 Chat 阅读顺序与产品 token，重构状态区域，不对截图像素复刻。优先级为 requirement.md v2 的事实与权限语义、用户确认方案、此交互原型、既有组件与附件问题截图。全部使用模拟数据，无 API、无命令发送；原型预览不等于产品实现。PNG 暂不要求。

## 页面与组件拆解

页面是 Chat 消息局部，保留一条独立历史失败轮次用于说明归属。当前轮次结构：#current-turn → #activity（主状态、业务说明、工具次数、模型）→ #feedback（异常及正文缺口）→ #body / #rejected-output → 允许的恢复动作 → #trace-detail（阶段、原执行、轨迹、证据）。会话底部无独立恢复面板。#scenario、#theme 是原型控制器，不进入产品。

25 个场景覆盖排队、准备、执行、停止请求、校验、应用、回读、完成、校验拒绝、待校验、失败可恢复、已停止、未知、失败无正文、正文缺口、无最终答复、普通聊天、读取中、读取失败、完成后读取失败、恢复中、恢复完成、无权限、过期、版本冲突。普通聊天无六阶段；已完成证明与原失败终态可并存；所有组合按 FR-008 判定，HTML 是代表样本而非完整测试实现。

## 动作按钮与弹窗矩阵

| 动作 | modal 类型 | selector | 状态 | 验收证据 |
|---|---|---|---|---|
| 运行状态行 | 内联执行详情 | #activity / #trace-detail | 折叠/展开 | 双视口、正确轮次、aria-expanded |
| 收起详情 | 无 | #close-detail | 展开 | 返回状态行焦点 |
| 查看证据 | 只读 dialog | #evidence / #action-dialog | 打开/关闭 | 本轮操作关联、关闭/Esc/外部点击 |
| 继续剩余步骤 | 确认 dialog | #resume / #confirm-action | 可用/确认/提交/冲突/失败 | 原对象、版本核验、无重复提交 |
| 重新生成草稿 | 非空草稿替换确认 dialog | #regenerate / #draft | 空草稿直接填入、非空确认/取消 | 不发送、不覆盖取消的草稿 |
| 刷新状态 | 无 | #refresh | 读取失败/待确认 | 仅查询、保留事实与上下文 |
| 原有停止/重试 | 复用原执行详情契约 | 产品既有 chat-stop-current / chat-retry | 原权限与终态限制 | 产品阶段回归，不新增模拟执行 |
| 拒绝原文展开 | details | #rejected-output | 折叠/展开 | 原文可读，拒绝说明保持可见 |

所有 dialog 支持关闭/取消与 Esc，关闭返回触发按钮；外部点击在 capture 阶段识别真实外部位置，内部点击不关闭。产品提交中不允许外部点击假装取消已提交请求，状态变化使旧确认失效；原型只演示请求已提交提示，不调用恢复 API，也不模拟真实幂等成功。

## 数据依赖与实现映射

依赖 conversation_id、turn_id、可信 operation_id、业务版本、原执行终态、阶段结果、正文完整性、allowed_actions 与权限。恢复尝试关联原操作；历史缺关联不匹配最新 candidate。候选实现：TurnActivity 负责入口，ConversationMessages 负责轮次容器，RecoveryOperationPanel 内容迁入本轮详情，ExecutionPanel/TrajectoryView 复用轨迹。只迁移组件，禁止按正文关键词清理 DOM。产品稳定 selector 在 Change 中确定。

## 响应式与视觉验收

1440×900：内容最大宽 1008px（含左右 24px 内边距），正文 14px/1.5，主状态优先、模型信息弱化，详情内联；600px 以下主区 16px、状态换行，390×844 无横向溢出。dialog 最大 520px、窄屏左右留 16px、最大 80vh 可滚动。使用深浅主题产品 token、6px 控件圆角、细边框。重点采样 font-size/line-height/color/background/padding/gap/width/overflow/z-index；双视口覆盖默认完成、异常、恢复确认、证据和草稿替换。

## 验证边界

原型拆解与产品实现已核对；骨架、双视口视觉和 computed style 证据见 Change verification.md。初始骨架为1470px，1440/390为补证，不追写用户首轮签认。原型中确认、刷新、草稿均是本地展示状态，不写业务数据。验收 AC-015—022 与 AC-PROTOTYPE 覆盖实现阶段真实身份/版本/权限/幂等及视觉，不能以原型成功替代产品测试。

## 生命周期与核验补充场景

新增 #consistency-card，展示可信生命周期“已评审”与“执行结果待核对”并存，加入迭代禁用；#recheck 只模拟核验，#difference 复用只读 dialog，#original-run 展开当前模拟轮次详情。真实能力、原因与时间来自后端 BUG 契约，无能力不开放入口。

| 动作 | modal 类型 | selector | 状态 | 证据 |
|---|---|---|---|---|
| 重新核验 | 无 | #recheck | 待核验/处理中/未收敛 | 不重放执行、失败保留原事实 |
| 查看差异 | 只读 dialog | #difference / #action-dialog | 开/关/无权限 | 关联异常操作、Esc/外部点击、焦点返回 |
| 查看原执行 | 内联详情 | #original-run / #trace-detail | 当前轮次 | 不切换到最新无关操作 |

卡片是独立场景示意，不表示与上方每个 scenario 的模拟数据自动联动；移动端按钮换行，AC-023—026 的真实双视口证据、冲突与恢复准入结果见 Change verification.md；最终联合验收以逐 AC 报告为准。


## 产品实现核对

实际入口为 turn-status-trigger，详情为 recovery-panel，证据为 recovery-evidence，差异为 operation-differences，卡片为 requirement-operation-status。状态及反馈14px/21px，桌面消息最大1008px；保留既有正文13px/1.75，不扩大到正文排版改造。弹窗520px/移动358px，阶段看板有意横向滚动，卡片内容无横向溢出。原型14px正文为示意，产品已有正文样式优先。核验由后端事实驱动；测试预览只位于src/web/tests，不作为产品路由。

## 跨入口一致性返修约定

卡片只呈现一次当前动作的阻塞摘要，历史成果、核验时间、重新核验、差异和原执行收进默认折叠的“状态详情”。运行详情仍归属于原Chat轮次。归档准入采用当前Change的结构化验收证据和明确人工签认，与CLI共用只读判定；进度统计按AC身份去重，自动通过不等于用户人工签认。旧评审历史保留，经过验证的后续合法流转可承接旧保护，真实冲突、未知占用、权限变化、缺失或过期证据仍阻断。覆盖REQ与BUG，不能按具体编号特判。

后续补充评审仍为 approved 且对象身份一致时，只有完整评审文件被当前有效验收证据覆盖，才能承接旧评审保护；结论拒绝、未覆盖或过期仍阻断。关联解析统一支持 related_change、related_changes 与 openspec_changes 的字符串/对象形式。

## 再次验收后归档准入

本轮不改变原型布局或动作族。验收完成与归档可执行分别判断；报告和运行追溯更新不使恢复记录自失效。输入框错误文案按交付输入变化、旧记录过期、规格基线缺证、身份冲突、记录损坏分类，具体文案来自后端统一准入；原型展示不代表实际可发送。
