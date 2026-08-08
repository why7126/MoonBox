---
purpose: iterations Sprint 生命周期阶段目录规范
content: change / archive 两阶段目录职责、准入条件、迁移时机与路径解析
source: 项目团队确认
update_method: Sprint 流程或目录边界变化时同步更新
created_at: 2026-06-27 23:45:00
updated_at: 2026-08-07 00:00:00
note: 与 issues plan/review/archive 互补；机器索引仍为 sprint.yaml
---

# iterations 生命周期阶段目录

## 1. 目标

在 `iterations/` 下，用 **change / archive** 两目录表达 Sprint 在「迭代进行中 → 归档闭环」中的物理位置，与 `sprint.yaml` 的 `status` 互补：

- **status**：逻辑状态机（`planning`、`in_progress`、`completed`）
- **lifecycle_stage**（物理目录）：`change` | `archive`

## 2. 目录结构（MUST）

```text
iterations/
├── README.md
├── change/                    # 未归档：规划中或开发中
│   └── sprint-xxx/
│       ├── sprint.yaml
│       ├── sprint.md
│       ├── release-note.md
│       └── acceptance-report.md
└── archive/                   # 已完成归档
    └── sprint-xxx/
        └── （同上四件套）
```

- 每个 `sprint-xxx/` 目录 **MUST** 仅存在于 `change/` 或 `archive/` 之一（不得多份拷贝）。
- 阶段子目录内 **禁止** 再嵌套 `change/archive`。
- 四件套规范见 `rules/document-governance.md` §4.1。
- Sprint ID **MUST** 使用 `sprint-xxx` 三位数字递增格式，例如 `sprint-002`；不得使用日期、主题词或混合命名作为 Sprint ID。

### 2.1 Sprint 自动编号（MUST）

- 当当前没有 `iterations/change/sprint-xxx/` 进行中迭代，且命令需要为 active Change 自动创建 Sprint 时，系统 MAY 自动创建下一个 Sprint。
- 自动创建时 MUST 扫描 `iterations/archive/` 与 `iterations/change/` 下符合 `sprint-[0-9]{3}` 的目录和 `sprint.yaml:sprint_id`，取最大编号加一；例如最新归档为 `sprint-001` 且无进行中迭代时，新建 Sprint MUST 为 `sprint-002`。
- 自动创建 Sprint MUST 落在 `iterations/change/sprint-xxx/`，四件套中的 `sprint_id`、标题、路径引用、Workflow Sync、AI Usage 和校验命令 MUST 使用同一个规范编号。
- 如果已存在 `iterations/change/sprint-xxx/` 进行中迭代，MUST 优先复用或要求用户明确选择；不得默认另建并行 Sprint。
- 若发现新建 Sprint 使用了非规范名称，MUST 立即重命名为自动编号结果，并同步所有引用与校验记录。

### 2.2 遗留扁平路径（兼容）

历史 Sprint 可能仍在：

```text
iterations/sprint-xxx/   # 遗留，deprecated
```

- 工具链 **SHOULD** 继续可读遗留路径（见 `scripts/workflow_sync/collect.py` 的 `resolve_sprint_dir()`）。
- 新建 Sprint **MUST** 落在 `change/` 下，**MUST NOT** 在 `iterations/` 根下新建 `sprint-*`。
- 批量迁移时使用 `scripts/migrate-iterations-lifecycle-stage.py`。

## 3. 两阶段定义

| 阶段目录 | 含义 | 典型 sprint.yaml `status` |
|---|---|---|
| **change** | **未归档**：迭代规划、开发、验收进行中 | `planning`、`in_progress` |
| **archive** | **已完成归档**：Sprint 内 Change 已全部 `/opsx-archive`，迭代验收与发布说明已收尾 | `completed` |

`planning` 是 `/sprint-propose` 成功后的正式 Sprint 状态，表示范围已纳入但尚未批量执行；它 **不是** “没有启动 Sprint”。只要 Sprint 四件套已落在 `iterations/change/<sprint>/` 且范围、Issue trace、Change trace 已同步一致，`/opsx-apply` MUST 允许解析并执行该 planning Sprint 中的 Change。

