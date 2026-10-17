---
bug_id: BUG-0035-requirement-center-acceptance-readiness-projection
title: 需求中心验收状态与文档持续展示偏差根因分析
status: confirmed
created_at: 2026-10-09 22:41:00
updated_at: 2026-10-09 22:41:00
owner: 产品团队
---

# 需求中心验收状态与文档持续展示偏差根因分析

## 根因状态

status: confirmed

确认范围是需求中心卡片展示与文档清单投影。当前证据没有显示服务端归档门禁失效；BUG-0025 的归档仍被交付证据门禁阻断。

## 现象

BUG-0025 卡片显示研发、测试任务满格及“完成 / 归档”入口，关联 Chat 实际归档却提示验收和交付证据未闭环。已存在的 `acceptance.md` 等 Issue 治理文档在关联 Change 或后续阶段从卡片入口消失。

## 证据链

| id | type | source | 摘要 | 支持的判断 |
|---|---|---|---|---|
| E1 | screenshot | 用户本次对话中的 BUG-0025 卡片与 Chat 归档反馈截图 | 同一对象的任务进度满格，Chat 归档提示 AC-051、AC-052 待真实产品复验及 AF-040 视觉证据不足 | 展示的任务完成度不能代表归档门禁通过；原图未复制到仓库 |
| E2 | code_path | `src/backend/app/services/requirement_center.py`：`_build_issue`、`_display_document_names` | 验收中卡片的研发/测试进度取 Change `tasks.md` 分类结果，`manual_acceptance_count` 固定为 0；关联 Change 有文档后优先返回 Change 清单，仅特例保留 Issue `trace.md` | 待验收事实未进入卡片，Issue 文档被替代 |
| E3 | reproduction | 在 `src/backend` 使用 `.venv/bin/python` 对 `_display_document_names` 构造临时 Issue 与 Change | Issue 实有 `acceptance.md`、`trace.md`，Change 实有 `tasks.md`、`trace.md`；`applied` 返回 `['tasks.md', 'trace.md']`，`acceptance_present=False` | 相同触发条件可稳定复现 Issue 验收文档入口丢失，不依赖真实数据 |
| E4 | code_path | `src/web/src/pages/catalog/RequirementCenterPage.tsx`：`stageVisibleDocs`、`visibleIssueDocuments`、`canArchive` | 阶段白名单过滤已提供的文档；后续阶段未列入 `acceptance.md` 等 Issue 文档；`canArchive` 仅看测试进度与人工验收待办数 | 前端再次隐藏文档，且无法利用后端固定为 0 的待办数识别实际待验收 |
| E5 | test_failure | `src/web/src/requirement-center.test.tsx` 的阶段过滤用例 | 用例明确断言已提供的 `acceptance.md` 在 capture 卡片不可见；本轮运行被 Node 25 / Vitest 的 localStorage 初始化错误阻断，未进入业务断言 | 隐藏是现有产品约定；本轮不把测试文件本身当成已通过的运行回归 |
| E6 | reproduction | `src/backend` 下 `uv run pytest tests/test_governance_board.py -q -k 'trace_always_targets_issue or missing_issue_trace'` | 23 项通过，确认 Issue trace 在各阶段指向 Issue，缺失时不能借用 Change trace | 同名文档的来源必须保持明确，不能靠合并名称覆盖 |

## 已排除假设

| 假设 | 排除证据 |
|---|---|
| 只因 `acceptance.md` 不存在而未显示 | E3 的 Issue 文件实际存在，返回清单仍无该文档 |
| 研发、测试满格证明验收已通过 | E1 的真实归档反馈仍列出待复验和缺证据；E2 的进度只读取任务分类 |
| 仅前端隐藏导致文档入口丢失 | E3 表明后端在关联 Change 后已经丢失 Issue 文档；E4 是第二层过滤 |
| 已确认服务端归档错误放行 | E1 观察到服务端阻断；当前无错误放行证据 |

## 已确认根因

需求中心把“任务完成度”“验收结果”“归档准备”投影为不同且未对齐的数据：卡片进度从 `tasks.md` 推导，验收待办数未从验收事实计算而固定为 0，归档入口只做简化前端判断；Chat 归档执行独立交付证据门禁，因此出现卡片可操作而归档被阻断。文档入口使用阶段白名单，且后端在关联 Change 后用 Change 文档替代 Issue 文档；两层过滤让已生成的治理 MD 随阶段消失。

## 修复方向

- 保留 `tasks.md` 作为研发与测试任务进度来源；建立独立、可追溯的验收状态投影，区分 AC 标准、验证结果、人工复验与证据缺口，不把 AC 无差别计入任务分母。
- 卡片归档提示消费与服务端归档门禁一致的阻断摘要；任何前端提示都不能替代服务端最终校验。
- 从当前授权对象聚合真实存在的 Issue、关联 Change 与 Sprint 治理 MD，生成后在后续阶段持续可达；同名文档按来源分组并指向正确路径。保持现有读取权限与分阶段写权限，归档后只读展示，不伪造不存在文件。

## 验证闭环

已完成：E3 合成复现、E6 后端 23 项聚焦回归、E1 用户提供的实际归档反馈与 E2/E4 代码路径相互印证。待修复后以验收文档逐项验证多阶段文档入口、权限、同名来源、验收状态与实际归档阻断一致。前端聚焦用例当前因 Node 25 / Vitest localStorage 初始化错误未运行到断言，该环境问题需在实现验证时单独处理；不影响上述代码路径和合成后端复现结论。
