---
change_id: add-chat-workbench-codex
type: add
status: applied
requirement: REQ-0025-chat-workbench
sprint: sprint-004
created_at: '2026-09-08 12:15:12'
updated_at: 2026-09-14 00:03:14
source_requirement: issues/requirements/archive/REQ-0025-chat-workbench/
knowledge_base_refs:
- docs/knowledge-base/best-practices/prototype-driven-ui-gate.md
- docs/knowledge-base/best-practices/admin-modal-width-css-cascade.md
- docs/knowledge-base/best-practices/admin-list-page-consistency.md
- docs/knowledge-base/retrospectives/sprint-003-retrospective.md
prototype_refs:
- path: issues/requirements/archive/REQ-0025-chat-workbench/prototype/web/prototype.html
  role: sanitized-interaction-reference
- path: issues/requirements/archive/REQ-0025-chat-workbench/prototype/web/context.md
  role: decomposition-and-replication-contract
prototype_gate:
  decomposition: done
  ui_skeleton: done
  visual_acceptance_1440: passed
  req_final_consistency: passed
product_data_collection_observability:
  status: applicable
  affected_layers:
  - web_request_wrapper
  - api
  - db
  - usage_events
  - request_logs
  - task_traces
  - task_trace_spans
  reason: 真实 Codex 长耗时执行、上下文和会话持久化涉及权限与观测；无附件上传和新增管理页。
  validation: 后端71项、MySQL43项、Web22项及真实隔离/常驻/当前账号执行证据通过，保留权限、脱敏、真实计量和链路ID，详见evidence/target-deployment。
---

# Change Trace

## Requirement Readiness Report

Ready：29/29任务完成，实际部署、当前登录账号两轮执行及既有视觉证据通过；最终交付范围与验证入口见本文末尾。

## 影响与分类

add：新增web-catalog-chat-workbench与codex-session-execution；backend/web/database/api受影响，admin/miniapp不新增页面，storage不引入附件链路。已完成Chat页面、状态容器、共享侧边栏、API/DB、常驻worker与隔离执行接入及相关测试。

## Conflict Report

保留原型区域和动作，按用户确认使用Ops视觉。停止确认、断连、删除、快照和当前运行控制差异在design Conflict Resolution明确；现有需求中心抽屉保留，因此无既有规格MODIFIED/REMOVED。

## UI证据状态

| 项 | 状态 | 入口 |
|---|---|---|
| 原型拆解 | done | 来源prototype/web/context.md |
| UI Contract与参考复刻契约 | defined | design.md |
| UI Skeleton | done | evidence/ui/skeleton-dark-1440.png |
| 1440px与关键交互PNG | partial | evidence/ui下4张骨架截图，动作族仍pending |
| computed style | batch-1 passed | evidence/ui/skeleton-computed.json和ds-baseline.json |
| Mock/API | 未接入 | 原稿模拟只作参考；正式生产禁止模拟成功 |
| REQ最终一致性 | pending | 实现结束回填 |

## 风险与条件

RC-001版本/能力/隔离实测、RC-002配置阈值和副本清理尚未闭环；RC-003设计选择保留抽屉并增加显式Chat入口，待实现验证；RC-004目标视觉证据待实施。Sprint缓冲2人天，仅6.67%，不重复计量两个能力规格。

## 验证

本阶段运行OpenSpec strict、中文优先、上下文预算、目录结构、Sprint scope与Workflow Sync校验；初次中文校验发现CLI模板英文标题，已改为中文后复验。不运行真实模型、不修改生产环境。

## 变更记录

| 时间 | 事件 | 说明 |
|---|---|---|
| 2026-09-08 12:15:12 | req.opsx | CLI创建Change并生成proposal、design、两份新增规格与25项任务，已关联sprint-004，实施验证待执行。 |


## 首轮apply证据与阻塞

进度3/25：1.1–1.3完成，其余22项未勾选，真实执行、全功能与完整视觉验收未通过。

- Cross-cutting：前台modal类比admin-modal；AC-XCUT、knowledge_base_refs和best-practices读取齐全，PROCEED。弹窗未实现，不能宣称动作族通过。
- Prototype/Reference：batch-1完成；Skeleton首轮浏览器确认已执行。完整UI任务仍待RC-001及剩余交互证据，无需重新选择风格。
- 类型检查：pnpm exec tsc --noEmit --incremental false通过。
- 聚焦测试：Chat 7、Homepage 5，共2文件12测试通过；覆盖不可执行边界、主题/折叠、未登录跳转与状态容器。
- 浏览器：项目Node Playwright/Chromium，临时服务18112，脚本src/web/scripts/check-chat-skeleton.cjs（在src/web运行）；Python未安装Playwright，使用项目依赖。1440×900深浅、1024×600、390×844，发送禁用且边界可达；PNG和computed JSON见evidence/ui。合成登录标记无API权限，仅用于骨架检查，不是服务端鉴权通过证据。
- 首轮窄屏存在栅格/侧栏宽度过渡导致截图时刻不一致；根据computed style和DOM尺寸关闭本页宽度过渡、布局稳定后重采并覆盖旧图，增加发送左右/上下边界断言。
- 协议证据见evidence/protocol-probe.json：隔离临时配置握手和只读线程创建成功，account_present=false。没有使用宿主个人凭证或发起模型轮次。双轮修改、恢复、中止、断连、进程终态和隔离仍需专用平台测试配置。
- 本轮观测验证：无业务请求/API/DB写入，通用请求和执行采集N/A；整体Change仍applicable，页面行为采集也尚未实现，3.3未完成。
- RC-002具体限额等待响应；RC-003仅入口设计完成；RC-004仅骨架证据完成。估算暂沿用13人天，未关闭排期风险。
- 下一轮先补齐平台专用认证与RC-002，再实测1.4；不以Mock绕过真实验证前置门禁。

| 2026-09-08 14:16:34 | opsx.apply | 完成前置与Skeleton，3/25；真实接入与限额待补齐。 |


## 工作流同步兼容性

发现simple YAML解析器忽略顶层无缩进openspec_changes列表，使状态保持proposed。将REQ trace列表改为等价的缩进格式后，opsx.apply正确派生in_progress并记录事件；未修改脚本或人工伪造applied。建议后续通过/spec-opt补充无缩进合法YAML列表兼容测试，本轮未自动创建Issue/Change。AI Usage自动发现无可归属记录，usage_mode unavailable、command_run_count 0、warning 1；不虚构用量。


## 本地部署验证

用户授权直接部署验证后，执行docker compose build web及docker compose up -d --no-deps web，更新现有18102本地Web服务。未重建后端或操作数据库、对象存储。镜像及验证摘要见evidence/local-deployment.json。

实际容器/chat返回200，未登录浏览器跳转/login；后端健康接口200且容器healthy。使用项目Playwright针对18102运行check-chat-skeleton.cjs，1440深浅、1024、390四张截图与样式证据存于evidence/deployed-ui/。合成前端会话仅用于布局，不作为后台权限认证证据。

实际/api/v1/chat/conversations返回404，符合当前后端尚未实现的事实。当前进程、根环境文件与现有后端容器未发现Codex平台配置项；只检查配置名和是否存在，未输出凭证。部署成功不代表Chat业务可用；任务仍3/25，RC-001真实双轮执行及worker隔离未完成。

复跑方式：在src/web运行node scripts/check-chat-skeleton.cjs http://127.0.0.1:18102 ../../openspec/archive/2026-09-13-add-chat-workbench-codex/evidence/deployed-ui。本轮仅改进验收脚本可指定地址/证据目录并覆盖未登录跳转，未新增API、DB、部署变量或客户端生成变更。


## 已登录执行端的受控验证

用户确认登录后，codex login status实测为Logged in using ChatGPT。使用现有本机登录在一次性合成仓库调用App Server，未复制个人凭证到MoonBox容器。首轮实际文件0→1并completed；停止并重建App Server进程，thread/resume恢复原线程后第二轮1→2并completed。证据见evidence/authenticated-protocol-probe.json，不保存线程ID、本机路径、认证值或原始输出。

