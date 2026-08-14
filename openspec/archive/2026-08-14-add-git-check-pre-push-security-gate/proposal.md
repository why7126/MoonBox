## 背景

MoonBox 已有 `.gitignore` 和 env ignore 校验，但缺少推送前统一检查 staged/tracked 内容的安全门禁。新增 `/git-check` 能在代码进入 Git 仓库前发现真实环境文件、运行时数据、数据库文件、大文件、密钥/Token/连接串、本机绝对路径和隐私数据，降低治理与发布阶段的泄露风险。

## 变更内容

- 新增 `/git-check` Agent 命令，MVP 仅作为显式命令运行，不强制接入 Git `pre-push` hook。
- 新增 `scripts/git-check.py` 或等价脚本入口，默认扫描 staged + tracked 文件。
- 复用 `scripts/validate-env-ignore-policy.py`，保留真实 env 本地存在但被 ignore 且未进入 Git 时不阻断的规则。
- 增加禁止提交路径、敏感内容、大文件/二进制产物、脱敏报告和返回码规则。
- 增加脚本级测试或等价验证，覆盖真实 env、示例 env、运行时数据、连接串、占位符误报和脱敏输出。
- 不修改业务 `src/`，不新增 API、DB、Web UI 或生产部署拓扑。

## 能力范围

### 新增能力

- `git-check-security-gate`: 定义 `/git-check` 推送前安全检测命令、默认扫描范围、env ignore 复用、路径/内容/大文件检测、脱敏报告、返回码和测试验收。

### 修改能力

无。

## 影响范围

- `.agents/skills/`：新增或更新 `/git-check` 命令入口。
- `scripts/`：新增 `git-check.py`，复用 `validate-env-ignore-policy.py`。
- `tests/`：新增脚本级测试或等价验证用例。
- `rules/`、`docs/`：如实现引入新的命令、检测策略或安全边界，需同步相关治理文档。
- `iterations/archive/sprint-002/` 与 `issues/requirements/review/REQ-0009-git-check-pre-push-security-gate/`：由 Workflow Sync 维护追溯关系。
