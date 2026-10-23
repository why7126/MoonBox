# governance-feedback-loop Specification

## Purpose
TBD - created by archiving change optimize-governance-feedback-loop. Update Purpose after archive.
## Requirements
### Requirement: 执行量化与可信用量
治理调用 MUST 记录唯一运行身份、版本、开始与结束、质量、Token 来源与完整性；缺失不冒充零，暂态数据不冒充完整用量。

#### Scenario: 未获得模型用量
- **WHEN** 运行结束但无可归因 Token
- **THEN** 保留耗时与用量不可用标记，采集降级不阻断主任务，不计算 Token 收益。

### Requirement: 分级优化与前置门禁
自动治理优化 MUST 在有效授权范围内，保留 Change、Sprint、验证、预算与防递归门禁，脚本不得执行会话内任意代码。

#### Scenario: 优化任务递归触发
- **WHEN** 优化子运行结束再次请求优化
- **THEN** 只计入自身成本，不启动下一层优化。

#### Scenario: 超范围或门禁缺失
- **WHEN** 候选包含业务文件、受保护规则或没有有效迭代Change
- **THEN** 禁止自动实施，记录明确原因，不改变主任务状态。

### Requirement: 可比收益与质量保护
修复通过与收益确认 MUST 分开；评估只接受同组完整样本，扣除全部优化成本，质量退化优先于性能收益。

#### Scenario: 性能改善但质量下降
- **WHEN** 后续样本失败或验收未通过
- **THEN** 标记退化并建议只撤回本次优化，不签认收益。

#### Scenario: 样本不足或成本缺失
- **WHEN** 可比样本不足、Token不可用或优化成本不完整
- **THEN** 对相应指标保持待观察，不伪造节省比例。