首个立即中止请求返回-32600，尚不能确认竞争根因；聚焦复测等待运行建立后发送turn/interrupt，收到turn/completed status=interrupted。需要后续worker状态机覆盖启动与中止竞争，不能将第一次失败隐藏为全通过。

登录问题已排除，本地个人认证可用于受控协议验证；平台专用认证、容器资源/凭证隔离和MoonBox会话API仍未完成。任务1.4保持未勾选，已完成其中双轮修改、进程重建后的线程恢复与中止确认子项。此次不要求用户重复登录，不把本机登录等同于平台认证部署完成。


## 后端接入与隔离部署首批

用户明确要求继续后端及隔离部署，已实现app/chat模块、7张增量表、12条路由、恢复worker和Orval客户端。迁移有SQLite在线备份，后端和chat-recovery已部署。验证见evidence/backend/verification.json：SQLite 9例、MySQL 8.2.0 9例、既有健康/用户接口20例、TypeScript、Orval及容器隔离。

实际完成的是会话CRUD、轮次查询/事件读取、中止状态基础、worker抢占/fencing/unknown恢复；新发送因额度与执行隔离未闭环而拒绝，worker主循环不领取模型任务。本轮没有复制个人凭证到容器。无网络恢复容器的隔离证明仅适用于该进程，不能用来关闭真实模型执行RC-001。

任务2.1–2.7/3.1–3.3/5.1/5.4均推进但未完整完成：额度预留、对象关联权限快照、live executor、重试、代码基准及有历史的清理仍缺，不勾选整项。保持3/25，避免把模块存在当作全项验收。前端仍为骨架，未接API。

产品采集声明继续applicable；本轮Chat请求摘要已验证不含Prompt/认证头，服务端request_id独立生成、记录失败只写固定降级事件；通用usage_events、Task Trace/spans及请求日志保留任务尚待补齐。

MySQL初次测试因当前Python缺PyMySQL、项目环境缺pytest而未启动，改用uv临时测试依赖后9例通过；Orval原未安装/无配置，已补齐固定8.29.0和Chat标签配置，生成成功。生产MySQL8.4、全功能及真实执行隔离不在通过范围。


## 2026-09-08 会话管理、事件与预留增量

进度4/25：新增完成3.2；其他大项仍有缺口，不按文件数量标记完成。会话管理已从Skeleton接通鉴权API，包括空间选择、搜索、分页、新建、置顶、重命名、归档/恢复、空会话删除；共用Dialog支持忙碌禁用、错误重试保留草稿、capture外部关闭和焦点管理。需求中心增加显式入口，旧抽屉保持；携带主对象和关联编辑尚未完成。

执行详情读取真实持久化轮次、SSE事件及Diff，事件续读按游标去重；查看历史轮次不改变停止当前运行目标。消息分页使用纯文本展示，未宣称Markdown或文件级Diff完成。内部admission事务补齐用户/空间并发、月份Token及容量预留、同请求并发幂等、确认终态后幂等结算。API发送仍返回未就绪，恢复worker仍不领取模型任务；未知状态不释放预留。

验证：SQLite Chat13例及既有API20例通过；独立MySQL 8.2.0 Chat13例通过；Chat前端14例、需求中心59例、首页5例通过；TypeScript与Orval通过。合成浏览器API的9张截图覆盖1440深浅、1024×600、390×844，history/rename/picker样式见evidence/session-ui/computed.json；人工检查1440深色和390浅色截图无裁切。真实本地登录态确认授权空间可见、历史空列表正常、仓库未配置时禁用新建。两类证据明确区分，未保存真实空间名、认证头或用户数据。

product_data_collection_observability: applicable；affected_layers: Web鉴权fetch、API请求摘要、DB消息/额度预留。validation: 继续复用可信服务端request_id、不在URL放Token，鉴权与撤权测试通过；执行链路Task Trace与用量来源尚未接入真实worker，不能宣称全链路观测通过。部署仍为本地，未生产升级、未提交Git。

剩余：平台执行worker、仓库工作区隔离、主对象与快照授权、硬额度/容量中止、重试/unknown核实、完整删除/副本/备份清理、文件级Diff和完整视觉AC。具体生产限额未设默认值，不要求用户重复登录。


## 2026-09-08 App Server与可信执行增量

完成2.1和2.5，整体6/25；schema为spec-driven。新增workspace、app_server、execution模块和workspace_baselines表，10张表与增量索引已就绪。单轮执行器关联worker generation，保存真实回复、工具白名单元数据、用量与前后内容基准。原样重命名给出previous_path；内容变化重命名保守展示新增/删除；二进制、大内容和符号链接只给准确元数据及原因。

真实验证见evidence/backend/real-runner.json：一次性合成仓库与独立SQLite，两次通过入队/worker抢占/run_claim完成0→1→2修改，第二次重建App Server进程并恢复原线程；本轮1→2和累计0→2差异均断言通过。本机个人登录只用于该受控验证，不复制认证到容器，也不据此关闭平台隔离RC-001。协议参考官方文档 https://learn.chatgpt.com/docs/app-server 与本机0.153.4导出schema，运行时版本不自动升级。

证据化排查：首轮真实测试失败为executor_timeout，补充稳定RPC阶段错误码后确认executor_timeout_turn_interrupt。原实现同步等待中止应答期间不消费终态通知；改为发送中止请求、限频重发并持续消费原轮次通知，只有匹配turn/completed决定终态。补充“缺少中止ACK但收到终态”的合成stdio回归后通过，真实两轮复测也通过。没有把失败第一次改写为成功；失败时保留unknown与资源预留。

验证结果：SQLite/API/适配/工作区48通过，真实模型用例默认跳过；显式真实用例1通过，包含两轮。MySQL8.2.0 Chat16通过、真实用例跳过，存在一条既有httpx弃用警告。SQLite另验证删除索引后迁移补建。Orval及TypeScript通过。没有UI改动，本轮复用既有Skeleton与动作族截图，不声称新增平台执行UI验收完成。

Cross-cutting为执行/API/DB，沿用已读知识库；AC-XCUT与观测声明适用，非BUG来源根因Gate不阻断。Prototype/Reference Gate为warn：Skeleton done，1440及会话动作族已通过，完整关联/执行界面证据仍pending；Mock/API边界已声明。

product_data_collection_observability: applicable；affected_layers: execution、db、request_logs、web_request_wrapper。validation: 只持久化归属ID、用量、白名单工具阶段及受控输出；凭证形态文本过滤、错误稳定编码，原始命令/配置/协议错误不落盘。完整Task Trace/行为采集仍待3.3，不将内部usage事件替代平台账单事实。

部署：在线备份SQLite后增表/索引，更新backend及无网络恢复worker，刷新Nginx。模型执行没有在平台容器开放；现有后端镜像不是配置完毕的Codex运行时。平台认证方式已通过原生卡片询问，未收到配置前继续保持发送关闭。正式额度、关联权限快照、重试/unknown核实、删除副本/备份清理和完整UI仍未完成，不具备归档条件。


## 连续 apply 检查点：关联、快照与展示

承接用户最新选择：先完成开发与隔离验证，暂不配置正式限额和删除时限。RC-002 保持未关闭；平台专用认证仍待配置，个人本机登录不替代多用户平台认证。执行入口继续关闭，未执行 applied 完成同步。

已实现对象目录绑定、主对象/引用 API、immutable 每轮快照、撤权后的详情与列表计数过滤；目录描述符读取拒绝 symlink/hardlink/超限，正文总量48KB。新增 chat_relations/chat_object_access 两表。SQLite18项、独立MySQL8.2.0同18项通过（在后续重试增量前）；MySQL容器已移除。后端/app健康200、12张Chat表已部署，恢复worker read_only=true/network=none/restarts=0。

