---
bug_id: BUG-0033-opsx-apply-governance-scope-source-readonly
title: 产品内执行 opsx-apply 源码写权限回归验收
acceptance_status: passed
owner: 产品团队
created_at: 2026-10-06 22:32:47
updated_at: 2026-10-17 16:45:27
---

# 产品内执行 opsx-apply 源码写权限回归验收

## 验收状态与前置条件

根因已通过原失败轮次证据、浏览器观察和完整策略内存对照确认为字段契约不兼容。当前原部署代码与工作区修复文件哈希一致，受控 BUG/REQ 产品轮次与撤权轮次已复验；11 项自动验收结论见文末。历史 BUG-0029 会话不能重跑，不补造当时的决策字段。

## 验收矩阵

以下复选框是需求中心卡片验收进度的计数来源；下表保留验收启动时的操作、证据和隔离测试结果，当前逐项结论及证据入口见文末。

- [x] AC-001：还原原失败对象及相同事实条件，核对权限分支、实际 profile 与失败因果关系。
- [x] AC-002：合法 BUG apply 获得实现写权限，完成范围内测试源码写入与还原。
- [x] AC-003：合法 REQ apply 与 BUG 保持相同的实现写入语义。
- [x] AC-004：缺少 Sprint 成员、Change 关联或未评审对象不得获得源码写权限。
- [x] AC-005：只读成员或不可访问项目不得绕过访问与只读边界。
- [x] AC-006：来源字段别名、直接 Change 主对象与 applied 阶段按事实契约正确判定。
- [x] AC-007：执行中撤销权限或改变事实后停止越权写入并保留原因。
- [x] AC-008：治理生成与完善命令保持治理目录边界，不能写源码。
- [x] AC-009：原失败部署模式修复后以真实产品轮次确认问题消失。
- [x] AC-010：治理文档与证据一致且不含凭证或原始会话。
- [x] AC-011：同一轮次的权限决策与执行器 profile 可关联且记录脱敏。

| 编号 | 场景与操作 | 期望结果 | 必需证据 | 当前结果 |
|---|---|---|---|---|
| AC-001 | 还原原失败对象及相同事实条件 | 可解释具体权限分支、实际 profile 与源码失败的因果关系 | 原 turn 证据、浏览器观察、完整策略内存对照 | 根因取证通过；原轮次 reason_code 未持久化 |
| AC-002 | 对满足成员、Issue、Sprint、活动 Change 门禁的 BUG 执行 apply | 获得 implementation_write / moonbox-write，完成 Change 范围内测试源码写入与还原 | 策略结果、实际 profile、写入差异及还原结果 | 未执行 |
| AC-003 | 对满足相同门禁的 REQ 执行 apply | 与 BUG 的合法实现行为一致 | 同 AC-002 | 未执行 |
| AC-004 | 分别缺少 Sprint 成员、Change 关联或使用未评审对象 | 不获得源码写权限，明确门禁缺项；不误报实现成功 | 负向策略结果、拒绝结果、源码无差异 | 未执行 |
| AC-005 | 只读成员或不可访问项目尝试实现操作 | 保持访问及只读边界，不被治理回退分支绕过 | 授权拒绝证据、无源码写入 | 未执行 |
| AC-006 | 来源字段别名、直接 Change 主对象、applied 状态分别进入策略 | 按确认后的事实契约及命令阶段明确处理；不无条件放开权限 | 每个变体的预期依据与实际决策 | 未执行；预期细节待根因确认 |
| AC-007 | 执行过程中撤销合法权限或改变相关事实 | 按设计停止写入并保留明确原因，不继续越权执行 | 脱敏时间线、终止结果、撤销后无写入 | 未执行 |
| AC-008 | 治理生成、完善命令执行 | 维持治理目录边界，源码不能写；当前会话不能冒充 apply 证据 | 实际治理 profile 和边界结果 | 未执行 |
| AC-009 | 原失败部署模式的修复后回归 | 同一触发条件下问题消失，部署版本与验证代码一致 | 版本摘要、真实 turn 和最终结果 | 未执行 |
| AC-010 | 核对证据与治理文档 | 不含凭证或原始会话；bug/trace/注册表/索引一致，完成时间不伪造 | 聚焦校验及真实文件差异 | 本轮草稿检查，非修复验收通过 |
| AC-011 | 记录每轮权限决策并与执行器启动关联 | 同一 turn 可核对脱敏 `write_scope`、`reason_code`、实际 profile、事实版本摘要与时间；权限降级和拒绝分支同样可诊断 | 持久记录与执行器 `turn_context` 的同轮次对照；敏感字段扫描 | 未实施；原失败 turn 仅保留实际 profile，缺服务端决策字段 |

## 合成验证与真实观察边界

root-cause.md 的 E7 为 8 个函数级合成断言通过，只证明当前策略函数的输入输出；不计为 AC-001 至 AC-009 的通过，不代表修复已实现。源码写入与还原测试仅在后续明确授权的测试环境执行。

## 数据采集与链路观测

