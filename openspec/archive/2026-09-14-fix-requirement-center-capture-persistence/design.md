---
change_id: fix-requirement-center-capture-persistence
bug_id: BUG-0014-requirement-center-capture-not-persisted
created_at: 2026-09-12 16:40:10
updated_at: 2026-09-12 22:17:09
---

## 设计背景

根因见 BUG-0014 root-cause.md：submitCapture 仅更新 React 状态，两类合成执行均无网络调用。BUG 已 approved 后纳入 sprint-005，估算5人天。现有 app/governance/writer.py 具备项目锁、操作记录、幂等和恢复能力；add-local-project-governance-loop 已有项目限定读取与写入设计，实施前核对当前能力，避免在同一项目另建互不协调的写通道。

## 目标与非目标

目标：REQ/BUG Capture 真正落盘，完整ID与有效字段可恢复，错误可见、输入保留，跨项目授权正确。
非目标：自动评审、自动入Sprint、在线执行全部治理命令、导入功能重做、视觉改版、历史临时卡片自动恢复、生产部署。

## 设计决策

### D1 创建接口与操作结果

新增 `POST /api/v1/requirement-center/captures`，复用登录及 space_id/repository_id 写授权。请求包含 type(requirement/bug)、title、description、对应类型的priority或severity、owner、source 与幂等键；标题去空格后必填，长度与现有表单一致（标题60、描述200），枚举由schema固定。客户端不能指定本机目录或正式ID。

复用治理操作记录及异步完成查询：接口返回202与operation_id，表示已受理，不能提示已创建；已有操作查询通道返回终态和完整Issue结果。仅 applied 后显示创建成功。若现有查询schema缺少结果对象，以兼容新增字段扩展并同步客户端。拒绝未授权、未绑定或维护中的项目；错误使用统一响应，不泄漏路径。

采用已有操作机制可协调文件写入与崩溃恢复；单独增加不持久化的内存队列或直接文件散写无法覆盖重试与部分失败，因此不采用。

### D2 编号、事实源与受控写入

在与现有写通道一致的项目锁内，读取目标类型注册表及plan/review/archive目录，取next_id与已分配最大编号的安全上界；服务端生成稳定slug，形成完整REQ/BUG ID，禁止覆盖已存在目录。请求字段按现有capture模板写入capture.md，trace记录captured/plan、时间、对应类型分级及关联空值；REQ仅保存priority，BUG仅保存severity，取用户明确选择值，不写旧hint。

写入集合包括plan目录、capture.md、trace.md、注册表entry/next_id和CHANGELOG当前行。借鉴现有受控应用的快照版本、预写日志、逐文件替换及恢复机制，全部验证后才将操作标记applied。读取方在应用/恢复期间不得展示半成品；与现有assert_readable策略一致。外部编辑造成前置版本冲突时拒绝或进入受控恢复，不覆盖新内容。

不将跨文件写入称为文件系统原子事务：一致性由协调锁、预写日志、读取屏障和恢复检查共同保证。恢复按前后镜像向前续写，不删除既有目录或文件；有后续修改或权限故障则进入recovery_blocked，保留数据并按部署文档的离线核验步骤处理。

### D3 幂等与重复提交

同一操作者、项目、幂等键绑定请求摘要；相同摘要返回同一操作与最终ID，不再分配编号，不同摘要返回冲突。前端首次提交生成键，超时重试复用；修改内容后开启新提交键。双击禁用按钮，服务端仍承担最终去重。编号分配及落盘计划在项目锁内完成，跨worker由现有锁/fencing机制协调。

### D4 前端与失败反馈

替换submitCapture本地编号分支，提交完整字段，展示提交/处理中/成功/失败状态。终态成功使用服务端Issue或重新读取上下文，不虚构document available。失败与超时保留表单输入，允许查询原操作再重试；项目切换使旧异步响应失效，不能写入新项目状态。Mock仅用于测试，不进入真实生产路径。

保持现有.rc-capture-dialog、标题焦点、键盘提交、字段布局与导入选择；本次无附件或参考稿复刻。需进行1440px和窄屏错误态/按钮可达性验证；若实施触及原型视觉行为，补对应UI Contract并同步父需求原型材料后验收。

### D5 观测与数据边界

```yaml
product_data_collection_observability:
  status: applicable
  affected_layers: [web, api, request_logs, usage_events, task_traces, task_trace_spans]
  reason: Capture创建是界面触发的异步多文件写操作，需要请求、操作及恢复节点关联。
  validation: SQLite/MySQL回归、真实浏览器request_id与operation_id关联、私有镜像恢复及Compose权限验收；详见trace与evidence。
```

复用请求封装的行为关联字段；直接API不伪造usage_events。复用已有行为采集能力，不引入独立事件存储；记录request_id、operation_id及任务节点的脱敏摘要，禁止表单全文、凭证和本机路径进入日志。Task Trace覆盖授权/计划/写入/恢复/结果，沿用既有保留期，不增加观测表。DB沿用现有governance操作记录，SQLite/MySQL都验证操作结果与幂等；若需schema或持久化语义扩展，同步数据库文档与迁移。对象存储N/A：产物为项目本地治理文件，无上传需求。部署拓扑N/A：复用当前worker和写通道，不新增容器；但实际挂载写权限需要验证。

## 风险与权衡

- 现有writer未覆盖目录创建 → 实施首项核验并补创建计划/恢复适配，不能直接旁路写入。
- 注册表被外部命令改动 → 版本校验与冲突反馈；锁仅协调注册写入方，不声称控制任意外部编辑。
- 与REQ-0022修改相同模块 → 顺序集成、保留已有读取/应用回归；不以全部归档作为硬依赖。
- 5人天估算上浮 → 在sprint-005剩余7人天缓冲内评估，超容量时重新规划。