Web 已实现 RelationsBar/RelationsDialog、需求中心对象提示链接、安全Markdown子集、本轮/累计文件Diff、停止确认及本轮快照展示。关联动作族13张截图与computed style见 evidence/session-ui；1440深浅、1024、390无横向溢出和弹窗越界。浏览器使用明确合成API响应，只证明UI行为，不代表平台模型或真实业务目录已配置。77项Web测试通过；最后增加的快照展示仍需复跑。

正在验证：手动重试仅允许失败/停止轮次、保留原快照、重新授权；排队停止原子结算预留；仓库撤销阻止历史和worker续用。随后重跑客户端生成、测试和部署。剩余独立工作包括删除/副本清理状态、治理只读执行策略、观测链路及最终文档AC映射；不能把这些未完成事项归因于认证待配置而提前结束。

product_data_collection_observability: implemented_partial；affected_layers: backend/api/database/web-request；validation: 授权快照仅业务表存储，通用请求日志不记录正文/对象目录路径，错误稳定脱敏；执行追踪与清理审计尚待补齐。


## 连续 apply 检查点：配置依赖边界

身份：REQ-0025-chat-workbench → add-chat-workbench-codex → sprint-004。任务已验证12/25；新增完成3.3观测、4.1入口、4.2动作族、4.4主题与安全Markdown、5.2前端校验、5.3视觉验收。其他宽任务即使部分实现已有证据，也保留未完成。

完成的独立实现：对象与仓库撤权、不可变引用快照、单主对象/多引用、原快照显式重试、停止排队的预留结算、未知轮次准确读取/确认、主存储删除及当前代码检查、独立副本清理状态、治理只读策略、稳定行为与Task Trace、观测保留清理和故障降级。关闭停止确认时冻结原活动轮次，避免自然完成后误停新轮次；输出达到预留边界会持久化截断提示并请求中止。

验证：后端41通过、2个显式外部探针默认跳过；独立真实Codex双轮1通过；双容器隔离1通过。前端79个不同用例通过，包含原需求中心59项和新停止竞争用例；TypeScript/Orval与构建通过。最终MySQL和镜像指纹以evidence/backend/relations-lifecycle-verification.json为准。视觉23张：深浅1440、低视口1024、窄屏390，历史/重命名/删除/关联/执行与停止确认均有证据；Diff选择器最终computed样式与轮次选择器一致。全部使用合成浏览器API，不当作真实平台业务执行证据。

失败及修复证据：排队停止自动结算后旧测试仍期待二次结算成功，已调整为幂等不重复释放；Diff视觉定位因文件名同时出现在summary和patch造成strict locator歧义，改为summary；视觉发现Diff选择器未复用DS控件样式，已补齐并重新采样。均在当前apply修复，不转opsx-modify。未改无关技能/治理Change，未提交或推送。

硬依赖与未完成事项：
- 平台专用认证方式/配置路径和正式仓库绑定尚未提供。本机个人登录仅获准用于合成验证；不能把它复制进多用户平台。持续执行worker的凭证代理、部署接入及实际副本删除适配依赖该部署边界，涉及1.4、2.2、2.4、2.6、3.1与5.4。
- 用户已明确选择暂不配置正式限额及删除时限；不是默认接受建议值。1.5、2.7、4.3及对应最终容量/副本验收不能关闭。当前API发送/重试503、历史删除配置门禁仍关闭；内部原运行终态核实不会假定未知用量为0。
- 正式平台端到端与副本/备份实际清理证据缺失，2.3全量部署边界、5.1、5.5和5.6仍待闭合。独立墓碑恢复与备份清理必须随已配置备份服务验证，不能仅凭pending记录声称实现彻底删除。

可续接动作：获得平台专用认证配置与仓库绑定后，从2.2的运行环境接入继续，保留当前证据和测试；正式额度/时限仍按用户决定等待，不反复询问或静默配置。REQ六件套与prototype context已完成本轮一致性扫尾，保留原附件HTML作为参考，不篡改为实现产物。估算维持13人天，未扩展Sprint范围。

Workflow Sync仅运行dry-run，errors=0、7个子文档检查无阻塞，acceptance仍pending；未执行applied同步，AI Usage完成钩子随之跳过。按连续执行契约记录该真实配置依赖边界，不宣称apply完成或可归档。执行链路复盘：范围与事实源一致，问题均有修复证据；暂无需新增治理Issue的建议，未自动创建Issue/Change。

最终部署复核：后端与恢复worker镜像52ccb991e158，Web镜像9800cf614dcf；三容器running/restarts=0，health200，16张受管表全部存在。execution_limits=false、retention=false，未写入正式值。SQLite41/MySQL28/Web79、真实双轮探针和容器探针，以及23张最终截图/computed证据均记录在evidence目录。恢复worker仍是无网络只读恢复进程，不把它描述成已上线的模型执行worker。

## 共享侧边栏验收与部署（2026-09-08）

本批共享侧边栏已完成并部署：WorkbenchSidebar 统一品牌、版本、八项导航、折叠、用户/空间动作；useWorkbenchTheme 统一持久化与跨页主题。个人私有说明仅保留在会话区。需求中心原有账号和空间操作由共享模块承接，Chat 的空间选择限定于其授权目录，设置空间和进入后台分别遵循空间与账号权限。

验证：9个测试文件87项通过；实际18102构建页面52张截图、12组双页computed style完全一致（1440×900/1024×600/390×844，深浅×展开/折叠），16份账号/空间弹窗样式样本；跨页导航、主题持久化、只读空间、取消与Esc焦点返回通过，pageerror=0。另重新生成23张会话/关联/执行/停止截图，避免沿用旧CSS证据。所有浏览器业务响应均为合成API，不等同真实平台执行通过。证据：openspec/archive/2026-09-13-add-chat-workbench-codex/evidence/sidebar-ui/{computed.json,verification.json,*.png} 与 evidence/session-ui。

源码证据确认根因：原Chat独立导航缺少分组、版本、折叠和账号菜单，通用按钮选择器覆盖rc样式。本轮浏览器又验证并修复390px空间浮层越界、空间设置遮罩留白/分列越界，以及CSS收敛造成的执行栏select颜色回归。最终导航展开224px/折叠72px，导航行高40px、padding=0 12px、gap=11px、font-size=13px，分组标题padding=16px 12px 7px；两页同状态值一致。

门禁：Cross-cutting tags=无admin-*（前台复用账号动作），AC-XCUT/knowledge_base_refs=pass，prototype与modal CSS经验已承接，PROCEED；本批Prototype Gate=pass，既有Skeleton承接，1440px/关键动作/computed=pass，Mock/API边界已声明；UI Reference Replication Gate=pass（共享壳、导航、账号动作、响应式）。REQ六件套及prototype context完成本批一致性回填，整体归档一致性仍待其他任务完成。

影响面：Web页面、共享组件、CSS、前端测试及验收脚本；复用已有鉴权API，不新增接口、DB迁移、客户端生成、部署变量或权限政策。product_data_collection_observability：本批not_applicable、affected_layers=[]，API/DB/请求日志/usage_events/Task Trace及请求封装字段未改变，详情见design补充合同。仅重建Web，后端与recovery镜像保持原值；健康接口ok、Chat页面200，镜像指纹见verification.json。

### 本批结束检查点

REQ-0025-chat-workbench → add-chat-workbench-codex → sprint-004。新增4.5通过，当前13/26项完成。用户本轮要求的侧边栏统一、回归和隔离部署已处理；整个Change仍in_progress，未执行applied同步或归档。其余任务继续受此前已记录的平台专用认证/正式仓库绑定、真实运行/副本清理证据依赖限制；正式额度和删除时限按用户明确决定暂缓，不重复请求配置或静默开启。恢复入口仍为 /opsx-apply REQ-0025-chat-workbench，获得平台接入输入后从2.2续接。

执行链路复盘：Sprint Scope有效，缺陷有源码和浏览器断言证据，已在当前apply内修复。新增可复跑双页共享组件验收脚本作为预防；无需另建治理Issue/Change。Workflow Sync仅dry-run，保持整体未完成事实。

