# local-project-governance-loop Specification

## Purpose
定义本地存量项目接入 MoonBox 后的项目绑定、可信治理基准、Chat 关联会话、治理成果候选、显式确认、受控写入、恢复处理和真实闭环验收规则，确保需求中心与 Chat 工作台围绕同一个授权项目协同推进。
## Requirements
### Requirement: 项目绑定与关联会话

系统 SHALL 以授权空间和仓库共用项目身份，卡片进入本人兼容Chat但不自动发送。

#### Scenario: 卡片进入Chat
- **WHEN** 用户选择所授权对象的Chat入口
- **THEN** 系统校验会话所有者及项目一致性，带入完整对象身份，等待用户发送

### Requirement: 治理动作可信基准

系统 SHALL 为已接入真实写入链路的治理动作准备原仓库当前治理快照与隔离副本基准，保护未提交内容和既有成果。

#### Scenario: 未提交文档存在

- **WHEN** 目标治理文档有未提交修改
- **THEN** 快照包含其稳定内容并记录摘要，不静默执行旧版本

#### Scenario: 工作区有未处理改动

- **WHEN** 既有会话含未处理成果
- **THEN** 系统 MUST 保留原副本与草稿，提示先核验未处理成果；无未决执行且用户明确选择另建时才创建兼容会话，不因忙碌静默新建

#### Scenario: Bug Generate 准备治理基准

- **WHEN** 授权用户对采集池 `BUG-*` 对象发起 `bug-generate`
- **THEN** 系统 SHALL 校验项目绑定、对象权限、对象阶段、`capture.md` 与 `trace.md` 可读且非空
- **AND** 系统 SHALL 建立与 `req-generate` 同级的治理准备会话、稳定快照和隔离副本
- **AND** 准备响应 SHALL 返回完整对象 ID、action、候选会话和待发送建议，不自动发送用户消息

### Requirement: 不可变治理成果

系统 SHALL 只将成功的合法治理动作转换为固定版本候选，并验证对象、状态和联动文件集合。

#### Scenario: 生成合法需求文档

- **WHEN** req-generate成功并只修改允许文件
- **THEN** 系统展示完整实际Diff和候选版本，原仓库状态保持不变

#### Scenario: 生成合法缺陷文档

- **WHEN** bug-generate成功并只修改允许文件
- **THEN** 系统 SHALL 展示完整实际Diff和候选版本，原仓库状态保持不变
- **AND** 允许文件 SHALL 限定为目标 BUG 的 `bug.md`、`trace.md`、`issues/bugs/_registry.yaml` 和 `issues/bugs/CHANGELOG.md`
- **AND** 候选 manifest SHALL 记录 action、对象 ID、文件摘要、binding revision 和候选 revision

#### Scenario: 越界或失败成果

- **WHEN** 输出包含其他对象改动、源码或执行失败/停止
- **THEN** 系统保留普通差异但禁止当作可应用完整成果

#### Scenario: 执行器不可用与治理校验失败分离

- **WHEN** 发送前 sandbox/dry-run preflight 失败，或执行结果显示 namespace/bwrap 失败、dry-run 未能启动
- **THEN** 系统 SHALL 将治理候选标记为 `executor_unavailable`
- **AND** 系统 SHALL NOT 创建可应用候选或 application
- **WHEN** 执行器完成但成果不符合对象、状态、标题或文件边界
- **THEN** 系统 SHALL 将治理候选标记为 `governance_validation_failed`
- **AND** 系统 SHALL 保留轻量错误或轨迹提示，不展示治理成果面板

#### Scenario: 未接入命令成果拒绝

- **WHEN** complete、review、sprint-propose、opsx 系列命令尚未接入真实治理写入链路
- **THEN** 系统 SHALL 拒绝将其普通 Chat 输出登记为可应用治理候选
- **AND** 拒绝结果 SHALL 包含安全的原因码，不包含文档正文、本机绝对路径或堆栈

#### Scenario: 写入型对象命令事实源 stale 阻断

- **WHEN** 用户从产品入口触发 complete、review、sprint-propose、opsx 或其他写入型对象命令
- **AND** 当前源工作区与治理投影的 manifest/revision 实际不一致
- **THEN** 系统 SHALL 在创建或复用 Chat 会话前阻断发送
- **AND** 阻断原因 SHALL 使用 `workspace_fact_source_stale`
- **AND** 阻断响应 SHALL 使用 `reason: manifest_mismatch` 表示内容不一致，不返回本机绝对路径或文档正文
- **AND** 系统 SHALL NOT 创建活动执行 turn、治理候选或伪成功状态
- **AND** 系统 SHALL 以当前文件内容校验 source_root 与治理投影，不因 Git dirty 阻断
- **AND** revision 一致时系统 SHALL 自动将授权的未提交治理文件同步至隔离工作区，执行前后复核 revision；已应用成果精确匹配时允许同会话继续，其他工作区修改不得覆盖

