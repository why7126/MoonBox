## 背景

MoonBox 现有 BUG 生命周期包含 `root-cause.md`、`logs/` 和 `screenshots/`，探索命令也要求证据优先；但当前门禁主要检查文件是否存在，没有强制“已确认根因必须绑定证据”。当问题排查、验收返修或效果不如预期时，AI 仍可能把未经验证的假设写成根因，导致修复方向靠猜、返工成本升高。

## 变更内容

- 新增证据化根因分析治理规则，定义根因状态、证据链、人工补证和禁止猜测定根因的硬门禁。
- 更新 `/explore`、`/bug-explore`、`/bug-complete`、`/opsx-apply`、`/opsx-modify` 技能，使问题探索、BUG 完善、实现前检查和验收返修都必须先确认根因证据。
- 新增人工补证操作步骤模板，覆盖 Console、Network、后端日志、UI 截图/computed style、数据库、部署和权限登录等场景。
- 更新测试、日志、安全、UI 验收相关规范，要求 BUG 修复、效果不符和运行时异常都保留可复核证据。
- 新增 `scripts/validate-root-cause-evidence.py`，用于校验 BUG 或 Change 的 root-cause evidence gate。
- 不修改业务 `src/`、API、DB schema、Web UI 或生产部署拓扑。

## 能力范围

### 新增能力

- `root-cause-evidence-governance`: 证据化根因分析规则、人工补证操作步骤、BUG/返修/测试/UI/日志门禁和脚本校验。

### 修改能力

- `agent-workflow-tooling`: Agent 命令在问题排查、BUG 完善和返修中必须区分已确认根因、强推测、待验证假设与未知状态。
- `testing`: BUG 修复和返修测试必须回扣根因证据和复现路径，不能用只跑通过替代根因验证。

## 影响范围

- `rules/`：新增根因证据规则，并同步 BUG、测试、UI、安全、全局入口等治理规范。
- `docs/standards/`：补充测试治理和 prototype UI 验收对证据链的要求。
- `.agents/skills/`：更新 explore、bug-explore、bug-complete、opsx-apply、opsx-modify 的门禁。
- `scripts/`：新增 root-cause evidence 校验脚本。
- `openspec/changes/establish-root-cause-evidence-governance/`：记录本次治理 Change 的 proposal、design、tasks、delta spec。
- `iterations/change/sprint-003/`：承载本次纯治理 Change。
- `docs/spec-logs/`：写入治理迭代日志和索引。
