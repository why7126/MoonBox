---
bug_id: BUG-0037-change-status-projection-unknown
title: 需求看板端口迁移 Change 状态异常根因分析
status: confirmed
created_at: '2026-10-11 10:12:03'
updated_at: '2026-10-11 10:12:03'
---

# 需求看板端口迁移 Change 状态异常根因分析

## 根因状态

status: confirmed

确认范围：当前仓库中端口迁移 Change 的状态投影与产品看板排除逻辑。运行容器是否读取完全相同的治理快照尚未直接确认；不能据此认定运行容器内的具体文件版本或造成原始状态缺失的写入命令。

## 现象

Firefox 刷新本地 `/requirements` 后，`migrate-local-host-ports-to-39000-range` 持续列在“数据异常”，普通卡片与统计中均不可见。异常文案只称“状态或归档版本存在歧义”。

## 证据链

| id | type | source | 摘要 | 支持的判断 |
|---|---|---|---|---|
| E1 | reproduction | 2026-10-11 本地 Firefox `/requirements` 刷新、展开“数据异常” | 页面仍列出目标 Change，独立 Change 统计不含该对象 | 证明当前产品可见症状持续存在；不单独证明容器文件版本 |
| E2 | data_sample | `openspec/changes/migrate-local-host-ports-to-39000-range/trace.md`、`tasks.md`、`iterations/change/sprint-009/sprint.yaml` | 当前仓库 trace 无 `status` 与 `execution`，任务 4/4，Sprint 变更清单包含该 Change | 支持生命周期事实缺失；任务进度与 Sprint 摘要不可充当完成事实 |
| E3 | reproduction | 项目后端虚拟环境，`PYTHONPATH=src/backend src/backend/.venv/bin/python` 只读构建 `ChangeIndex(Path.cwd())` | 返回 `stage=unknown`、`source_kind=active`、实体版本 1、`sprint_id=sprint-009`，trace status 为 null 且无 execution | 在当前仓库相同输入下稳定得到目标异常状态，排除本地样本的重复归档身份和 Sprint 归属歧义 |
| E4 | code_path | `src/backend/app/governance/change_index.py` 的活动 Change 状态映射 | 仅从 trace 的 `status` 或受支持的 `execution` 取得阶段；缺失时映射为 `unknown` | 解释 E2 输入到 E3 输出的条件分支 |
| E5 | code_path | `src/web/src/pages/catalog/RequirementCenterPage.tsx` 的 `filteredIssues`、`diagnosticIssues` 与异常区 | `unknown` 从卡片和统计中剔除，异常区使用统一文案且无对象入口 | 解释 E3 输出如何形成 E1 的产品表现，以及用户无法自助核对的原因 |

## 已排除假设

| 假设 | 排除证据 |
|---|---|
| 当前仓库中该 Change 因多个归档版本而无法唯一识别 | E3 显示唯一活动目录，`source_kind=active`、实体版本 1 |
| 当前仓库中该 Change 没有有效 Sprint 归属 | E2、E3 均显示 `sprint-009` 关联 |
| 任务 4/4 可以安全证明执行已完成 | `tasks.md` 只记录进度；`ChangeIndex` 明确不将任务勾选作为生命周期完成事实，E3 仍为 `unknown` |
| 仅刷新缓存即可恢复 | E1 是刷新后的页面，异常仍存在；仍需核对服务端数据源与生命周期事实 |

## 已确认根因

当前仓库的历史 Change trace 缺少产品状态投影所要求的生命周期事实；后端对这种输入返回 `unknown`。前端又把 `unknown` 对象从普通卡片及统计中移除，异常区未传达具体缺失字段、可证实的任务进度与治理文档入口。两层机制叠加，使已存在的 Change 在产品中近似“消失”。

原始状态字段为何未写入，以及运行容器绑定的治理快照是否与当前仓库一致，仍需在修复设计和真实环境验收中核查；不把它们写成已确认根因。

## 修复方向

1. 治理读取端输出具体、安全的异常原因与来源摘要；对缺状态事实、无效 schema、身份冲突分别处理。异常对象可被授权用户查看，但不进入未经确认的正常阶段或完成统计。
2. 产品提供只读核对入口及受控恢复动作。恢复必须基于可信执行事实，经过权限、版本、幂等和审计检查；不得从任务 4/4 或 Sprint 文字摘要自动写出 `applied`。
3. 检查新 Change 创建、执行启动、首次 apply、返修和归档的状态写入契约，并用回归测试防止再次产生无法识别的 trace；历史记录按受控迁移或人工核对处理，不要求用户手改 Frontmatter。

## 验证闭环

已完成：E1 浏览器页面复现、E2 当前仓库样本核查、E3 后端实际只读投影、E4/E5 代码路径复核。后续实现验收需在目标运行环境核对治理根目录和上下文响应，对正常与异常 Change、来源 Change、权限隔离和状态恢复前后统计做真实页面回归；同一请求关联的诊断不得泄露绝对路径、文档正文或凭证。