#### Scenario: 本地真实仓库模式直接读写 source_root

- **GIVEN** 仓库绑定显式声明 `workspace_mode: source`
- **AND** 用户具备当前空间和目标治理对象写权限
- **WHEN** 用户从产品入口发送已接入的治理写入命令
- **THEN** 执行器 SHALL 以 `source_root` 当前工作树作为工作区
- **AND** 系统 SHALL NOT 创建或覆盖 `<workspace_root>/<conversation_id>` 会话副本
- **AND** 命令成果 SHALL 直接落入真实仓库工作树
- **AND** generate 成果通过对象、状态、allowlist、manifest 和差异校验后 SHALL 直接标记候选与 application 为已应用
- **AND** 系统 SHALL NOT 再要求用户审阅候选、点击二次应用或执行副本同步
- **AND** 项目级串行写入协调、权限校验、Task Trace、请求日志和看板事实源刷新 SHALL 保持生效
- **WHEN** 完整对象 ID、registry path、trace status 或关键文档不满足命令前置状态
- **THEN** 系统 SHALL 使用 `governance_validation_failed` 阻断发送
- **AND** `req-explore`、`bug-explore` 和 `open-chat` SHALL 保持只读打开，不因本地 dirty fact source 被阻断

### Requirement: 显式确认与版本冲突

系统 SHALL 在用户确认固定成果集合后重新验证权限、绑定及内容版本，任何预检冲突阻止整批写入。

#### Scenario: 确认内容已过期
- **WHEN** 源文件或候选版本发生变化
- **THEN** 系统返回冲突且不覆盖文件，不以HEAD不变绕过内容检查

#### Scenario: 不具备独占条件
- **WHEN** 受控写入口未统一或无法建立维护窗口
- **THEN** 系统拒绝应用并说明原因

### Requirement: 串行幂等与可恢复应用

系统 SHALL 对受控写入统一协调，以持久日志记录多文件应用，不将文件系统宣称为跨文件事务。

#### Scenario: 重复请求
- **WHEN** 同幂等键同成果重复提交
- **THEN** 系统返回同一操作结果，不重复推进状态

#### Scenario: 中断后恢复
- **WHEN** 控制器重启且操作未终态
- **THEN** 先校验日志和前后镜像再恢复，未知外部内容进入recovery_blocked，不覆盖外部修改

#### Scenario: 并发编辑
- **WHEN** 需求中心保存与成果应用同时发生
- **THEN** 由同一项目写通道串行执行并校验版本，外部编辑依赖维护窗口和版本检查

### Requirement: 应用结果及保留

系统 SHALL 区分执行完成、待应用、已应用、冲突、失败和恢复阻塞，保留未终态恢复依据。

#### Scenario: Bug Generate 应用成功

- **WHEN** `bug-generate` 固定候选通过 allowlist、manifest、revision、dry-run 和冲突预检
- **THEN** 系统 SHALL 串行写入目标 BUG `bug.md`、`trace.md`、BUG registry 和 BUG CHANGELOG 中的合法变更
- **AND** 系统 SHALL 在后端 collect/controller 链路使用 controller-ready 写入服务门禁自动创建 application 并应用 generate 候选，不要求用户再建立或确认人工维护窗口
- **AND** 前端 SHALL 只轮询后端已有 operation，不得代表用户发起自动 application POST
- **AND** 系统 SHALL 将目标 BUG 的下一步同步为 `/bug-complete <BUG-full-id>`
- **AND** 系统 SHALL 持久化 governance candidate、application、幂等键结果和 Task Trace
- **AND** 需求中心刷新后 SHALL 以真实文件事实源展示规划中阶段

#### Scenario: Generate 自动应用异常轻量提示

- **WHEN** 已接入真实治理候选链路的 generate 命令自动应用失败、版本冲突、越界、恢复阻塞或产生校验 warning
- **THEN** 系统 SHALL 停止写入或保留未终态恢复依据
- **AND** 系统 SHALL 在 Chat 主对话区避免展示治理成果大面板、`查看成果`、`待应用成果` 或 `审阅治理成果` 弹窗
- **AND** 系统 SHALL 通过轻量错误、轨迹提示或重新准备指引暴露处置入口
- **AND** 系统 SHALL NOT 将未接入真实候选链路的命令登记为可自动应用成果

