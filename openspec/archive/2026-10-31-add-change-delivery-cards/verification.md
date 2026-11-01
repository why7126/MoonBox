---
title: 需求中心独立交付卡片实施验证
---
# 需求中心独立交付卡片实施验证

## 交付结果

前期保留 Issue，交付按 Change 唯一成卡；标题、历史 Sprint、任务、文档、独立估算与验收均取自身。完整来源可追溯，统计去重，不写回旧交付事实。阶段操作绑定当前 Change 会话并持久化来源；执行权限、版本与恢复再次校验。

## 验证与边界

- 后端卡片/ACL/文档/写入回归169项通过；最终权限与执行扩大回归155项通过、1项需显式CHAT_LIVE_PROBE授权的旧入口跳过（本轮另做固定镜像真实隔离观察）、21个子测试通过。另有早期执行保护/观测等回归，具体最终自动验收以 manifest 为准，不将重叠批次相加。
- 前端146项通过，TypeScript与Vite构建通过；抽屉焦点与窄屏溢出发现后均在当前 apply 修复并复验。
- 真实产品：用户登录后核对 REQ-0056 与 REQ-0048。REQ-0048 当前实际为两张已完成历史交付，分别保留 sprint-016、sprint-015；第二张 tasks.md 定位正确。旧问题截图不是当前状态依据。
- 真实隔离执行：固定容器镜像中执行 synthetic-alpha，主动停止；同目标成果待核对时重试409；改绑 synthetic-beta 后原轮次重试409 delivery_target_mismatch。只有1个实际轮次，alpha执行标记存在、beta无标记。见 observations/interruption-target.json。此为真实执行器上的合成业务样本，不是正式业务交付或成功续接签认。
- 四类权限×两主题×两视口共16组卡片证据，以及任务/交付验收/来源验收/返修/归档浮层20组证据、历史筛选8组证据。浏览器为Codex侧边浏览器；实际组件，合成只读响应不发起业务写入。目视与样式采样确认身份可读、浮层不越界、只读禁用、受限隐藏。真实管理员页面观察单独存 product-*。
- 测试执行器首次版本不匹配、原生入口缺固定镜像能力均在启动前阻断；随后在登记的固定镜像中取得观察。临时run f9e2114b28674e8da66351b936ca6970已cleanup并check：容器0、网络0，所有一次性本机服务及测试目录清理。
- 自动验收界面入口暂不支持明确目标，按AC-015禁用并解释；CLI验收不受此按钮限制。没有数据库迁移、部署参数或对象存储变化；API增加兼容字段，生成客户端及API索引已同步。安全影响为目标/来源联合授权及执行权限校验收紧，未增加用户角色权限。

## 最小入口矩阵

| 入口 | 事实与环境 | 正向/拒绝及证据 |
|---|---|---|
| 看板/文档 | 当前源仓库、真实本地产品API；Change trace和来源注册表 | 自身历史Sprint及兄弟文档；product-*截图、delivery_cards回归 |
| 准备/幂等 | primary Change、完整来源命令、持久baseline/journal | 改目标拒绝、旧来源多Change拒绝；execution_guard及delivery_cards |
| 执行权限 | 当前Sprint成员、来源/Change ACL、阶段 | 可写范围及失效拒绝；permission_governance_contract及delivery_cards |
| 中断/恢复 | 独立临时仓库+真实固定镜像 | alpha运行停止，beta重试拒绝；interruption-target.json |
| 完成/归档 | 当前Change验证来源、工作流及验收计划 | 仅同步apply并自动验收；未经授权不实际归档 |

## 逐项证据映射

| AC | 主要证据 |
|---|---|
| AC-001～003、018 | test_delivery_cards、test_change_visibility、test_governance_board：前期、共享来源、缺失冲突、活动/归档唯一性与ACL |
| AC-004～006、010 | 历史Sprint固定样本、source详情、历史哈希不变；history-*、product-req0048-* |
| AC-007、017 | test_governance_writer/version/幂等、直接API越权拒绝；test_permission_governance_contract |
| AC-008、011～013 | delivery-cards/object-chat-entry/requirement-center前端回归；兄弟目标、迟到响应、来源搜索、去重、独立估算 |
| AC-009 | 自身计划证据不借用来源或任务；overlay-acceptance-*与overlay-source-* |
| AC-014、015、020 | delivery-action、目标会话校验；overlay-modify-*、overlay-archive-*；自动验收禁用 |
| AC-016 | 持久baseline与重试拒绝回归；真实中断及错误目标拒绝观察（不声称成功续接） |
| AC-019 | 16组角色/主题/视口，overlay-styles.json；任务焦点、关闭焦点及窄屏全文 |
| AC-021 | 行为/请求/Task Trace metadata受控字段，直接API不伪造行为、遥测降级回归 |
| AC-PROTOTYPE-001/002 | design契约及evidence/skeleton/desktop-1440.png；用户已确认骨架 |
| AC-PROTOTYPE-003/005 | evidence/acceptance/ui角色、历史、浮层、computed style；修复后重采 |
| AC-PROTOTYPE-004、AC-XCUT-004 | PRD/故事/流程/acceptance/trace/context最终一致性；原型静态示例与真实事实分开 |
| AC-XCUT-001～003 | 同源历史文件哈希不变、partial独立、容量事实不修改、未知估算不填零 |

## 视觉签认

本轮已目视核对桌面卡片及窄屏长身份换行、两层验收抽屉、阶段确认和筛选浮层；computed style确认桌面卡片radius11px、padding15px 16px 18px，深浅主题使用既有token。窄屏卡片266px且文档标签换行；抽屉390px、确认342px无越界。可写/只读/受限差异与16组DOM结果一致。此签认仅为实现视觉自检，不替代用户业务签认。

## 最终验收与用量

30项验收通过；运行20261031182048982884-f75aa82a，完整清单，无失败、受阻或待采集。实际回归命令2次，同轮去重28项；证据readiness为ready，归档副本预演通过。实现/验收AI Usage分别回填sprint-018；隔离产品观察轮次报告actual_tokens为75,424，仅代表该产品测试轮次，不与本命令总用量混算。未正式归档、提交或推送。


## 最终归档门禁阻塞

本次30/30项验收通过，证据就绪，临时副本归档预演通过；最终共享归档门禁未通过，不能宣称可归档。`--archive-readiness` 返回 `acceptance_source_invalid`，直接调用保护规则检查定位为 `incomplete_archive_history`。

受影响历史来源：
- `2026-08-13-add-requirement-center-real-data-integration`：trace为applied，但缺少execution.completed_at。
- `2026-09-04-update-requirement-center-card-document-actions-ai-chat`：trace仍为in_progress。

两者与本次规格修改存在相同条目，当前completed_archive检查不认可其完成事实。未修改历史档案、未绕过门禁、未实际归档。本次保留applied及验收passed；后续需独立核实上述历史归档事实后，再执行本REQ的opsx-accept增量复核。此问题不改变本次实现和逐AC证据结论。

## 历史核实后验收结果
2026-10-31：两份历史Change的归档事实已核实并仅更正trace状态；增量规格全文已纳入验收输入。此前历史记录与规格覆盖阻塞已消除。最新运行20261031193424806046-3530fd99：30/30通过，2次命令执行、同轮去重28项，失败/受阻/待采集均0；证据ready及副本预演通过。Workflow Sync与AI Usage收尾成功；本轮最终共享归档准入为ready，recovery_reason为空。不实际归档。历史修正依据见evidence/acceptance/history-verification/status-correction.json。
