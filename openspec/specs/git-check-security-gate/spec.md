# git-check-security-gate Specification

## Purpose
TBD - created by archiving change add-git-check-pre-push-security-gate. Update Purpose after archive.
## Requirements
### Requirement: git-check 命令入口

MoonBox SHALL provide a `/git-check` Agent command for pre-push security checks. The MVP SHALL run as an explicit command and SHALL NOT require installing a Git `pre-push` hook.

#### Scenario: 显式运行 git-check
- **WHEN** 用户或 Agent 运行 `/git-check`
- **THEN** 系统 SHALL execute the pre-push security check workflow
- **AND** the command SHALL report the scan scope and result summary

### Requirement: 默认扫描 staged 和 tracked 文件

`/git-check` SHALL scan staged files and tracked files by default. The command SHALL support an optional full-repository scan mode, but full-repository scan SHALL NOT be the default behavior.

#### Scenario: 默认扫描范围
- **WHEN** `/git-check` runs without full-scan options
- **THEN** the command SHALL scan staged files
- **AND** the command SHALL scan tracked files
- **AND** the command SHALL mark the report scan scope as `staged+tracked`

#### Scenario: 可选全仓扫描
- **WHEN** `/git-check` runs with the full-repository scan option
- **THEN** the command SHALL scan the configured full-repository scope
- **AND** the report SHALL mark the scan scope as `all`

### Requirement: env ignore 策略复用

`/git-check` SHALL reuse `scripts/validate-env-ignore-policy.py` or equivalent logic to verify real environment files are ignored and example environment files remain trackable.

#### Scenario: env ignore 策略失败
- **WHEN** real environment files are not covered by Git ignore
- **THEN** `/git-check` SHALL return a non-zero exit code
- **AND** the report SHALL include an error explaining the env ignore policy failure

#### Scenario: 示例 env 被误 ignore
- **WHEN** `.env.example`, `deploy/**/*.env.example`, or `scripts/build-images.env.example` is ignored by Git
- **THEN** `/git-check` SHALL return a non-zero exit code
- **AND** the report SHALL instruct the user to fix the ignore policy

### Requirement: 禁止提交路径检测

`/git-check` SHALL detect forbidden staged or tracked paths, including real environment files, runtime databases, runtime data directories, upload data, object storage runtime data, local MinIO/MySQL volumes, temporary files, build artifacts, archives, and system cache files.

#### Scenario: 真实环境文件进入 Git 范围
- **WHEN** a real environment file is staged or tracked
- **THEN** `/git-check` SHALL report an error
- **AND** `/git-check` SHALL return a non-zero exit code

#### Scenario: 运行时数据进入 Git 范围
- **WHEN** a staged or tracked path matches runtime data or database patterns
- **THEN** `/git-check` SHALL report an error
- **AND** `/git-check` SHALL return a non-zero exit code

### Requirement: 敏感内容检测与占位符豁免

`/git-check` SHALL scan staged and tracked text files for likely real secrets, API keys, AccessKey, SecretKey, Token, Authorization headers, Cookie values, database connection strings, object storage credentials, private production addresses, local absolute paths, and likely privacy data. Local absolute paths SHALL be treated as privacy data and reported as error-level findings. The command SHALL distinguish placeholder examples from likely real values.

#### Scenario: 真实 Authorization header
- **WHEN** a staged or tracked text file contains a likely real Authorization header
- **THEN** `/git-check` SHALL report an error
- **AND** the report SHALL NOT print the complete header value

#### Scenario: 合法占位符
- **WHEN** a staged or tracked text file contains placeholders such as `<access_token>`, `change-me-in-local-env`, `example`, or `localhost`
- **THEN** `/git-check` SHALL NOT classify the placeholder itself as an error

#### Scenario: 本机绝对路径进入 Git 范围
- **WHEN** a staged or tracked text file contains a local absolute path such as `/Users/<name>/...` or `/home/<name>/...`
- **THEN** `/git-check` SHALL report an error
- **AND** `/git-check` SHALL return a non-zero exit code

### Requirement: 脱敏报告

`/git-check` SHALL redact sensitive values in all reports. Reports MAY include file path, line number, rule name, severity, and redacted snippet, but SHALL NOT print complete secrets, tokens, cookies, Authorization headers, database connection strings, real `.env` lines, or customer privacy data.

#### Scenario: 命中敏感值时输出脱敏片段
- **WHEN** `/git-check` detects sensitive content
- **THEN** the report SHALL include the rule and location
- **AND** the report SHALL include only a redacted snippet
- **AND** the report SHALL NOT include the complete sensitive value

### Requirement: 返回码与报告结构

`/git-check` SHALL return a non-zero exit code when error-level findings exist. The report SHALL include a scan summary, error list, warning list, pass summary, and remediation suggestions.

#### Scenario: 存在 error 级问题
- **WHEN** `/git-check` finds one or more error-level findings
- **THEN** the command SHALL return a non-zero exit code
- **AND** the report SHALL include remediation suggestions

#### Scenario: 无 error 级问题
- **WHEN** `/git-check` finds no error-level findings
- **THEN** the command SHALL return zero
- **AND** the report SHALL remain concise on the success path

### Requirement: 测试覆盖

The implementation SHALL include script-level tests or equivalent validation for real env files, example env files, database files, runtime directories, real connection strings, placeholder false-positive control, and redacted output.

#### Scenario: 验证覆盖完成
- **WHEN** the implementation is complete
- **THEN** the validation suite SHALL cover high-risk path checks
- **AND** the validation suite SHALL cover sensitive content checks
- **AND** the validation suite SHALL verify redacted output

### Requirement: 治理变更日志关联

REQ/BUG-driven Changes that modify governance assets SHALL be recorded in `docs/spec-logs/`. Governance assets include Agent skills, `AGENTS.md`, `rules/**`, `docs/spec-logs/**`, `docs/standards/**`, governance scripts, validation scripts, Workflow Sync rules, OpenSpec/Sprint/REQ/BUG workflow rules, and project command indexes.

#### Scenario: REQ 驱动治理类 Change 完成实现
- **WHEN** a REQ-driven Change modifies governance assets
- **THEN** the implementation SHALL create or update a `docs/spec-logs/YYYYMMDDhhmmss-governance-xxx.md` record
- **AND** the implementation SHALL add a corresponding entry to `docs/spec-logs/CHANGELOG.md`
- **AND** the Change trace SHOULD reference the governance log