#### Scenario: Chat 工作台网络异常分层提示

- **WHEN** 工作台初始化、项目绑定、消息读取或执行轨迹轮询发生浏览器 fetch 网络异常
- **THEN** 系统 SHALL 使用中文局部提示表达工作台、项目、消息或轨迹暂不可用
- **AND** 系统 SHALL NOT 显示 `NetworkError when attempting to fetch resource.`、`Failed to fetch` 或等价浏览器原生英文错误
- **AND** 导航、历史恢复或组件卸载导致的 `AbortError` SHALL NOT 渲染为错误
- **AND** 已生成成功的 assistant 消息 SHALL 保留可见，不得被 turns/events/governance 轮询失败覆盖为全局错误

#### Scenario: 旧运行态不会恢复治理面板

- **WHEN** 用户从历史入口打开已存在治理候选的 Chat 会话
- **THEN** 前端 SHALL 检测当前 Web bundle 是否仍是最新构建资产，发现旧资产时自动刷新一次
- **AND** 前端 SHALL 清理旧版治理成果面板 DOM
- **AND** 前端 SHALL NOT 恢复或渲染治理成果大面板、查看成果按钮、待应用面板或审阅弹窗

#### Scenario: Chat 默认低推理执行

- **WHEN** 用户创建或打开可执行 Chat 会话且尚未手动选择推理程度
- **THEN** 后端 capabilities SHALL 返回 Low 作为默认推理程度
- **AND** 前端 Composer fallback SHALL 在 capabilities 尚未加载完成时同样显示 Low

#### Scenario: 应用成功但刷新失败

- **WHEN** 写入已验证完成而看板刷新失败
- **THEN** 仍显示已应用并仅重试读取，不重复应用

#### Scenario: 删除关联会话

- **WHEN** 存在未处理应用或恢复日志
- **THEN** 阻止清理其恢复依据，按受控保留机制处理

### Requirement: 真实闭环与原型验收

系统 SHALL 将原型作为设计输入，以design、REQ验收、1440px及关键交互证据、computed style、Mock/API边界和文档一致性共同判定交付。

#### Scenario: 单项目真实验证
- **WHEN** 真实浏览器在授权验证需求执行req-generate并审阅应用
- **THEN** 原仓库PRD、trace、registry、索引一致且看板自动更新，证据区分真实观察与合成回归

#### Scenario: 只有原型演示
- **WHEN** 仅模拟候选应用与卡片移动
- **THEN** 不得标为真实业务通过或关闭视觉/行为验收

#### Scenario: 文档读取复用稳定快照
- **WHEN** 读取关联Change文档
- **THEN** 授权和正文读取复用单份临时快照，保留既有一致性与权限检查，并记录脱敏分段耗时

#### Scenario: 合并同项目刷新
- **WHEN** context尚未返回且轮询或焦点触发刷新
- **THEN** 复用进行中请求，不互相取消；切换项目或卸载仍取消旧请求

### Requirement: 执行前准备失败明确终结

系统 SHALL 将未调用执行器的工作区准备失败记录为 failed，保留具体安全错误码、阶段事件与结构化日志，释放会话占用，保留未应用文件。不得将启动前失败作为持续等待的 unknown 展示。

#### Scenario: 上轮隔离成果尚未应用

- **WHEN** 新命令准备发现工作区存在不能安全覆盖的成果
- **THEN** 系统返回执行前阻断语义并保留成果，不覆盖文件、不声称已应用

#### Scenario: 恢复旧准备阶段未知态

- **WHEN** 旧轮次为 platform_workspace_unavailable 且没有执行器 turn ID，worker 与会话围栏匹配
- **THEN** 系统安全归并 failed，释放占用；真正执行中断或心跳丢失的 unknown 不被归并

#### Scenario: 评审操作记录准备不完整

- **WHEN** req-review 或 bug-review 的基线已写入，但操作记录缺失、损坏或身份不匹配
- **THEN** 系统 SHALL 在调用执行器前失败并保留基线与成果，返回具体原因及准备阶段，不启动完整模型轮次

### Requirement: 纯治理 Change 的受控归档执行

系统 SHALL 仅对已授权且已应用的纯治理 Change 归档命令授予最小归档写权限，并保证同一执行沙箱可以调用固定镜像内的治理工具。

