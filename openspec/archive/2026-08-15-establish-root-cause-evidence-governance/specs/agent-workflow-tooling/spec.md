## ADDED Requirements

### Requirement: 证据化根因分析治理
MoonBox SHALL 在问题探索、BUG 完善、验收返修和 BUG 来源 OpenSpec 实现前执行证据化根因分析门禁。系统 SHALL 区分 `unknown`、`hypothesis`、`probable` 和 `confirmed` 根因状态；只有存在可复核证据链时，才能将根因标记为 `confirmed`。

#### Scenario: 探索阶段不得猜测定根因
- **WHEN** `/explore` 或 `/bug-explore` 面对问题、异常、效果不如预期或疑似 BUG
- **AND** 当前证据不足以支撑根因
- **THEN** 系统 SHALL 将根因标记为 `unknown`、`hypothesis` 或 `probable`
- **AND** 系统 SHALL NOT 输出已确认根因
- **AND** 系统 SHALL 输出人工补证清单、操作步骤、返回字段、脱敏要求和返回格式

#### Scenario: 人工补证后再确认根因
- **WHEN** 用户按补证步骤返回日志、截图、Network、Console、测试失败、数据库样本、配置差异或其他证据
- **THEN** 系统 SHALL 先复核证据是否能支撑根因
- **AND** 证据充分时 SHALL 将根因状态提升为 `confirmed`
- **AND** 证据仍不足时 SHALL 继续输出剩余证据缺口和下一轮补证步骤

#### Scenario: BUG 完善要求 confirmed evidence
- **WHEN** `/bug-complete <BUG-full-id>` 生成或更新 `root-cause.md`
- **THEN** `root-cause.md` SHALL 包含根因状态、现象、证据链、已排除假设、已确认根因、修复方向和验证闭环
- **AND** 若根因状态不是 `confirmed` 或缺少证据链，系统 SHALL NOT 将 BUG 推进到 `pending_review`

#### Scenario: BUG 来源实现前校验证据链
- **WHEN** `/opsx-apply <BUG-full-id>` 准备实现 BUG 来源 Change
- **THEN** 系统 SHALL 运行或等价执行 `scripts/validate-root-cause-evidence.py --bug <BUG-full-id>`
- **AND** 校验失败时 SHALL 阻断实现并提示先补证或重新执行 `/bug-complete`

#### Scenario: 验收返修先记录偏差证据
- **WHEN** `/opsx-modify` 处理验收失败、效果不如预期、UI 不一致或运行异常
- **THEN** 系统 SHALL 先记录偏差证据、期望/实际、影响范围和复现条件
- **AND** 若证据不足，系统 SHALL 输出人工补证操作步骤
- **AND** 系统 SHALL NOT 在缺少证据时把修复方向描述为已确认根因
