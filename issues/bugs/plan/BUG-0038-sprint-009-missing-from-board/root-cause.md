---
bug_id: BUG-0038-sprint-009-missing-from-board
title: 需求看板未显示已存在的 sprint-009 迭代根因分析
status: probable
created_at: '2026-10-11 10:12:00'
updated_at: '2026-10-11 10:12:00'
owner: MoonBox 产品团队
---

# 需求看板未显示已存在的 sprint-009 迭代根因分析

## 根因状态

status: probable

当前证据可确认页面与本仓库存在对象身份错位，但尚不能确认运行服务的绑定目录、源目录和快照版本中哪个环节造成错位。

## 现象

本仓库 `sprint-009` 处于 `planning`；Firefox 刷新 `/requirements` 后看板仍显示 Sprint 8/8，页面中的 `BUG-0038` 标题也与本仓库不同。

## 证据链

| id | type | source | 摘要 | 支持的判断 |
|---|---|---|---|---|
| E1 | data_sample | `iterations/change/sprint-009/sprint.yaml` | `sprint_id: sprint-009`、`status: planning` | 当前仓库有可列入的规划迭代 |
| E2 | reproduction | 2026-10-11 Firefox `http://localhost:39002/requirements` 重新加载后的可见页面 | 页面完成同步后显示 Sprint 8/8；短 ID `BUG-0038` 为“隔离版本冲突与重试验收夹具” | 刷新后页面数据与本仓库身份不一致；服务当前可访问 |
| E3 | code_path | `src/backend/app/governance/reader.py`、`src/backend/app/governance/scope.py` | 请求读取已授权项目绑定的治理目录快照，并在该快照内解析需求中心 | 必须核查运行绑定及快照，不能仅以工作目录推断页面来源 |
| E4 | code_path | `src/backend/app/services/requirement_center.py` 中 Sprint 列表与指标函数 | 扫描治理根目录的 `iterations/change` 与 `iterations/archive`；`planning` 不被排除 | 若运行快照确有该文件，常规状态过滤不会使其消失 |

## 已排除假设

| 假设 | 排除证据 |
|---|---|
| 当前仓库不存在 `sprint-009` | E1 |
| 前端只因页面未刷新而显示旧指标 | E2：重新加载并等待显示“已同步”后仍为 8/8 |
| `planning` 状态被现有后端 Sprint 列表主动排除 | E4 |

## 待验证根因

最可能是当前页面所选项目绑定的治理目录与本仓库不同，或该绑定目录的投影、快照尚未包含本仓库新增内容。E2 中同短 ID 对应另一对象强化数据来源错位判断，但无法区分绑定选择错误、挂载旧内容和快照陈旧。不得据此宣称已确认具体部署根因。

## 修复方向

产品需让用户辨认所选项目和治理事实源，展示可核对的快照修订与同步时间，并在绑定错误、源投影过期或快照不一致时给出明确错误与恢复入口。统计、筛选选项和对象卡片必须来自同一授权快照；不得用前端硬编码补单个 Sprint。

## 验证闭环与证据缺口

已尝试仓库文件核对、Firefox 页面刷新和服务代码链路定位；容器 API 访问被拒，未能读取运行容器绑定。需要在已授权的运行环境取得：当前 `space_id`、`repository_id`、绑定修订或脱敏来源标识、上下文响应的 `snapshot_revision` 和 Sprint 字段，以及绑定目录下 `sprint-009/sprint.yaml` 是否存在。只需这些字段和布尔结果，不返回完整路径、凭证、Cookie、请求头或客户数据。对照三者后，才能确认具体触发条件，并用同一环境的刷新结果验证修复。
