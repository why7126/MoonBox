---
purpose: 缺陷（BUG）生命周期、状态机、目录与评审门禁
source: 项目团队 + AI v2 定稿
update_method: 命令族变更时同步更新
updated_at: 2026-08-19 12:10:48
---

# 缺陷管理规范

## 1. 目录

```text
issues/bugs/
├── _registry.yaml
├── CHANGELOG.md
├── README.md
├── plan/                      # 规划中并完成评审
│   └── BUG-NNNN-slug/
├── review/                    # 已评审通过，修复/验收中，未 OpenSpec archive
│   └── BUG-NNNN-slug/
├── archive/                   # 已修复并归档
│   └── BUG-NNNN-slug/
└── BUG-NNNN-slug/             # [遗留] 扁平路径，deprecated；勿新建
```

单条 BUG 目录内文件：

```text
BUG-NNNN-slug/
├── capture.md
├── bug.md
├── root-cause.md
├── workaround.md
├── acceptance.md
├── trace.md
├── review.md
├── logs/
└── screenshots/
```

**新建 MUST** 使用 `issues/bugs/plan/BUG-NNNN-slug/`。阶段含义、迁移时机见 `rules/issues-lifecycle.md`。

禁止在 `docs/bugs/` 存放缺陷记录。

## 2. 状态机

| status | 含义 |
|--------|------|
| `captured` | 已记录 |
| `exploring` | 复现/影响分析中 |
| `draft` | 仅有 bug.md |
| `enriching` | 缺陷包补齐中 |
| `pending_review` | 待评审 |
| `approved` | **确认修复**（可进 Sprint；不可直接 bug-opsx） |
| `rejected` | 非缺陷/误报 |
| `wont_fix` | 不修 |
| `deferred` | 延后 |
| `in_sprint` | 已纳入迭代 |
| `done` | 已修复验收 |

## 2.1 当前态看板索引

`issues/bugs/CHANGELOG.md` 是缺陷目录级当前态看板索引，用于每个 BUG 一行展示严重等级、当前状态、阶段、关联 Sprint、关联 Change、最近更新时间、下一步和事实源路径。完整事实源仍以各 BUG 目录内 `trace.md`、`issues/bugs/_registry.yaml`、OpenSpec Change、Sprint 四件套和正式规格为准；`CHANGELOG.md` 不得替代状态机、registry 或单条 BUG 文档包。

SHOULD 在以下事件后更新对应 BUG 当前态行：`capture`、`generate`、`complete`、`review.approve`、`review.reject`、`review.defer`、`sprint.include`、`opsx.create`、`apply.done`、`archive.done`、`status.sync`、`trace.fix`。`wont_fix` 可作为评审或状态同步结果更新。

普通文案润色、格式调整、错别字修复、非状态性验收措辞调整 MAY 不更新。当前态行 MUST 使用 `YYYY-MM-DD HH:mm:ss` 记录最近更新时间，并避免写入用户隐私、真实客户数据、密钥、未脱敏日志、复现日志原文、本机绝对路径、系统用户名或用户主目录。

## 3. 命令与阶段

| 命令 | 产出 |
|------|------|
| `/capture` | 类型未决时自动分类；BUG 部分同 `/bug-capture`（见 §3.2） |
| `/bug-capture` | capture.md、trace 壳（可一次输入多条，按 §3.1 评估拆分） |

### 3.2 `/capture` 与 bug-capture

用户不确定输入是需求还是缺陷时使用 `/capture`。AI **MUST** 先分类再落盘：判为缺陷的条目遵循 §3.1 拆分规则，产出与 `/bug-capture` 相同，且 frontmatter 含 `captured_via: capture`、`classification_rationale`。一条消息可同时产生 REQ 与 BUG。

### 3.1 `/bug-capture` 多条输入与拆分

用户可能在一条消息中描述多个缺陷。AI **MUST** 先评估再落盘：

- **拆分**：不同界面/层级、缺陷类型、修复面、严重度、交付优先级，或用户显式并列枚举 → 每条独立 `BUG-NNNN-slug/`。
- **合并**：同一页面/弹窗且一次修复可闭环，或同一根因不可分割 → 单条 BUG；回复中一句话说明不拆理由。
- **禁止** umbrella BUG（总记录 + 子 bullet）；每条 MUST 可独立走 explore → opsx → archive。
- 创建多条时，`next_id` 连续递增；Workflow Sync 对**每条**执行 `bug.capture`。
| `/bug-explore` | 默认无文件 |
| `/bug-generate` | bug.md |
| `/bug-complete` | root-cause、workaround、acceptance、trace |
| `/bug-review` | review.md、status |
| `/sprint-propose --bug` | 正式纳入 Sprint，status → in_sprint |
| `/bug-opsx` | openspec/changes/fix-* |

BUG 命令族输出下一步时 MUST 使用完整 `BUG-NNNN-slug`。`/bug-review --approve` 后下一步 MUST 是 `/sprint-propose --bug <BUG-full-id>`；`/sprint-propose` 同步为 `in_sprint` 后下一步才是 `/bug-opsx <BUG-full-id>`。当 BUG 已转 OpenSpec Change 后，后续 `/opsx-apply`、`/opsx-modify`、`/opsx-archive` 仍 MUST 使用该完整 BUG ID，不得改为 Change ID；Change ID 只作为内部解析和 Workflow Sync 参数。

## 4. 门禁

### 4.0 文档质量与追溯一致性（MUST）

BUG 文档包 MUST 在进入评审、纳入 Sprint、转 OpenSpec、apply、modify 或 archive 前保持可追溯一致：

