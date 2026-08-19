---
change_id: add-visual-evidence-temp-dir-governance
status: proposed
created_at: 2026-08-18 10:06:40
updated_at: 2026-08-18 10:06:40
---

# 设计

## 规则落点

- `.gitignore`：新增 `tmp/**`，确保根目录临时工作产物不会进入 Git。
- `rules/directory-structure.md`：声明根目录 `tmp/` 的临时性质、允许用途和禁止内容。
- `rules/document-governance.md`：声明临时证据与长期验收证据的转存边界。
- `docs/standards/prototype-ui-acceptance.md`：补充 UI 视觉证据目录归属和归档前转存要求。
- `scripts/validate-directory-structure.py`：忽略根目录 `tmp/`，避免本地临时证据阻断目录结构校验。

## 证据生命周期

1. `/opsx-apply` 或 `/opsx-modify` 运行 UI 验收时，可先把截图与 computed style JSON 写入 `tmp/visual-evidence/`。
2. 若证据需要支撑 Change 验收、Issue 验收或归档闭环，应转存到 `openspec/changes/<change-id>/evidence/`，或在 trace/acceptance 中写脱敏摘要。
3. `/opsx-archive` 前必须确认关键视觉证据已不只依赖本地临时路径。

## 安全边界

`tmp/` 不得存放真实客户数据、密钥、访问令牌、Cookie、Authorization header、真实 `.env`、运行时数据库、未脱敏日志或包含个人信息的截图。产品手册、release、OpenSpec archive 和 spec logs 不得复制未脱敏临时证据。