收尾校验：OpenSpec strict、中文优先、目录结构、Sprint Scope、git diff --check均通过。Workflow Sync dry-run errors=0、7个子文档无warning/blocker，acceptance=pending；整体applied完成同步未执行，因此AI Usage完成钩子跳过。当前会话误在根目录运行pnpm生成的空本地索引已清理，未保留新的根目录或构建缓存。


## 本地凭证与受控仓库真实执行验证（2026-09-08）

用户授权采用本地登录与可丢弃测试仓库，正式限额及删除时限继续暂缓。本批新增显式开启的 local_probe 认证工厂；仅复制登录文件到0700临时目录，文件0600，不加载个人配置、插件或历史。测试结束删除临时认证与执行历史；原登录文件不由测试写入。令牌刷新和异常宕机后的残留清理未在本次验证覆盖。

真实 codex-cli 0.153.4 通过后端 claim/run_claim 完成 counter.txt 的0→1→2修改、进程重建后同线程恢复、本轮及累计Diff和真实中止终态。原生命名权限配置隔离模型工具：凭证、相邻工作区与测试DB读取拒绝，仓库允许写入、.git禁止写入、工具外连拒绝；只读配置拒绝工作区写入。安装版本要求 initialize.experimentalApi，首次RPC拒绝经此修正后通过；增加读写降级回归。

真实测试1项通过（27.12秒）；后端回归41项通过、2项显式真实执行测试默认跳过。两轮完成用量分别22500和1455，均已结算；立即中止轮次未返回用量，标记usage_unavailable并保留reserved，不能按零消耗释放，实际用量对账仍未闭环。

证据：openspec/archive/2026-09-13-add-chat-workbench-codex/evidence/backend/local-credential-execution.json。使用合成API身份和独立SQLite，内部enqueue入队；本机原生执行不是已部署Docker worker或浏览器发送端到端证据。服务发送/重试仍503，未改真实环境、正式限额、删除期限或已有部署镜像。RC-001仅补齐本地正常路径及隔离子证据，进程异常/全链路部署等门禁不据此关闭。

影响：后端执行适配器、显式测试认证工厂、测试和部署说明。API契约、DB结构、UI、客户端生成均无变化。product_data_collection_observability=applicable；affected_layers=[api,db,task_traces]，沿用现有事件及额度持久化；validation=真实两轮、恢复、中止及保留未知用量预留通过，证据只保存状态和计量数值，不保存凭证或完整对话。

执行链路复盘：REQ-0025-chat-workbench → add-chat-workbench-codex → sprint-004，保持in_progress、13/26项，未标记整体applied或归档。此前“缺少本地执行认证授权”的依赖已解除；正式共享平台认证与完整部署验收仍独立待完成。建议沿用本批显式开启、默认跳过的真实执行回归，不另建治理Issue。


## 五步隔离执行闭环（2026-09-08）

用户本批明确授权执行到测试清理。已完成：有界接收终态后用量、单调去重及可信记录幂等补结算；受配置与有效期保护的独立常驻worker；真实登录后的测试账号/空间/仓库入队门禁；回环地址18121上的构建Web与真实API验收；最终停止服务并删除测试数据。正常部署仍默认关闭发送/重试，正式认证、运营限额和删除时限继续暂缓。

实际四轮：完成0→1、worker重启后同线程完成1→2、网页停止、运行中SIGTERM重启worker后停止。恰好四轮，无自动重放；两轮修改与第三轮停止已按33873/2489/28778 tokens结算，第四轮停止没有权威用量，保持usage_unavailable与reserved，未按零消耗释放。整个临时测试DB随后按用户授权删除，不能把删除测试DB表述为该轮已对账。缺失用量的处理路径是保留预留、读取待对账清单，只有可信执行端结算凭据可用时才补结算；无自动推算或手填零值接口。

真实浏览器通过：创建会话、鉴权发送、刷新恢复、停止确认、历史读取、本轮/累计Diff、其他账号访问404及执行白名单拒绝；没有业务API Mock。初次刷新丢失选中会话与终态后输入区旧活动状态，分别通过URL保存不透明会话标识后重新鉴权读取、活动会话轮询修复。第一次停止观察90秒超时，退出浏览器没有停止后台运行；重新连接同一轮次后停止确认通过，未新建重复任务。截图及最终样式采样覆盖1440×900；本批没有布局/CSS改动，深浅/窄屏基线承接此前共享侧边栏验收。

实际原生权限探针通过：凭证、相邻种子仓库和测试DB读取拒绝，.git写入拒绝，模型工具网络拒绝，只读配置禁止写入。API仅回环监听且仍使用正常登录验证；私有配置需isolated-test、独立临时SQLite、指定身份/空间/仓库、有效期与新鲜worker心跳。配置不包含可由浏览器传入的路径或执行命令。异常worker租约与fencing由单元测试覆盖；本轮实际重启使用SIGTERM，不宣称已做SIGKILL全链路验收。

证据：openspec/archive/2026-09-13-add-chat-workbench-codex/evidence/live-web-execution/verification.json、computed.json及7张真实页面截图。四条Task Trace均关联真实请求ID，事件source_id无重复，行为与节点记录存在，页面pageerror=0。临时认证、仓库、SQLite和线程历史目录均已删除，服务停止、18121端口释放已核验；运行端原登录缓存未由测试写入。保留的证据没有凭证、原始执行会话文件或真实客户数据。

影响面：后端执行/结算/隔离配置及worker、网页会话恢复、测试启动器与验收脚本。API字段和OpenAPI schema比较不变，不需重新生成Orval；API能力和发送行为、DB持久化语义、安全/部署边界均已同步文档，无新表字段或迁移。product_data_collection_observability：status=applicable；affected_layers=[usage_events,request_logs,task_traces,task_trace_spans]；validation=真实请求与Task Trace关联、可信用量去重/恢复、所有者拒绝及脱敏摘要通过。UI Reference Replication Gate承接既有合同，本批真实交互及computed样式通过。

执行链路复盘：REQ-0025-chat-workbench → add-chat-workbench-codex → sprint-004。RC-001受控接入Spike通过，对应任务1.4完成，整体14/26；本次用户指定的五步已处理，整个Change仍in_progress、acceptance=pending，不执行整体applied或归档。正式共享平台认证、生产限额/删除期限和完整部署矩阵仍独立待完成。建议保留真实网页回归与故障场景的显式测试入口，无额外治理Issue/Change自动创建。

本批最终验证：后端45 passed、2个显式真实探针默认skipped；前端7文件28 passed；构建通过。真实四轮与原生隔离证据独立记录，不以默认跳过替代。OpenSpec strict、中文、目录、Sprint scope、观测门禁、上下文预算、git diff --check通过；Workflow Sync仅dry-run，errors/warnings/blockers均0，7个子文档检查通过。整体Change未完成，不执行applied同步及其完成AI Usage钩子。


## 异常恢复、清理与部署补验（2026-09-09）

本批完成独占进程组守护：worker被SIGKILL或执行器崩溃时收回同组工具子进程，业务状态仍以可信终态为准。真实进程故障与协议适配10项通过；不能据此声称覆盖主动创建新session逃逸或整机断电后的凭证残留清理。

清理任务新增可信执行端/备份适配回调、失败重试和已清理状态幂等跳过；删除后的状态查询仍校验所有者及当前空间权限。真实codex-cli 0.153.4线程执行后通过thread/delete删除历史文件，代码与认证文件保留，测试退出删除临时认证。合成备份文件验证重试和代码保留，但实际备份清单、恢复后删除重放与删除成功后DB提交失败的对账仍未闭环；不能将到期或回调接口存在认定为副本已清理。