#### Scenario: 合法纯治理 Change 归档

- **WHEN** 有写权限成员在对应主对象会话发送完整归档命令，Change 已应用且位于当前 Sprint 正式范围
- **THEN** 系统 SHALL 授予归档专用权限，使规格合并、归档移动和工作流同步可以在受控工作区完成

#### Scenario: 归档条件不足

- **WHEN** 命令、主对象、来源类型、Change 状态、Sprint 范围或成员权限任一条件不匹配
- **THEN** 系统 MUST NOT 授予归档专用写权限
- **AND** 普通治理写权限 MUST NOT 扩展到生效规格或归档目录

#### Scenario: 归档命令工具可用

- **WHEN** 执行器镜像通过工具链预检并启动治理命令沙箱
- **THEN** 命令环境 SHALL 使用固定的镜像内工具路径解析 Python、Node 与 OpenSpec
- **AND** 不得继承宿主可写工具目录或开放执行网络

### Requirement: 评审迁移同步收尾

系统 SHALL 在标准评审目录迁移入口完成后定向同步注册表与索引，并验证注册表路径、阶段、状态与迁移后的事实源一致；同步失败必须保留评审文档且不得报告完整成功。

#### Scenario: 已迁移但注册表仍指向规划目录

- **WHEN** Issue 已在 review 目录且评审事实存在，但注册表仍为旧路径和状态
- **THEN** 重试迁移入口完成目标投影同步，不重复移动文件、不推进 Sprint，卡片按真实评审状态读取已有文档

#### Scenario: 同步失败或目录冲突

- **WHEN** 同步返回错误、返回成功但注册表未同步，或目标目录冲突
- **THEN** 命令返回非零并保留现有文档，允许修复原因后重试；预演不写入

### Requirement: 产品评审投影自动收尾

系统 SHALL 在产品评审成果收集时校验完整结论、迁移集合与权限，针对仍为旧值的注册表及索引执行定向投影收尾并回读；索引目标行的状态、阶段、下一步命令和 trace 路径均须与评审结论一致。失败保留成果，原候选可在归属和基准确认后重验。隔离评审工作区使用当前迁移与同步工具。

#### Scenario: 评审文档正确但投影遗漏

- **WHEN** 归属于当前轮次的完整评审成果通过非投影门禁，而目标注册表或索引保留旧状态、阶段、下一步或路径
- **THEN** 后端补齐目标投影并再次完整校验，成功后才记录应用；其他对象、权限和根因门禁保持不变

#### Scenario: 收尾失败后安全重试

- **WHEN** 收尾中断且原候选、绑定和轮次归属仍可确认
- **THEN** 保留已有文件并支持重新校验收尾，不清空成果；发生后续轮次、未知冲突或缺基准时阻断

### Requirement: 对象解析故障隔离

系统 SHALL 定向解析会话关联对象，候选目录中的未完成 Change 不得阻断无关对象或历史读取。准备态文件保留，缺失文档与权限拒绝分别处理，不降低现有路径安全或 ACL 门禁。

#### Scenario: 创建 Change 后文档尚未生成

- **WHEN** 新 Change 只有 .openspec.yaml 而原会话关联的 REQ 或 BUG 仍可读
- **THEN** 原会话历史和关联正常读取，列表仅跳过未就绪条目，不提示空间失权

#### Scenario: 目标文档缺失与真实拒绝

- **WHEN** 已授权对象的文档暂缺，或对象权限确实被撤销
- **THEN** 前者返回尚未就绪的 503，后者保持 403；不得通过 fallback 绕过路径与权限检查

### Requirement: 执行工具链可用性

系统 SHALL 在执行镜像提供 Node、npm、pnpm、OpenSpec CLI、uv 与治理文件处理工具，并在构建与模型启动前校验工具可用性和固定版本；工具安装不得扩大网络或文件写入权限。

#### Scenario: 镜像缺失工具

- **WHEN** 只读沙箱中工具缺失、版本不匹配或探针失败
- **THEN** 当前轮次以 container_toolchain_unavailable 明确失败，释放并发并提示标准部署更新，不调用模型、不无限等待、不删除历史成果

#### Scenario: 离线治理命令执行

- **WHEN** 工具链校验通过且工作区满足既有治理门禁
- **THEN** OpenSpec 创建、状态读取、指令读取及校验可在现有治理沙箱内执行，Git 和非授权路径仍不可写

