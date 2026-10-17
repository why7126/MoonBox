---
title: 需求中心治理命令链真实写入修复
created_at: '2026-09-29 16:07:39'
updated_at: 2026-10-07 15:35:00
---

# 需求中心治理命令链真实写入修复

## ADDED Requirements

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

## MODIFIED Requirements

### Requirement: 执行前准备失败明确终结

系统 SHALL 将未调用执行器的工作区准备失败记录为 failed，保留具体安全错误码、阶段事件与结构化日志，释放会话占用，保留未应用文件。不得将启动前失败作为持续等待的 unknown 展示。

#### Scenario: 上轮隔离成果尚未应用

- **WHEN** 新命令准备发现工作区存在不能安全覆盖的成果
- **THEN** 系统返回执行前阻断语义并保留成果，不覆盖文件、不声称已应用

#### Scenario: 恢复旧准备阶段未知态

- **WHEN** 旧轮次为 platform_workspace_unavailable 且没有执行器 turn ID，worker 与会话围栏匹配
- **THEN** 系统安全归并 failed，释放占用；真正执行中断或心跳丢失的 unknown 不被归并

### Requirement: 治理动作可信基准

系统 SHALL 为已接入真实写入链路的治理动作准备原仓库当前治理快照与隔离副本基准，保护未提交内容和既有成果。

#### Scenario: 未提交文档存在

- **WHEN** 目标治理文档有未提交修改
- **THEN** 快照包含其稳定内容并记录摘要，不静默执行旧版本

#### Scenario: 工作区有未处理改动

- **WHEN** 既有会话含未处理成果
- **THEN** 系统要求新建兼容治理会话，不覆盖原副本

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