独立MySQL 8.2矩阵32 passed、1 skipped；后端回归46 passed、1 skipped，随后新增清理权限测试与重试测试2 passed。条件跳过不作为真实执行通过证据。新镜像隔离部署验证只读根文件系统、非root、API健康、重启持久化、恢复worker无网络、重复恢复保持unknown及活动锁、不可重复领取。临时容器和数据卷已清理，未替换现有服务镜像。Docker部署探针不执行真实模型，真实模型证据来自受控原生运行。

证据：evidence/recovery-cleanup/verification.json、deployment.json、thread-delete.json、container-isolation.json。源码入口：src/backend/tests/chat_deployment_probe.py、chat_mysql_matrix.py、chat_thread_delete_probe.py、test_chat_process_guard.py、test_chat_cleanup_copies.py。

product_data_collection_observability：status=applicable；affected_layers=[request_logs,task_traces,task_trace_spans]；沿用可信轮次与请求标识，未增加正文采集或客户端字段；validation=故障恢复状态不伪造终态、原回归与隔离部署通过。DB无新表字段，API无契约变化，不需Orval重生；部署、安全、DB语义及验收说明同步。

执行链路复盘：REQ-0025-chat-workbench → add-chat-workbench-codex → sprint-004，任务2.6与5.1补证完成，累计16/26。整体仍in_progress、acceptance=pending，未执行applied同步或归档。平台共享认证、正式限额和删除时限、实际备份适配与模型容器部署仍未完成；用户已暂缓正式配置，不重复索取。建议后续保留显式故障/部署探针作为回归入口，本批未自动创建Issue/Change。

收尾校验：OpenSpec strict、中文优先、目录、Sprint scope、观测门禁、上下文预算、Python编译与git diff --check通过。Workflow Sync仅dry-run，errors/warnings/blockers=0，7个子文档检查通过，acceptance=pending；未执行applied状态同步及其完成AI Usage钩子。本批Docker测试容器与数据卷查询为空，临时MySQL依赖副本已删除。续接检查点：任务2.7/5.4需要实际备份库存与恢复链路、平台模型容器运行方案；任务1.5仍遵循用户暂缓正式配置决定。不得把合成备份测试或原生模型验证替代上述缺口。


## 推荐组合落地验收（2026-09-09）

用户选择当前阶段采用本地一致性备份＋每会话独立执行容器，正式方向为对象存储备份＋会话容器。完成任务6.1/6.2，当前18/28项；原10项未完成仍独立保留，不据本批测试提升整体applied或归档。

备份：新增SQLite在线备份、独立删除日志及副本摘要清单，删除意图先于主存储事务持久化。包括空会话在内，恢复前重放删除并移除消息/引用/事件/Diff；代码与审计独立保留。缺少日志、损坏摘要、错误数据库归属或输出已存在均拒绝操作。旧排队/活动任务恢复后保持unknown和互斥；额度账本须可信对账后才能启用。旧备份物理删除与恢复过滤分别验证，清理worker只有库存检查通过才将backup状态置purged。备份4项通过，最终删除相关组34 passed/1 skipped；未连接生产MySQL/S3备份。

执行：固定官方Codex 0.153.4 Linux包，SHA-512验证下载；每会话独立容器/work/runtime、非root、能力清空、禁止提权、只读根、.git只读和资源限制。默认Docker seccomp阻止bubblewrap命名空间，依据内核支持与实际错误补充嵌套命名空间所需系统调用；其余默认拒绝规则保留，不使用privileged、外层CAP_SYS_ADMIN或unconfined。专用策略增加内核攻击面，属于明确部署依赖，不等同虚拟机安全强度。合成凭证预检通过后才复制真实授权认证；两个独立会话的严格只读和写入权限预检通过，既有文件保持。

真实容器完成counter.txt的0→1→2、容器销毁后同线程恢复、运行中停止确认。首次立即停止探针未确认interrupted，改为等待真实工具启动后中止，终态通过；未修改产品终态判定。后端claim→容器→Diff持久化→结算通过，可信用量21621 tokens已结算。单独原生证据不再是本能力唯一依据，但本批没有重新执行完整网页双轮；网页交互证据承接此前原生worker验证，新增container启动器生命周期通过。

证据：evidence/recommended-deployment/backup-verification.json、container-execution.json、container-worker.json、sandbox-profile.json、harness-lifecycle.json。完整后端回归50 passed/3 skipped（新增空会话用例之前）；最终备份/清理/接口聚焦34 passed/1 skipped；真实claim1 passed、两个会话合成预检1 passed。显式跳过不替代真实证据。临时凭证/容器正常退出清理，不宣称整机崩溃清理、登录刷新和生产平台凭证轮换已经完成。

影响：app/chat备份、清理、容器适配、隔离worker；Dockerfile及专用构建白名单；测试和部署说明。API字段及业务DB表结构不变，无Orval重生；独立备份库新建identity/deletions/backups三张运行时表，不写入业务迁移。UI未改，原型门禁承接既有证据。product_data_collection_observability：status=applicable；affected_layers=[db,request_logs,task_traces,task_trace_spans]；validation=沿用真实请求和轮次关联、Diff/用量持久化、独立删除日志和脱敏备份结果；离线备份命令不伪造用户行为或业务请求，未新增正文日志。

执行链路复盘：REQ-0025-chat-workbench → add-chat-workbench-codex → sprint-004有效；备份与容器验证范围已处理，正式共享认证、S3/MySQL恢复、生产配额/期限及最终上线验收仍待后续。正式配置遵循用户暂缓决定，本批不修改真实.env或既有服务，不创建新Issue/Change。建议持续保留合成预检在真实凭证复制之前、恢复预检在在线切换之前；本批已落实于代码，无额外治理变更。

最终收尾：后端51 passed/3 skipped，独立MySQL 8.2矩阵33 passed/1 skipped；最终镜像两个合成会话预检1 passed，SQLite备份4项通过。实际执行镜像与最终镜像Codex二进制摘要相同，差异为后端打包与上下文/许可证收尾，最终预检独立记录。测试会话容器查询为0，临时MySQL容器与驱动副本由启动器清理。OpenSpec strict、中文、目录、Sprint scope、观测门禁、上下文预算和git diff --check通过；Workflow Sync只dry-run，errors/warnings/blockers=0，7子文档一致，acceptance=pending，未执行applied同步及其完成AI Usage钩子。新增6.1/6.2是原2.7/5.4的受控验证拆解，没有新增FR或调整正式13人天估算。


## 日常部署脚本闭环（2026-09-09）

完成任务6.3，当前19/29项。根up/down共用模式、env和项目目录解析，修复自定义ENV_FILE未同步运行时env_file的问题；启动拒绝数据库模式冲突，down不因数据库配置冲突阻止清理，不删除常规卷。新增显式--chat-test与只读--check，常规部署仍默认关闭平台发送。

--chat-test构建常规镜像与固定执行器，常规服务健康后通过私有Unix控制通道启动独立测试API/worker，导出本次Web镜像静态资源，初始化独立SQLite备份及删除日志。默认18121/一小时有效期，使用独立测试身份/仓库和授权本地凭证副本。幂等启停，拒绝占用端口与失联控制端，不依据持久化PID终止未知进程。该控制入口支持受控测试，不构成生产常驻平台交付。

实测完整脚本构建和启动通过；常规backend/Web/MinIO健康，最终后端及Web HTTP 200。真实登录、执行门禁、空会话备份、删除恢复不复活、worker确认旧备份清理及种子代码保留通过。未发送新的模型轮次，真实容器双轮/停止/用量证据沿用上一批。测试服务与数据已清理、18121端口释放，常规服务保留运行。脚本回归11项、控制通道5项、备份/隔离5项通过，bash语法通过；证据位于evidence/deployment-scripts/。

影响：部署脚本、Compose env_file选择、宿主测试控制器、测试启动器及后端构建忽略清单；API schema、业务表、UI组件均无新增变更，无客户端重新生成。文档同步README、部署/架构、env示例、REQ子文档和Sprint验收。

