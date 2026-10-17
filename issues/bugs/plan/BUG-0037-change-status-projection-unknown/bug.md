---
bug_id: BUG-0037-change-status-projection-unknown
title: 需求看板将端口迁移 Change 误判为状态异常
status: pending_review
created_at: '2026-10-11 10:08:57'
updated_at: 2026-10-11 10:12:48
severity: medium
owner: MoonBox 产品团队
discovered_at: '2026-10-11 09:51:50'
environment: local Docker；Firefox；/requirements
related_requirement: REQ-0012-frontend-requirement-center
related_change: null
product_data_collection_observability:
  status: applicable
  affected_layers: [web, governance_context_api, request_logs]
  reason: 看板诊断展示与治理上下文状态投影需要一致；若扩展 API 诊断字段，需遵守既有请求日志与脱敏边界。
  validation: 核对响应诊断原因、页面可见性、请求关联和敏感信息不外泄；是否新增协议字段在 Change 设计阶段确认。
---

# 需求看板将端口迁移 Change 误判为状态异常

## 现象与复现

1. 在本地 Docker 产品的 Firefox 浏览器打开 `/requirements` 并刷新。
2. 看板显示“数据异常 · 1 项”；展开后列出 `migrate-local-host-ports-to-39000-range`，仅解释为“状态或归档版本存在歧义”。该 Change 不显示为普通卡片，也不计入“独立 Change”与“全部对象”统计。
3. 当前仓库中该 Change 是唯一活动目录，归属 `sprint-009`；`tasks.md` 为 4/4，但 `trace.md` Frontmatter 缺少 `status` 和 `execution` 生命周期事实。

## 期望与实际

| 场景 | 期望 | 实际 |
|---|---|---|
| 状态投影 | 依据经过验证的 Change 生命周期事实展示阶段；缺事实时明确标注待核实，不推断完成 | 后端投影为 `unknown`，前端将对象排除卡片和统计 |
| 异常解释 | 显示具体原因、对象身份、事实源和可执行核对入口 | 所有 `unknown` 共用“状态或归档版本存在歧义”，用户无法区分字段缺失、非法 schema 或身份冲突 |
| 安全与进度 | 任务完成数与生命周期状态分开展示；无完成事实时禁用依赖完成态的动作 | 异常区无法看到任务 4/4 与 Sprint 归属，也没有受控核对入口 |
| 后续创建及同步 | Change 创建、apply、modify、archive 事件持续写入可识别的状态事实，避免同类记录再被隐藏 | 该历史 Change 缺少状态事实；同类写入链路与历史数据治理仍需验证 |

## 影响范围与严重度

严重度初判 `medium`：独立 Change 从常规看板和统计中消失，诊断信息不足，可能误导迭代交付判断；目前没有数据丢失、越权或错误归档的证据。影响面包括治理上下文读取、Change 状态投影、看板诊断与统计、Change 生命周期写入和历史记录核对。与 BUG-0038 的 Sprint 总览缺失分别闭环。

## 根因状态与证据

当前仓库样本的根因判断为 `confirmed`；运行容器是否读取同一治理快照仍为 `unknown`，不得将本地证明扩展为运行服务文件事实。

| 证据 | 来源 | 可复核结论 |
|---|---|---|
| 页面复现 | 2026-10-11 本地 Firefox `/requirements` 刷新后的可见页面 | 产品持续显示该 Change 的数据异常并排除普通卡片 |
| 治理事实 | `openspec/changes/migrate-local-host-ports-to-39000-range/trace.md`、`tasks.md`、`iterations/change/sprint-009/sprint.yaml` | 当前仓库 trace 无 `status`/`execution`；任务 4/4；唯一 Sprint 归属为 `sprint-009` |
| 聚焦读取 | 使用项目后端虚拟环境以 `ChangeIndex` 只读加载当前仓库 | `stage=unknown`、`source_kind=active`、实体目录数 1、`sprint_id=sprint-009`；说明本地样本不是归档身份冲突 |
| 代码路径 | `src/backend/app/governance/change_index.py` 与 `src/web/src/pages/catalog/RequirementCenterPage.tsx` | 缺状态事实时索引映射到 `unknown`；前端将 `unknown` 排除卡片和统计并显示统一文案 |

## 产品修复要求与建议验收

1. 治理上下文为异常 Change 提供稳定、可测试的原因码及安全摘要，至少区分生命周期事实缺失、执行 schema 无效、活动与归档身份冲突；不得把所有原因合并成一条通用提示。原因摘要不暴露本机路径、密钥或文档正文。
2. 看板保留授权用户可访问的异常对象入口，展示 ID、标题、当前可证实的来源、Sprint 归属、任务进度及待核实原因。异常数与正常阶段统计分别标明；不把 `unknown` 强行计为 proposed、applied 或 done。
3. 提供从产品进入的只读核对和受控恢复路径：展示相关 `trace.md`、`tasks.md` 与 Sprint 关联；只有取得可信执行事实并通过权限、版本和幂等校验后，才允许通过正式治理流程补齐状态。无法确认时保留待核实，不靠任务勾选或 Sprint 摘要自动认定 `applied`。
4. 检查 Change 创建及 `opsx.start`、`opsx.apply`、返修、归档的写入链路，保证新生成记录具有受支持的生命周期 schema，且已完成执行事实不会被返修状态覆盖。对历史缺事实记录提供一次性受控核对，不要求用户直接编辑仓库 Frontmatter。
5. 回归覆盖缺事实、非法 schema、重复归档身份、正常独立 Change、来源于 REQ/BUG 的 Change，以及无权读取对象；异常对象可诊断但无权对象不得泄露。状态恢复后应自动回到正确看板阶段、更新计数并保留诊断追溯。

## 待补证与边界

- 运行服务实际读取的治理根目录、目标 Change `trace.md` Frontmatter、上下文接口中该对象的 `stage`、`source_kind`、Sprint 关联及诊断字段仍需在同一请求范围内核对。当前页面刷新只能证明可见结果，不能证明运行容器内的文件内容。
- 需要复查产品内 Change 创建和执行完成的真实写入路径，判断状态事实缺失是历史数据迁移、命令未同步还是运行快照版本差异。未经该核对，不将某一写入命令认定为已确认根因。
- 对这条历史 Change，`tasks.md` 4/4 和 Sprint 摘要中的 `applied` 仅为核对线索；不能代替有时间和来源的执行完成事实。
