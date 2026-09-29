---
requirement_id: REQ-0028-chat-skill-codex
title: Chat 工作台支持多图片输入、仓库 Skill 快速引用与 Codex 截图基线体验增强
terminal: web-catalog
version: v1
status: done
owner: product
source: capture.md
parent_requirement: REQ-0025-chat-workbench
created_at: 2026-09-14 11:02:44
updated_at: 2026-09-29 14:30:31
priority: P1
---

# Chat 工作台多图片输入与 Skill 快速引用

## 1. 背景与价值

Chat 工作台已经通过 REQ-0025 交付个人会话、真实 Codex 执行、对话与轨迹双视图、权限校验、停止重试、Diff 和工具详情。用户现在希望进一步贴近 Codex 使用体验：在同一输入区上传多张图片，快速引用仓库中的 Skill，并以提供的 Codex 截图作为对话区视觉基线。

本需求是 Chat 工作台的体验与输入能力增强。它不重做 REQ-0025 的会话架构、执行安全和轨迹详情，也不覆盖 REQ-0035 的 Agent、模型和推理配置选择。多图片输入与 Skill 引用都必须进入真实执行链路，不能只停留在前端装饰；同时继续保留 MoonBox 的空间、仓库、对象权限和 OpenSpec 治理边界。

用户已在探索阶段确认：

1. REQ-0028 与 REQ-0035 保持独立，REQ-0028 聚焦图片与 Skill 引用。
2. Codex 截图作为后续 UI Reference 基线，需要在补全文档或 OpenSpec 阶段提供附件或路径。
3. Skill 快速引用首版只作为本轮上下文引用，不自动执行 Skill 命令或绕过治理门禁。

## 2. 目标用户

- 产品负责人：在描述需求、验收反馈或界面问题时附多张截图，并引用仓库 Skill 让 Codex 按项目规则理解上下文。
- 开发与项目成员：在 Chat 工作台中引用测试、OpenSpec、REQ/BUG 或治理 Skill，减少反复复制规则说明。
- 平台维护者：需要确保图片、Skill 内容和执行上下文受权限、脱敏、容量和观测边界约束。

## 3. 范围

### 3.1 首版包含

- Chat 工作台输入区支持多图片选择、预览、移除、上传状态和发送前校验。
- 图片随本轮消息进入后端执行请求或等价上下文构造链路，执行端无法读取或读取失败时明确提示。
- 输入区支持快速引用当前仓库内可用 Skill，首版以 `.agents/skills/` 或后续服务端 Skill 索引为候选来源。
- Skill 引用作为本轮上下文材料传入 Codex，展示引用名称、来源路径或摘要，不自动执行 Skill 命令。
- 对话区视觉以用户提供的 Codex 截图为参考基线，进行风格迁移或局部一致，而不是逐像素复刻 MoonBox 以外的业务语义。
- 保留现有对话/轨迹双视图、消息复制、本轮轨迹入口、停止、重试、Diff、权限和会话历史能力。
- 覆盖深浅主题、1440px 桌面、窄屏、多图片、长 Skill 名、上传失败、发送中禁用和历史轮次回显。

### 3.2 首版不包含

- 不新增 Agent、模型和推理强度选择；该范围归属 REQ-0035。
- 不新增需求中心 Capture 的图文候选审阅与确认采集；该范围归属 REQ-0029。
- 不自动执行所引用 Skill 的命令，不自动创建 REQ/BUG、OpenSpec Change、Sprint 或代码修改授权。
- 不支持任意文件类型上传、批量目录上传、外部网盘导入或图片 OCR 编辑器。
- 不新增后台 Skill 管理页面、Skill 市场、跨仓库 Skill 订阅或个人自定义 Skill。
- 不改变 Chat 工作台个人私有、服务端执行、同会话串行、权限重验、停止重试和删除保留规则。
- 不把截图参考稿中的非 MoonBox 业务信息、私有路径、账号信息或示例回复复制进产品。

## 4. 功能要求

### FR-001 多图片输入

聊天输入区应提供图片添加入口，支持一次选择多张图片并在发送前展示缩略预览、文件名或顺序、上传状态、移除动作和错误提示。图片数量、格式、单张体积、总大小和文本长度应由前后端共享配置或服务端能力返回，不得仅依赖前端限制。

文字与图片均为空时不得发送。仅图片输入是否允许由后续补全文档确认；若允许，页面需要提示图片会作为本轮上下文输入。图片上传失败、格式不支持、体积超限或服务端不可读时，必须阻止发送或标记该图片不可用，不能让用户误以为 Codex 已读取图片。

### FR-002 图片执行链路

