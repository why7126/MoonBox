---
bug_id: BUG-0033-opsx-apply-governance-scope-source-readonly
title: 产品内执行 opsx-apply 误授治理写权限导致源码只读
status: done
owner: 产品团队
created_at: 2026-10-06 22:27:51
updated_at: 2026-10-12 23:44:08
discovered_at: 2026-10-06 22:22:15
environment: 产品内 Chat 工作台，部署模式和运行版本待核实
related_requirement:
related_change:
related_bug: BUG-0026-chat-platform-opsx-archive-source-permission
lifecycle_stage: review
root_cause_status: confirmed
severity: high
---

# 产品内执行 opsx-apply 误授治理写权限导致源码只读

## 现象

用户报告：在产品内对已纳入 Sprint、已创建 Change 的对象执行 `/opsx-apply`，执行器获得治理写权限，源码只读，导致实现任务无法继续。原 BUG-0029 失败 turn 的实际 profile、Change 字段及 Chat 阻塞表现已取得；完整策略对照确认权限回退机制。不能据此认定所有满足门禁的对象均受影响。

## 复现步骤

1. 使用对目标项目具有编辑权限的账号，打开受影响 REQ 或 BUG 的对象会话，记录主对象 ID、关联 Change、Sprint 和部署版本。
2. 对照 Issue 注册表与 trace，核对 `status`、`iteration`、`related_change`；对照 Change trace 的状态、Sprint、来源 Issue 字段，以及 Sprint 的 `requirements` / `bugs` 和 `changes`。
3. 在测试环境发送该对象的完整 `/opsx-apply` 命令，记录同一 turn 的权限决策原因、`write_scope` 和实际执行器 profile。已存在失败 turn 时优先只读复核，避免重复业务操作。
4. 在已授权实现任务内核对源码修改结果，保存仓库相对路径与脱敏失败摘要。观察是否被限制为治理目录写入。不要通过修改权限或生产源码来制造复现。

以上为待运行态核验的复现流程，本轮完成的是下文函数级合成验证。

## 期望与实际

| 项目 | 期望 | 实际与证据范围 |
|---|---|---|
| 实现权限 | 合法满足 Sprint、Change 和成员权限门禁的实现任务获得 `implementation_write`，映射到 `moonbox-write` | 用户报告获得治理写权限；失败 turn 的实际字段待补证 |
| 源码修改 | 能修改当前 Change 范围内的源码，同时遵守安全边界 | 用户报告源码只读，阻断实现 |
| 门禁不满足 | 明确提示缺失事实或不支持的执行阶段，不误导为可继续实现 | 当前代码可在实现检查失败后回退 `governance_write`；该分支与本次故障的关联待确认 |

## 影响范围与严重等级

严重度为 `high`，与当前 trace 保持一致。正式开发执行可能被阻断；尚无数据损坏、越权写入或所有用户均受影响的证据，不上调为 critical 或 blocker。

潜在影响面为产品内 Chat 的权限策略、对象事实解析与执行器 profile 映射。REQ 与 BUG 共用实现权限检查；直接以 Change 为主对象的入口是否涉及本次报告待核实。其他部署模式、独立 CLI、归档命令的影响尚未验证。

BUG-0026 聚焦 `/opsx-archive` 的归档目录权限，本条聚焦 `/opsx-apply` 的源码写入，保留关联，不合并两者的根因或验收结论。

## 证据与自主补证

| 编号 | 类型 | 来源 | 结果及边界 |
|---|---|---|---|
| E1 | 用户反馈 | 本 BUG 的 capture.md 与用户授权引用快照 | 报告已纳入 Sprint 的 apply 获得治理写权限；未含目标 turn 证据 |
| E2 | code_path | `src/backend/app/chat/policy.py:19`、`:73` | 实现检查要求注册表状态精确为 in_sprint、有效单一 related_change/iteration、活动 Change 状态 proposed/in_progress、sprint 相符、来源字段 requirement/bug 和 Sprint 双向包含；检查返回 False 后可回退治理写权限 |
| E3 | code_path | `src/backend/app/chat/relations.py:62` | REQ/BUG 的 entry 来自注册表；直接 Change entry 使用 status: change，不能通过实现检查的 in_sprint 条件 |
| E4 | code_path | `src/backend/app/chat/app_server.py:64` | governance_write 与 implementation_write 分别映射 moonbox-governance 与 moonbox-write；未证明失败 turn 实际使用哪个 profile |
| E5 | reproduction | 本轮对 policy.py 的 `_implementation_ready`、`_governance_writable` 原函数 AST 做内存合成输入验证 | proposed + bug + 双向 Sprint 关联：True；仅改为 source_bug：False 且治理条件 True；仅改为 applied：False 且治理条件 True；直接 Change entry：False。命令退出码 0，无源码或业务数据写入 |