### Requirement: 评审成果受控自动回写

系统 SHALL 为 req-review/bug-review 创建当前轮候选，校验评审结论、完整目标目录迁移、registry、trace、索引和生命周期；校验通过后由后端 controller 自动应用。删除记录必须持久化、可重放，冲突不得清空成果或绕过门禁。模型执行完成与事实源应用成功分别呈现。

#### Scenario: 同会话完善后评审

- **WHEN** review.md 仅使用 status 或 result 声明合法结论
- **THEN** 使用该结论执行完整迁移校验；双字段冲突明确拒绝，保留原成果

#### Scenario: 同会话拒绝成果重新校验

- **WHEN** 最新已完成评审因契约兼容问题被拒绝，且原基准、绑定和工作区归属可确认
- **THEN** 受控恢复保留原基准和文件，重验后复用原候选自动回写；后续轮次、已有应用或事实源冲突不得被覆盖

#### Scenario: 完善后创建本轮评审候选

- **WHEN** 同一会话已有 applied complete 候选并执行 review
- **THEN** 创建本轮 review 候选，通过后迁移目标目录并同步已评审事实，历史候选不替代本轮权限或结果

#### Scenario: 停止评审后同会话继续治理命令

- **WHEN** 前一评审轮次已停止而其候选仍为 running，同一会话发送新的 Sprint 命令
- **THEN** 工作区准备仅选当前轮次绑定或合法未绑定的候选，旧轮次候选不得阻断新命令
- **AND** 系统 SHALL 保留旧轮次成果，并继续执行当前事实源、权限和工作区冲突校验

#### Scenario: 评审迁移中断恢复

- **WHEN** controller 在写目标文件或删除旧路径后中断
- **THEN** 根据原基准与显式删除记录继续校验和重放，不丢失既有成果；应用成功后才更新工作区基准

#### Scenario: 历史执行成功但尚未回写

- **WHEN** 原轮次可归属、无活跃执行且目标源文件未发生冲突
- **THEN** 保留原成果，通过同一校验和应用链恢复，不重跑模型、不直接改看板状态

#### Scenario: 评审记录初始化与收尾一致

- **WHEN** 评审进入准备、预检及完成检查
- **THEN** 系统 SHALL 使用一致动作契约验证 baseline 与 operation 的归属，不能静默跳过初始化后在收尾要求必需记录，也不能无条件跳过完整性检查

#### Scenario: 历史基线单独存在

- **WHEN** 历史评审仅有 baseline，或操作记录不可读取
- **THEN** 系统 SHALL 区分旧版兼容与缺失损坏，只有身份、权限、绑定、基线和既有应用证据满足条件才沿原候选恢复核验；证据不足时保留成果并明确阻断，不伪造空操作记录或修改失败轮次终态

#### Scenario: 重复恢复与过期成果

- **WHEN** 评审应用响应丢失后再次核验，或对象在恢复前已改变
- **THEN** 系统 SHALL 回读已有应用以避免重复迁移；版本、权限或项目绑定不匹配时拒绝过期应用，不覆盖新成果

#### Scenario: 具体错误贯穿结果链

- **WHEN** 评审因操作记录或恢复核验失败而未应用
- **THEN** 系统 SHALL 在轮次、候选和结果中保留原始错误与阶段，不统一误报执行器不可用；助手成功措辞不能覆盖业务失败事实

### Requirement: 零差异治理结果幂等核验

系统 SHALL 对无文件差异的治理候选执行完整文档、身份、状态、权限和事实源版本校验，一致时返回 unchanged，不创建写入应用或推进状态。不能把空差异直接判为失败，也不能绕过真实冲突和文档缺失。

#### Scenario: 同会话重复完善

- **WHEN** 已保存草稿再次完善但无新增差异且事实源一致
- **THEN** 显示已核验无需更新，不写文件；历史旧 rejected 不覆盖最新结果

#### Scenario: 零差异但事实源变化

- **WHEN** 工作区没有新增修改但源版本已变化或必需文档不完整
- **THEN** 拒绝核验成功，保留事实源，不创建空写入应用

### Requirement: 缺陷完善草稿自动回写

系统 SHALL 为 bug-complete 创建当前轮次治理候选并收集正式目标文档，通过身份、版本、文件范围和根因门禁后自动应用。历史已应用候选不得导致当前轮次只读回退。

#### Scenario: 根因尚待确认

- **WHEN** 根因为 unknown、hypothesis 或 probable 且草稿校验通过
- **THEN** 系统保存目标文档并同步 enriching，保留完成时间，不推进待评审