product_data_collection_observability：status=applicable；affected_layers=[request_logs,task_traces,task_trace_spans]；validation=实际API登录/删除沿用请求日志，未发轮次故未新增Task Trace；控制通道不伪造业务行为、用量或执行记录。证据只有脱敏状态和计数，无凭证/连接串/正文。

执行链路复盘：REQ-0025-chat-workbench → add-chat-workbench-codex → sprint-004，整体in_progress、acceptance=pending，未执行整体applied与归档。正式认证/限额/期限、MySQL/S3恢复及上线验收继续保留；6.3是既有5.4部署验证拆解，不新增FR或调整13人天正式估算。建议后续沿用显式测试入口和同一env文件配对启停，无额外Issue/Change自动创建。

收尾校验：OpenSpec strict、中文优先、目录、Sprint scope、产品数据观测门禁、env ignore、上下文预算与git diff --check通过。Workflow Sync仅dry-run，errors/warnings/blockers均0、7子文档检查通过，acceptance=pending；整个Change未完成，未执行applied同步及完成AI Usage钩子。Chat测试标签容器为0。


## 终态并发释放返修（2026-09-09）

用户实际续执行完成但usage_unavailable，空间/用户active_runs各为1，阻止下一次发送；证据为evidence/user-browser-continuation/。根因是并发释放仅在Token结算路径发生，confirmed；不据此认定执行端用量缺失原因。

修复预留表新增concurrency_released（INTEGER NOT NULL DEFAULT 0），重复迁移兼容SQLite/MySQL，历史settled标为已释放。可信终态与并发释放同事务，unknown保持占槽；迟到Token结算不重复递减。worker对账循环补偿旧终态reserved的并发占用，但保持Token和容量预留、不填零用量。任务2.4的此缺陷修复完成，不扩大其余任务完成范围，整体保持19/29。

实际先对原隔离DB创建本地备份、迁移并重启worker，空间/用户并发1→0，原reserved Token保持。原测试环境随后到一小时有效期自动清理，停止确认未获证据，不记通过。重建新隔离环境后，真实网页发送sleep 45，收到当前轮次工具开始事件再确认停止；最终stopped，用量10642已结算；随后新消息completed，用量348已结算。刷新保留终态与回复，active_runs=0，浏览器pageerror=0。新环境仍运行供用户查看，旧临时登录资料失效。

验证：SQLite聚焦38 passed/1 skipped；Chat回归59 passed/5 skipped，两个进程守护用例因沙箱禁止ps失败，获准复测2 passed；MySQL 8.2隔离矩阵36 passed/1 skipped，覆盖旧结构重复迁移和并发补偿竞争。显式真实测试跳过不作为通过证据，网页真实停止独立记录于evidence/concurrency-release/。常规本地服务已通过根脚本重建部署，不改正式额度和认证配置。

影响app/chat/schema、admission、worker、accounting、execution及聚焦测试；新增业务DB内部字段，API公开字段/UI组件不变，无Orval重生。product_data_collection_observability：status=applicable；affected_layers=[db,task_traces,task_trace_spans]；validation=保留可信终态与用量、幂等释放、迁移补偿不伪造用户行为，真实停止与后续轮次正常持久化。UI承接既有合同，无布局变更。

执行链路复盘：REQ-0025-chat-workbench → add-chat-workbench-codex → sprint-004保持in_progress/acceptance=pending。本缺陷在既有Change内修复，未自动新建Issue/Change。建议后续账本回归始终分开验证执行终态、资源释放和可信计量；本批已增加对应回归。正式共享认证、运营配置和最终上线验收仍待完成，未执行整体applied或归档。

收尾：常规API/Web及新Chat测试API均HTTP 200，常规数据库增量字段核验通过。OpenSpec strict、中文、目录、Sprint scope、观测门禁、git diff --check通过；Workflow Sync仅dry-run，7子文档一致、errors/warnings/blockers均0、acceptance=pending。未执行整体applied同步或完成AI Usage钩子。


## 用量范围修复与剩余任务收口（2026-09-09）

通过三轮真实协议探针确认App Server每次新进程恢复线程后total为进程累计：10598、10801、11005，各轮单模型调用时total等于last。旧实现扣减上一进程token_total导致少计或usage_unavailable，根因confirmed。run_claim现在只采纳匹配线程/轮次的非负total并单调去重，末尾迟到通知仍受同样规则；不使用last替代多工具调用累计。receipt新增usage_scope=app_server_process_v1，旧scope缺失不能自动结算。workspace token_total保留为兼容记录但不参与计费基线，迟到对账也不覆盖新轮次的记录。

真实claim两轮结算10572/10775，逐轮等于原始进程数值，同一线程恢复通过；测试工作区/凭证已清理。双标签页同时发送HTTP 200/409，只产生一轮，Token10582按新scope结算，worker重启/刷新后无重放。此前多轮旧算法结算数值不再用作准确计量证据；历史测试DB已经到期的记录不能推算回填，仍存在的已结算旧记录不自动改写。证据：evidence/usage-scope/。

权限新增运行中撤权直接回归：关闭执行器、unknown保留锁与预留、历史403且不落盘撤权后输出。SQLite42 passed/1 skipped，MySQL8.2独立矩阵39 passed/1 skipped，Web7文件22 passed。Chat OpenAPI paths/schema未变，不需Orval生成；业务无新字段迁移。已有并发释放迁移及正常脚本部署承接上批；本批正常服务与受控worker已更新。

任务2.3/2.4/3.1/4.3按现有实现、增量回归和真实证据完成；任务5.5的34功能/8横切/8原型映射全部回填，未通过项保持不通过。整体24/29，未完成1.5、2.2、2.7、5.4、5.6：正式额度/期限及平台认证尚未确定；正式执行端配置与备份清理范围没有可验证的生产事实；整体最终验证依赖上述项。用户已明确暂缓正式运营配置，不重复索取。无其他不依赖这些条件的当前范围任务遗留。

product_data_collection_observability：status=applicable；affected_layers=[db,task_traces,task_trace_spans]；validation=进程范围计量、真实执行端数值与可信receipt一致，重复/乱序/迟到/旧scope拒绝回归，不新增正文或凭证日志。UI Reference Replication Gate承接既有共享侧边栏和执行区证据，无本批UI改动，Cross-cutting PROCEED。

执行链路复盘：REQ-0025-chat-workbench → add-chat-workbench-codex → sprint-004；整体in_progress、acceptance=pending。当前受控开发与验证范围完成，正式范围受已暂缓决定及平台接入事实缺失约束；不执行整体applied/归档。建议固定运行时升级必须回归计量范围，本批已增加真实容器回归，未自动创建额外Issue/Change。

最终收尾：后端64 passed/6个显式探针默认skipped，真实协议3轮及真实容器claim2轮独立通过；MySQL39 passed/1 skipped，Web22 passed。常规API/Web和隔离Chat均HTTP 200。OpenSpec strict、中文、目录、Sprint scope、观测门禁、上下文预算及git diff --check通过；Workflow Sync只dry-run，7子文档一致、errors/warnings/blockers均0、acceptance=pending。13人天估算保持原范围，无新增功能范围；剩余正式配置依赖未解除，未执行整体applied同步和完成AI Usage钩子。


## 单机常驻执行续接点（2026-09-09）

REQ-0025-chat-workbench → add-chat-workbench-codex → sprint-004；用户已确认单机Compose、SQLite、独立本地备份、本机Codex认证单文件和unlimited运营策略。任务1.5/2.2/2.7完成，整体27/29。剩余5.4实际目标仓库/空间部署及5.6最终同步；已向用户询问仓库路径/空间名称，等待映射，其他正式运营决策已解除阻塞。未修改真实env或既有运行服务，未整体applied/归档。

实现：显式unlimited语义、真实记账、常驻Worker/心跳与配置摘要门禁、--chat-platform Compose入口、独立初始Git基线；只保留API/容器/协议技术安全边界，不以大整数模拟无配额。控制器Docker权限不下放给执行容器。执行凭证使用单文件挂载和每轮私有副本更新；宿主文件inode改变需重建worker。备份每次启动及24小时周期创建，无自动过期；主动删除先记录删除日志，未物理expire的旧备份保持pending/retry。

