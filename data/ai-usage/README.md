---
purpose: AI Usage 派生事实说明
content: 本地 session JSONL 输入、脱敏持久化、自动发现、历史回填和安全边界
created_at: 2026-09-04 16:05:54
updated_at: 2026-09-04 16:05:54
owner: MoonBox 产品团队
---

# AI Usage 派生事实说明

`data/ai-usage/` 只保存从本地 Codex session JSONL 提取后的脱敏派生事实，用于 Sprint 复盘、发布复盘和命令执行成本分析。原始 session JSONL 是本机输入源，禁止复制进仓库。

## 目录约定

```text
data/ai-usage/
├── command-runs/   # 单次命令运行的脱敏聚合事实
├── sprints/        # Sprint 级快照
└── README.md       # 本说明
```

如需临时放置 raw 或 local 输入，必须使用被 Git ignore 覆盖的本地临时目录，不得作为长期事实源。

## Session 输入发现

普通 workflow hook 使用以下顺序定位本地 session JSONL：

1. 显式 `--session-jsonl <local-session.jsonl>`。
2. `AI_USAGE_SESSION_JSONL`。
3. `CODEX_SESSION_JSONL`。
4. `AI_USAGE_SESSIONS_DIR` 下的近期 `*.jsonl`。
5. 默认本地 Codex sessions 目录 `~/.codex/sessions` 下的近期 `*.jsonl`。

自动发现会使用 workflow event、REQ/BUG、Change、Sprint、release 和 slash-command 词项匹配近期 session。若自动发现失败、候选缺少 `token_count`，或覆盖范围不足，命令应输出 `usage_mode: unavailable` 或 `estimated_fallback`、reason、impact 和 `recommended_action`，不得编造真实 token 统计。

历史回填或审计不得依赖自动发现；必须提供显式 `--session-jsonl`，必要时提供 `--manual-map`，按 `turn_hash` 补齐无法自动分类的命令归因。

## 可持久化字段

允许保存：

- token、模型调用、工具调用、重试次数等聚合指标。
- workflow event、REQ/BUG、Change、Sprint、release 等治理 ID。
- session hash、turn hash、时间范围、行号范围和快照元数据。
- Sprint 或 release usage matrix 的聚合结果。

禁止保存：

- 原始 prompt、聊天原文、system/developer 指令、skill 正文、完整 session JSONL。
- 工具输出正文、完整日志、完整 diff、截图中的个人信息。
- 密钥、访问令牌、Cookie、Authorization header、真实 `.env` 内容、数据库连接串。
- 本机绝对路径、系统用户名、用户主目录、真实客户数据。

用户可见成功摘要保持紧凑，只输出 status、usage mode、command run count、snapshot 或 release artifact 状态、warning count 和推荐动作；不得打印完整 hook JSON 或派生文件正文。