## 迁移与回滚

先隔离项目测试与双数据库验证，再真实浏览器及现有部署挂载验证；不自动部署生产。不迁移旧临时卡片，其丢失描述无法可靠恢复。回滚按proposal：停收新操作、收敛在途任务、保留已写数据，网页创建临时禁用，使用治理命令规避。

## 待核验事项

无需要用户补充的产品决策。现有写入恢复机制对新目录和结果对象的支持由任务1.1核验；若超出设计边界，先回填设计和影响评估。

## M1 部署验收返修

证据confirmed：当前backend缺MOONBOX_GOVERNANCE_STATE_ROOT，启动Compose仅基础和Chat overlay，无governance-controller；store.root明确返回2605/503。上次隔离验证未覆盖当前服务接入。

本次用户已授权当前本地部署接入。复用既有controller容器，显式配置MOONBOX_GOVERNANCE_CAPTURE_MODE=continuous，仅Capture使用常驻门禁；其余治理操作仍要求限时maintenance.json。Capture常驻门禁核验同一绑定版本、可写治理目录和最近controller心跳，继续授权、锁、前后镜像校验与恢复屏障。不是自动续签维护声明，也不声称能锁住任意外部编辑器；检测外部版本变化仍拒绝覆盖。关闭模式或controller失联时停止新建。

增加授权项目Capture就绪查询，弹窗在提交前显示检查中/可用/不可用，失败不暴露路径；提交仍服务端复核。此为原Capture可用性补齐，无新增对象存储或DB表。API及部署文档同步。

| 附件/截图编号 | 页面/状态 | 对照对象 | 期望表现 | 实际表现 | 偏差项 | 检查方式 | 处置结论 | 证据入口 |
|---|---|---|---|---|---|---|---|---|
| 无用户附件；历史capture-error-390 | 需求中心Capture错误态 | 上轮真实截图与本轮错误文本 | 提交前解释服务不可用，恢复后可刷新 | 提交后才显示存储未配置 | 就绪状态缺失 | 代码、容器配置、接口及新1440/390截图 | 本次补状态，不改整体布局 | evidence/capture-error-390.png；store.root；运行容器配置白名单 |

动作矩阵：新建Capture→既有.rc-capture-dialog→检查中/可用/不可用；新增刷新状态按钮重查；创建按钮仅可用时启用。沿用布局与title焦点，采样dialog宽度/overflow和按钮可达性，测试网络未就绪与controller失联。无参考稿复刻或原型布局变更。

## Capture 分级返修契约

证据confirmed：表单统一优先级，API只接受priority，writer将BUG固定medium，与分级规范不一致。本轮仅修正既有Capture字段。

### 附件截图逐项视觉对照表

|证据|页面/状态|期望|实际/偏差|检查方式|处置/证据入口|
|---|---|---|---|---|---|
|历史capture-1440.png及源码，无用户附件|/requirements，Capture需求/BUG，1440及390|REQ三档priority、BUG五档severity|共享P0-P3，BUG无严重度选项|Capture分组DOM、类型切换、截图及computed style宽度/颜色|修正共享分级区；本轮grading视觉证据|

REQ提交priority P0/P1/P2/P3，BUG提交severity blocker/critical/high/medium/low；异类字段、缺失或非法分级拒绝。切换类型保留各自选值，默认REQ P1、BUG medium由表单明确展示。capture/trace/registry/index只写对应正式字段，不映射等级，不迁移历史记录。

product_data_collection_observability: applicable；affected_layers: Web/API/governance writer；沿用governance.capture与操作关联，不新增事件或正文日志。validation：类型字段、落盘一致性与浏览器状态；DB schema/对象存储N/A，无新增表或存储域。

## 扩宽与分级说明返修契约

用户明确要求REQ支持P0-P3，覆盖此前三档约束；本轮同步规范与API，不变更权限、存储或业务域。

### 附件截图逐项视觉对照表

|证据|页面与状态|期望|实际偏差|检查方式|处置与证据|
|---|---|---|---|---|---|
|grading-bug-1440.png、grading-capture-390.png，无新附件|/requirements Capture桌面/窄屏，深色|桌面840px，手机留边|现有560px|.rc-capture-dialog宽度、max-height、overflow计算样式及截图|仅扩桌面宽度，保留响应式|
|同上及分级源码|REQ/BUG选项，悬停/聚焦/触屏|REQ四档、BUG中文五档及解释|三档/英文/无说明|分组按钮、tooltip、aria-describedby、选中说明；hover/focus/tap观察|集中维护标签和说明；本轮evidence/help-*|

分级按钮共用说明组件，鼠标hover/键盘focus显示tooltip，选择后下方持续显示说明供触屏阅读；中文严重性映射既有英文值。验证1440/390宽度、tooltip不裁切、焦点、触屏选择以及P3持久化。

## 提示去重返修契约

### 附件截图逐项视觉对照表

|证据|页面/状态|期望|实际偏差|检查方式|处置|
|---|---|---|---|---|---|
|help-tooltip-1440.png、help-tooltip-390.png，无新附件|/requirements，深色1440/390，分级hover/focus|只保留下方选中说明|tooltip与下方文案重复|CaptureGrading DOM、hover/focus截图与说明计数|移除浮层及样式，保留原生按钮键盘操作和下方aria-live|
|help-capture-1440.png及页面源码|Capture服务ready|不显示成功提示，不占空白|成功状态容器持续存在|.rc-capture-readiness数量和布局；异常/检查态回归|仅检查中/失败显示状态容器，校验不变|

本轮覆盖此前Hover/焦点浮层契约；840px、P0-P3及中文严重性不变。API/DB/权限无变化。新视觉证据见evidence/quiet-*。
