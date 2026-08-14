---
purpose: git-check 推送前安全检测治理日志
content: 记录 REQ-0009 驱动的 Git 安全门禁、隐私阻断和 spec-logs 自动关联规则
created_at: 2026-08-09 08:18:35
updated_at: 2026-08-09 08:18:35
owner: MoonBox 产品团队
---

# git-check 推送前安全检测治理日志

## 迭代目标

为 MoonBox 新增 `/git-check` 推送前安全检测命令，覆盖 staged/tracked 范围内的真实环境文件、运行时数据、数据库文件、大文件、密钥/Token/连接串、本机绝对路径和不应进入 Git 的本地数据；同时补齐 REQ/BUG 驱动治理类 Change 与 `docs/spec-logs/` 的强制关联规则。

## 变更摘要

- 新增 `.agents/skills/git-check/SKILL.md` 命令入口。
- 新增 `scripts/git-check.py` 检测脚本，默认扫描 staged + tracked，支持 `--all` 全仓扫描。
- 复用 `scripts/validate-env-ignore-policy.py`，真实 env ignore 策略失败时阻断。
- 将 `data/s3/**` 纳入禁止提交路径，并通过 Git 索引迁出保留本地对象存储运行时数据。
- 将本机绝对路径片段作为隐私数据纳入 error 阻断，并脱敏历史归档文档中的本机路径。
- 增加 `tests/unit/test_git_check.py` 单元测试，覆盖禁止路径、占位符、敏感值脱敏、连接串和本机路径阻断。
- 将 REQ/BUG 驱动但触达治理资产的 Change 强制纳入 `docs/spec-logs/` 记录和 `CHANGELOG.md` 索引。

## 影响范围

- Agent 命令：`.agents/skills/git-check/SKILL.md`
- 治理脚本：`scripts/git-check.py`、`scripts/validate-env-ignore-policy.py`
- 安全规范：`rules/security.md`
- 文档治理：`rules/document-governance.md`、`docs/spec-logs/README.md`、`docs/spec-logs/CHANGELOG.md`
- OpenSpec：`openspec/changes/add-git-check-pre-push-security-gate/`
- Sprint：`iterations/change/sprint-002/`
- REQ：`issues/requirements/review/REQ-0009-git-check-pre-push-security-gate/`

## 更新文件

- `.agents/skills/git-check/SKILL.md`
- `scripts/git-check.py`
- `tests/unit/test_git_check.py`
- `.gitignore`
- `AGENTS.md`
- `project.yaml`
- `rules/security.md`
- `rules/document-governance.md`
- `docs/spec-logs/README.md`
- `docs/spec-logs/CHANGELOG.md`
- `docs/spec-logs/20260809081835-governance-git-check-security-gate.md`
- `openspec/changes/add-git-check-pre-push-security-gate/**`
- `iterations/change/sprint-002/**`
- `issues/requirements/review/REQ-0009-git-check-pre-push-security-gate/**`

## 验证结果

- `python scripts/git-check.py`：通过，`errors=0`，剩余 warning 为历史原型疑似邮箱复核项。
- `uv run pytest tests/unit/test_git_check.py`：通过，6 passed。
- `python scripts/validate-env-ignore-policy.py`：通过。
- `openspec validate add-git-check-pre-push-security-gate --strict`：通过。
- `python scripts/validate-openspec-language.py`：通过。
- `git diff --check`：通过。
- `python scripts/sync-workflow-status.py --event opsx.modify --change add-git-check-pre-push-security-gate --sprint auto`：通过。
- `python scripts/extract-ai-usage.py --post-command-hook --workflow-event opsx.modify --change add-git-check-pre-push-security-gate --sprint sprint-002 --json`：通过。

## 影响矩阵

| 领域 | 影响 |
|---|---|
| API | 无 |
| DB | 无 |
| Web | 无 |
| 客户端 | 无 |
| 管理端 | 无 |
| Orval | 无 |
| Docker Compose | 无 |
| 安全治理 | 新增 Git 推送前安全检测门禁 |
| 文档治理 | 新增 REQ/BUG 驱动治理类 Change 的 spec-logs 强制关联规则 |

## 跨项目落地提示词

```text
请在本项目新增 /git-check 推送前安全检测命令，默认扫描 staged + tracked 文件，检测真实环境文件、运行时数据、数据库文件、大文件、密钥/Token/连接串、本机绝对路径和不应进入 Git 的本地数据；报告必须脱敏，有 error 时返回非 0。同时请规定：只要 REQ/BUG 驱动的 Change 触达治理资产，也必须写入 spec-logs 治理日志并同步 CHANGELOG 索引。
```

## 后续建议

- 后续 `/opsx-archive REQ-0009-git-check-pre-push-security-gate` 前复跑 `/git-check`，确保没有新增 error。
- 可在后续治理脚本中自动识别治理资产触达范围，提示或校验 `spec_log_refs` 与 `CHANGELOG.md` 是否同步。