## 3.1 Sprint 容量门禁（MUST）

`/sprint-propose` 在生成正式四件套或更新 REQ/BUG/Change trace 前 MUST 计算候选范围的容量占用率：

```text
capacity_usage = estimated_person_days / capacity_person_days
```

- 若容量或估算缺失导致无法计算，MUST 先补齐输入；不得默认通过。
- 当 `estimated_person_days > capacity_person_days * 1.2` 时，MUST 硬阻断正式规划：不得创建 `iterations/change/<sprint>/` 四件套，不得更新 `trace.md` 的 `iteration` 或 Change trace，并提示拆分 Sprint、移出低优先级项或替换范围后重新运行 `/sprint-propose`。
- 当 `capacity_person_days < estimated_person_days <= capacity_person_days * 1.2` 时，MAY 继续生成 Sprint，但 MUST 在 `sprint.md` 记录容量风险、fix 缓冲影响和延后项建议。
- 当 `estimated_person_days <= capacity_person_days` 时，按既有 Review Gate、Readiness Gate 和 Scope 规则继续。
- 已存在 Sprint 追加或修正正式范围时，MUST 先用 `python scripts/add-sprint-scope-item.py --sprint <sprint-id> [--req <REQ-id>|--bug <BUG-id>] [--change <change-id>] ...` 更新 `sprint.yaml` 机器事实源，再运行 Workflow Sync 派生刷新人读文档；不得只手工编辑 `sprint.md`、Issue trace 或 Change trace。
- 多个范围项写入同一 `sprint.yaml` 时，MUST 串行执行，禁止并行写入同一个 Sprint scope。
- `/sprint-propose` 写入或更新范围后，MUST 运行 `python scripts/validate-sprint-scope.py <sprint-id> [--item <REQ|BUG|change-id>]`，确认新增或更新项出现在 `sprint.md` `## 2. Scope` 主表和 workflow-sync 派生表；该校验失败时必须修复后重跑，不得仅以 `sprint.yaml` 或 trace 一致作为完成依据。
- `sprint.md` `## 2. Scope` 主表 SHOULD 使用六列：`类型 | 编号 | 标题 | 状态 | 估算 | 说明`。派生表可按 requirements / bugs / changes 分组，但主表不得用 `范围项` 窄表替代。

`/sprint-propose` 一旦通过门禁并生成正式四件套，MUST 立即执行 Workflow Sync，将正式纳入的 REQ/BUG `trace.md` 同步为 `status: in_sprint` 与 `iteration: <sprint-id>`；不得留下 `approved + iteration` 的半纳入状态。

## 3.2 opsx-apply 迭代纳入门禁（MUST）

`/opsx-apply <change-id>` 对来源于 REQ/BUG 的 Change 执行前，目标 Change **MUST** 已纳入某个 `sprint-xxx` 正式范围。门禁判定以 Sprint 四件套与 Issue trace 双向一致为准：

- `iterations/change|archive/<sprint>/sprint.yaml` 的 `changes[]` MUST 包含 `<change-id>`。
- 若 Change 关联 REQ，`requirements[]` MUST 包含对应 `REQ-*`；若关联 BUG，`bugs[]` MUST 包含对应 `BUG-*`。
- 关联 REQ/BUG `trace.md` MUST 存在 `iteration: sprint-xxx`，且状态为 `in_sprint` 或后续交付态。
- `python scripts/sync-workflow-status.py --event opsx.apply --change <change-id> --sprint auto --dry-run` 或等价解析 MUST 能定位到该 Sprint；若报告 sprint skipped / unresolved，MUST 停止 `/opsx-apply`。
- 若解析到的 Sprint 为 `status: planning`，仍视为通过迭代纳入门禁；不得要求额外 `/sprint-apply` 或手工“启动 Sprint”后才允许 `/opsx-apply`。
- 若 REQ/BUG 已在 Sprint 中但创建 Change 时 `changes[]` 尚未回填，MUST 先运行对应 `/req-opsx` 或 `/bug-opsx` 的 Workflow Sync，确保 `changes[]` 与 `scope_estimates[].change` 同步后再 apply。
- 若 `/sprint-propose` 声称已纳入 REQ/BUG/Change，但 `/opsx-apply --dry-run` 仍报告无法解析 Sprint scope，根因优先按 `sprint.yaml` 机器事实源缺失处理；不得要求用户重复口头确认同一纳入动作。

