---
title: 统一运行状态实施与联合验收记录
created_at: '2026-10-20 14:01:00'
updated_at: '2026-10-20 16:16:14'
---

# 统一运行状态实施与联合验收记录

## 交付与边界

每轮状态行统一执行、业务结果、正文完整性和读取覆盖层。完成默认折叠，详情保留原终态、实际阶段、证据及恢复动作；独立底部面板已移除。卡片显示历史可信结果、下一步准入、核验原因和时间，可重新核验、查看差异及定位原轮次。新增只读 operation/turn 关联字段；API、OpenAPI、Orval 已同步，无新增数据库迁移或权限。

## 验证记录

- 前端完整串行回归 385 项：376 通过，9 项失败均在未修改的 capture-persistence.test.tsx，断言缺失的 Capture 标题控件；相关 CaptureDialog 与该测试均与 HEAD 一致。最终卡片历史标签补充测试单项通过，未重复全仓无关测试。
- 后端相关 73 项及 6 个子场景通过；新增卡片原轮次身份断言后的交接模块 17 项通过。独立 MySQL 8.2 矩阵 27 项通过。SQLite 与 MySQL 使用独立合成数据。
- TypeScript 与生产构建通过，保留既有单包体积警告。最终逐 AC 命令与指纹由 acceptance/ 报告记录。

## 产品观察与证据等级

当前独立副本 REQ-9096 真实轮次首次完成，application=applied/verified、guard=validated、handoff=confirmed；仅 1 轮、1 候选、1 应用，首次数据库观测交接耗时 7.485 秒；持久 Task Trace 首次 completion_confirmed 的保守口径为 26.305 秒。修改临时副本的相关评审文件后，通过 Chat 的真实 POST 核验显示历史完成且下一步受限；恢复文件后，从卡片 POST 核验恢复 validated，仍为 1 轮、1 应用。没有手工改守卫或重放模型。证据：evidence/current-real-turns.json、final-restored.json、关联BUG的evidence/live-req46-joint-verification.json 及 final-conflict-card-*、final-conflict-differences-*截图。

BUG-9096 真实轮次生成 review_result 字段，现有评审契约仅接受 status/result，被 review_outcome 正确拒绝。执行完成不等于业务完成，页面为待处理/结果未通过校验，应用数为 0。此样本作为负向证据，不能签认为正常成功。用户另行授权的 BUG-9097 正常样本已完成：guard=validated、handoff=confirmed、应用verified，1轮1应用，交接6.303秒；原失败样本保持不变。

读取失败通过 Chrome 设备工具的临时 Offline 模式实际触发：完成状态与原文保留，显示“上次确认，更新失败；写操作暂不可用”；恢复 No throttling 后刷新收敛。证据为 final-read-failure-1440x900.png。未模拟接口成功结果。

恢复语义：失败/停止后手动续接、预算、草稿替换、版本失效和无权限由组件/API 合成回归覆盖。历史真实应用中断恢复证据引用 openspec/archive/2026-10-19-add-governance-command-durable-recovery/verification.md 及其 evidence/live；该样本为原模型 completed 后应用阶段恢复，不冒称本版本真实 stopped/manual-resume 首次执行。状态投影使用实际恢复次数，原终态不改写。

## 视觉与交互

1440×900、390×844 的真实 Chat、内联详情、卡片、证据和差异弹窗已采集，经过脱敏筛选的文件以 final- 前缀区分；不合格及重复初稿已转移到私有临时目录。状态行 14px/21px，桌面消息区最大 1008px；移动消息区无横向溢出。弹窗桌面 520px、移动 358px、两侧 16px，最大高度 80vh；移动卡片 266px，阶段看板保留设计内横向滚动。computed JSON 与截图同名关联。状态矩阵与浅色主题的 synthetic-* 来自测试入口，使用真实投影/弹窗组件和模拟状态，不当作真实执行。

实现前骨架留有 1470px 截图，1440px、390px 补证为 synthetic-skeleton-*；如实保留时间顺序，不追写为实现前用户签认。本轮自主视觉检查已通过，用户产品验收与自动技术验收分开。

桌面与移动端相关差异弹窗显示同一 operation，相关成果修改 1 项；卡片生命周期仍为已评审。正文保留原回答，不把结构化核验写回模型原文。最终卡片提示修正后不再把已可信的历史结果标为“结果待核对”。

## 文档一致性与观测

PRD、业务流程、用户故事、验收标准、trace、prototype/context 和 HTML 的每轮状态、原终态、只读刷新、核验 POST、草稿不自动发送与历史保留语义一致。原型仅展示设计状态，不成为后端事实源。

