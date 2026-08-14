## ADDED Requirements

### Requirement: spec-study 日志优先学习顺序

`/spec-study` 在学习对象存在 `docs/spec-logs/CHANGELOG.md` 时，MUST 优先从日志索引入手理解治理演进，再读取相关单次日志，并横向校验真实治理资产；日志不得替代当前资产、OpenSpec Change、Sprint 四件套或正式规格事实源。

#### Scenario: 学习对象存在 spec-logs 变更历史

- **WHEN** `/spec-study` 学习对象包含 `docs/spec-logs/CHANGELOG.md`
- **THEN** Phase 1 MUST 先读取该文件作为治理演进入口地图
- **AND** MUST 根据主题读取相关 `YYYYMMDDhhmmss-study-xxx.md` 或 `YYYYMMDDhhmmss-governance-xxx.md`
- **AND** MUST 再回到 `AGENTS.md`、`rules/`、`docs/`、Agent 目录、`scripts/`、部署与环境示例等真实资产做横向校验
- **AND** SHOULD 只在证据不足或需要确认实际执行语义时读取必要代码、脚本或配置片段

#### Scenario: 日志与真实资产存在漂移

- **WHEN** `CHANGELOG.md` 或单次日志描述与当前治理资产不一致
- **THEN** `/spec-study` MUST 在候选学习内容中标注漂移风险
- **AND** MUST 以当前真实资产和正式规格作为最终事实依据
- **AND** SHOULD 将日志内容作为历史背景或设计意图参考
