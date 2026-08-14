## 背景

REQ-0009 已明确 MVP 只做显式 `/git-check` 命令，默认扫描 staged + tracked，全仓扫描作为可选增强。当前项目已有 `.gitignore` 和 `scripts/validate-env-ignore-policy.py`，但它们不能发现已经 staged/tracked 的敏感文件、运行时数据、连接串或文档泄密。

本 Change 属于治理安全命令，不涉及 API、数据库、Web UI 或业务源码。实现应遵守 `.agents/skills/` 作为唯一 Agent 命令入口的边界，并把检测逻辑放在 `scripts/`。

## 目标与非目标

**Goals:**

- 提供 `/git-check` 命令入口。
- 提供可测试的 `scripts/git-check.py` 检测实现。
- 默认扫描 staged + tracked 文件。
- 复用 env ignore 校验。
- 检测禁止提交路径、敏感内容、大文件/二进制产物。
- 输出分级且脱敏的报告。
- 为常见风险与误报场景补充测试。

**Non-Goals:**

- 不强制安装 Git `pre-push` hook。
- 不默认扫描完整 Git 历史。
- 不自动修改 `.gitignore`、不自动 unstage、不删除本地文件。
- 不引入第三方 secret scanner 作为必需依赖。
- 不读取或输出被 ignore 且未 staged/tracked 的真实 `.env` 内容。

## 技术决策

### D1. 命令入口与脚本分离

`/git-check` SHOULD 作为 `.agents/skills/git-check/SKILL.md` 或等价 Agent 命令入口，实际检测逻辑放在 `scripts/git-check.py`。

理由：Agent 命令负责工作流说明和输出契约，脚本负责可测试逻辑，便于 CI、手工执行和后续 Git hook 复用。

替代方案：仅写 Agent Skill 不写脚本。放弃原因是不可自动化验证，也难以在推送前复用。

### D2. 默认扫描 staged + tracked

脚本默认收集 staged 文件和 tracked 文件。staged 用于即将提交的风险，tracked 用于发现已经进入仓库索引的敏感文件或本地数据。

全仓扫描作为可选参数，例如 `--all`。MVP 不默认扫描未跟踪全仓内容或 Git 历史。

### D3. env ignore 作为前置检查

脚本 MUST 调用 `scripts/validate-env-ignore-policy.py` 或复用其等价函数。该检查失败时直接作为 error。

真实 env 本地存在但被 ignore 且未 staged/tracked 时，不应阻断。

### D4. 分级检测与脱敏输出

检测结果分为 error、warning、info。禁止提交路径、真实 env、数据库文件、运行时目录、真实连接串、Authorization header、Cookie、本机绝对路径等高危或隐私项应为 error。低置信个人信息等可作为 warning。

报告只输出文件、行号、规则名、风险级别和脱敏片段，不完整输出密钥、Token、Cookie、连接串、真实 `.env` 行或隐私数据。

### D5. 允许名单与误报控制

脚本 SHOULD 内置合法占位符与公开示例识别，例如 `<access_token>`、`change-me-in-local-env`、`example`、`localhost` 和明确脱敏 fixture。后续可扩展项目级允许名单，但不得允许绕过真实密钥、真实客户数据、真实环境文件或运行时数据库文件。

## 风险与权衡

- 误报过多 → 通过占位符识别、warning 分级和允许名单降低摩擦。
- 漏报真实敏感信息 → 先覆盖高风险模式，后续基于实际命中迭代规则。
- 报告本身泄密 → 所有命中输出必须经过脱敏函数，测试覆盖脱敏输出。
- 扫描性能影响体验 → 默认只扫 staged + tracked；全仓扫描显式启用。

## 迁移计划

1. 新增脚本和命令入口。
2. 增加测试覆盖路径策略、内容策略、env ignore 复用和脱敏输出。
3. 同步必要规则或文档。
4. 运行 `python scripts/git-check.py`、`python scripts/validate-env-ignore-policy.py` 和相关测试。

## 待决问题

无阻塞问题。大文件阈值可在实现阶段给出项目默认值，并在测试中固定。