product_data_collection_observability: applicable。affected_layers: web/api/request_logs/task_traces。复用原 request/operation/turn 关联和权限校验；不新增埋点、usage_events、数据库表、对象存储或请求封装。证据仅保留合成对象标识、计数和相对文件哈希，不保存凭证或原始提示。真实模型验收在隔离 source 环境完成；最终实现已通过标准脚本构建并更新本地 Docker 环境，不涉及生产部署。

## 执行链路复盘

发现并修正状态读取覆盖、历史结果与准入提示、宽度规则优先级等问题。真实模型评审字段漂移被既有校验拦截，建议后续统一技能模板与运行时评审 schema，默认仅记录建议，未自动创建新 Issue/Change。完成门禁与归档就绪以逐 AC 报告为准；本记录不自动授权归档。

长耗时真实样本发现原20次轮询预算耗尽后未随终态重读，已由refreshKey（原轮次状态/候选状态）、可见性恢复及核验事件重新启动有限读取预算修复；新增超过63秒后终态到达的回归通过，不增加模型调用。最终前端指纹在构建后更新；后端及已完成真实轮次保持不变。

最终轮询修复的32项定向回归通过（状态26、恢复6）；视觉布局和状态文案未改变，既有对应截图按组件未变范围复用，最终构建回读真实REQ/BUG。全仓结果376/385是修复前完整基线，不冒称最终全仓全绿。

## 最终本地部署与检查例外

标准 docker-up.sh self-storage-sqlite 已构建并更新本地服务。首次启动被控制器过期 operation.tmp 心跳阻断：固定角色UUID目录中的文件仅含 time/actions/schema_min/schema_max，时间已过期，严格临时文件校验因时间不同拒绝覆盖。核对普通文件、单硬链接与字段集合后原地重命名保留隔离备份；没有修改业务操作记录或执行保护。控制器随后自行重启，backend、worker、controller均healthy，API健康检查成功。此环境恢复不计为业务自动恢复验收。

静态 assert-runtime-bundle 检查命中“审阅治理成果”字串；该字串实际在既有 runtimeBuild.ts 的旧DOM清理选择器中，相关DOM回归通过，未作为新界面渲染。静态检查仍记失败/误报，不声称全仓门禁全绿，未扩大范围修改检查器。

文档抽屉既有长测试在5秒及15秒期限下超时；保持所有断言不变，60秒上限单项复验通过，实际测试耗时5.5秒。最终相关套件使用60秒单项上限，避免负载波动导致假失败；正式结果以逐AC报告为准。

最终相关前端回归：9个文件213项全部通过，覆盖状态、恢复、活动、正文、准备失败、多轮消息、工作台、会话及需求中心；串行总耗时121.13秒。Docker构建使用Linux Node22/pnpm，JS哈希与宿主npm构建不同，CSS哈希一致；本地实际资源指纹及最终refreshKey/核验事件等标记记录于evidence/local-deployment.json，真实模型证据仍归属隔离环境。


## 跨入口归档准入返修验证（本轮）

本节与 acceptance-fixes.md 为本轮返修口径；前述真实评审、Chat 状态与恢复记录保留为历史证据，不代表本轮重新执行评审。共享验收事实源覆盖标题式、勾选式及原型 AC，产品读取与 CLI 复用当前指纹；人工验收未签认、真实依赖冲突、运行中占用仍阻断。

修复同时覆盖 REQ、BUG、合法后续阶段与独立 Change 兼容路径，不按 REQ-0046 ID 特判。执行器识别 req_id 等既有别名并拒绝歧义；归档准备与 CLI 包装脚本提前检查交付证明。已结束且有可信零写入证明的尝试，补齐当前证据后可重新进入归档；原终态和历史负例保留。

本轮独立验证：需求中心 137 项前端测试通过；共享准入及执行保护 40 项与 6 子测试通过；归档准备、证明与重入 29 项通过。实际模型归档样本、最终工作流状态及逐 AC 结果以 evidence/cross-entry-archive-verification.json 和最新 acceptance 报告为准，未生成该文件前不表示真实联合验收完成。

UI 证据使用 modify-card-*；Chrome 设备预览按 Fit to window 缩放，实际 CSS 视口和 computed style 在同名 JSON 中记录，不把图片像素尺寸冒称 CSS 视口。未改动的 Chat 状态和弹窗族按原证据复用；卡片折叠、展开和相关变化入口重新检查。

本轮不新增 API 字段、数据库迁移、权限、客户端生成或生产部署。product_data_collection_observability: applicable；affected_layers: web/api/task_traces；复用既有关联与脱敏记录，validation 为共享准入、CAS 重试和跨入口验证。
