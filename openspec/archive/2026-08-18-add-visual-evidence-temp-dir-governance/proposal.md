---
change_id: add-visual-evidence-temp-dir-governance
status: proposed
created_at: 2026-08-18 10:06:40
updated_at: 2026-08-18 10:06:40
---

# 明确视觉证据临时目录归属与 ignore 策略

## 背景

当前 UI 验收和返修流程会生成 1440px 截图、computed style JSON 和人工视觉对照中间证据，已有 Change trace 多次引用 `tmp/visual-evidence/`。但根目录 `tmp/` 尚未在目录结构治理和 ignore 策略中明确归属，导致目录结构校验将既有临时目录识别为未登记顶层目录。

## 目标

- 明确 `tmp/visual-evidence/` 是本地临时视觉证据采集目录。
- 明确 `tmp/` 必须被 `.gitignore` 覆盖，不属于正式项目目录。
- 明确长期验收证据必须转存到对应 Change `evidence/` 目录或脱敏摘要中。
- 更新目录结构校验，使被 ignore 的根目录 `tmp/` 不再阻断治理校验。

## 非目标

- 不迁移历史截图文件，不补做历史 UI 验收。
- 不修改业务 `src/` 代码、API、数据库、部署或客户端生成物。
- 不放宽新增正式顶层目录的治理边界。
