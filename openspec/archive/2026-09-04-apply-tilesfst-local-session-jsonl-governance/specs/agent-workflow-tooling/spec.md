## MODIFIED Requirements

### Requirement: Sprint AI Usage 矩阵语义

MoonBox MUST 在 Sprint AI Usage 复盘矩阵中区分真实数值 `0` 与未观测 workflow 阶段，避免将采集缺口误读为真实零成本。MoonBox MUST 通过本地 Codex session JSONL 生成脱敏 AI Usage 派生事实，并在普通 workflow hook 中优先尝试本地 session 自动发现。

#### Scenario: 未观测 workflow 阶段显示为短横线

- **WHEN** Sprint AI Usage 矩阵中某个对象和 workflow 阶段没有匹配 command run
- **THEN** 数据层 MUST 将该单元标记为 `unknown`
- **AND** Markdown 复盘输出 MUST 将该单元渲染为 `-`
- **AND** 已观测但 token 或调用次数为零的单元 MUST 保持数字 `0`

#### Scenario: 普通 workflow hook 自动发现本地 session

- **WHEN** workflow 命令完成同步并运行 AI Usage post-command hook
- **AND** 操作者未显式提供 `--session-jsonl`
- **THEN** 系统 MUST 依次检查 session 环境变量、`AI_USAGE_SESSIONS_DIR` 和默认本地 Codex sessions 目录 `~/.codex/sessions`
- **AND** 系统 MUST 使用 workflow event、REQ/BUG、Change、Sprint、release 或 slash-command 词项匹配近期 JSONL
- **AND** 自动发现失败、候选缺少 `token_count` 或覆盖不足时，系统 MUST 输出 unavailable 或 estimated fallback 与推荐动作
- **AND** 系统 MUST NOT 持久化 raw session JSONL、prompt、system/developer 指令、工具输出正文、密钥、真实 `.env` 内容或本机绝对路径

#### Scenario: 历史回填使用显式 session 和 manual map

- **WHEN** 操作者需要对历史 workflow 命令做 AI Usage 回填或审计
- **THEN** 系统 MUST 要求显式 session JSONL 输入
- **AND** 当历史 turn 无法自动归因到 REQ/BUG、Change、Sprint 或 workflow event 时，系统 SHOULD 支持使用 manual map 按 turn hash 补齐归因
- **AND** 系统 MUST NOT 将普通自动发现结果作为历史回填的唯一事实源
