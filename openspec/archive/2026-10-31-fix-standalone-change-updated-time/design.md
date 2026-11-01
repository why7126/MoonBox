---
title: 独立 Change 卡片可信时间修复设计
created_at: "2026-10-31 22:33:14"
updated_at: "2026-10-31 22:53:51"
---

# 独立 Change 卡片可信时间修复设计

## 背景与现状

复用 BUG 根因 E1–E5：历史样本已归档，trace 缺 created_at/updated_at；change_index.cards 仅读顶层两个字段，前端无法格式化则显示未知；execution.transition 只替换已有 updated_at，缺字段未插入。2026-10-30 浏览器刷新观察属于故障历史证据，不等于本次验收。原始漏写入口的历史归责仍未知。

## 根因

时间写入和读取契约不完整。不能通过将 execution.completed_at 填入 updated_at 或读取时使用当前时间来掩盖缺口。当前其他 Change 已更新共享卡片，实施前重新定位代码片段并保留其行为。

## 修复方案

### 业务时间维护

复用共享 Frontmatter 写入能力。新建时 created_at 与 updated_at 取真实创建事件时刻；已有对象仅在内容或状态发生有效变化时刷新 updated_at，保留合法 created_at。缺失 created_at 的旧对象不得用本次事件时刻填充历史创建时间；有效变更可首次记录真实 updated_at。无变化重放、只读查询及已完成对象的提前返回不补造时间。顶层 execution_tasks 保存执行事件已观测的完成数/总数，使同名 progress 事件在任务进度实际变化时刷新时间；该字段不代表额外执行完成事实。opsx.start、apply、modify 和归档闭环按实际变化统一处理，首次 execution.completed_at 始终保留。

### 卡片投影与显示

独立 Change 优先取有效 updated_at，其次有效 created_at、execution.completed_at、execution.started_at；每个候选独立校验，非法高优先级字段不阻止合法低优先级事实。保留 updated_at 的业务语义，不将执行时间写入该字段。增加可选 card_time 与 card_time_source（updated/created/execution_completed/execution_started/missing），后端生成，Web 只负责格式化与标签。来源分别显示“更新于”“创建于”“执行完成于”“执行开始于”；完全缺失显示“时间未记录”。真实更新时间格式沿用 YY/MM/DD HH:mm，使用 Asia/Shanghai；带时区转当地时间，既有无时区治理时间按项目时区解释，拒绝非法日期。

摘要与完整投影共用解析，不增加磁盘深度扫描、执行检查或历史写入。REQ/BUG 卡原有字段及行为保持。API schema、OpenAPI 与客户端生成物随新增可选字段同步，不手改生成代码。

### UI 参考与验收契约

用户截图仅作为故障定位参考，无整页复刻任务。沿用当前卡片 footer 与 .rc-updated 样式；实施时核对实际 selector。时间文本可访问且窄屏不拆分，footer 动作允许换行。保留优先级和验收检查按钮的状态、弹窗及授权，不新增动作或 modal。对比截图中“更新时间未知”与新来源标签，记录文本、字号、间距、颜色、overflow 的 computed style，验证不挤压现有按钮。

## 测试策略

| BUG 验收项 | 验证方法 |
|---|---|
| AC-001 | 隔离缺顶层时间而有执行时间样本，后端及前端断言来源、标签与值 |
| AC-002 | 新建及有效变更时间维护单测，created_at 不变 |
| AC-003 | start/apply/modify/归档缺字段回归，首次完成时间不变 |
| AC-004 | 同事件重放及已完成对象字节/字段快照保持，禁止查询时间回退 |
| AC-005 | 非法日期、空值、全部缺失、非法高优先级字段矩阵；禁止 mtime/复制时刻 |
| AC-006 | 活动/归档独立卡、合法时间、REQ/BUG 卡与时区边界回归；深浅主题×1440×900/390×844 |
| AC-007 | API/规则同步检查，真实产品刷新截图与合成测试分别归档 |

实施阶段建立可执行 acceptance-plan 与 evidence/acceptance 证据映射，再通过 opsx-accept 验收。历史截图不能标记修复通过。读取归档样本只读，合成样本位于隔离测试目录。

## 风险

共享卡片改动可能影响已交付优先级/验收入口，需聚焦回归；新可选字段需要前后端共同发布，旧客户端仍允许未知时间。历史证据不修写，因此数据缺口可能长期存在，通过明确来源解释而非隐藏。

## 回滚方案

按 proposal 回退代码及客户端生成物，不回滚真实时间事实、不重放历史执行事件，无数据库回滚步骤。

## 数据采集与链路观测

product_data_collection_observability:
- status: applicable
- affected_layers: [web, api, governance]
- reason: 卡片响应新增时间来源，执行同步维护业务事实；不新增业务动作、日志字段、Task Trace span 或采集存储。
- validation: 检查直接 API 与摘要/完整投影一致、既有请求链路 ID 和授权保持、日志脱敏及 OpenAPI/Orval 生成一致；无新增行为事件，CLI 不伪造界面事件。DB、对象存储、日志保留周期及部署不改变，相关迁移测试不适用。


## 实施核对与入口矩阵

| 入口 | 事实源及版本 | 场景与证据 |
|---|---|---|
| CLI 新建/执行 | 当前 initialization、execution、timefmt | 初始化、start/apply、重复事件与缺字段：治理回归 |
| 返修/归档前文档写入 | persist_markdown 实际正文差异 | 有效变更补 updated_at、无变化不写、首次完成事实不变；投影事件不推断未提供的源码差异 |
| 产品卡片 | 当前工作区构建加载本地服务，真实 API | 原归档样本刷新显示执行完成时间；源文件只读 |
| 摘要/完整 API | 同一 ChangeIndex 时间解析 | 两种 view 响应一致，既有权限/请求封装保持 |
| 执行器权限/完成证明 | 不修改权限、执行或归档证明逻辑 | 仅既有入口回归，不发送模型任务或执行真实归档 |

横切门禁：管理列表、表单、弹窗和上传标签不适用，AC-XCUT 为 n/a；承接 S16-A001 的幂等与历史保护，S17-A002 容量不变。无独立 prototype，不需要新建页面骨架。用户截图为故障参考，局部一致模式沿用当前卡片；只替换 .rc-updated 内容，footer、优先级及动作族保持。动作映射：完成/归档 → DeliveryActionDialog；返修 → 既有 Chat 入口；检查验收条件 → 原只读检查，不新增 modal。布局、权限及禁用状态由既有组件决定。

样式采样覆盖 .rc-updated 的字号、字体、行高、颜色、nowrap、overflow，以及 footer gap/wrap 和卡片边界；结果见 evidence/visual/computed-style.json。按数据投影、标签、桌面/窄屏四组合分批验证。合成页只从 change-time.preview.html 进入，生产入口不导入该文件、不 Mock 产品 API。

自检发现重复归档身份下 record.directory 为 null，既有优先级路径会崩溃；增加空路径保护，保留 unknown 展示与只读策略，原 test_archive_active_precedence_unknown_and_missing_tasks 已通过。
