## ADDED Requirements

### Requirement: REQ Review 默认正向评审路径

系统 MUST 将 `/req-review <REQ-full-id>` 作为需求评审的默认正向通过命令，并保留显式反向结果和治理收尾。

#### Scenario: 默认调用 req-review 评审通过

- **WHEN** 用户执行 `/req-review REQ-xxxx-slug`
- **AND** 目标需求满足评审前置条件且评审清单无阻断项
- **THEN** 系统必须将本次评审结果记录为 `approved`
- **AND** 系统必须写入或更新 `review.md`
- **AND** 系统必须同步 `trace.md` 与 `requirement.md` 的主状态
- **AND** 系统必须在 Workflow Sync 前将需求目录从 `plan/` 迁移到 `review/`
- **AND** 系统必须刷新 `issues/requirements/CHANGELOG.md` 当前态看板行
- **AND** 系统必须输出下一步 `/sprint-propose --req REQ-xxxx-slug`

#### Scenario: 显式反向评审结果

- **WHEN** 用户执行 `/req-review REQ-xxxx-slug --reject` 或 `/req-review REQ-xxxx-slug --defer`
- **THEN** 系统必须记录对应的 `rejected` 或 `deferred` 结果
- **AND** 系统不得将需求目录迁入 `review/`
- **AND** 系统必须刷新 trace、registry 和当前态看板

#### Scenario: 评审存在阻断风险

- **WHEN** 目标需求缺少评审必需文档、产品数据采集与链路观测声明、验收项或关键风险判断
- **THEN** 系统必须在通过前输出引导式反馈或阻断摘要
- **AND** 系统不得因为无 flag 默认语义而静默批准不满足门禁的需求

#### Scenario: req-review 收尾同步

- **WHEN** `req-review` 主操作完成且 Workflow Sync 成功
- **THEN** 系统必须运行 AI Usage Post-command Hook 或报告不可用原因
- **AND** 成功路径只输出 compact 摘要字段
- **AND** 最终回复必须包含下一步、待用户决策/处理和执行链路复盘