发送消息时，已确认可用的图片应进入本轮执行上下文。后端需保存图片引用、顺序、脱敏摘要、大小、类型、上传结果和本轮关联关系，确保刷新页面或查看历史时可以复核当轮使用了哪些图片。

执行端不支持图片、模型能力不足或图片读取失败时，应向用户展示可恢复提示，并记录本轮实际处理状态。系统不得在通用日志、请求日志、Task Trace metadata 或错误信息中保存完整图片内容、完整 Prompt、密钥、Cookie、Authorization header、本机绝对路径或真实客户敏感数据。

### FR-003 Skill 候选读取

聊天输入区应提供仓库 Skill 快速引用入口，例如 slash 菜单、`@` 引用或紧凑选择器。候选应来自当前会话绑定仓库中用户有权访问的 Skill 清单，首版可优先读取 `.agents/skills/` 的 Skill 元数据，或使用后续服务端索引能力。

候选展示应至少包含 Skill 名称、简短说明、来源路径或所属域。无法读取 Skill、仓库未绑定、权限不足或 Skill 元数据缺失时，应展示明确空态或错误原因，不暴露内部绝对路径、凭证或宿主机配置。

### FR-004 Skill 上下文引用

用户选中 Skill 后，输入区应展示已引用 Skill，并允许移除。发送时，引用的 Skill 只作为本轮上下文材料或约束提示传入执行链路，不自动触发对应 `/req-*`、`/bug-*`、`/opsx-*`、`/sprint-*` 或其他写入型命令。

若 Skill 内容过长，应按服务端安全策略截断或摘要，并提示用户实际注入范围。历史轮次应能追溯本轮引用的 Skill 名称、版本或内容摘要；后续仓库 Skill 发生变化时，不应重写历史轮次的引用事实。

### FR-005 对话区视觉基线

对话区应以用户提供的 Codex 截图为参考基线，在后续 `/req-complete` 或 `/req-opsx` 阶段建立 UI Reference Replication Contract。首版目标是风格迁移或局部一致：输入区、附件预览、Skill 引用、消息气泡、助手正文、轨迹入口、发送/停止状态和滚动阅读体验贴近参考，但仍保留 MoonBox Ops 视觉系统、共享导航、空间权限和现有业务语义。

在截图附件尚未补充前，本需求只能记录参考诉求，不能进入“严格复刻已完成”的验收结论。后续实现必须提供 1440px 桌面、窄屏、深浅主题、关键交互截图和必要 computed style 证据。

### FR-006 保留轨迹详情与权限边界

多图片和 Skill 引用不得削弱现有轨迹详情。用户仍可从消息定位本轮轨迹，查看工具节点、状态、Diff 和脱敏参数结果。图片和 Skill 引用应作为本轮上下文来源展示或追溯，但不得把完整图片内容、完整 Skill 文件或未脱敏工具输出塞入轨迹详情。

所有发送、读取、历史回显、图片下载或 Skill 读取均应重验会话所有者、空间成员、仓库授权和对象权限。仓库撤权、会话归档、运行中、停止中、状态未知或服务未就绪时，输入区控件状态必须与现有 Chat 工作台门禁一致。

### FR-007 状态、失败与恢复

页面应区分图片选择中、上传中、上传失败、Skill 读取中、候选为空、引用失效、发送中、停止中和执行失败。失败不应清空用户草稿、已成功上传图片或已选 Skill；用户应能移除失败项、重试上传或继续编辑。

重复点击、网络重发或响应丢失时，应复用既有会话与轮次幂等策略，不重复创建会话或重复提交同一批图片与 Skill 引用。若服务端判定图片或 Skill 版本已过期，应提示用户重新确认后再发送。

### FR-008 安全、容量与保留

图片上传、引用存储和执行上下文构造必须有容量边界。达到容量上限时，系统应保留已有历史查看和清理能力，拒绝新增或提示用户移除材料，不静默丢弃图片或引用。

图片业务保留、主动删除、备份副本和执行端副本策略需在后续设计中与 Chat 会话保留策略对齐。删除会话或清理副本时，应说明图片材料、Skill 引用摘要、业务主存储、执行副本和审计记录各自处理范围，不用删除列表来冒充全部副本已清除。

### FR-009 测试与文档

后续实现阶段应覆盖多图片选择、移除、上传失败、大小格式限制、仅文字、图文混合、仅图片策略、Skill 候选、Skill 引用移除、发送参数、历史回显、权限撤销、仓库缺失、服务不可用、运行中禁用和窄屏布局。

如新增或调整 API 字段，应同步 OpenAPI、客户端生成、错误码、API 文档和接口测试。如新增图片或引用持久化字段，应同步数据库设计、迁移、SQLite/MySQL 兼容测试和对象存储策略。

