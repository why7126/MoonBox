---
requirement_id: REQ-0009-git-check-pre-push-security-gate
acceptance_status: passed
created_at: 2026-08-09 07:21:45
updated_at: 2026-08-14 16:29:34
---

# 验收清单

## 功能 AC

- [ ] AC-001 项目提供 `/git-check` Agent 命令，MVP 阶段仅作为显式命令运行，不强制接入 Git `pre-push` hook。
- [ ] AC-002 `/git-check` 默认扫描 staged 文件和 tracked 文件，并在报告中标明默认扫描范围。
- [ ] AC-003 `/git-check` 支持可选全仓扫描模式，且全仓扫描不作为默认行为。
- [ ] AC-004 `/git-check` 复用 `scripts/validate-env-ignore-policy.py` 或等价逻辑；env ignore 策略失败时命令返回非 0。
- [ ] AC-005 真实 `.env`、`.env.local`、`.env.*`、`deploy/**/*.env`、`scripts/build-images.env` 出现在 staged/tracked 中时必须作为 error 阻断。
- [ ] AC-006 `.env.example`、`deploy/**/*.env.example`、`scripts/build-images.env.example` 被 Git ignore 误覆盖时必须作为 error 阻断。
- [ ] AC-007 staged/tracked 中出现 `*.sqlite`、`*.sqlite3`、`*.db`、`data/runtime/**`、`data/uploads/**`、`data/tmp/**`、`data/minio/**`、`data/mysql/**` 等运行时数据时必须作为 error 阻断。
- [ ] AC-008 staged/tracked 中出现构建产物、压缩包、系统缓存文件或超过阈值的大文件时，必须按文件类型和允许名单输出 error 或 warning。
- [ ] AC-009 文本扫描必须覆盖疑似真实密钥、API Key、AccessKey、SecretKey、Token、Authorization header、Cookie、数据库连接串、对象存储凭据、生产私有地址、本机绝对路径和疑似隐私数据；本机绝对路径命中时必须作为 error 阻断。
- [ ] AC-010 `<access_token>`、`change-me-in-local-env`、`example`、`localhost`、明确脱敏 fixture 等合法占位符不得仅因关键词命中而直接作为 error。
- [ ] AC-011 检测报告必须脱敏；不得完整输出密钥、Token、Cookie、Authorization header、数据库连接串、真实 `.env` 行或客户隐私数据。
- [ ] AC-012 存在 error 级问题时命令必须返回非 0；无 error 时命令可返回 0，并保留 warning 提醒。
- [ ] AC-013 报告必须包含扫描摘要、error 列表、warning 列表、通过项摘要和修复建议。
- [ ] AC-014 命令和脚本新增后必须遵守项目目录边界，不得新增或恢复 `.claude/`、`.codex/`、`.cursor/`、`.kiro/`、`.opencode/` 等历史 Agent 目录。
- [ ] AC-015 后续实现必须补充脚本级测试或等价验证，覆盖真实 env、示例 env、数据库文件、运行时目录、真实连接串、占位符误报和脱敏输出。

## 横切 AC（knowledge-base）

N/A — 本 REQ 为 Git 推送前命令/治理安全需求，不涉及管理后台列表、表单、弹窗或媒体上传 UI 场景；未命中 `/req-complete` 知识库横切标签。

## 验收结果回填

```yaml
acceptance_status: passed
accepted_at: 2026-08-14 16:29:34
accepted_by: workflow-sync
source_change: add-git-check-pre-push-security-gate
source_sprint: sprint-002
evidence: []
failed_items: []
source_event: sprint.archive
notes: 由 Workflow Sync 根据 Change/Sprint 状态回填。
```