- `trace.md` 是机器状态事实源，MUST 包含 `status`、`iteration`、`openspec_changes`、`lifecycle`、严重等级和 `## 变更记录`。
- `bug.md` 是人类入口主文档，MUST 与 `trace.md` 的当前主状态、严重等级和影响范围保持一致。
- `root-cause.md` 的 `status: confirmed` 必须绑定可复核证据链；证据不足时不得推进到可评审修复状态。
- `acceptance.md` SHOULD 使用 `acceptance_status` 表达验收状态，避免旧 `status` 被误读为主生命周期状态。
- 已纳入 Sprint 的 BUG MUST 能从 BUG `trace.md`、`issues/bugs/_registry.yaml`、`issues/bugs/CHANGELOG.md`、`iterations/change|archive/<sprint>/sprint.yaml` 和 OpenSpec Change 互相追溯。
- `## 变更记录` MUST 使用表头紧跟章节标题的标准 Markdown 表格；新增命令记录不得写在表头前。

当发现上述文档质量或追溯漂移时，AI MUST 优先通过 Workflow Sync、根因证据校验或聚焦修复恢复事实源一致，不得手工编辑 Workflow Sync marker 块或把 CHANGELOG 当成唯一事实源。

### 4.1 评审门禁（统一，MUST）

与 `rules/requirement-management.md` §4.1 一致。BUG 对应状态门禁如下：

- `/sprint-propose` 要求 `status: approved` 或后续状态。
- `/bug-opsx` 要求 `status: in_sprint` 或后续交付态；`approved` 必须先 `/sprint-propose --bug <BUG-full-id>`。
- `/sprint-apply` 要求 `status: in_sprint` 或后续交付态。

未评审 BUG **不得**写入 Sprint 四件套正式范围；仅可记入 `sprint.md`「延后项（待评审）」并提示 `/bug-review BUG-xxxx --approve`。

`/sprint-propose` 成功写入正式 Sprint 四件套后，Workflow Sync MUST 将纳入的 BUG 从 `approved` 同步为 `in_sprint`，并写入 `iteration: sprint-xxx`。`sprint.yaml` `status: planning` 已满足正式纳入条件，不存在额外“未启动 Sprint”状态门禁。

### 4.2 opsx-apply 迭代纳入门禁（统一，MUST）

来源于 BUG 的 OpenSpec Change 在 `/opsx-apply` 前 **MUST** 已正式纳入某个 `sprint-xxx`：

- BUG `trace.md` MUST 满足 `status: in_sprint`（或后续交付态）且 `iteration: sprint-xxx` 非空。
- 对应 `iterations/change|archive/<sprint>/sprint.yaml` MUST 在 `bugs[]` 与 `changes[]` 中包含该 BUG 与 Change。
- `/opsx-apply` MUST 先用 `--sprint auto` 或等价检查确认能解析到 Sprint；解析失败时必须停止，提示先执行 `/sprint-propose`。
- 若解析到的 Sprint 为 `planning`，且上述双向追溯一致，`/opsx-apply` MUST 允许继续。

`approved` 只表示已评审通过，可进入 Sprint 规划；不得仅凭 `approved` 直接 `/bug-opsx` 或 `/opsx-apply`。

### 4.3 其他门禁

- `/bug-opsx`：**仅** 已评审并纳入 Sprint 后的 `in_sprint` 或后续交付态；`approved` 必须先 `/sprint-propose --bug <BUG-full-id>`
- `/bug-complete` 与 `/bug-review --approve`：MUST 遵守 `rules/root-cause-evidence.md`。`root-cause.md` 中 `status: confirmed` 必须有可复核证据链；证据不足时只允许保持 `unknown`、`hypothesis` 或 `probable`，并输出人工补证操作步骤，不得把 BUG 推进到可评审修复状态。
- `/bug-opsx` 与 `/opsx-apply <BUG-full-id>`：BUG 来源修复前 MUST 通过 `python scripts/validate-root-cause-evidence.py --bug <BUG-full-id>` 或等价校验；失败时先补证或重新 `/bug-complete`。
- Sprint：**P0 BUG** 优先于功能 REQ
- 旧命令 `/bug-to-change` 已删除 → `/bug-opsx`

## 5. 严重等级

```text
blocker | critical | high | medium | low
```

## 6. 知识沉淀

修复后若有复用价值，可更新 `docs/knowledge-base/incidents/`（由 bug-opsx tasks 提醒）。

## 7. 父需求反向追溯

BUG 的 `related_requirement` 不只是单向引用。若 `related_requirement` 非空，AI 在以下阶段 MUST 同步更新父需求 `issues/requirements/<REQ-ID>/trace.md` 的 `## 关联缺陷` 索引表：

- `/bug-complete` 或 `/bug-review` 确认父需求后。
- `/bug-opsx` 创建或确认修复 Change 后。
- BUG 纳入 Sprint、完成 `/opsx-apply`、完成 `/opsx-archive` 或状态变化后。

父需求 trace 中只记录索引级信息：`BUG`、`严重等级`、`状态`、`关联 Change`、`说明`。MUST NOT 在需求 trace 中复制 BUG 复现步骤、根因全文、日志或截图。

`trace.md` 的 `lifecycle` 与 `## 变更记录` 中所有时间记录 MUST 遵守 `rules/document-governance.md` §2.3（`YYYY-MM-DD HH:mm:ss`）。

Frontmatter **MUST** 含 `created_at`、`updated_at`；更新 trace 时刷新 `updated_at`，不得修改 `created_at`。

状态变更后 MUST 运行 `python scripts/sync-workflow-status.py`（见 `rules/document-governance.md`；如项目提供 Agent 技能，参照对应 `workflow-sync` 说明）。

## 8. 参考命令

对应 Agent 工具入口中的 `bug-*` 技能说明。
