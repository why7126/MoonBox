# explore-improvement-loop Specification

## Purpose
TBD - created by archiving change improve-explore-feedback-loop. Update Purpose after archive.
## Requirements
### Requirement: 探索反馈保持只读并分类
系统 MUST 在探索会话内区分项目事实、局部偏好、执行遗漏、环境问题和通用方法缺陷；无证据不制造候选，不持久化反馈或改变业务状态。
#### Scenario: 用户纠正项目事实
- **WHEN** 用户纠正仅属于本项目的部署事实
- **THEN** 探索承接该事实但不写通用 Skill，不创建私有反馈台账

### Requirement: 统一维护去重与评测
系统 MUST 经 spec-opt 交接脱敏证据与候选，复用统一治理去重和授权门禁；更新前检查失败案例、正常案例及不适用反例，区分静态验证与真实行为。
#### Scenario: 已有相同规则或候选
- **WHEN** 反馈对应已有规则或未解决候选
- **THEN** 先检查执行遗漏或关联原候选，不重复追加指令或创建候选

### Requirement: 版本生效与效果观察
系统 MUST 绑定加载版本，新任务重新读取最新 Skill，当前任务显式切换时重新核对；验证通过与收益确认分开，退化只撤回本次差异。
#### Scenario: 当前任务期间文件更新
- **WHEN** Skill 文件内容发生变化但任务尚未显式切换
- **THEN** 不声称当前会话已经采用新规则，后续任务重新读取并记录版本

