---
change_id: apply-tilesfst-local-session-jsonl-governance
status: proposed
created_at: 2026-09-04 16:05:54
updated_at: 2026-09-04 16:05:54
---

# 设计说明

## 1. 学习来源与适配原则

学习对象记为 `ProjectTilesFST（本地只读项目）`。本变更只采纳通用治理能力：本地 session JSONL 自动发现、脱敏派生事实、历史回填显式输入、AI Usage gate 和脚本测试。不采纳学习对象业务域、历史数据、raw session 或本机路径。

## 2. Session 输入发现

普通 workflow hook 的输入发现顺序统一为：

1. 显式 `--session-jsonl`。
2. `AI_USAGE_SESSION_JSONL`。
3. `CODEX_SESSION_JSONL`。
4. `AI_USAGE_SESSIONS_DIR`。
5. 默认本地 Codex sessions 目录 `~/.codex/sessions`。

自动发现使用 workflow event、REQ/BUG、Change、Sprint、release 和 slash-command 词项匹配近期 JSONL 文件。若失败或缺少可归因 token 事件，只输出 unavailable / estimated fallback 和推荐动作。

## 3. 持久化安全边界

`data/ai-usage/README.md` 作为目录级说明，声明仅保存脱敏聚合事实。禁止持久化 raw session JSONL、prompt、system/developer 指令、skill 正文、工具输出正文、完整日志、本机绝对路径、密钥、`.env`、客户数据或个人信息。

用户可见成功摘要继续保持 compact，不打印完整 hook JSON、派生文件正文或 session 输入路径。

## 4. 历史回填边界

历史回填或审计的目标不是“最近一次当前命令”，自动发现容易命中当前会话或同名历史文本。因此历史回填必须使用显式 `--session-jsonl`，必要时使用 `--manual-map` 按 `turn_hash` 补齐归因。

## 5. 测试策略

新增 `tests/unit/test_ai_usage.py`：

- 自动发现根据 workflow context 命中正确 session。
- 缺 session 时推荐本地 sessions 目录、`AI_USAGE_SESSIONS_DIR` 和显式 session。
- 缺 `token_count` 时进入 `estimated_fallback`，并提示刷新或显式 session。
- unsafe 记录被跳过，不崩溃、不写入 unsafe 派生事实。

## 6. 影响声明

本变更只影响治理脚本、命令说明、规则文档、测试和学习报告。API、数据库、Web、客户端、管理端、Orval、Docker Compose 与部署运行时均不变。
