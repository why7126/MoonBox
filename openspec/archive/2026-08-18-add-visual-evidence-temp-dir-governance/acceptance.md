---
change_id: add-visual-evidence-temp-dir-governance
status: proposed
created_at: 2026-08-18 10:06:40
updated_at: 2026-08-18 10:06:40
---

# 验收

- `.gitignore` 覆盖根目录 `tmp/` 临时产物。
- 目录结构规则明确 `tmp/visual-evidence/` 只用于本地临时取证。
- UI 验收标准明确长期证据必须转存到 Change `evidence/` 或脱敏摘要。
- 目录结构校验不再因根目录 `tmp/` 失败。
- OpenSpec、语言和上下文预算校验通过。
