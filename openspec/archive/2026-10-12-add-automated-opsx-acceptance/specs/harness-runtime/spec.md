## ADDED Requirements

### Requirement: 独立验收阶段与状态保护

系统 MUST 在 apply、modify 和 archive 之间提供独立验收入口，并以可校验的证据清单驱动归档就绪。Workflow Sync MUST 保留仍有效的通过结论，且不得因归档事件单独推断验收通过。

#### Scenario: Apply 完成后进入验收

- **WHEN** Change 完成 apply 门禁
- **THEN** 自动启动或明确续接 `/opsx-accept`，产出逐 AC 结论与证据入口。

#### Scenario: 修改后重新验收

- **WHEN** `/opsx-modify` 完成
- **THEN** 只有输入指纹已变化的 AC 失效并重跑，未变化的通过项保留。

#### Scenario: 归档检查

- **WHEN** Change 有新验收计划并请求归档
- **THEN** 归档前核对 passed 清单与当前输入指纹；缺失或过期时阻断归档。