E5 使用标准库 AST 抽取原函数，注入内存 YAML 文件读取器；合成 Issue 为 BUG-9999-synthetic、Change 为 fix-synthetic、Sprint 为 sprint-999。结果仅验证函数分支，不是完整 write_policy、成员授权、数据库、容器或产品端到端测试。合成 ID 未创建为业务对象。

## 根因确认与历史补证摘要

当前根因状态为 `confirmed`，最终依据见“根因确认补证”及 review.md；以下保留早期 hypothesis/probable 的探索记录。候选方向是：服务端读取到的对象事实未满足实现权限检查，随后回退治理写权限。已验证的候选差异包括来源字段别名、Change 状态与直接 Change 对象形态；尚不知道本次实际命中了哪一个条件，也不能排除运行版本、准备候选分支、工作空间事实滞后或 profile 下发差异。

基准输入能够通过实现检查，故不能将“所有 opsx-apply 均无法获得实现权限”当成代码结论。`applied` 场景也可能属于命令阶段选择问题，不能仅凭检查返回 False 判定应放开权限。

已尝试聚焦读取 capture/trace、策略及映射代码、现有测试索引和 logs 文件名，并执行合成验证。未发现 BUG-0033 专属日志文件；当前工具未提供浏览器能力，此前未获得失败目标；现已由用户确认目标为 BUG-0029，但仍缺产品访问入口或脱敏 turn 轨迹，无法自主完成产品复现。当前 bug-generate 会话的权限不能替代先前 opsx-apply 失败 turn 的证据。

## 人工补证步骤

为区分治理事实不匹配与执行器下发错误，请在产品中定位原失败会话，按同一 turn 汇总下列信息；优先导出现有记录，无需重新执行生产实现任务。

1. 返回部署模式、版本、发生时间和目标 REQ/BUG、Change、Sprint 标识，确定取证对象。
2. 在会话详情或浏览器 Network 的会话详情响应中查看 `write_scope`、`write_reason_code`；另从同一 turn 的受控执行记录确认实际权限 profile。会话详情可能反映当前事实，请注明采集时间，不能将当前结果冒充失败时结果。
3. 返回当时注册表条目的 status/iteration/related_change、Change trace 的 status/sprint/requirement/bug/source_requirement/source_bug 和 Sprint 包含关系摘要，定位未满足的判断条件。
4. 返回失败源码的仓库相对路径与错误码或短摘要，以核验权限与失败是否存在因果关系。

返回格式可用字段表；缺失值写“未取得”。不提供密码、Token、Cookie、真实环境文件、原始聊天内容、客户数据或本机绝对路径。

## 数据采集与链路观测声明

- `product_data_collection_observability`: applicable，需用最小脱敏权限决策与执行结果建立 Agent Workflow 证据链。
- `affected_layers`: Agent Workflow 权限决策与执行器；request_logs、task_traces、task_trace_spans 的现有关联能力待运行态核实。
- N/A：本轮只生成缺陷主文档并同步状态，不修改 API、DB、UI、部署、安全策略或客户端生成物，不新增埋点、存储字段或日志采集；usage_events 不是本轮函数级合成验证的来源，不伪造用户事件。
- `validation`: 代码路径核查与函数级合成验证已完成；真实 turn、实际 profile 和源码失败对应关系待补证。后续修复范围由评审及 OpenSpec 确认。

## 本轮缺陷完善进展

已保存 [根因分析](root-cause.md)、[临时规避方案](workaround.md) 与 [回归验收草稿](acceptance.md)。根因仍为 hypothesis，主状态为 enriching。本轮新增证据 E6（执行器权限下发及运行中撤销检查）和 E7（REQ/BUG 共 8 个合成断言）详见 root-cause.md；这些证据不构成原失败 turn 的根因确认。既有现象及 E1–E5 保留。未执行完成态同步，未推进待评审，补证字段及步骤见 root-cause.md。

## 进一步补证结果

已在 BUG-0029 的实际 Change 中找到 apply 源码只读阻塞记录。其 trace 使用 bug_id/iteration，而权限检查要求 bug/sprint；原文件输入检查为 False，仅在内存同时追加两字段后变为 True，4 个对照断言通过。Sprint 双向包含条件已核实，相关对象文件没有修改。容器治理 profile 只开放治理目录，与源码只读机制一致。证据 E8–E11 及限定见 root-cause.md。