- `product_data_collection_observability`: applicable。
- `affected_layers`: Agent Workflow 权限决策、执行器下发和执行结果；按可用事实关联 request_logs、task_traces、task_trace_spans，不假设它们已覆盖权限决策。
- 证据最小集：脱敏 turn 标识、时间、事实版本摘要、scope、reason_code、实际 profile、源码相对路径及错误码；不存完整 prompt、原始聊天、凭证、客户数据或本机绝对路径。
- N/A：本轮只完善治理草稿，API/DB/UI/部署/安全策略及客户端生成未变化，不增加 usage_events 或日志字段；合成验证不伪造行为事件。
- `validation`: 静态链路核查及 E7 合成验证已完成；真实失败和修复回归尚未执行。

## 完成判定

根因达到 confirmed 并具备可复核证据链后，才执行完成态 dry-run、相关完成校验和 Workflow Sync 到 pending_review。pending_review 表示可评审，不表示缺陷修复验收通过；后续真实行为验证仍按上表逐项记录。

## 进一步补证验收记录

E10 使用真实治理文件输入的 4 个内存对照断言通过，仅证明两个字段的兼容缺口，不计为 AC-001 至 AC-009 通过。后续 AC-006 明确加入 bug_id/iteration 字段组合及单字段变体；保留 Sprint 双向包含、成员权限和命令阶段的负向边界。AC-001 的原失败对象已由用户确认为 BUG-0029；仍需同一 turn 的实际决策证据。完整策略集成测试未执行：当前 Python 缺少 pytest。所有产品行为验收保持未完成。

用户对象确认 E12 只补齐事件归属，不计为产品行为验收通过。

## 原失败 turn 自动取证更新

AC-001 已定位原 turn 并取得当时 Change 字段及主文档快照，证据 E13–E16；权限决策/profile 和服务端治理输入版本仍缺，因此 AC-001 未通过。未执行产品写入或修复回归，其他产品行为验收结果不变。

## 原执行器 profile 与后续留痕验收

E17–E20 已确认原失败 turn 的实际 profile 为 `moonbox-governance`，源码根目录只读；Firefox 原会话显示任务停留 0/7。AC-001 的 profile 子项已补齐，服务端历史 `write_scope`、`reason_code` 和当时注册表版本仍未直接留存，故 AC-001 继续待补证。AC-011 将权限决策留痕列为后续修复验收项；先记录，再用同一 turn 的服务端决策与执行器 profile 复核重建的 `governance_object_writable`，不以仅有 UI 标签或当前策略结果替代。

## 根因确认后的验收边界

E21–E22 完成原会话当前完整策略的正反对照：原事实返回治理写权限，只在内存补齐 `bug`、`sprint` 后返回实现写权限。结合原 turn profile、原 Change 字段和浏览器阻塞表现，AC-001 的根因取证已通过。原轮次服务端 `reason_code` 仍无历史日志，此缺口由 AC-011 在修复后新 turn 留痕并复核；AC-002 至 AC-009、AC-011 均未因本次取证视为通过。

## 验收结果回填

```yaml
acceptance_status: passed
accepted_at: 2026-10-17 16:45:27
accepted_by: workflow-sync
source_change: fix-opsx-apply-governance-scope-source-readonly
source_sprint: sprint-008
evidence: [openspec/archive/2026-10-12-fix-opsx-apply-governance-scope-source-readonly/evidence/acceptance/20261012233916906064-2796abb8/summary.md]
failed_items: []
source_event: sprint.archive
notes: 由 Workflow Sync 根据 Change/Sprint 状态回填。
```

## 本次实现与验证进度

已实现 Change 来源/Sprint 字段别名归一化、冲突/类型/来源匹配拒绝、执行器 profile 一致性检查和同 turn 脱敏权限事件。新增 test_permission_governance_contract.py 的 8 组 unittest 通过，包含完整 write_policy + 隔离 SQLite、REQ/BUG 别名矩阵、治理候选、只读成员、阶段门禁、profile 下发和事件持久化/去重/脱敏/降级。没有改变归档权限判定。

上述环境限制为先前检查点，本轮已通过本机缓存和一次性容器解除；历史 reason_code 缺失事实保持原样。

## 本轮逐项回填（隔离测试环境）

- AC-001：原轮次根因取证保持通过，历史服务端 reason_code 不可追补。
- AC-002：通过。BUG-0029 字段形态 `bug_id/iteration` 的真实容器执行写入一次性 `counter.txt`，同一 turn 记录 `implementation_write` 和 `moonbox-write`；原产品仓库未修改。
- AC-003：通过合成 REQ 策略矩阵和容器 profile 探针；未对真实 REQ 产品会话执行模型写入。
- AC-004 至 AC-006：通过 SQLite/MySQL 权限负向矩阵、字段别名和冲突/阶段测试；对非授权对象无产品部署操作。
- AC-007：通过策略重检与现有执行器回归；真实运行中途撤权尚未单独做产品交互测试。
- AC-008：通过治理候选拒绝提升及容器只读边界探针。
- AC-009：待部署复验；测试环境不能代替原失败部署版本和会话。
- AC-010：Change 文档、中文优先和 Sprint scope 校验通过；原产品部署结果不在本项内。
- AC-011：SQLite/MySQL 事件关联、去重、脱敏、异常降级通过；真实隔离 turn 中 selected/acknowledged profile 与写入同轮次。acknowledged 单独不等于 OS 授权证明。