## 5. UI 约束

- 输入区应保持紧凑，不因多图片或 Skill 引用挤压文本输入、发送按钮、停止按钮或执行状态。
- 图片预览应有稳定尺寸、删除入口、上传进度或错误态；长文件名需要截断或 tooltip。
- Skill 引用应以轻量 token、菜单或列表表达，避免把完整 Skill 内容直接展开在输入区。
- 所有按钮、菜单、预览、错误提示和 tooltip 应沿用 MoonBox Ops 风格、近直角、细边框、金色强调和深浅主题 token。
- 窄屏下图片和 Skill 区域可换行或折叠，但不得造成页面横向溢出。
- Codex 截图参考稿进入后，后续文档必须拆解页面壳、输入区、消息区、轨迹入口、附件预览、Skill 引用、滚动行为和交互状态。

## 6. 关联需求

| 条目 | 关系与边界 |
|---|---|
| REQ-0025-chat-workbench | 父需求，提供 Chat 工作台、真实 Codex 执行、会话、轨迹、权限和保留基础。 |
| REQ-0029-capture-multimodal-candidate-review | 同涉及多图片输入，但作用于需求中心 Capture 候选审阅，不替代 Chat 工作台输入增强。 |
| REQ-0035-chat-agent-model-reasoning-selector | 同属聊天输入区增强，但聚焦 Agent、模型和推理配置选择；本需求不包含该范围。 |
| REQ-0023-product-workbench-modern-ops-visual-system | 关联前台 Ops 视觉体系，后续 UI 需延续品牌和组件规则。 |

## 7. 产品数据采集与链路观测

```yaml
product_data_collection_observability:
  status: applicable
  affected_layers:
    - web_request_wrapper
    - api
    - db
    - object_storage
    - usage_events
    - request_logs
    - task_traces
    - task_trace_spans
  reason: 多图片上传、Skill 候选读取、Skill 上下文引用和本轮发送会影响 Web 请求封装、API 字段、可能的持久化结构、对象存储、行为事件、请求日志和 Codex 执行 Task Trace。
  validation: 后续 req-complete、OpenSpec 和实现阶段需验证图片和 Skill 引用只记录脱敏标识、数量、大小、类型、来源摘要和处理结果；请求日志与 Task Trace 不保存完整图片、完整 Prompt、完整回复、完整 Diff、密钥、凭证、本机绝对路径或真实客户敏感数据；观测失败不阻断主流程但保留脱敏降级摘要。
```

行为事件可记录添加图片、移除图片、选择 Skill、移除 Skill 和发送结果；属性只保存脱敏数量、类型和结果摘要。请求日志可记录接口状态、错误码、材料数量和脱敏配置摘要。Task Trace 可记录上传校验、Skill 解析、上下文构造、执行提交和结果处理节点，便于定位图片不可读、Skill 失效或执行端降级。

## 8. 待确认事项

| 标识 | 事项 | 推荐建议 | 可选方向与影响 |
|---|---|---|---|
| D-001 | Codex 截图基线 | 补充截图或文件路径，并在 `/req-complete` 拆解为 UI Reference Contract | 若不补截图，只能按现有 Chat 工作台和文字描述做风格迁移，视觉验收强度较低 |
| D-002 | 图片限制 | 由服务端返回数量、格式、单张体积和总大小，并覆盖前后端一致校验 | 若仅前端限制，接口和执行端仍需防绕过；若限制过高，会增加容量和执行失败风险 |
| D-003 | 仅图片输入 | 默认允许但必须明确“图片作为本轮上下文”，执行端不支持时阻止发送 | 若要求必须有文字，可降低歧义但增加用户输入成本 |
| D-004 | Skill 来源 | 首版读取当前仓库 `.agents/skills/` 元数据或服务端索引 | 若允许跨仓库或个人 Skill，需要新增权限、索引和缓存策略 |
| D-005 | Skill 注入范围 | 注入 Skill 摘要或关键说明，并保留引用快照 | 若注入完整 Skill，需处理超长上下文、敏感内容过滤和历史快照容量 |

## 9. 状态块

```yaml
status: done
lifecycle_stage: review
iteration: sprint-006
openspec_changes:
  - change_id: add-chat-workbench-image-skill-context
    type: add
    status: archived
source_material:
  - capture.md
  - req-explore REQ-0028-chat-skill-codex
  - issues/requirements/archive/REQ-0025-chat-workbench/requirement.md
  - issues/requirements/plan/REQ-0029-capture-multimodal-candidate-review/requirement.md
  - issues/requirements/plan/REQ-0035-chat-agent-model-reasoning-selector/requirement.md
  - docs/standards/product-data-collection-observability.md
next: 无
```