根因与修复：新工作区仅git init、导入文件未跟踪会误阻止删除，补充初始提交和干净状态断言；首次真实Worker失败为main:49 FileNotFoundError，镜像内docker-cli缺失，替换包并加脱敏位置日志后通过。没有放宽隔离或删除断言。

验证：真实容器Worker双轮10569/10769 Tokens已结算，重启无重放；主动删除、离线恢复删除重放、执行线程清除与显式备份expire后状态闭环通过，代码保留；凭证副本/测试控制容器清理。MySQL43 passed/1 skipped、Web22 passed、部署脚本4 passed、真实Compose只读合并通过。证据：evidence/platform-local/verification.json。

product_data_collection_observability：status=applicable；affected_layers=[db,request_logs,task_traces,task_trace_spans]；reason=实际计量与常驻执行门禁、后台备份；validation=保持真实请求/轮次链路，后台不伪造用户行为，错误只记录类型和函数行号、不含路径和凭证。公开API字段及业务schema未变，无客户端重生；UI仅就绪提示文案更新，原型/共享侧边栏证据承接，Cross-cutting PROCEED，REQ子文档同步。

执行链路复盘：当前in_progress、acceptance=pending；暂停依赖仅为尚未指定的正式仓库与空间。建议保留镜像内命令存在性及新工作区干净基线回归，本批已落实；未自动创建Issue/Change。下一可执行动作是收到仓库映射后补齐私有env、执行--chat-platform预检与实际目标部署验收；无凭证内容需要用户发送。

最终验证：后端71 passed/7显式探针默认skipped，真实Worker另行1 passed；MySQL43 passed/1 skipped，Web22 passed，脚本4 passed。OpenAPI paths/schema未变，OpenSpec strict、中文、目录、Sprint scope、观测、env ignore、上下文预算与diff检查通过；Workflow Sync仅dry-run，7子文档、0errors/warnings/blockers、acceptance=pending。本次探针控制器及执行容器剩余0。正式映射缺失，未执行applied及完成AI Usage钩子，13人天原估算和既有Sprint范围保持。


### 实际单机部署检查点（2026-09-09）

用户指定当前MoonBox项目仓库及MoonBox空间。读取实际后端确认唯一空间编码moonbox对应显示名“AI原生软件工厂”，未新建或重命名空间。私有env保存仓库/空间映射、local-codex和unlimited策略，原env有私有备份；路径、ID与凭证不复制到治理证据。根up/down可根据已保存执行模式自动加载常驻Compose覆盖文件，脚本4项回归通过。

实际根up部署完成，API、Web、MinIO、Chat Worker均healthy；控制器非root，单认证文件只读挂载，API无认证文件及Docker socket，后台就绪摘要/空间权限/未配置仓库拒绝和独立备份日志核验通过。所选仓库已提交树1573文件、38876348字节成功初始化干净独立基线，源目录未改动，未提交代码不自动导入。证据：openspec/archive/2026-09-13-add-chat-workbench-codex/evidence/target-deployment/。

任务5.4完成，整体28/29；5.6最终当前账号端到端验收和完成同步仍待登录。现有浏览器会话失效，使用已配置初始密码的一次登录返回401，不再重试、不重置账号、不伪造会话；已打开正常登录页并请求用户自行登录。独立环境的真实双轮/重启/删除恢复证据承接上一批，不冒充本次用户账号下的实际发送。常驻服务保留运行，不清理业务数据；下一动作是在当前有效登录下验证发送与刷新恢复，再执行最终完成同步。未执行applied/归档及完成AI Usage钩子。

product_data_collection_observability：status=applicable；affected_layers=[request_logs,task_traces,task_trace_spans,db]；reason=实际部署接入和身份验收；validation=仅保存部署布尔结果和计数，初始密码及日志未外泄；后台只读检查不伪造用户行为，尚无本批真实用户轮次。不涉及公开API字段、业务schema或客户端重生；UI布局不变，既有原型证据继续适用。

执行链路复盘：REQ-0025-chat-workbench → add-chat-workbench-codex → sprint-004，in_progress/acceptance=pending。仓库和空间依赖已解除，剩余是当前有效账号登录；建议以空间唯一编码辅助解析显示名称，本批已交叉核对，未自动创建Issue/Change。

## 当前交付事实（最终验收回填）

用户确认的单机Compose、SQLite、本地独立备份、本机Codex认证单文件和显式unlimited策略已实际部署到所选项目仓库及moonbox编码空间。用户重新登录后通过真实页面完成两轮发送，分别结算14969/15189 Tokens；刷新保留两轮回复，轮次数量2、互斥及并发占用归零、两轮Diff均为空。证据：openspec/archive/2026-09-13-add-chat-workbench-codex/evidence/target-deployment/account-verification.json及logged-in-acceptance.png。实际源仓库未被模型修改，工作区从已提交树初始化，当前目录未提交改动不会自动导入。

最终需求边界：无用户/空间运营配额；同会话互斥、单机顺序调度、有限结果处理缓冲和容器/协议安全边界保留。聊天和备份不自动过期；主动删除主数据、记录独立删除日志，旧备份物理expire前保持待清理，恢复前重放删除。API不挂载凭证或Docker socket，受信任控制器使用单文件认证，执行容器保持隔离。本期不交付MySQL/S3正式灾备、异机灾备或独立平台账号；SQLite与MySQL的业务兼容测试保留。

34项功能、8项横切、8项原型AC均有实现及验证映射；RC-001至004已关闭。Ops样式迁移、共享侧边栏、深浅主题、1440/1024/390视口及computed style承接evidence/sidebar-ui和live-web-execution，视觉Mock范围明确；本批当前账号Web/API/Worker/模型验证不使用Mock。PRD、流程、故事、验收、review、trace及prototype context已按最终认证/配额/保留策略核对一致。前文的未实现、暂缓、待映射、待登录及阶段进度均为历史检查点，不代表当前待办。归档与发布仍为后续独立动作。


最终检查点：29/29实现与验证条件已满足；Workflow Sync已完成，关联REQ中的Change状态为applied，归档验收状态依工作流保留pending。13人天估算与已批准业务范围保持，新增诊断和基线修复属于原验收范围；不创建额外Issue/Change，不自动归档。

AI Usage Hook：status=warning，usage_mode=unavailable，command_run_count=0；自动发现未生成可归属计量，Sprint用量快照跳过。不影响真实Chat执行计量与功能验收；需要开发用量时可提供明确的本地session输入重跑。

## 2026-09-10 执行展示返修

连续相邻、同消息和同执行轮次的文字事件归并显示；工具/状态/消息身份变化及序号缺口保留边界。原始事件默认折叠，保留最近1000条窗口说明。所选轮次当前状态单独展示，时间线状态明确标为历史。安全Markdown新增表格（表头、对齐、转义管道、行内代码、空单元格），窄屏在表格内滚动，保持HTML/图片/危险链接不可执行。旧事件缺少消息身份时仅按连续区段归并，不伪造缺失边界。

本次只改变Web展示，事件持久化、SSE、API、DB、鉴权、停止/重试、Token计量不变，无需迁移或客户端生成。文件路径链接不在本次范围。

### 本次返修验证结果

8个测试文件27项通过，TypeScript及Vite生产构建通过；Web已重新构建部署。合成API搭配实际部署Web的1440/390深浅主题8张截图、computed style及无页面溢出检查通过，12个原始事件显示为5组，原始事件默认折叠/展开通过。首轮截图发现深色表格文字被全局样式覆盖，已显式继承rc-text并重新构建复验。证据：evidence/event-display/verification.json、events-dark-1440.png及同目录其余截图。附件对照三项均已修复；无新增modal，原停止/重试测试通过。