根因由 hypothesis 提升为 probable，主状态仍为 enriching；用户已确认原失败对象为 BUG-0029；仍待取得当时服务端事实、reason_code 和实际 profile。未运行完整产品链路；现有 pytest 集成测试因环境缺少 pytest 未执行。此前各轮 hypothesis 描述作为历史记录保留，不表示当前状态。未调用完成态同步。

## 原失败对象确认

用户本轮明确确认：原失败对象为 BUG-0029-chat-workbench-nonempty-page-scroll。关联 Change 为 fix-chat-workbench-nonempty-page-scroll，Sprint 为 sprint-008（后二者依据已核对的当前治理文件）。此项确认将 E8–E11 的文件对照关联到用户报告对象；不代表用户确认了失败时的权限分支或实际 profile。根因保持 probable，主状态 enriching。

## 原失败 turn 自动取证进展

已只读定位 BUG-0029 原 apply turn（2026-10-06 21:31:22），取得 Issue 主文档快照版本，并从 sequence=61 的成功工具事件确认当时 Change 已使用 bug_id/iteration、缺少 bug/sprint。证据 E13–E16、片段指纹及重建边界见 root-cause.md。尚未取得显式权限决策、历史 profile 名称及服务端完整治理输入版本；根因保持 probable，主状态 enriching。此前“未取得 turn”描述是历史补证阶段记录，以本节为准。

## 原执行器 profile 补证

已从原执行器 rollout 的同一 turn 上下文取得实际 `moonbox-governance` profile，确认 `/work` 只读而治理目录可写；Firefox 中原 Chat 会话也显示 apply 因源码只读阻塞、任务保持 0/7。历史服务端 `write_scope` 与 `reason_code` 没有独立留存，只能按策略重建，根因保持 probable。后续修复需保留同轮次脱敏权限决策与实际 profile 的关联，再复核重建原因；细节见 root-cause.md E17–E20 与 acceptance.md AC-011。

## 根因确认补证

对原 BUG-0029 会话只读运行完整 `write_policy`，结果为 `governance_write / governance_object_writable`；同一进程仅在内存中为目标 Change trace 补齐 `bug`、`sprint`，结果变为 `implementation_write / implementation_change_in_sprint`。原失败轮次实际使用治理 profile，原 Change 已使用不兼容的 `bug_id`、`iteration`，Firefox 原会话显示源码只读阻塞。证据链确认字段契约不兼容导致实现权限回退，根因状态提升为 confirmed。原轮次的 `reason_code` 没有持久记录，当前复现值不得写成历史原文。修复仍需通过评审、Sprint 和 OpenSpec；权限决策留痕按 acceptance.md AC-011 验收。

## 修复评审结论

评审通过，状态 approved，确认修复，严重度 high 不变。原轮次 profile、原 Change 字段与完整策略正反对照支持 confirmed；历史 reason_code 未留存的限制继续保留，按 AC-011 在修复后验证。尚未纳入 Sprint、创建 Change 或完成修复验收。此前各补证章节中的状态和待补证描述为历史阶段记录，当前状态以本节和 review.md 为准。最终项目事实源是否应用以后端应用结果为准。

## 本次实现与验证进度

已实现 Change 来源/Sprint 字段别名归一化、冲突/类型/来源匹配拒绝、执行器 profile 一致性检查和同 turn 脱敏权限事件。新增 test_permission_governance_contract.py 的 8 组 unittest 通过，包含完整 write_policy + 隔离 SQLite、REQ/BUG 别名矩阵、治理候选、只读成员、阶段门禁、profile 下发和事件持久化/去重/脱敏/降级。没有改变归档权限判定。

这不是修复后产品验收通过：真实 BUG-0029 场景 apply、MySQL 事件回归、既有 pytest 集成与执行中撤权全链路仍待运行。pytest/httpx 缺失，虚拟环境解释器不可用，临时安装依赖因网络 DNS 失败；当前无可用浏览器工具和可调用 Docker/MySQL 测试环境。AC-002 至 AC-009、AC-011 不因此自动通过；AC-011 仅完成隔离事件与适配器单元验证。历史 reason_code 缺失事实保持原样。

继续保持在研，未执行 opsx.apply 完成态同步；不得据源码已改或请求已确认宣称真实权限验收完成。后续先在已授权测试环境完成真实写入/拒绝和同 turn 决策事件核验，再处理归档。