#### Scenario: 同会话生成后完善

- **WHEN** generate 候选已应用且用户继续 complete，根因为 confirmed 并有证据
- **THEN** 系统使用本轮候选写入并自动应用 pending_review 成果，不能借用历史候选或绕过冲突校验

### Requirement: 长任务不受固定五分钟截断

系统 SHALL 默认不设置固定 300 秒总执行截止，继续保留停止、权限、额度和协议边界校验。

#### Scenario: 长任务跨越五分钟

- **WHEN** 已授权任务仍在执行且没有停止或安全门禁触发
- **THEN** 不因经过 300 秒而标记 unknown；执行器权威终态决定结果

#### Scenario: 中断轮次恢复

- **WHEN** 恢复读取原 thread 和 turn 获得 interrupted
- **THEN** 将该轮次归并为停止而非成功，保留部分文件与待核算用量，允许在校验后续接

### Requirement: 执行服务就绪恢复

系统 SHALL 在启动预检成功后独立更新 Worker 心跳；前端能力探测 SHALL 自动重试并保留草稿，服务未就绪时继续禁止发送。

#### Scenario: 心跳暂时不可用后恢复

- **WHEN** 工作台读到心跳过期或网络暂时不可达，随后 Worker 恢复就绪
- **THEN** 工作台在后续能力探测成功后恢复发送按钮，保留会话、草稿和既有回复，不自动发送、不要求重载页面

#### Scenario: 维护阻塞与退出

- **WHEN** Worker 正在维护或备份，或开始正常退出
- **THEN** 维护不阻塞独立心跳发布；正常退出停止心跳线程并删除就绪文件，API 保留配置指纹与有效期校验

### Requirement: 对象治理执行互斥与可核验恢复

系统 MUST 在治理发送事务内，以授权项目与规范化对象身份原子获取持久执行守卫，统一覆盖卡片、助手、已识别直接 Chat 和直接 API。守卫版本 MUST 防止陈旧回调释放新执行；同内容幂等重放返回原结果，不同内容同幂等键受控拒绝。

#### Scenario: 双标签页跨会话并发
- **WHEN** 多请求并发向同项目同对象发送治理命令
- **THEN** 系统 MUST 至多接受一个新执行，其余受控返回忙碌或原幂等结果，不依赖前端禁用

#### Scenario: 失败停止与未知终态
- **WHEN** 执行失败、停止、失联或服务重启且存在已写成果
- **THEN** 系统 MUST 保留成果与原终态，先核验执行和业务结果再决定提交阶段或恢复发送，不因租约到期重复执行

#### Scenario: 恢复确认有效成果
- **WHEN** 失败轮次的成果经独立业务验证及同步确认有效且旧执行已结束
- **THEN** 系统 MUST 幂等记录恢复核验结果并允许有效迁移，保留原失败事实

#### Scenario: 外部命令同步
- **WHEN** 无关联产品轮次的外部治理文件更新被发现
- **THEN** 系统 MUST 通过治理验证收敛且不伪造Chat轮次，同对象存在未决产品执行时先核验冲突

#### Scenario: 入口与观测边界
- **WHEN** 已接入治理操作完成准备、拒绝、执行或恢复
- **THEN** 系统 MUST 提供脱敏对象、请求、任务及轮次关联摘要，直接 API 不伪造行为事件
- **AND** 未接入命令 MUST 明示不支持，不将共享代码测试当作逐入口真实验收

系统 MUST 分离可信历史成果与当前准入；应用核验完成 MUST 持久交接并在健康服务下60秒内收敛，不依赖打开页面。自动尝试最多3次，预算跨重启保留；确定性冲突立即阻断，保留具体原因与最近核验时间。

#### Scenario: 无关变化后的历史证明
- **WHEN** 原证明匹配重建历史成果且仅不属于操作及必要依赖的内容变化
- **THEN** 系统 MUST 验证历史事实并在权限、身份、守卫版本和当前准入通过后解除原保护，不以全局摘要变化拒绝

#### Scenario: 相关冲突与缺损证明
- **WHEN** 必要依赖变化、证明缺损或篡改、权限失效或存在新执行
- **THEN** 系统 MUST 返回具体拒绝原因，保留已证实的历史事实，不覆盖当前成果、不释放新守卫

#### Scenario: 核验完成窗口崩溃
- **WHEN** 应用已verified但保护确认前进程退出
- **THEN** 系统 MUST 在重启后60秒内恢复调度，通过持久幂等交接完成核对，不重复模型、应用或迁移

