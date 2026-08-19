## ADDED Requirements

### Requirement: BUG 修复与返修测试证据
MoonBox SHALL 要求 BUG 修复、验收返修和效果不符问题的测试验证回扣根因证据链。测试通过只能作为验证结果，不能替代根因证据。

#### Scenario: BUG 修复包含复现或替代证据
- **WHEN** 系统修复 BUG 或 BUG 来源 Change
- **THEN** 系统 SHALL 添加可复现回归测试
- **AND** 若无法自动化复现，系统 SHALL 在验收记录中说明原因并提供替代证据，例如日志、截图、Network、computed style、数据库样本或配置差异
- **AND** 验证记录 SHALL 关联 `root-cause.md` 中的证据项

#### Scenario: 返修测试验证偏差被消除
- **WHEN** 验收返修完成
- **THEN** 系统 SHALL 运行与偏差证据对应的测试、截图、日志或样式检查
- **AND** 验证记录 SHALL 同时说明原偏差、修复后结果和仍然存在的例外
