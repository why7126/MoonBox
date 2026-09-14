---
change_id: add-chat-workbench-codex
created_at: 2026-09-08 12:15:12
updated_at: 2026-09-13 23:30:00
---

## 1. 前置合同与可行性门禁

- [x] 1.1 复核 REQ-0025 in_sprint 与 sprint-004 双向追溯、RC-001至004、现有 API/DB/部署边界；固定单一路线及运行时版本验证计划。
- [x] 1.2 承接原型反向工程、selector与组件文件映射、动作按钮及modal矩阵、computed style基线；冻结现有DS样式采样与分批证据计划。
- [x] 1.3 创建 /chat UI Skeleton、状态容器和无副作用占位边界，完成1440px首轮截图确认；通过前不进入细节实现。
- [x] 1.4 在受控测试仓库验证接入创建/恢复、两轮实际修改及Diff、停止确认/断连/进程终态、权限与凭证隔离；记录证据关闭RC-001，不能用Mock替代。
- [x] 1.5 固定额度/并发/容量/预留配置、超限行为、备份及执行端副本删除时限，明确入口设计并回填RC-002/003；未配置不得开放真实执行。

## 2. 存储与执行服务

- [x] 2.1 实现SQLite/MySQL增量schema与迁移、会话/消息/轮次/快照/事件/Diff/锁/预留模型及查询索引，验证迁移可重复和兼容。
- [x] 2.2 实现平台认证适配、独立worker与预配置仓库工作区/分支生命周期；防目录和符号链接逃逸。
- [x] 2.3 实现会话所有者/空间/对象授权、快照引用及撤权后历史内容/执行端上下文限制，覆盖AC-002/008至011/024至026。
- [x] 2.4 实现幂等发送、持久化互斥、worker fencing、排队/资源预留与额度结算；验证双标签页和worker重启不重复写入。
- [x] 2.5 实现真实事件持久化、归一化和游标重放，乱序终态保护；可信前后基准及本轮/累计Diff。
- [x] 2.6 实现停止中/未知/终态确认与原运行恢复，显式重试复用授权快照；覆盖停止竞争和网页断连。
- [x] 2.7 实现主动删除、当前变更保护、容量边界和结果预留、主存储/副本/备份清理追踪；审计与代码独立保留。

## 3. 接口与观测

- [x] 3.1 实现design列明的会话、关联、轮次、中止、重试、事件和Diff接口，复用ApiResponse与认证，登记冲突/额度/容量/状态未知错误。
- [x] 3.2 实现鉴权fetch事件流及断点读取，不将凭证放URL；同步OpenAPI流式契约、Orval客户端与docs/03-api-index.md。
- [x] 3.3 盘点并补齐本能力必要行为/请求/执行观测链路，关联可信ID，持久化前脱敏及采集降级；验证AC-029/030。

## 4. 页面与动作族细节

- [x] 4.1 在Skeleton确认后接通导航与需求中心显式Chat入口，保留原抽屉及阶段反馈；会话列表、搜索和新建只使用授权数据。
- [x] 4.2 统一实现历史、重命名、归档/恢复、删除及关联Dialog动作族，关闭/取消、disabled/error/focus和fixed toast一致。
- [x] 4.3 实现消息、输入、额度容量反馈和执行详情，选历史仍可停止当前运行；空Diff、二进制、大内容及未知状态真实呈现。
- [x] 4.4 完成深浅主题、详情折叠及窄屏布局；移除演示控制/固定样例，验证安全Markdown及键盘/外部关闭。

- [x] 4.5 按需求中心基线提取共享侧边栏与账号/空间动作，统一主题偏好、折叠及窄屏；完成两页样式、权限和菜单回归及隔离部署证据。

## 5. 交付验证与文档回填

- [x] 5.1 运行后端接口/权限/互斥/重启/清理测试及SQLite/MySQL矩阵；并发与停止竞争先串行验证，再运行互不干扰测试。
- [x] 5.2 运行聚焦Vitest/Testing Library及OpenAPI客户端校验，覆盖原需求中心抽屉和新入口回归。
- [x] 5.3 完成1440×900、1024×600与390×844分批截图、computed style、动作族与内部stopPropagation交互证据，关闭RC-004。
- [x] 5.4 验证实际部署worker、挂载、凭证、网络与数据保留，更新docs/01-architecture.md、02-deployment.md、04-database-design.md及无真实值配置示例；不自动执行生产升级。
- [x] 5.5 完成34条功能、8条横切和8条原型AC映射回填，同步REQ所有子文档、prototype context与Change trace；无证据不勾选通过。
- [x] 5.6 运行OpenSpec、中文优先、目录、Sprint scope与Workflow Sync校验；复核13人天估算，超量先调整Sprint，所有任务完成后才能进入归档。


## 6. 推荐组合受控落地