具体命令和测试边界见 Change `verification.md`。本回填不改变 Workflow Sync 管理的验收状态块；发布后的 AC-009 应另行复验。

## 2026-10-12 自动验收预检

本轮按 AC-001～011 建立逐项计划并运行预检，结论为 `blocked / diagnostic`（11 项受阻，0 项本轮通过、0 项功能失败）。产品轮次类 AC 缺授权本地只读 SQLite 数据源及对应真实 turn ID；原部署更新与 AC-009 真实复验也未完成。预检按规范阻止全部计划检查，故本轮单独运行的 8 组权限契约测试通过只作技术回归，不计为自动验收通过。Firefox 当前需求中心显示 BUG-0033“验收 0/11”，仅证明页面可访问及未签认状态，不证明权限修复。保持 `acceptance_status: pending` 和所有 AC 未勾选。证据入口：[20261012231705079742-e736da50](../../../../openspec/archive/2026-10-12-fix-opsx-apply-governance-scope-source-readonly/evidence/acceptance/20261012231705079742-e736da50/summary.md)。

### 2026-10-12 同轮追加诊断

确认当前本地 MoonBox 后端容器的 `policy.py`、`execution.py`、`app_server.py` 与工作区源码哈希逐一相等，产品 SQLite 可只读访问。现有产品事件未找到 BUG-0033 修复后可归属的真实复验 turn。通过 `--only` 运行 AC-001、004、005、006、010 的命令检查，5 项技术诊断通过，另外 6 项未选中；这是 `diagnostic` 清单，不构成完整验收或产品行为签认。入口：[20261012232503649051-374c142b](../../../../openspec/archive/2026-10-12-fix-opsx-apply-governance-scope-source-readonly/evidence/acceptance/20261012232503649051-374c142b/summary.md)。

### 2026-10-12 隔离真实写入复验

用户确认使用隔离验证环境；真实 Codex 容器的 BUG `bug_id/iteration` 一次性样本写入及同 turn 权限事件检查通过。此证据补强 AC-002 与 AC-011 的隔离样本部分，仍不替代 AC-009 原部署复验，也不构成全部 AC 签认。证据：[隔离复验记录](../../../../openspec/archive/2026-10-12-fix-opsx-apply-governance-scope-source-readonly/evidence/acceptance/isolated-live-retest-20261012.md)。

## 2026-10-12 自动验收完成结论

逐项验收计划完整运行 11/11 `passed`，`--readiness` 为 `ready`；证据包：[summary.md](../../../../openspec/archive/2026-10-12-fix-opsx-apply-governance-scope-source-readonly/evidence/acceptance/20261012233916906064-2796abb8/summary.md)。本轮验收者为 Codex 技术复验，签认依据为下列分层证据。

| AC | 结论 | 检查来源与边界 |
|---|---|---|
| AC-001 | 通过 | 原失败 turn、历史 profile 和完整策略红绿对照；历史 reason_code 未留存，不补造。 |
| AC-002 | 通过 | 原部署受控 BUG turn 完成，源码临时计数文件写入，权限事件同轮；隔离容器复验亦通过。 |
| AC-003 | 通过 | 原部署受控 REQ turn 完成，`requirement_id/iteration` 获得实现写入。 |
| AC-004 | 通过 | Sprint 成员、Change 关联、未评审与阶段缺失负向策略矩阵；没有对这些非授权对象发起产品写入。 |
| AC-005 | 通过 | 只读成员与项目访问负向策略矩阵；没有对非授权身份发起产品写入。 |
| AC-006 | 通过 | 字段别名、冲突、直接 Change 与 applied 阶段矩阵，旧字段形态的原部署正向轮次。 |
| AC-007 | 通过 | 原部署真实 turn 在 selected 后撤权，最终 `stopped / write_permission_revoked`，无目标写入且执行器已退出。 |
| AC-008 | 通过 | 完整策略治理候选测试与既有容器只读边界探针；本轮未在原部署运行正式治理完善命令。 |
| AC-009 | 通过 | 原部署当前修复代码哈希匹配，受控 BUG `bug_id/iteration` 真实 turn 完成并写入；原 BUG-0029 历史会话不可重跑，不把受控样本写成历史轮次。 |
| AC-010 | 通过 | Change、中文标题、证据路径及脱敏检查；临时夹具已移除。 |
| AC-011 | 通过 | 同一真实 turn 的 selected/acknowledged scope、reason_code、profile 和治理输入摘要可关联；原历史 reason_code 仍缺。 |

产品对象临时会话已归档并解除测试对象关联，临时 BUG/REQ/Sprint/Change 与计数文件已清理；产品数据库保留脱敏可核对的 turn 事件。没有自动执行真实 Change 归档。
