---
requirement_id: REQ-0045-isolated-acceptance-data-source-label
title: 隔离验收环境在需求中心显示数据源标识验收标准
acceptance_status: not_started
created_at: '2026-10-11 10:30:14'
updated_at: 2026-10-11 10:37:48
owner: 产品团队
source: requirement.md
---

# 隔离验收环境在需求中心显示数据源标识验收标准

## 功能 AC

- [ ] AC-001 隔离验收服务即使占用常规需求中心地址，标题旁也持续显示“隔离验收数据”；不得依据 URL、端口或目录名推断来源。
- [ ] AC-002 正常服务返回受控的正常项目数据类别，页面不显示隔离警示；部署身份缺失、异常或与绑定不一致时显示“数据来源待确认”，不得默认正常。
- [ ] AC-003 标识、当前授权项目、短快照版本和卡片数据来自同一次需求中心上下文响应；切回正常服务并刷新后，已归档 Change 显示“已完成”，标识同步改变。
- [ ] AC-004 项目或空间切换后，旧项目的标识和卡片不冒充新项目当前态；迟到响应不能覆盖新选择。
- [ ] AC-005 刷新失败时若仍展示上次成功读取的卡片，应显示旧快照提示与重试入口；无权限时不泄露无权项目的来源信息。
- [ ] AC-006 短快照版本仅用于人工核对，不暗示与源工作区实时一致；无可信生成时间时不展示“生成于”时间。

## UI 与安全 AC

- [ ] AC-UI-001 标识位于“需求研发流转看板”标题旁，1440px、390px 和深浅主题下均可读，不遮挡“新建 Capture”、筛选或看板列头。
- [ ] AC-UI-002 隔离、正常、未知和旧快照使用可区分的文本与视觉状态；颜色不是唯一信息渠道，屏幕阅读器可读取状态名称。
- [ ] AC-SEC-001 页面、公开 API 响应和请求日志不得暴露宿主机路径、容器挂载源、环境变量原文、密钥、完整治理文档或完整快照哈希。

## API、部署与观测 AC

- [ ] AC-API-001 来源类别使用稳定枚举并由服务端可信部署声明确定；接口响应字段、OpenAPI、客户端生成物与 `docs/03-api-index.md` 保持一致。
- [ ] AC-DEPLOY-001 正常与隔离验收部署入口均明确配置来源类别，配置缺失时按未知态处理；部署文档和环境示例解释该边界。
- [ ] AC-DATA-001 请求日志仅保留受控来源类别、结果和必要耗时摘要；不新增持久行为事件或 Task Trace 时，在 Change 中记录理由，若范围扩大则重新评估。

## 知识库适用性

本需求为前台需求中心的页面级状态标识，不命中 `admin-list`、`admin-form`、`admin-modal` 或 `media-upload` 标签，因此无对应 AC-XCUT。引用 `docs/knowledge-base/best-practices/prototype-driven-ui-gate.md` 的原型与视觉门禁，以及 Sprint-007 复盘中“需求中心状态显示保持事实源优先”的经验；相关要求已写入功能、UI 和原型 AC。

## 原型驱动 UI AC

- [ ] AC-PROTOTYPE-001 原型拆解包含页面清单、标题区与标识组件层级、隔离/正常/未知/旧快照状态、刷新触发、数据依赖、响应式断点和 1440px 验收焦点。
- [ ] AC-PROTOTYPE-002 后续 Change 设计写入 UI Contract 与 UI Skeleton，先确定标题区、标识插槽、状态容器、稳定 selector 和 Mock/API 边界，再实现细节。
- [ ] AC-PROTOTYPE-003 实现阶段提供 1440px 桌面视口的正常、隔离与未知状态视觉证据，并采样标题、标识和操作按钮的关键 computed style。
- [ ] AC-PROTOTYPE-004 实现阶段验证 390px 窄屏、深浅主题、长项目名和刷新失败状态，标题、标识与主操作不重叠。
- [ ] AC-PROTOTYPE-005 归档前核对 REQ 主文档、验收标准、trace、Change 设计和最终截图；返修后旧视觉证据失效并重新取证。

## 验收结果回填

```yaml
acceptance_status: not_started
accepted_at: null
accepted_by: null
source_change: null
source_sprint: null
evidence: []
failed_items: []
source_event: req.review
notes: 由 Workflow Sync 根据 Change/Sprint 状态回填。
```