- [x] 6.1 实现SQLite一致性备份、独立删除日志、离线恢复前重放及校验失败关闭；验证删除不复活、代码和审计保留。
- [x] 6.2 实现每会话独立执行容器，验证固定Linux运行时、真实双轮/恢复/停止及凭证、网络、工作区隔离；清理临时资源并记录限制。

- [x] 6.3 完善常规部署脚本env/模式/停止行为，显式--chat-test接入容器执行、备份初始化和受控启停，验证幂等、失败关闭及不删除常规数据。

## 验收返修记录

- [x] 建立附件截图逐项对照、selector与折叠动作契约，确认逐delta渲染和表格分支缺失根因。
- [x] 修复事件归并、当前/历史状态及安全Markdown表格，完成聚焦测试和生产构建。
- [x] 补齐1440深浅与390视觉/样式证据、部署复验及文档同步。

REQ子文档一致性扫尾：PRD、业务流程、用户故事、验收、trace及prototype context同步；原prototype.html保留原参考资产，偏差与最终意图记录于context和design；无需修改原型HTML或历史截图。
product_data_collection_observability: applicable；affected_layers=[web_event_display]；reason=仅现有事件的展示归并，不新增采集或改变API/DB/request_logs/usage_events/Task Trace/请求封装；validation=去重和边界测试、安全渲染回归。


## 2026-09-11 验收返修：Harness 对话与轨迹

以本机 DeepSeek Harness 的对话/轨迹结构为新参考，保持 MoonBox 共享导航与空间/对象权限。对话为右侧用户气泡、无边框助手正文、紧凑自适应输入、消息复制与本轮轨迹入口；Enter发送、Shift+Enter换行、中文输入法不误发送。活动轮次显示过程摘要，失败附着轮次。消息历史加载更早页，滚动阅读不强制跳底；轨迹标签隐藏保留阅读状态。

轨迹包含按原标识配对的工具节点、搜索、内容折叠、事件概览与可调整宽度的详情。详情提供概述、参数、结果、Schema可用性及计时；窄屏上下排列。现有停止确认、原轮次重试、引用快照及Diff保留。事件每窗口最多1000条，可以读取后续窗口或从头查看；窗口边界缺少工具开始记录时不伪造开始时间。旧数据未采集字段明确显示不可用。耗时概览按对数缩放并显示说明，不冒充模型请求计时。

新增工具详情仅存于本人会话事件JSON：白名单参数、截断输出、退出码、状态、记录时间和耗时来源。先脱敏再限长；不新增表/接口/认证/部署范围。平台日志与审计不记录这些正文。明确final_answer可用时最终消息使用最终正文，其余过程留在轨迹；旧协议保持兼容。Schema、模型请求层级、缓存率、内部推理不编造，也不增加模型切换、附件、分支入口。

验证：前端31项聚焦回归通过；后端工具/权限/结算聚焦回归与构建记录见本批最终验证摘要。真实组件+合成API在1440桌面和390窄屏深浅主题观察；样式与无横向溢出记录于 evidence/harness-trajectory/verification.json。未宣称与参考逐像素相同，原始参考截图含私人路径而未落盘。新一轮真实模型执行与合成视觉验收明确区分。

- [x] 建立参考契约、源码/截图差异及状态矩阵。
- [x] 完成双视图、工具详情与兼容数据采集。
- [x] 完成前端行为与浏览器深浅/窄屏检查。
- [x] 完成本批最终后端验证、部署与文档同步。


### 本批最终验证与一致性扫尾

后端48 passed、1 skipped（需显式启用的真实模型测试）；前端31 passed，TypeScript及生产构建通过。工具详情通过模拟App Server→Worker→真实测试数据库的入库、脱敏、结果、退出码及耗时断言；不冒充本轮真实模型验证。Web与Worker按原Compose配置更新并健康，更新前活动运行数为0；运行Worker的execution.py和tool_record.py摘要与工作树一致。原有recovery容器保留。

REQ 子文档一致性扫尾：requirement、business-flow、user-stories、acceptance、prototype/web/context已同步；trace由工作流同步。prototype.html保留原始历史参考，不覆盖附件来源，新基线冲突与覆盖范围记录在context和design。Schema、模型请求级分组、内部推理、附件与分支不属于本批；界面明确不可用，不伪造采集。产品数据采集影响声明承接本次design契约，无新表或OpenAPI结构变化，不需迁移或Orval再生成。既有SSE payload为开放JSON，本次字段说明同步API索引和DB设计。

本Change严格规格、中文优先、目录、Sprint scope与上下文预算检查通过。全仓中文优先校验被另一活动Change的既有英文标题阻断，未修改无关Change。浏览器验收为合成API配合真实组件，1440/390深浅截图已在工具输出中观察，脱敏样式摘要为长期证据；尚未进行与DSH逐像素差异断言。


### 首次输入返修（2026-09-11）

confirmed：Composer无conversation时禁用输入，SessionDialogs新建要求确认；创建API缺少请求幂等字段。证据与动作对照先记录于design。本次在既有会话能力内调整，不新增权限/存储/部署边界。

