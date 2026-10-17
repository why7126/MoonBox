---
change_id: fix-requirement-center-command-chain-write-gap
title: 需求中心治理命令链真实写入修复
status: applied
bug: BUG-0025-requirement-center-command-chain-write-gap
iteration: sprint-008
created_at: '2026-09-29 16:07:39'
updated_at: 2026-10-14 00:27:52
acceptance_refs:
  - verification.md
product_data_collection_observability:
  status: applicable
  affected_layers:
    - web
    - api
    - usage_events
    - request_logs
    - task_traces
    - task_trace_spans
  reason: 需求中心治理命令准备、候选、应用和未实现命令反馈会影响Web、API与治理写入观测链路。
  validation: 提案阶段声明观测边界；实施阶段需以脱敏请求日志、治理candidate/application、Task Trace和前端回归验证。
execution:
  schema_version: 1
  started_at: 2026-09-29 16:13:28
  completed_at: 2026-09-29 16:21:04
  last_event: opsx.apply
---

# 需求中心治理命令链真实写入修复

## 验证摘要

2026-10-14 AF-045：AC-051 隔离 BUG 首轮虽自动应用，CHANGELOG 阶段和下一步仍为旧值；后端目标行收尾与完整校验已补齐。修复后 BUG、REQ 两轮真实产品评审均 completed、候选/应用 applied/verified，registry、目录、trace、CHANGELOG 与看板一致；59 项评审聚焦回归通过，copy checkpoint 与异常门禁由回归覆盖。证据见 [AC-051 复核](evidence/acceptance/inputs/AC-051-review.md)、[返修台账](acceptance-fixes.md#af-045-ac-051-评审索引阶段与下一步遗漏)及[完整诊断](evidence/acceptance/20261014002725865559-09fdb17f/summary.md)。完整诊断因旧输入指纹变化与其他证据缺口仅 AC-051 通过、51 项预检受阻；整体验收仍 pending，canonical applied 与首次 apply 时间不变。

2026-10-13 AF-044 修正未知治理命令在真实模式误建产品对象会话；提示完整 Codex 命令，已接入命令链保持原路由。需求中心前端完整 125 项、后端候选与独立未知命令测试 46 项通过；AC-007/008/009/010 及指纹受影响的 AC-001/025/043/044 定向通过，Workflow Sync 后[完整诊断](evidence/acceptance/20261013201313131288-d2d63b81/summary.md)为 21/52 passed、31 blocked。复核依据见 [返修台账](acceptance-fixes.md#af-044-未接入命令误建产品对象会话)和各 AC review。Change 保持 applied、Issue pending；隔离产品镜像尚未更新，未把组件回归写成新产品轮次通过。

2026-10-13 AF-043 修正旧未绑定候选阻断 BUG-0039 原会话续接；隔离产品新 `bug-complete` 轮次完成并自动应用，文件与看板保持 enriching/unknown、完成时间 null。聚焦后端 3 passed，证据及标准镜像构建限制见 [返修台账](acceptance-fixes.md#af-043-旧未绑定候选阻断同会话续接)。同日 AC-038、041、043、044 的定向机器验收通过，完整批量诊断已复用 17 项通过、35 项仍缺证据；[当前证据包](evidence/acceptance/20261013195401693342-ea59ff96/summary.md)。Change 保持 applied，首次 apply 完成时间不变，Issue pending，不归档。

2026-10-13 `/opsx-accept` 完整运行生成[诊断证据包](evidence/acceptance/20261013165839477668-5a2608ef/summary.md)。52 项中 14 项通过、38 项预检受阻，范围为 diagnostic，归档就绪未通过。新增 AC-004、012、052 复用此前授权隔离产品轮次，经只读核对同轮命令、候选与应用状态；未将合成 API 的视觉回归当成真实业务写入。既有 Issue 历史签认仍为 24/52。当前容器绑定共享源，本轮无产品写入或重启；Change 保持 applied、Issue 保持 pending。

2026-10-12 续验：将九条现行规格缺失的 delta Requirement 从 MODIFIED 纠正为 ADDED；严格校验与临时副本归档合并通过，正式 Change 未归档。AF-041 在独立真实产品副本以 BUG-9101 卡片候选取得同轮 `applied/verified` 应用，可信文件与索引为 draft，详见 `acceptance-fixes.md`。Issue 其余 AC 仍待验，不归档。

2026-10-11 隔离项目真实产品批量复验已达 24/52，28 项仍待验证；BUG-0038/0039 确认 AC-052 的旧基准阻断、原文件保留、新 key 续接与重建后错误提示。AF-042 补全 2606 错误 kind，聚焦回归 1 passed。Issue pending、Change applied、首次执行完成时间不变，不归档。详见 `verification.md` 与 `acceptance-fixes.md`。

2026-10-10 按证据驱动方式复核 BUG-0025 的 52 条 AC：15 条有足够的直接回归及所需运行态证据，已在 Issue `acceptance.md` 勾选；37 条仍缺完整的当前产品场景或复合条件证据。逐项映射、聚焦复跑和缺口见 `verification.md`。Issue 验收结论保持 pending，Change canonical applied 与首次执行时间不变；归档仍被验收门禁阻断。

11:20 真实产品创建验收专用 `BUG-0036-bug` Capture，registry/CHANGELOG、capture/trace 和看板投影一致。紧接从卡片发起 `bug-generate`，Chat 提示候选失效，发送返回「项目文件已变化，请重新准备治理动作」；再次从看板进入仍失效，未产生 `bug.md` 或执行轮次。详情见 `verification.md` 与 Issue `acceptance.md`。本轮未新增 AC 勾选，15/52 与 pending 不变；该对象不纳入 Sprint，亦非真实缺陷认定。

AF-041：11:28 与 11:43 两次 BUG-0036 产品轮次均完成模型输出并写出 draft 文件，但 candidate 均 rejected、无 application。首轮因分级同步无语义改写 capture 超出四文件边界；已让正确 Frontmatter 保持字节不变，聚焦回归 6 passed。第二轮 capture 不再变化，仍受同一项目并行写入其他 BUG/Change 文档阻断。完整证据见 `acceptance-fixes.md`、`verification.md`；canonical applied 与首次完成时间不变，15/52、pending、不归档。

## 当前摘要

AF-040：用户 BUG-0028 卡片截图显示多余“草稿”标签；规划中卡片现不渲染 draft/enriching 独立状态标签，内部状态、文档与动作不变。对照、验证和部署边界见 `acceptance-fixes.md`；canonical applied 事实不变。

AF-039：BUG-0028 产品生成命令在候选准备后遭遇事实源版本变化，worker 触发 2606 却映射成通用准备失败。已修正为 `workspace_fact_source_stale`，保留旧候选和文件，新候选续接回归 51 项通过。产品新轮次 completed，正式 bug.md 与 draft 状态已核对；标准部署后的错误提示复验见 `acceptance-fixes.md`，首次 applied 事实不变。

AF-038：后端在完整评审门禁通过后补齐 registry/索引遗漏，隔离评审分支同步当前迁移及校验工具；source 原轮次失败恢复、copy 回写及基准更新已覆盖。128 项回归通过，运行态未部署/未重跑模型，待产品复验。详见 acceptance-fixes.md、evidence/af038-review-finalization.md，首次 applied 事实不变。

AF-037：修复评审目录迁移和注册表同步脱节，已迁移对象支持安全重试与最终一致性核验；BUG-0033 已恢复 approved/review，Firefox 已评审卡片和文档读取正常。详见 acceptance-fixes.md 与 evidence/af037-review-projection.md；不改变首次 applied 时间，不推进 BUG-0033 Sprint 或实现状态。

AF-036：隔离未完成 Change 解析失败，定向读取关联对象，区分文档未就绪与权限拒绝；后端 90 passed/1 skipped、前端 7 passed。标准部署和真实 Firefox 原会话恢复验证通过，草稿及准备态成果保留。证据见 acceptance-fixes.md 与 evidence/af036-object-isolation.md；首次 applied 事实不变。

AF-035：补齐固定 Node/OpenSpec/pnpm/uv 和文件工具；构建及启动沙箱预检、凭证与工具缓存 HOME 分离、明确失败提示。标准部署已更新，真实容器命令回归通过；详见 acceptance-fixes.md 与 evidence/af035-toolchain.md。保留首次 applied 事实，本轮未重跑业务模型或修改历史未知轮次。

AF-034：已评审 REQ/BUG 加入迭代卡片命令补齐 `--req`/`--bug` 并验证两类点击跳转 Prompt。偏差、合成回归与真实运行态待复验边界见 acceptance-fixes.md；首次 apply 事实保持不变。

AF-033：原会话评审停止后候选残留 running，后续 Sprint 命令误取旧候选并在准备阶段报 2604。已按当前轮次限制候选选择并保留合法未绑定候选兼容；后端 82 项回归通过，运行态复验见 acceptance-fixes.md。canonical applied 与首次完成时间不变。

AF-032：修正评审 status/result 契约及 acceptance source_event 未修改时误拒绝，增加安全原因码和 rejected 原候选重验；验证与 BUG-0024 恢复结果见 acceptance-fixes.md，首次 applied 时间不变。

AF-031：评审当前轮候选、迁移删除记录及后端自动回写已接通。标准部署后安全恢复 REQ-0027 原评审轮次，candidate/application applied/verified，registry/trace approved、review.md 可读，工作区基准已确认且干净。真实 Firefox 卡片进入已评审；测试与证据、文档扫尾见 acceptance-fixes.md。未新建 Issue/Change，不改变首次 apply 事实。

AF-030：移除完善中标签，保留内部状态/门禁和完善入口；长负责人截断提示及回归记录见 acceptance-fixes.md。

AF-029：草稿与完善中展示分离、实际子文档入口与补证提示，继续完善不被提示禁用。后端 91、前端 111 项通过；标准部署、真实 BUG-0024 投影与双视口合成 API 浏览器验证通过。全仓 DS 既有 176 项违规单列，canonical applied 不变，证据及子文档扫尾见 acceptance-fixes.md。

AF-028：零差异完整核验后返回 unchanged，不创建 application；修正历史旧 rejected 优先选择。79 项后端与 15 项前端通过；标准部署后原会话重复 complete 真实候选 unchanged、无 application、完整文件字节不变；1440px 浏览器历史恢复通过。详见 acceptance-fixes.md，保留首次 applied 事实，待复验不归档。

AF-027：缺陷完善当前轮候选、草稿 enriching 与确认后 pending_review 自动回写；历史候选权限回退已修正。135 项后端回归通过、1 项跳过；标准部署后同会话 BUG-0024 真实轮次、候选与应用成功，本地正式文档 enriching，工作区基准自动更新。证据见 acceptance-fixes.md。不修改首次 applied 执行事实，不归档。

AF-026：原工作区 REQ-0027 成果已通过真实续接与 controller 自动应用，状态 pending_review；保留原文件并同步工作区基准。115 项后端回归通过、1 项跳过。详情见 acceptance-fixes.md，保留首次 applied 执行事实，不归档。

AF-025：修正准备阶段异常吞并为 unknown；旧准备失败按严格条件归并 failed 并保留文件。细节及验证见 acceptance-fixes.md。该批次未将 REQ-0027 隔离成果视为已应用，后续恢复见 AF-026。

本 Change 来自 BUG-0025，目标是修复需求中心看板命令展示与真实治理写入能力不一致：`bug-generate` 进入真实候选和应用链路，未接入的 complete、review、sprint-propose、opsx 系列在产品真实模式中不再模拟成功。

## 变更记录

| 时间 | 事件 | 说明 |
|---|---|---|
| 2026-09-29 16:07:39 | bug.opsx | CLI创建fix Change并生成proposal/design/specs/tasks，关联BUG-0025与sprint-008；不写业务代码。 |

## 提案阶段验证

OpenSpec strict 校验、当前 Change 中文校验、全仓残留分离报告、中文标题校验、Workflow Sync、Sprint scope 校验均已通过。AI Usage Hook 返回 warning/unavailable，command_run_count=0，Sprint 快照因 no-command-runs 跳过；不影响本次 bug.opsx 工件创建与事实源同步。

## 验证记录

### 2026-09-29 apply 实施验证

- 后端聚焦回归：`uv run pytest src/backend/tests/test_governance_candidates.py src/backend/tests/test_governance_writer.py -q`，22项通过，覆盖 `req-generate` 不回退、`bug-generate` allowlist、越界拒绝、下一步校验和 application 写入。
- 后端相邻回归：`uv run pytest src/backend/tests/test_governance_scope.py src/backend/tests/test_governance_read_cache.py tests/integration/api/test_requirement_center.py -q`，38项通过，覆盖项目授权、稳定快照和需求中心上下文。
- 前端聚焦回归：`node node_modules/vitest/vitest.mjs run src/requirement-center.test.tsx`，107项通过，覆盖 BUG 生成入口、未接入命令提示和既有需求中心行为。
- 类型校验：`node node_modules/typescript/bin/tsc --noEmit` 通过。
- OpenAPI：`bash scripts/generate-openapi-client.sh` 已导出 `src/web/openapi.json`；脚本内 Orval 阶段因本机 pnpm/corepack 缓存缺失提示跳过，随后直接运行 `./node_modules/.bin/orval --config orval.config.ts` 生成客户端成功。
- Workflow Sync：`opsx.apply` 同步成功，Updated=5、Errors=0，BUG acceptance_status 回填为 pending。
- AI Usage Hook：返回 warning/unavailable，command_run_count=0，Sprint 快照因 no-command-runs 跳过。
- Mock/API 边界：本轮验证为后端单元/集成测试与前端合成 API 组件测试，尚未声明真实部署浏览器观察。

## 验收返修记录

### AF-024 原轮次恢复与默认时限取消

原轮次经权威 interrupted 记录校正 stopped，保留部分文件及用量待核算。默认总时限取消；有界历史 RPC 读取修正恢复失败。44 项后端回归通过，1 项显式真实探针跳过；详细恢复与续接情况见 acceptance-fixes.md。

### AF-023 未落库运行输出满宽

修正 turn-user 内临时 TurnActivity 的布局归属，保留用户气泡约束。验证与附件逐项对照见 acceptance-fixes.md；新增真实页面网络驱动 DOM 回归，覆盖运行、落库、历史恢复。

### AF-022 Worker 心跳与能力恢复

心跳独立更新，能力探测自动重试并保留草稿，已应用刷新回调稳定化。后端 5 项、前端 29 项回归通过，TypeScript 与 Web 构建通过；运行态证据及部署结果统一见 acceptance-fixes.md。保留 canonical applied，不重写首次 apply 事实。

### AF-020 当前工作树事实源同步

取消 Git dirty 阻断，使用当前文件 manifest/revision 校验并同步所有写入型命令隔离工作区。精确匹配已应用成果的同会话工作区可继续 complete；额外修改保护不变。偏差、验证和文档一致性证据见 acceptance-fixes.md 的 AF-020；保留首次 applied 与 execution.completed_at。

### AF-021 本地真实仓库工作区执行模式

新增显式 `workspace_mode: source`：平台 worker 在该模式下直接把 `source_root` 作为执行工作区，治理准备/收集不再覆盖隔离副本，generate 成果验证通过后直接记录 candidate/application 为已应用。会话删除、diff 状态和未知任务恢复适配 `workspace_id=source`，保留项目级串行、权限、产物校验和看板刷新。验证证据见 acceptance-fixes.md 的 AF-021；受当前本机依赖限制，Workflow Sync 待可用项目 Python 环境复跑。

### 2026-09-29 AF-001 输入框内部治理约束裸露

- 反馈摘要：`bug-generate` 产品准备态把内部治理约束直接放入 Chat 输入框；期望用户只看到简洁命令，内部约束隐藏或折叠传递。
- 证据入口：用户附件 `codex-clipboard-c1f11dd1-4009-4cad-9f47-809a2151227c.png`；完整对照表与代码路径见 `acceptance-fixes.md`。
- 调整摘要：需求中心准备态先切到短命令展示；AF-009 最终收口为 Chat turn 只保存 display_prompt，执行器完整治理约束由后端根据 candidate 恢复，不再依赖前端隐藏 prompt。
- 文档同步：已更新 `acceptance-fixes.md`、`tasks.md`、`design.md`、`specs/web-catalog-requirement-center/spec.md`、BUG acceptance 和 Sprint acceptance-report；API、DB、部署、安全、对象存储与客户端生成不适用。
- 验证摘要：前端聚焦回归 2 个测试文件、123 个用例通过；TypeScript 通过；OpenSpec 当前 Change 中文优先与结构校验通过；中文标题校验通过 14 份文件；diff whitespace 校验通过；Workflow Sync `opsx.modify` 通过，Updated=2、Errors=0；AI Usage Hook 返回 warning/unavailable，command_run_count=0。

### 2026-09-29 AF-002 历史消息与空成果面板继续裸露

- 反馈摘要：发送 `/bug-generate BUG-0024` 后，消息历史仍显示完整内部治理约束；输入框上方 `prepared` 且 0 文件的治理成果面板一直显示，用户不理解其用途。
- 证据入口：用户附件 `codex-clipboard-0bc4837d-c9c5-4a6e-88e9-81a0d48dc41a.png`；完整对照表、根因证据与代码路径见 `acceptance-fixes.md`。
- 调整摘要：`ConversationMessages.tsx` 在用户消息展示层识别治理执行 prompt，只显示第一行短命令，复制消息同样使用可见短命令；`GovernanceResult.tsx` 对 `prepared` 且 0 文件、无应用操作的 candidate 不再渲染大型治理成果面板。
- 文档同步：已更新 `acceptance-fixes.md`、`tasks.md`、`design.md`、`specs/web-catalog-requirement-center/spec.md`、BUG acceptance 和 Sprint acceptance-report；API、DB、部署、安全、对象存储与客户端生成不适用。
- 验证摘要：前端聚焦回归 4 个测试文件、138 个用例通过；TypeScript 通过；OpenSpec 当前 Change 中文优先与结构校验通过；中文标题校验通过 14 份文件；diff whitespace 校验通过；Workflow Sync `opsx.modify` 通过，Updated=1、Errors=0，BUG acceptance_status 保持 pending；AI Usage Hook 返回 warning/unavailable，command_run_count=0。

### 2026-09-29 AF-003 Generate 候选二次应用确认过重

- 反馈摘要：`bug-generate` 已生成 4 个文件后仍停留在“待应用成果”，需要用户打开审阅弹窗、勾选维护窗口并再次点击“确认应用”；期望覆盖所有已接入真实治理候选链路的命令，校验通过后自动应用，异常时才人工确认。
- 证据入口：用户附件 `codex-clipboard-fc195caa-8226-4814-a0c2-8a4a686c50ff.png`、`codex-clipboard-5785b9c5-e981-45dc-8bd9-fc53df9baa51.png`；完整对照表、根因证据与代码路径见 `acceptance-fixes.md`。
- 调整摘要：早期先在 `GovernanceResult.tsx` 对 `pending` candidate 自动提交应用请求；AF-009 已将该职责迁移到后端 collect/controller，前端只轮询后端 operation。
- 文档同步：已更新 `acceptance-fixes.md`、`tasks.md`、`design.md`、`specs/web-catalog-requirement-center/spec.md`、`specs/local-project-governance-loop/spec.md`、BUG acceptance 和 Sprint acceptance-report；API、DB、部署、安全、对象存储与客户端生成不适用。
- 验证摘要：前端聚焦回归 4 个测试文件、139 个用例通过；TypeScript 通过；OpenSpec 当前 Change 中文优先与结构校验通过；中文标题校验通过 14 份文件；diff whitespace 校验通过；Workflow Sync `opsx.modify` 通过，Updated=1、Errors=0，BUG acceptance_status 保持 pending；AI Usage Hook 返回 warning/unavailable，command_run_count=0。

### 2026-09-29 AF-004 Chat 对话区治理成果面板仍占位

- 反馈摘要：`bug-generate` 执行中仍在 Chat 主对话区显示 `BUG-0024-capture / 正在生成 / 查看成果` 治理成果大面板；期望所有命令都不显示该面板。
- 证据入口：用户附件 `codex-clipboard-529b08ea-1e85-4886-95cc-752786646856.png`；完整对照表、根因证据与代码路径见 `acceptance-fixes.md`。
- 调整摘要：`GovernanceResult.tsx` 改为不可见后台控制器，保留自动应用、已有 operation 轮询和异常轻量提示，不再渲染治理成果卡片、查看成果按钮、维护窗口 checkbox 或审阅治理成果弹窗；`ChatWorkbenchPage.tsx` 接入自动应用成功刷新和轻量 toast。
- 文档同步：已更新 `acceptance-fixes.md`、`tasks.md`、`design.md`、`specs/web-catalog-requirement-center/spec.md`、`specs/local-project-governance-loop/spec.md`、BUG acceptance 和 Sprint acceptance-report；API、DB、部署、安全、对象存储与客户端生成不适用。
- 验证摘要：前端聚焦回归 4 个测试文件、139 个用例通过；TypeScript 通过；OpenSpec 当前 Change 中文优先与结构校验通过；中文标题校验通过 14 份文件；diff whitespace 校验通过；Workflow Sync `opsx.modify` 通过，Updated=1、Errors=0，BUG acceptance_status 保持 pending；AI Usage Hook 返回 warning/unavailable，command_run_count=0。

### 2026-09-29 AF-005 Assistant 消息宽度未占满

- 反馈摘要：Chat 对话区 assistant 输出没有占满消息历史可用宽度；期望 assistant 输出满宽展示，不再受 `.chat-message` 的 `720px/72%` 限制，用户消息仍保持右侧气泡宽度限制。
- 证据入口：用户附件 `codex-clipboard-c66e473e-f934-4680-9440-2de0aed78bea.png`；完整对照表、根因证据与代码路径见 `acceptance-fixes.md`。
- 调整摘要：`chat-workbench.css` 为 `.turn-assistant .chat-message` 增加 `width: 100%` 与 `max-width: none`，并让 assistant bubble 占满列宽；保留 `.chat-message-user` 的右侧气泡宽度限制。`chat-messages.test.tsx` 新增布局回归断言。
- 文档同步：已更新 `acceptance-fixes.md`、`tasks.md`、`design.md`、`specs/web-catalog-requirement-center/spec.md`、BUG acceptance 和 Sprint acceptance-report；API、DB、部署、安全、对象存储与客户端生成不适用。
- 验证摘要：前端聚焦回归 4 个测试文件、140 个用例通过；TypeScript 通过；OpenSpec 当前 Change 中文优先与结构校验通过；中文标题校验通过 14 份文件；diff whitespace 校验通过；Workflow Sync `opsx.modify` 通过，Updated=1、Errors=0，BUG acceptance_status 保持 pending；AI Usage Hook 返回 warning/unavailable，command_run_count=0。

### 2026-09-29 AF-006 历史轨道、自动应用和历史恢复偏差

- 反馈摘要：执行中 assistant 消息外层历史轨道仍未占满对话区；执行完成后 pending candidate 未自动应用和刷新事实源；从历史打开会话时又出现治理成果面板。
- 证据入口：用户附件 `codex-clipboard-fd85eeda-4509-4f86-8ce7-46092a27be9e.png`、`codex-clipboard-99a52e20-d07e-4720-8630-34e034d3c50b.png`；完整对照表、根因证据与代码路径见 `acceptance-fixes.md`。
- 调整摘要：`chat-workbench.css` 将 `.chat-message-history` 改为 `width: 100%`、`max-width: none`；AF-009 已将 pending、有文件和 manifest 的候选 application 创建迁移到后端，`GovernanceResult` 仅轮询 operation 且继续不渲染任何治理成果面板；测试补充 Network/DOM 证据。
- 文档同步：已更新 `acceptance-fixes.md`、`tasks.md`、`design.md`、`specs/web-catalog-requirement-center/spec.md`、BUG acceptance 和 Sprint acceptance-report；API、DB、部署、安全、对象存储与客户端生成不适用。
- 验证摘要：前端聚焦回归 5 个测试文件、149 个用例通过；TypeScript 通过；OpenSpec 当前 Change 中文优先与结构校验通过；中文标题校验通过 14 份文件；diff whitespace 校验通过；Workflow Sync `opsx.modify` 通过，Updated=1、Errors=0，BUG acceptance_status 保持 pending；AI Usage Hook 返回 warning/unavailable，command_run_count=0。

### 2026-09-29 AF-007 Assistant 正文视觉块未铺满

- 反馈摘要：执行中 assistant 消息视觉块仍不像占满整行；期望不仅取消 CSS max-width，还要让 assistant 正文 bubble/markdown 容器在运行态 computed width 等于消息历史可用宽度。
- 证据入口：用户附件 `codex-clipboard-0f5ace22-c4cb-4966-b23b-bc74dbdea89f.png`；完整对照表、根因证据与代码路径见 `acceptance-fixes.md`。
- 调整摘要：`chat-workbench.css` 为 `.chat-assistant-col`、`.turn-assistant .chat-message-bubble` 与 `.turn-assistant .chat-markdown` 增加 stretch/full-width/box-sizing 规则；`chat-messages.test.tsx` 注入真实 CSS 并渲染消息 DOM，校验运行态 computed style。
- 文档同步：已更新 `acceptance-fixes.md`、`tasks.md`、`design.md`、`specs/web-catalog-requirement-center/spec.md`、BUG acceptance 和 Sprint acceptance-report；API、DB、部署、安全、对象存储与客户端生成不适用。
- 验证摘要：前端聚焦回归 5 个测试文件、150 个用例通过，其中 `chat-messages.test.tsx` 新增 DOM + computed style 断言；TypeScript 通过；OpenSpec 当前 Change 中文优先与结构校验通过；中文标题校验通过 14 份文件；diff whitespace 校验通过；Workflow Sync `opsx.modify` 通过，Updated=1、Errors=0，BUG acceptance_status 保持 pending；AI Usage Hook 返回 warning/unavailable，command_run_count=0。

### 2026-09-29 AF-008 运行态构建与自动应用回退

- 反馈摘要：产品运行态疑似仍使用旧前端构建，导致治理面板和人工应用流程回退；期望重新构建并部署 Web 产物，补充 dist/运行态 bundle 文案断言、历史入口 DOM 断言和 governance_applications 自动创建断言。
- 证据入口：用户附件 `codex-clipboard-80d225ca-e11f-4361-b239-1dda31b47c54.png`、`codex-clipboard-2b089c6c-6d86-4444-b7fb-c881f0375530.png`；完整对照表、运行态 bundle 和数据库事实源证据见 `acceptance-fixes.md`。
- 调整摘要：新增 dist bundle 文案断言脚本并重建 Web；`req-generate` / `bug-generate` 固定候选自动应用改用 controller-ready 受控写入门禁，避免无人工维护窗口时无法创建 application；AF-009 后历史入口只轮询后端 operation，不再自动 POST application。
- 文档同步：已更新 `acceptance-fixes.md`、`tasks.md`、`design.md`、`specs/web-catalog-requirement-center/spec.md`、`specs/local-project-governance-loop/spec.md` 和 BUG acceptance；API schema、DB schema、对象存储与 Orval 生成物不适用。
- 验证摘要：后端 writer 聚焦回归 11 个用例通过；AF-009 后以前端历史入口单项证明只轮询后端 operation、不自动 POST application 且 DOM 不渲染旧治理面板；`chat-messages` 与 `governance` 聚焦回归通过；TypeScript build、Vite build、dist bundle 断言、Docker 运行态部署和 `localhost:18102` bundle 断言通过。

### 2026-09-29 AF-009 后端 controller 生成链路收口

- 反馈摘要：生成命令产品链路仍未达到预期；需要将 `req-generate`/`bug-generate` 低风险候选自动应用迁移到后端 controller，发送前增加 executor sandbox/dry-run preflight，区分 `executor_unavailable` 与 `governance_validation_failed`，Chat 历史只保存 display_prompt，所有历史入口不恢复 GovernanceResult 面板。
- 证据入口：本轮用户文字反馈；完整对照表、代码路径与 DB/文件事实源证据见 `acceptance-fixes.md`。
- 调整摘要：`prepare` 只返回短命令 display_prompt，`run_claim` 根据治理 candidate 恢复 execution prompt；`check_send` 执行 preflight；`collect` 在合法候选后端自动创建 application；`list_candidates` 返回后端 application；`Composer` 只发送 display_prompt；`GovernanceResult` 不再 POST application，只轮询已有 operation 并输出轻量提示。
- 文档同步：已更新 `acceptance-fixes.md`、`tasks.md`、`design.md`、`specs/web-catalog-requirement-center/spec.md`、`specs/local-project-governance-loop/spec.md`、BUG acceptance 与 API 文档；DB schema、对象存储和 Orval 生成物不适用。
- 验证摘要：后端治理候选与 writer 回归 24 个用例通过；前端 `governance`、`chat-composer`、`chat-messages` 36 个用例通过；历史入口单项通过，证明只轮询 operation、不自动 POST application 且 DOM 不渲染旧治理面板；TypeScript、Vite build 和 dist bundle 文案断言通过。

### 2026-09-29 AF-010 历史入口旧前端实例与缓存回退

- 反馈摘要：历史入口再次出现已移除的 GovernanceResult 治理成果面板；需要增加应用启动时构建版本校验、旧 bundle 自动刷新、历史入口 DOM 清理断言，并补充浏览器运行态 Network/DOM 证据。
- 证据入口：用户附件 `codex-clipboard-35d09be9-5698-4b5b-9698-349c6141ebad.png`；完整对照表、代码路径、运行态 bundle 与浏览器 DOM 证据见 `acceptance-fixes.md`。
- 调整摘要：Vite 构建注入 `__MOONBOX_BUILD_ID__`；应用启动时以 no-store 拉取最新 HTML 并比对当前脚本资产，旧 bundle 自动刷新一次；Chat 历史入口按会话和 candidate 恢复时清理旧治理面板 DOM；重复清理不影响普通消息文本。
- 文档同步：已更新 `acceptance-fixes.md`、`tasks.md`、`design.md`、`specs/web-catalog-requirement-center/spec.md`、`specs/local-project-governance-loop/spec.md` 与 BUG acceptance；API schema、DB schema、对象存储、权限模型和 Orval 生成物不适用。
- 验证摘要：`runtimeBuild`、`chat-messages`、`governance` 聚焦回归 23 个用例通过；历史入口单项回归通过；TypeScript、Vite build、dist bundle 断言、Docker Web 重建和 `localhost:18102` 运行态 bundle 断言通过；Playwright 历史入口 DOM 采样得到 buildId 且旧治理面板计数为 0。

### 2026-09-29 AF-011 Chat 推理程度默认值

- 反馈摘要：Chat 推理程度默认值当前显示 High；需要将新会话默认值改为 Low，并同步后端 capabilities、前端 Composer fallback 与回归测试。
- 证据入口：本轮用户文字反馈；代码证据见 `acceptance-fixes.md` 的 E-AF-031 与 E-AF-032。
- 调整摘要：`settings.py` 将 `execution_config().defaults.reasoning` 改为 `low`；`Composer.tsx` 将 fallback 执行配置改为 `low`；前端新增 capabilities 未加载时默认 Low 的回归断言。
- 文档同步：已更新 `acceptance-fixes.md`、`tasks.md`、`design.md`、`specs/web-catalog-requirement-center/spec.md`、`specs/local-project-governance-loop/spec.md` 与 BUG acceptance；API schema、DB schema、权限、部署、对象存储和 Orval 生成物不适用。
- 验证摘要：后端 `test_chat.py` 39 个用例通过、1 个跳过；前端 `chat-composer.test.tsx` 17 个用例通过；TypeScript 通过。

### 2026-09-29 AF-012 部署验收链路统一

- 反馈摘要：前序返修仍使用裸 `docker compose ... backend web` 局部重建作为运行态证据，导致 Web、backend、chat-worker、governance-controller 和治理 overlay 可能不在同一最新服务集合内；期望 BUG-0025 验收统一使用项目标准 `scripts/docker-down.sh` / `scripts/docker-up.sh self-storage-sqlite` 配对入口。
- 证据入口：`acceptance-fixes.md` 的 AF-012、E-AF-033、E-AF-034，以及 `docs/02-deployment.md` 中“日常脚本与 Chat 受控测试”部署入口说明。
- 调整摘要：长期部署文档明确原生 Compose 命令仅适用于基础局部调试；Chat + governance 产品运行态验收必须由根脚本解析 `.env`、加载 overlay 并统一启动完整服务集合。BUG acceptance、Sprint acceptance-report 和本 Change 台账同步增加部署验收口径。
- 文档同步：已更新 `docs/02-deployment.md`、`acceptance-fixes.md`、`tasks.md`、BUG acceptance 和 Sprint acceptance-report；API、DB schema、权限、对象存储和 Orval 生成物不适用。
- 验证摘要：`bash scripts/docker-down.sh self-storage-sqlite` 成功停止 Web、backend、MinIO、chat-worker、governance-controller；`bash scripts/docker-up.sh self-storage-sqlite` 通过 Chat 常驻部署和治理私有目录预检，重建 backend/web/executor/chat-worker 并等待五个运行态服务健康；`docker ps --filter name=moonbox` 显示 Web、backend、MinIO、chat-worker、governance-controller 均已启动，其中 backend、MinIO、chat-worker、governance-controller healthy；`docker exec moonbox-backend ... execution_config()` 返回默认 reasoning=`low`；`localhost:18102` 运行态 bundle 对 `待应用成果`、`查看成果`、`审阅治理成果`、`确认应用` 命中数为 0。

### 2026-09-30 AF-013 所有 AI/assistant 消息满宽

- 反馈摘要：`req-generate` 执行中 assistant 文案仍未占满整行；期望所有 role=assistant / AI 输出不区分命令或状态，外层 block、article、bubble、markdown、TurnActivity 与 status/alert 文案运行态 computed width 均占满消息历史可用宽度，用户消息继续保持右侧气泡限制。
- 证据入口：用户附件 `codex-clipboard-441ae6e3-dbd0-4940-a278-5ad6721fc285.png`；代码路径确认执行中输出来自 `ConversationMessages.tsx` 的 `TurnActivity` 与 `TurnActivity.tsx` 的 `p[role="status"]`，前序满宽断言未覆盖该层级。
- 调整摘要：`chat-workbench.css` 增加 assistant `chat-turn-activity`、直接子层、`status/alert` 文案的 stretch/full-width/box-sizing 规则；`chat-messages.test.tsx` 增加运行中 assistant activity/status computed style 断言；新增 Playwright 宽度采样脚本覆盖 req-generate、bug-generate、普通完成消息和历史恢复。
- 文档同步：已更新 `acceptance-fixes.md`、`tasks.md`、`design.md`、`specs/web-catalog-requirement-center/spec.md`、BUG acceptance 和 Sprint acceptance-report；API、DB schema、权限、部署、安全、对象存储和客户端生成物不适用。
- 验证摘要：`chat-messages.test.tsx` 8 个用例通过；`tests/chat-assistant-width.cjs` 浏览器采样 4 类场景通过，assistant block/article 与 history 同宽，activity/status/bubble/markdown 与 assistant column 同宽，用户气泡仍受限；相邻前端回归 4 个测试文件、145 个用例通过；`tsc --noEmit` 通过。`chat-workbench.test.tsx` 单文件测试池挂起后中断，记录为测试稳定性 warning。

### 2026-09-30 AF-014 Assistant 执行状态条漂浮

- 反馈摘要：工具调用/完成状态条漂在消息正文上方中间，和 assistant 头像及正文左边界脱节；期望状态条作为轻量 meta 左对齐到 assistant 内容列，正文和执行输出继续保持满宽。
- 证据入口：用户附件 `codex-clipboard-fa823727-9f96-406a-b100-223ad91c0d62.png`；代码路径确认 `button.chat-tool-summary` 是工具摘要，`p[role="status"]` / `p[role="alert"]` 才是执行输出。
- 调整摘要：`chat-workbench.css` 将 assistant TurnActivity 子元素满宽规则收敛为 `:not(.chat-tool-summary)`，并让 `chat-tool-summary` 使用 `fit-content`、透明背景与左对齐；status/alert、bubble、markdown 继续满宽。
- 文档同步：已更新 `acceptance-fixes.md`、`tasks.md`、`design.md`、`specs/web-catalog-requirement-center/spec.md`、BUG acceptance 和 Sprint acceptance-report；API、DB schema、权限、部署、安全、对象存储和客户端生成物不适用。
- 验证摘要：`chat-messages.test.tsx` 8 个用例通过；`tests/chat-assistant-width.cjs` 浏览器采样 4 类场景通过，summary left=assistant column left，summary width 小于 column，status/bubble/markdown 仍与 column 同宽。

### 2026-09-30 AF-015 Chat 工作台 NetworkError 裸露

- 反馈摘要：发送 `/req-generate REQ-0027` 后页面显示“正在连接工作台”，随后裸露 `NetworkError when attempting to fetch resource.`；同一会话的 assistant 成功消息仍存在，说明局部网络/轮询失败污染了全局连接态。
- 证据入口：用户附件 `codex-clipboard-2733f99c-b395-4879-8f0c-a6b1583692aa.png`、`codex-clipboard-db0f08c5-8ada-4635-9b1f-e65ddb8b3aed.png`；详细截图对照和代码证据见 `acceptance-fixes.md`。
- 调整摘要：统一包装 `chatRequest`、governance 请求与 events SSE fetch 异常；`NetworkError` / `Failed to fetch` 转中文局部提示，`AbortError` 不渲染错误；turns 与 selected refresh 局部失败不再覆盖全局工作台错误，已生成成功消息保持可见。
- 文档同步：已更新 `acceptance-fixes.md`、`tasks.md`、`design.md`、`specs/web-catalog-requirement-center/spec.md`、`specs/local-project-governance-loop/spec.md`、BUG acceptance 和 Sprint acceptance-report；API、DB schema、权限、部署、安全、对象存储和客户端生成物不适用。
- 验证摘要：Network 聚焦回归 3 个测试文件通过；历史会话局部失败聚焦回归 2 个用例通过；前端 TypeScript build 通过。全四文件 Vitest 集合因既有 `chat-workbench` 轮询定时器未自然退出被中断，已记录为测试稳定性 warning。

### 2026-09-30 AF-016 Assistant 运行中满宽按命令漏测

- 反馈摘要：`req-complete` 执行中 assistant 消息仍未占满整行；验收期望所有 role=assistant 运行中输出不区分 req-generate、req-complete、bug-generate、bug-complete、review、sprint、opsx 或普通 Chat。
- 证据入口：用户附件 `codex-clipboard-2eb05297-c164-4919-bbe1-b01fa5500fd3.png`；运行中输出路径为 `ConversationMessages.tsx` 渲染的 `.turn-assistant` 与 `TurnActivity.tsx` 的 `p[role="status"]`。
- 根因结论：前序满宽回归样本偏向 generate、完成态和历史恢复；通用 `.chat-turn-activity > *` 限宽规则仍未按 assistant 角色隔离，导致非 generate 运行中输出表现像未命中修复。
- 调整摘要：`chat-workbench.css` 将 assistant 外层 block、article、内容列、TurnActivity、status/alert、bubble 与 markdown 均按 `.turn-assistant` stretch/full-width；通用 activity 限宽收敛到非 assistant 消息，用户消息气泡限制保持不变。
- 文档同步：已更新 `acceptance-fixes.md`、`tasks.md`、`design.md`、`specs/web-catalog-requirement-center/spec.md`、BUG acceptance 和 Sprint acceptance-report；API schema、DB schema、权限、部署、安全、对象存储和客户端生成物不适用。
- 验证摘要：`chat-messages.test.tsx` 9 个用例通过；`tsc -b` 通过；Playwright 命令矩阵宽度采样 11 类场景通过、errors=[]，覆盖 req-complete 截图场景、complete/review/sprint/opsx/普通 Chat running、完成态和历史恢复。

### 2026-09-30 AF-017 产品写入命令事实源 stale 门禁

- 反馈摘要：`/req-complete REQ-0027-requirement-center-command-chain-realization` 在产品运行态允许执行，但执行器 `/work` 仅看到旧 `REQ-0027-capture` 且缺少 `requirement.md`；用户要求所有命令产品链路统一修复，而非只修 `req-complete`。
- 证据入口：用户附件 `codex-clipboard-32068244-de58-4910-aae5-0688ce081fba.png`；代码证据为 `prepare_workspace()` 从 committed `HEAD` 初始化 `/work`，旧 `prepare_object_session()` 未检查 executor 可见事实源。
- 根因结论：对象会话链路缺少 generate candidate 的 baseline overlay，也缺少发送前 committed fact source 一致性门禁，导致需求中心事实源未同步时仍可进入执行。
- 调整摘要：`prepare_object_session()` 对 complete、review、sprint、opsx 等写入型对象命令统一执行 stale fact source、完整对象 ID、registry path、trace status 和主文档校验；dirty governance roots 返回 `workspace_fact_source_stale` 且不创建会话，clean 但缺文档或状态不匹配返回 `governance_validation_failed`；`req-explore`、`bug-explore` 和 `open-chat` 保持只读打开。
- 文档同步：已更新 `acceptance-fixes.md`、`tasks.md` 和 BUG acceptance；API schema、DB schema、权限、部署、安全、对象存储和客户端生成物不适用。
- 验证摘要：`uv run pytest src/backend/tests/test_governance_candidates.py -q` 31 个用例通过，覆盖写入型命令矩阵 stale 门禁、只读 explore 例外、缺主文档拒绝和 clean draft 会话创建。

### 2026-09-30 AF-018 workspace_fact_source_stale 提示分层

- 反馈摘要：需求中心点击写入型命令时仍统一提示“确认标准部署已更新”，无法帮助用户判断本地事实源、部署版本或 Git 快照问题。
- 调整摘要：后端 `workspace_fact_source_stale` 错误增加安全 `reason`、`roots`、`categories` 与 `suggested_action`；前端需求中心按原因生成 Toast，显示阻断文件类别和处理建议，缺少 reason 时作为旧部署兜底。
- 文档同步：已更新 `acceptance-fixes.md`、`tasks.md`、BUG acceptance、design、delta specs 与 API 索引；错误详情不记录本机路径、完整对象 ID、文档正文或 Git 输出全文。

### 2026-09-30 AF-019 source_root Git 快照根

- 反馈摘要：产品 backend 的 `governance_root` 是 `/app/governance` 治理投影且不含 `.git`，事实源门禁直接在该目录运行 `git status` 会与 Codex 命令运行在真实仓库的语义不一致。
- 调整摘要：`ProjectScope` 保留治理内容读取根 `governance_root`，并新增 `source_root` Git 快照根；写入型对象命令优先用 `source_root` 校验 `issues/`、`iterations/`、`openspec/`、`docs/`、`rules/` 的 committed 可见性。标准 Chat 部署为 backend 增加 `MOONBOX_CHAT_SOURCE_ROOT` 只读挂载，source_root 不可读时按 `standard_deployment_outdated` 阻断。
- 文档同步：已更新 `acceptance-fixes.md`、`tasks.md`、BUG acceptance、design、delta specs 与部署文档；不新增 API schema、DB schema、权限、安全、对象存储或客户端生成物。

AC-047：专用隔离 SQLite 构造 stopped 评审 + running 旧候选，同一产品 Chat 新 Sprint 轮次 `d5833d7f-d6e3-41fe-8411-d2bfaabcdb97` completed，旧候选与 approved/review 成果保留；因 Sprint 容量硬门禁未纳入。定向验收项 passed；完整诊断 `evidence/acceptance/20261014080837406538-58fc17a0/summary.md` 为 AC-047 passed、其余 51 项 blocked，整体仍 pending。证据见 `evidence/acceptance/inputs/AC-047-review.md`。

AC-045：专用隔离 REQ-0996 同会话 complete→review 两候选与 application 均 applied/verified，后端回写 approved/review 并迁移目录；8 条 plan 删除记录和看板 review.md 入口经隔离服务重启仍可回读。前两次模型 complete 虽 completed 但后端拒绝，事实源未前进；冲突保护由聚焦回归覆盖。定向验收 passed；完整诊断 `evidence/acceptance/20261014082927748188-08201237/summary.md` 为 AC-045 passed、其余 51 项 blocked，整体仍 pending。证据见 `evidence/acceptance/inputs/AC-045-review.md`。

### 2026-10-14 自动验收完成

完整验收 `evidence/acceptance/20261014172956802529-b362b5ea/summary.md` 为 complete/passed，52 项全部通过；readiness 返回 ready、stale=[]。29 项旧缺口以当前命令、真实产品轮次、浏览器 DOM/computed style、隔离文件回读及明确标注的 HTTP/接口夹具证据补齐。AC-040 使用已授权的隔离 REQ-0996 对照对象，正式 REQ-0027 未写入；AC-041 使用隔离 BUG-1001 同会话新轮次，候选与应用 applied/verified，根因 unknown 保持 enriching。共享与隔离 SQLite 分别按验收计划数据源别名读取；工作流同步 `opsx.accept` 已完成，Issue acceptance_status 为 passed。此结论只表示可归档，不执行归档。
