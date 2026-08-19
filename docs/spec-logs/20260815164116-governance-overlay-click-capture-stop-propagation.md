---
purpose: 治理迭代日志
content: 记录浮层外部点击 capture 阶段覆盖弹窗内 stopPropagation 场景的 UI 交互验收规则沉淀
created_at: 2026-08-15 16:41:16
updated_at: 2026-08-15 16:41:16
owner: MoonBox 产品团队
---

# 浮层外部点击捕获阶段 stopPropagation 验收规则

## 迭代目标

将“浮层外部点击必须在 capture 阶段覆盖弹窗内 `stopPropagation` 场景”沉淀为 UI 交互验收规则，避免 click outside 关闭能力只在理想冒泡链路下被验证。

## 变更摘要

- 在 UI 浮层交互规则中明确：声明支持点击外部关闭的浮层，必须覆盖内部 `stopPropagation` 后外部点击仍可关闭的验收场景。
- 在原型驱动 UI 验收标准中补充 UI Contract、视觉截图门禁和独立验收条款。
- 新增 Design System OpenSpec delta spec，确保后续归档可进入正式规格。
- 将纯治理 Change 纳入 `sprint-003`。

## 影响范围

- UI 交互验收规范
- prototype UI Gate
- Design System 正式规格的待归档 delta
- Sprint scope 与治理日志索引

## 更新文件

- `rules/ui-design.md`
- `docs/standards/prototype-ui-acceptance.md`
- `openspec/changes/add-overlay-click-capture-stop-propagation-rule/`
- `iterations/change/sprint-003/sprint.yaml`
- `docs/spec-logs/20260815164116-governance-overlay-click-capture-stop-propagation.md`
- `docs/spec-logs/CHANGELOG.md`

## 验证结果

- 通过：`python scripts/validate-agent-context-budget.py`
- 通过：`python scripts/validate-openspec-language.py`
- Warning：`python scripts/validate-directory-structure.py` 因既有未登记根目录 `tmp/` 失败；本次未新增或修改该目录。
- 通过：`openspec validate add-overlay-click-capture-stop-propagation-rule`
- 通过：`python scripts/validate-sprint-scope.py sprint-003 --item add-overlay-click-capture-stop-propagation-rule`
- 通过：`python scripts/sync-workflow-status.py --event opsx.apply --change add-overlay-click-capture-stop-propagation-rule --sprint auto`
- 通过：`python scripts/extract-ai-usage.py --post-command-hook --workflow-event opsx.apply --change add-overlay-click-capture-stop-propagation-rule --sprint sprint-003 --json`

## API/DB/Web/客户端/管理端/Orval/Docker Compose 影响

- API：无影响。
- DB：无影响。
- Web：无业务实现变更，仅影响后续 UI 验收规则。
- 客户端生成 / Orval：无影响。
- 管理端：无业务实现变更，仅影响后续 UI 验收规则。
- Docker Compose：无影响。

## 后续建议

后续可评估将 click outside capture 阶段与 `stopPropagation` 覆盖情况接入 UI Contract 模板或自动化验收脚本。
