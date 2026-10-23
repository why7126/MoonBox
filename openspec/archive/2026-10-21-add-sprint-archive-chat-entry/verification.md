---
title: 迭代归档会话入口实施验证
change_id: add-sprint-archive-chat-entry
created_at: '2026-10-21 22:18:00'
updated_at: '2026-10-21 22:18:00'
---

# 迭代归档会话入口实施验证

## 实现与影响面

- 需求中心容量条改为直接准备 SPRINT 对象会话；完整范围非空且全部完成才开放，容量与签署不拦入口。
- 对象会话支持受信 Sprint 身份、主关联、个人会话排序及并发创建；准备无消息、candidate、turn 或模型调用。
- Chat 消费项目和会话隔离的一次性意图；不同草稿 inline 保留/填入，附件与 Skill 继续使用原 Composer 上下文；正在执行时只查看原会话。
- 主动发送重新检查完整范围、权限与签署；执行路由、同步结果、完成证明和中断恢复使用既有治理设施。
- API 索引、OpenAPI/Orval 已同步。数据库沿用现有字符串关联，无 schema 迁移。部署配置、存储与客户端外其他平台无新增边界。

## 命令回归

定向后端 103 项通过（恢复服务后再次执行仍通过）；MySQL 8.2 隔离矩阵 20 项通过；前端 2 文件 10 项通过；TypeScript 与 Vite 构建通过。当前 Change 中文、严格规格、中文标题与 Sprint 范围校验通过。

全仓 Design System 检查仍报 183 项现有违规；新增 Sprint 草稿组件使用 shared Button 与 semantic token，未新增该组件违规。此前扩大回归 161 项中 157 通过，另 4 项涉及其他治理夹具缺少恢复心跳/归档证据，未通过放宽门禁掩盖。以上不计为本次定向通过项。

## 视觉与交互证据

正式页面由浏览器实测，测试对象与账号均为隔离样本。ui/default-1440.png、default-768.png、default-390.png 同时覆盖可用/禁用容量入口；ui/draft-conflict-1440.png、draft-conflict-768.png、draft-conflict-390.png 覆盖 inline 草稿选择。截图按 CSS 视口 1440×900、768×900、390×844 采集，浏览器设备模拟截图像素大小可能缩放。

computed-styles.json 记录视口、布局宽度与组件位置。草稿组件为 static 文档流，13px 字体、12px 14px padding 与 1px token 边框；窄屏命令换行，页面无水平溢出，选择按钮不遮挡 Composer。容量入口沿用 34×34、radius 6px 基线。loading-1440.png 为禁用且 aria-busy 的准备状态。较早截图中的权限标签为完全只读；最终构建已改为发送时校验，不改变布局，replaced-command.png 与 busy-reused.png 记录最终文字及实际操作。

用户已确认骨架。真实页面观察包括保留草稿、刷新不重放、主动填入后 turn 数仍为零，以及执行中再次点击入口复用相同会话、保留草稿、不创建第二轮次。附件与 Skill 保留另外由 Composer 集成回归核对，不把该合成回归标为真实附件上传观察。

## 真实产品执行

- sprint-099：未签署时入口可用；预填 session=1、turn=0；发送被门禁拒绝，保持未归档。测试操作员只在隔离样本签署后主动发送，原轮次 completed、guard validated/done，实际同步命令成功，需求中心移除该当前迭代并更新统计。
- sprint-098：独立恢复样本；执行中重入仍为同一 session/turn，保留运行中草稿。正式同步完成后主动中断原轮次，原状态保持 stopped；点击核验当前成果后为 recovered_valid/done，仍为 1 个会话、1 个轮次、1 次非 dry-run 正式同步。详见 recovery-observation.json 与 recovery-interrupt.json。
- 原始 dry-run 与实际写入同步在导出中以 dry_run 区分，不把 dry-run 当作归档完成。原始事件保留于授权隔离数据库，仓库只存脱敏计数、状态与标识。

## 数据采集声明

product_data_collection_observability: applicable。affected_layers: API、会话关联、行为事件、执行 Task Trace、Web 请求与治理同步。沿用既有请求/任务标识和安全元数据，不在新增事件中持久化草稿、Prompt、凭证或本机路径。数据库迁移 N/A：无表结构变化；对象存储 N/A：无新增对象读写；部署 N/A：无新增端口或配置。validation：接口回归、双数据库并发测试及脱敏真实事件导出。