未通过时的修复路径：先运行 `/sprint-propose` 将 REQ/BUG/Change 纳入 `iterations/change/<sprint>/`，完成 Workflow Sync 后再重新执行 `/opsx-apply`。

## 4. 目录迁移时机（MUST）

AI 在执行下列命令并成功后 **MUST** 移动目录（`git mv` 或等价），并更新 `sprint.yaml` 的 `lifecycle_stage`：

| 事件 | 命令示例 | 自 → 至 |
|---|---|---|
| 新建 Sprint | `/sprint-propose` | — → `change/` |
| 迭代归档闭环 | `/sprint-archive`（`status: completed`） | `change/` → `archive/` |

**不迁移**：

- 仅 `/sprint-explore`、`/sprint-apply` 进行中 → 保留在 `change/`
- 单 Change `/opsx-archive` → Sprint 目录 **不** 单独迁移（整 Sprint 归档时一并迁移）

迁移后 **SHOULD** 运行 `python scripts/sync-workflow-status.py --check`。

## 5. sprint.yaml 字段

阶段目录变更时，在 `sprint.yaml` 中维护：

```yaml
lifecycle_stage: change | archive
```

`status` 与 `lifecycle_stage` **SHOULD** 一致：

- `planning` / `in_progress` → `change`
- `completed` → `archive`

`sprint.md` 的变更记录 **SHOULD** 记录迁移，例如：`change → archive（/sprint-archive）`。

## 6. 路径引用

- 文档与脚本引用时使用完整路径，例如：
  `iterations/change/sprint-003/` 或 `iterations/archive/sprint-002/`
- Workflow Sync、Sprint 命令 **MUST** 通过 `resolve_sprint_dir()` 解析路径，**禁止** 硬编码仅根目录扁平路径。

## 7. 与 issues / OpenSpec 关系

| 层级 | 职责 |
|---|---|
| `iterations/change/` | 当前或规划中的 Sprint 四件套 |
| `iterations/archive/` | 已结束 Sprint 四件套（历史保留） |
| `issues/*/review/` | 已评审、开发中 REQ/BUG |
| `openspec/changes/` | 进行中的 Change |
| `openspec/archive/` | 已归档 Change |

Sprint 归档 **MUST** 在 `/sprint-archive` 时同步：Change → `openspec/archive/`，关联 REQ/BUG → `issues/*/archive/`（若尚未迁入）。
Sprint close / `/sprint-archive` 前 MUST 执行 readiness 复核：

```bash
python scripts/validate-sprint-archive-readiness.py --sprint <sprint-id>
python scripts/generate-sprint-fact-sheet.py --sprint <sprint-id> --summary
python scripts/check-sprint-close-stale-scan.py --sprint <sprint-id>
```

复核必须确认 Sprint 四件套中不存在与真实 Issue/Change 生命周期冲突的“待 `/req-opsx` / `/bug-opsx` / `/opsx-apply`”、`proposed`、`applied` 等中间态文案，以及作为 canonical archive path 的 `openspec/changes/archive/` 旧路径引用。

## 8. AI 检查清单

```text
□ 新建 Sprint 是否落在 change/ ？
□ sprint-archive 后是否迁入 archive/ ？
□ sprint.yaml 是否更新 lifecycle_stage ？
□ 路径引用是否使用 change/ 或 archive/ 前缀？
□ 是否确认 sprint.md Scope 主表、workflow-sync 派生表与 sprint.yaml 一致？
□ 是否确认 Sprint close 前无过期中间态文案？
□ 是否运行 validate-sprint-archive-readiness / generate-sprint-fact-sheet / check-sprint-close-stale-scan？
□ 是否运行 sync-workflow-status.py --check ？
```