当前应用内浏览器认证失效，未读取现有真实会话；视觉数据为合成，不声称本批真实模型执行通过。数据层与执行协议未变，现有消息及事件在重新登录并刷新后使用新渲染。未请求重新登录作为修复阻塞；无发消息或模型用量。


## 2026-09-11 验收返修：Harness 对话与轨迹

以本机 DeepSeek Harness 的对话/轨迹结构为新参考，保持 MoonBox 共享导航与空间/对象权限。对话为右侧用户气泡、无边框助手正文、紧凑自适应输入、消息复制与本轮轨迹入口；Enter发送、Shift+Enter换行、中文输入法不误发送。活动轮次显示过程摘要，失败附着轮次。消息历史加载更早页，滚动阅读不强制跳底；轨迹标签隐藏保留阅读状态。

轨迹包含按原标识配对的工具节点、搜索、内容折叠、事件概览与可调整宽度的详情。详情提供概述、参数、结果、Schema可用性及计时；窄屏上下排列。现有停止确认、原轮次重试、引用快照及Diff保留。事件每窗口最多1000条，可以读取后续窗口或从头查看；窗口边界缺少工具开始记录时不伪造开始时间。旧数据未采集字段明确显示不可用。耗时概览按对数缩放并显示说明，不冒充模型请求计时。

新增工具详情仅存于本人会话事件JSON：白名单参数、截断输出、退出码、状态、记录时间和耗时来源。先脱敏再限长；不新增表/接口/认证/部署范围。平台日志与审计不记录这些正文。明确final_answer可用时最终消息使用最终正文，其余过程留在轨迹；旧协议保持兼容。Schema、模型请求层级、缓存率、内部推理不编造，也不增加模型切换、附件、分支入口。

验证：前端31项聚焦回归通过；后端工具/权限/结算聚焦回归与构建记录见本批最终验证摘要。真实组件+合成API在1440桌面和390窄屏深浅主题观察；样式与无横向溢出记录于 evidence/harness-trajectory/verification.json。未宣称与参考逐像素相同，原始参考截图含私人路径而未落盘。新一轮真实模型执行与合成视觉验收明确区分。


### 本批最终验证与一致性扫尾

后端48 passed、1 skipped（需显式启用的真实模型测试）；前端31 passed，TypeScript及生产构建通过。工具详情通过模拟App Server→Worker→真实测试数据库的入库、脱敏、结果、退出码及耗时断言；不冒充本轮真实模型验证。Web与Worker按原Compose配置更新并健康，更新前活动运行数为0；运行Worker的execution.py和tool_record.py摘要与工作树一致。原有recovery容器保留。

REQ 子文档一致性扫尾：requirement、business-flow、user-stories、acceptance、prototype/web/context已同步；trace由工作流同步。prototype.html保留原始历史参考，不覆盖附件来源，新基线冲突与覆盖范围记录在context和design。Schema、模型请求级分组、内部推理、附件与分支不属于本批；界面明确不可用，不伪造采集。产品数据采集影响声明承接本次design契约，无新表或OpenAPI结构变化，不需迁移或Orval再生成。既有SSE payload为开放JSON，本次字段说明同步API索引和DB设计。

本Change严格规格、中文优先、目录、Sprint scope与上下文预算检查通过。全仓中文优先校验被另一活动Change的既有英文标题阻断，未修改无关Change。浏览器验收为合成API配合真实组件，1440/390深浅截图已在工具输出中观察，脱敏样式摘要为长期证据；尚未进行与DSH逐像素差异断言。


## 首次输入返修（2026-09-11）

进入工作台即可编写本地草稿，首次发送自动创建个人会话再提交轮次；单仓库自动选择，多仓库在输入区选择。新建会话只打开新草稿，无前置弹窗、无空会话写入。服务未就绪仍可编辑，发送继续校验认证、仓库及执行能力。

创建和发送分别使用稳定请求标识；创建响应丢失重放得到同一会话，创建成功后发送失败复用已有会话与轮次请求，连续点击不重复提交。创建幂等按用户隔离并重验权限；参数冲突拒绝、删除记录不复活。草稿仅内存驻留并按空间/实例隔离，刷新不保证保存未发送内容。首次未关联会话仍遵循原只读策略；需要写入时按既有流程关联对象与Change。

证据与状态矩阵见design及evidence/first-send/verification.json。OpenAPI脚本受本机pnpm版本检查影响；契约已导出并通过本地Orval生成客户端。最终验证与部署结果另行回填。


### 首次输入最终验证

前端5文件23项相关测试通过（含空间草稿隔离），TypeScript及生产构建通过；后端39项通过、1项真实模型选择性跳过。1440/390深浅主题完成截图观察和样式采样，合成API浏览器首次发送进入会话并更新URL，新建直接回草稿，无弹窗。证据：evidence/first-send/verification.json。

Web/API已按原Compose更新且healthy，更新前活动运行为0；实际HTTP OpenAPI幂等字段及运行后端源码摘要与本地一致，Web产物匹配。不需要DB迁移，未额外启动模型任务或修改凭证、配额、保留策略。

OpenSpec严格、中文优先、目录、上下文预算、Sprint scope及观测门禁通过。本批文件空白检查通过；全仓diff检查发现其他需求中心测试的既有/并行尾随空格，本批未修改。OpenAPI生成脚本存在本机pnpm版本检查不匹配，已导出契约并使用项目本地Orval成功生成。


## 顶部精简验收调整（2026-09-11）

Chat移除顶部空间工具栏和项目连接栏；会话标题行仅承接原展开/收起按钮，历史和新建动作保留。空间和主题通过共享侧边栏菜单切换。当前唯一授权仓库自动选中，首次发送创建会话；多仓库保留输入区选择，无仓库仍显示真实不可用原因，不硬编码仓库路径或绕过权限。消息区填满剩余空间、输入卡居中，切换轨迹不丢草稿。

顶部精简最终验证：27项前端测试通过，最终Docker构建包含输入居中修正且TypeScript通过；Web运行且HTTP冒烟通过（无独立Docker Health字段），后端和Worker未重启。OpenSpec严格/中文优先/目录/预算/Sprint scope/观测及本批空白检查通过。视觉为真实组件+合成接口，不新增真实模型运行。


## 会话标题与历史入口返修（2026-09-11）

已创建会话的标题及编辑图标作为重命名入口，复用既有弹窗；空草稿显示“新会话”，首次发送创建后才可改名。删除标题下拉及快速切换弹窗，其他会话统一从历史弹窗选择。移除对话/轨迹栏常驻“个人会话”标签，权限说明保留在历史弹窗：仅本人可查看，同时遵循空间、仓库与关联对象权限。保存成功同步标题及历史，空白禁用保存，失败保留编辑内容，取消不修改。后端权限校验及接口无变化。

标题编辑视觉验收：1440/390深浅主题真实组件配合合成接口通过，弹窗宽680/366px，标题13px，无横向溢出；保存/历史同步/取消已观察，证据evidence/title-edit/verification.json。

标题编辑返修收尾：Web部署产物已核对且HTTP冒烟通过；21项相关测试、构建、OpenSpec严格/语言/目录/Sprint scope/预算/观测与本批空白检查通过，未新增模型运行。


### 输入框提示精简返修（2026-09-13）

输入框正常就绪时不显示常驻执行说明或空提示节点；仅保留服务未就绪、归档、原运行未终止、缺少仓库及发送失败提示。发送按钮在有无提示时均右对齐，权限校验与请求流程不变。

验证：Composer 6项测试、TypeScript和生产构建通过。1440×900及390×844深浅主题截图已在浏览器工具观察；正常态hint节点不存在，右边界差0px，无横向溢出。真实组件配合合成API，未触发真实执行。

部署：本地Web已更新，构建资产index-DqDXCzWu.js，HTTP冒烟通过；后端无需变更。全仓中文校验受其他Change fix-requirement-center-apply-lifecycle-sync的6处英文标题影响，本Change严格校验通过，未修改其他Change。