- [x] 本地草稿、输入区仓库选择、移除新建弹窗；失败保留标识。
- [x] 创建可选幂等字段、原主键竞争去重及旧接口兼容；同步OpenAPI/Orval。
- [x] 单仓库/多仓库、离线输入、响应丢失与并发/撤权/删除测试。
- [x] 1440深浅与390交互截图观察、computed style和合成首发验证。

REQ 子文档一致性扫尾：requirement、business-flow、user-stories、acceptance、prototype/web/context同步；trace由Workflow Sync回填。无需更新prototype.html及历史截图，原因：保留原始参考资产，本次冲突以design/context明确覆盖。API与DB设计同步可选幂等语义，无DDL迁移；权限、安全、部署规则、对象存储及保留周期未改变，无需修改对应规则。


### 首次输入最终验证

前端5文件23项相关测试通过（含空间草稿隔离），TypeScript及生产构建通过；后端39项通过、1项真实模型选择性跳过。1440/390深浅主题完成截图观察和样式采样，合成API浏览器首次发送进入会话并更新URL，新建直接回草稿，无弹窗。证据：evidence/first-send/verification.json。

Web/API已按原Compose更新且healthy，更新前活动运行为0；实际HTTP OpenAPI幂等字段及运行后端源码摘要与本地一致，Web产物匹配。不需要DB迁移，未额外启动模型任务或修改凭证、配额、保留策略。

OpenSpec严格、中文优先、目录、上下文预算、Sprint scope及观测门禁通过。本批文件空白检查通过；全仓diff检查发现其他需求中心测试的既有/并行尾随空格，本批未修改。OpenAPI生成脚本存在本机pnpm版本检查不匹配，已导出契约并使用项目本地Orval成功生成。


### 顶部精简返修

- [x] 先补附件逐项对照、默认仓库与按钮动作族契约。
- [x] 移除Chat顶部两行调用，迁移切换按钮，修正自适应布局及输入卡居中。
- [x] 27项前端测试、TypeScript及构建通过；1440/390深浅主题截图观察、computed style与切换草稿检查完成。

REQ 子文档一致性扫尾：requirement、business-flow、user-stories、acceptance、prototype/context同步，trace由Workflow Sync回填。原prototype.html与历史截图不改，原因：保留原始参考，本次覆盖在design/context中声明。不修改共用ProjectBinding，以免影响其他页面。API、DB、权限、存储、部署规则及客户端生成无变化，无需后端测试或重新生成。证据见evidence/compact-header/verification.json。

顶部精简最终验证：27项前端测试通过，最终Docker构建包含输入居中修正且TypeScript通过；Web运行且HTTP冒烟通过（无独立Docker Health字段），后端和Worker未重启。OpenSpec严格/中文优先/目录/预算/Sprint scope/观测及本批空白检查通过。视觉为真实组件+合成接口，不新增真实模型运行。


### 标题编辑返修

- [x] 补齐标题/历史动作族与固定标签对照契约，confirmed为重复入口。
- [x] 复用重命名弹窗，移除picker及常驻权限标签，历史保留说明。
- [x] 21项前端相关测试通过，构建通过；标题保存、空白、失败保留、空草稿不提前创建及历史切换覆盖。

REQ子文档一致性扫尾：requirement、business-flow、user-stories、acceptance、prototype/context同步；trace由Workflow Sync回填。原prototype.html和历史截图保留，不覆盖历史事实；新契约以design/context为准。API、数据库、安全校验、请求采集及客户端契约不变，无需迁移、后端重测或生成客户端。集成代码重新引入的项目连接行按上一轮用户授权继续从Chat移除；治理数据逻辑不改。

标题编辑视觉验收：1440/390深浅主题真实组件配合合成接口通过，弹窗宽680/366px，标题13px，无横向溢出；保存/历史同步/取消已观察，证据evidence/title-edit/verification.json。

标题编辑返修收尾：Web部署产物已核对且HTTP冒烟通过；21项相关测试、构建、OpenSpec严格/语言/目录/Sprint scope/预算/观测与本批空白检查通过，未新增模型运行。


### 输入框提示精简返修（2026-09-13）

输入框正常就绪时不显示常驻执行说明或空提示节点；仅保留服务未就绪、归档、原运行未终止、缺少仓库及发送失败提示。发送按钮在有无提示时均右对齐，权限校验与请求流程不变。

验证：Composer 6项测试、TypeScript和生产构建通过。1440×900及390×844深浅主题截图已在浏览器工具观察；正常态hint节点不存在，右边界差0px，无横向溢出。真实组件配合合成API，未触发真实执行。

REQ 子文档一致性扫尾检查：requirement、acceptance、prototype/context已同步；business-flow及user-stories无需更新，原因：创建、发送、权限与状态流转不变，仅删除默认说明。trace由Workflow Sync更新。prototype.html和截图为历史参考保留；API、数据库、安全、部署契约及客户端生成无需更新。
