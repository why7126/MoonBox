---
purpose: 浮层退出路径与轻量选择确认规则治理日志
content: 记录 UI 浮层必须明确退出路径且轻量选择避免额外确认按钮的规范沉淀
created_at: 2026-08-15 15:24:58
updated_at: 2026-08-15 15:24:58
owner: MoonBox 产品团队
---

# 浮层退出路径与轻量选择确认规则治理日志

## 迭代目标

沉淀一条 UI 规则：浮层交互必须明确退出路径，同时避免在轻量选择场景中引入额外确认按钮。

## 变更摘要

- 在 `rules/ui-design.md` 新增“浮层交互”章节。
- 明确浮层必须至少有一种可理解的退出路径。
- 明确轻量选择优先选择即应用、点击外部关闭等低摩擦模式。
- 明确高成本编辑、提交、删除、权限、不可逆动作等场景可以使用确认按钮，但需说明原因。

## 影响范围

- UI 规则：影响后续 UI Contract、原型验收、浮层返修和视觉交互复核。
- OpenSpec：新增纯治理 Change `add-overlay-exit-lightweight-selection-rule`。
- Sprint：纳入 `sprint-003` 纯治理范围。
- 业务实现：不触碰 `src/`。

## 更新文件

- `rules/ui-design.md`
- `openspec/changes/add-overlay-exit-lightweight-selection-rule/`
- `iterations/change/sprint-003/sprint.yaml`
- `docs/spec-logs/CHANGELOG.md`
- `docs/spec-logs/20260815152458-governance-overlay-exit-lightweight-selection.md`

## 验证结果

- `python scripts/validate-agent-context-budget.py`：通过。
- `python scripts/validate-openspec-language.py`：通过。
- `python scripts/validate-directory-structure.py`：失败，原因为根目录存在既有未登记目录 `tmp/`；本次未修改该目录。
- `openspec validate add-overlay-exit-lightweight-selection-rule`：通过。
- `python scripts/validate-sprint-scope.py sprint-003 --item add-overlay-exit-lightweight-selection-rule`：Workflow Sync 刷新后通过。
- `python scripts/sync-workflow-status.py --event opsx.apply --change add-overlay-exit-lightweight-selection-rule --sprint auto`：通过，更新 2 个派生文档，无错误。

## API/DB/Web/客户端/管理端/Orval/Docker Compose 影响

- API：无。
- DB：无。
- Web：仅影响后续 UI 设计与验收规则，不修改运行时代码。
- 客户端：无。
- 管理端：仅影响后续 UI 设计与验收规则，不修改运行时代码。
- Orval：无。
- Docker Compose：无。

## 后续建议

后续可评估是否将轻量浮层的退出路径、确认按钮使用理由纳入 prototype UI Gate 或 UI Contract 模板检查。