#### Scenario: 核对失败预算耗尽
- **WHEN** 瞬态失败连续消耗3次自动尝试
- **THEN** 系统 MUST 停止自动重试，提供retry_exhausted、最近核验事实与合法动作，重启不重置预算

#### Scenario: 生命周期与准入独立投影
- **WHEN** 历史评审可信完成而当前仍有未决准入原因
- **THEN** 系统 MUST 返回可信业务阶段与独立准入异常，不以旧confirmed_stage覆盖生命周期；实际发送仍在服务端校验

#### Scenario: 原现场核验与多轮迟到
- **WHEN** 用户正式核验历史操作或旧确认事件迟到
- **THEN** 系统 MUST 鉴权并按原操作幂等核对，当前相关冲突可拒绝，保留原轮次终态，不覆盖新操作

### Requirement: 评审识别既有需求追溯身份
需求评审校验 MUST 接受 trace 中既有的 req_id 或 requirement_id，并保持主文档及评审记录原身份要求；存在多个身份字段时 MUST 全部匹配目标对象，缺失或冲突不得通过。

#### Scenario: 需求追溯使用既有简写身份
- **WHEN** trace 的 req_id 与目标一致且其他评审门禁通过
- **THEN** 不因缺少 requirement_id 拒绝成果

#### Scenario: 追溯包含冲突身份
- **WHEN** req_id 与 requirement_id 不一致或任一显式字段无效
- **THEN** 拒绝应用并保留原事实

### Requirement: 评审收尾同步验收来源事件
系统 MUST 在完整评审校验通过后，将验收文档中既有 complete 来源事件同步为对应 review 事件，再次校验后进入正式同步回读，不改变验收状态或验收内容。

#### Scenario: 模型保留验收子文档原文
- **WHEN** 有效评审成果仍保留 req.complete 或 bug.complete 来源事件
- **THEN** 收尾同步对应 review 事件，重复收尾无额外变化

### Requirement: 源码执行使用可信源码根目录同步
源码模式 MUST 从已授权 source_root 执行 Workflow Sync；治理 root 只挂载文档时不得要求其包含脚本。同步前后 MUST 同时校验源码与治理投影文件一致，禁止客户端指定执行路径。

#### Scenario: 治理投影与源码根分离
- **WHEN** 治理投影只有文档而可信源码根包含同步脚本
- **THEN** 在源码根运行同步并核对两处治理事实，任一漂移则阻断

### Requirement: 归档包装脚本完成证明

系统 SHALL 对归档包装脚本内部同步与最终迁移结果执行可信核验，不能仅依赖顶层命令文本或模型成功回复。

#### Scenario: 完整归档成功

- **WHEN** 已授权归档执行结束且正式文件、同步派生结果、Issue迁移及最终摘要均通过可信核验
- **THEN** 系统 SHALL 记录绑定对象、动作及原执行的完成证明，并确认对象门禁
- **AND** 看板与正式归档阶段一致且对象保持只读

#### Scenario: 内部步骤失败或证明不可信

- **WHEN** 同步或迁移失败、证明身份不匹配、摘要变化或材料不足
- **THEN** 系统 SHALL 保留结果待核对与原成果，并提供具体阻断原因
- **AND** 不得凭脚本名称、退出码或回复文本单独确认成功

### Requirement: 原归档执行受控重核验

系统 SHALL 支持已结束归档执行的可信重核验，且不重放归档或模型任务。

#### Scenario: 原结果恢复

- **WHEN** 原执行缺少同步识别记录但正式归档结果可重新可信验证
- **THEN** 系统 SHALL 将恢复证明关联原执行并收敛门禁，保留原历史步骤事实
- **AND** 不重复迁移Issue、不重复应用、不启动模型

#### Scenario: 摘要漂移与旧执行竞争

- **WHEN** 当前文件与旧记录摘要不同或门禁已归属新的执行版本
- **THEN** 系统 SHALL 重新验证变更边界和当前一致性，并在无法证明安全时阻断
- **AND** 旧执行不得覆盖新执行，重复确认和重启恢复保持幂等

#### Scenario: 直接同步回归

- **WHEN** 执行顶层正式同步或仅check、dry-run命令
- **THEN** 系统 SHALL 保留直接同步核验能力，且仅检查命令不得产生完成证明

### Requirement: 跨入口当前动作一致性

