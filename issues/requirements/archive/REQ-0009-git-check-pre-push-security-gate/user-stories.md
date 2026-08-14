---
requirement_id: REQ-0009-git-check-pre-push-security-gate
created_at: 2026-08-09 07:21:45
updated_at: 2026-08-09 07:21:45
---

# 用户故事

## US-001 推送前执行安全检测

作为开发者，我希望在推送到 Git 仓库前运行 `/git-check`，以便提前发现 staged/tracked 文件中的敏感数据、本地运行时文件和不应提交的大文件。

验收要点：

- 命令必须能显式运行，MVP 不强制安装 Git `pre-push` hook。
- 默认扫描范围必须包含 staged 文件和 tracked 文件。
- 扫描完成后必须输出通过摘要、error、warning 和修复建议。

## US-002 复用 env ignore 策略

作为项目维护者，我希望 `/git-check` 复用现有 env ignore 校验，以便真实环境文件不会进入 Git，而 `.env.example` 等示例文件仍可提交。

验收要点：

- 必须复用 `scripts/validate-env-ignore-policy.py` 或等价逻辑。
- 真实 `.env`、`.env.local`、`.env.*`、`deploy/**/*.env`、`scripts/build-images.env` 未被 ignore 时必须失败。
- `.env.example`、`deploy/**/*.env.example`、`scripts/build-images.env.example` 被误 ignore 时必须失败。

## US-003 阻断禁止提交路径

作为 Agent 执行者，我希望命令能识别运行时数据库、上传数据、MinIO/MySQL 本地卷、临时目录、构建产物和压缩包，以便避免把本地数据误提交。

验收要点：

- staged/tracked 中出现 `*.sqlite`、`*.sqlite3`、`*.db` 或 `data/runtime/**` 等运行时路径时必须失败。
- staged/tracked 中出现真实环境文件、上传目录、对象存储运行时目录、临时目录或本地数据卷时必须失败。
- 对允许提交的样例数据和说明文档必须支持白名单或明确规则。

## US-004 检测并脱敏报告敏感内容

作为发布与治理负责人，我希望命令能发现文档、代码或配置中的真实密钥、Token、连接串、Cookie、Authorization header、本机绝对路径和隐私数据，同时不在报告中泄露原文。

验收要点：

- 检测报告必须显示文件、行号、规则名和风险级别。
- 报告不得完整输出密钥、Token、Cookie、数据库连接串、真实 `.env` 行或客户隐私数据。
- 合法占位符和公开示例不应仅因关键词命中而被直接判为 error。

## US-005 可选全仓扫描

作为维护人员，我希望在发布前或人工复核时可以启用全仓扫描，以便扩大安全检查范围，同时不影响默认推送前体验。

验收要点：

- 默认行为不得扫描完整 Git 历史或全仓未跟踪内容。
- 命令应提供可选全仓扫描模式。
- 全仓扫描输出仍需遵守脱敏和分级报告规则。
