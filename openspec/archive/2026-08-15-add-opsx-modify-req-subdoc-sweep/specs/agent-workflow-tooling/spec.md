## ADDED Requirements

### Requirement: opsx-modify REQ 子文档一致性扫尾检查

MoonBox MUST 在 REQ 来源的 `/opsx-modify` 完成前执行 REQ 子文档一致性扫尾检查，避免只更新 PRD 或单一验收文档而遗漏业务流程、用户故事、`acceptance.md`、`trace.md` 和 `prototype/**` 等事实源。该检查 MUST 按 linked REQ 目录中实际存在的子文档和原型资产逐项判断是否需要同步；无需更新时 MUST 记录理由。

#### Scenario: REQ 来源返修完成前扫尾

- **GIVEN** `/opsx-modify` 目标 Change 来源于完整 `REQ-xxxx-slug`
- **WHEN** 返修实现、Change 文档和验证证据准备进入最终同步
- **THEN** 系统 MUST 定位 linked REQ 目录并检查现有 `requirement.md`、业务流程文档、用户故事文档、`acceptance.md`、`trace.md` 和 `prototype/**`
- **AND** 若返修改变产品行为、UI/交互、验收口径、Mock/API 边界、原型意图或用户故事，系统 MUST 同步更新受影响 REQ 子文档或原型说明
- **AND** 若某项无需更新，系统 MUST 在 Change `tasks.md` 验收返修记录或 Change `trace.md` 中记录无需更新的项目与原因

#### Scenario: 子文档漂移阻断返修完成

- **GIVEN** REQ 子文档一致性扫尾检查发现业务流程、用户故事或 `prototype/**` 与返修后行为不一致
- **WHEN** 该差异仍属于当前 Change 边界
- **THEN** 系统 MUST 先回填对应 REQ 子文档后再完成 `/opsx-modify`
- **AND** 若差异扩大当前 Change 边界，系统 MUST 阻断 `/opsx-modify` 完成并建议新建 REQ、BUG 或 OpenSpec Change
