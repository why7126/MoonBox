---
change_id: add-visual-evidence-temp-dir-governance
status: proposed
created_at: 2026-08-18 10:06:40
updated_at: 2026-08-18 10:06:40
---

# Tasks

## 1. 规则与脚本同步

- [x] 1.1 在 `.gitignore` 覆盖根目录 `tmp/` 临时产物。
- [x] 1.2 在目录结构规则中声明 `tmp/visual-evidence/` 的临时目录归属、禁止内容和长期证据转存要求。
- [x] 1.3 在文档治理和原型 UI 验收标准中同步视觉证据临时目录与长期证据边界。
- [x] 1.4 更新目录结构校验脚本，使被 ignore 的根目录 `tmp/` 不再阻断校验。

## 2. 记录与验证

- [x] 2.1 增加 OpenSpec delta，记录视觉证据目录治理能力。
- [x] 2.2 写入治理迭代日志并更新 spec-logs 索引。
- [x] 2.3 运行上下文预算、OpenSpec 中文、目录结构、env ignore、OpenSpec validate、Sprint scope、Workflow Sync 和 AI Usage 校验。