系统 SHALL 以同一结构化验收事实判定产品与CLI归档准入，并保留历史完成证明。合法后续阶段须有可信关联和当前证据，未知占用、真实冲突及证据过期不得放行。卡片仅显示一次阻塞摘要，历史核验细节默认折叠。

#### Scenario: 后续合法交付承接历史评审

- **WHEN** REQ或BUG已有可信评审成果且后续Change完成有效验收
- **THEN** 产品与CLI按当前归档动作作出一致判断，不因旧评审摘要变化永久阻断
- **AND** 历史操作与原终态保持不变，后续实质变更由当前证据覆盖

#### Scenario: 治理投影与源码根分离

- **WHEN** 部署中的治理根只包含治理文档，验收计划另有 src 或 scripts 输入
- **THEN** 系统 SHALL 仅从已配置的受信任源码根读取这些源码输入的指纹，治理文档与证据仍以治理根为准
- **AND** 缺失或过期输入仍阻断，不能以另一副本掩盖治理删除或变化

#### Scenario: 后续复核的证据承接
- **WHEN** 原评审之后发生同对象的补充 approved 评审，当前完整评审文件已被有效验收指纹覆盖
- **THEN** 可承接原保护且保留原操作终态；结论拒绝、身份不符、无覆盖或证据过期时仍拒绝

### Requirement: 发送快照冲突安全重试
系统 SHALL 在命令记录持久化之前有界重试瞬时快照冲突，重新执行当前权限、验收与执行保护检查。

#### Scenario: 快照冲突停止后发送
- **WHEN** 一次无关治理更新造成预检和基线版本不同且随后稳定
- **THEN** 系统重新预检并允许有效命令入队，同请求只创建一个轮次

#### Scenario: 持续冲突或门禁失效
- **WHEN** 三次读取仍冲突或当前权限、验收无效
- **THEN** 系统分类返回阻塞原因，不持久化未验证基线，不绕过门禁

### Requirement: 跨链路归档基线连续证明
系统 SHALL 在产品与 CLI 共用只读恢复准入，旧基线变化只接受完整连续的已完成归档哈希证据，所有中间归档须唯一、增量结果有效且与本对象规格范围不相交；未知变化、相关范围冲突和缺损证据继续阻断。显式刷新 SHALL 保留旧记录和衔接证据，不把已经合并的状态重置为待合并。

#### Scenario: 其他链路先完成归档
- **WHEN** 本对象恢复记录保留旧基线，其他独立 Change 已完成归档且连续哈希链与当前正式规格完全一致
- **THEN** 两入口一致允许当前动作或安全续接；不重复模型调用、规格合并或 Issue 迁移

#### Scenario: 无法证明的规格变化
- **WHEN** 哈希链缺失、范围重叠、归档未完成、结果被篡改或准备过程发生并发变化
- **THEN** 两入口一致拒绝，保留旧记录及文件现场，提示核验恢复基线

### Requirement: 恢复指纹隔离派生验收输出
系统 SHALL 再次验收产生的报告与 trace 运行正文属于派生输出，不得使归档恢复记录自失效；交付输入、链路身份、真实证据完整性及并发变化仍受门禁保护。验收收尾后必须通过产品与 CLI 共用的正式准入，验收 passed 不等于归档 ready。错误须区分交付输入变化、旧记录过期、规格基线缺证、身份冲突和记录损坏。

#### Scenario: 重新验收后归档
- **WHEN** 恢复记录存在且验收仅更新派生输出
- **THEN** 通过统一准入并保留归档输出，真实输入变化仍阻断

#### Scenario: 关联链路先归档
- **WHEN** 关联 Change 的验收证据随合法归档迁移
- **THEN** 关联链路先归档后，验收证据按唯一已完成归档身份定位，继续核对原内容哈希；活动目录仍存在、归档身份歧义、未完成或证据被篡改时仍阻断。

### Requirement: 跨日迁移后的归档恢复
系统 SHALL 以唯一 Change 身份及已证明的实际迁移位置恢复归档，保留准备日期，并读取归档自动验收证据而非回退人工勾选。

#### Scenario: 跨日中断后重复收尾
- **WHEN** 前一天准备的归档在次日迁移后中断并再次执行
- **THEN** 校验原证据、交付输入与规格结果，恢复收尾且不重复合并规格

#### Scenario: 归档证据不完整
- **WHEN** 自动验收缺项、附件被篡改或存在多个归档身份
- **THEN** 阻断收尾并保留已有迁移事实，不降级为人工验收

