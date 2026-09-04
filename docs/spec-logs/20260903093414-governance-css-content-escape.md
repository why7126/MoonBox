---
purpose: 规范工程治理日志
content: CSS content 非 ASCII escape 写法治理记录
created_at: 2026-09-03 09:34:14
updated_at: 2026-09-03 09:34:14
owner: MoonBox 产品团队
---

# CSS content 非 ASCII escape 写法治理

## 迭代目标

将 CSS `content` 中的非 ASCII 符号统一为 escape 写法，避免不同渲染、截图、字体 fallback、压缩或编码链路中出现符号漂移。

## 变更摘要

- 在 `rules/ui-design.md` 新增 CSS `content` 生成内容规则。
- 扩展 `scripts/validate-design-system.py`，扫描 `.css` 文件中 `content` 字符串内的原始非 ASCII 字符。
- 新增 `tests/unit/test_validate_design_system.py`，覆盖违规与豁免样例。
- 新增 OpenSpec Change `enforce-css-content-ascii-escape` 并纳入 `sprint-004`。

## 影响范围

- UI 规范：CSS 伪元素和样式生成内容。
- 治理脚本：设计系统校验。
- OpenSpec：设计系统校验能力 delta spec。
- 业务实现：N/A，本次不修改业务 `src/` 运行时代码。

## 更新文件

- `rules/ui-design.md`
- `scripts/validate-design-system.py`
- `tests/unit/test_validate_design_system.py`
- `openspec/archive/2026-09-03-enforce-css-content-ascii-escape/`
- `docs/spec-logs/20260903093414-governance-css-content-escape.md`
- `docs/spec-logs/CHANGELOG.md`
- `iterations/change/sprint-004/`

## 验证结果

- `uv run pytest tests/unit/test_validate_design_system.py`：3 passed。
- `python scripts/validate-design-system.py`：通过。
- `python -m py_compile scripts/validate-design-system.py`：通过。
- `python scripts/validate-agent-context-budget.py`：通过。
- `python scripts/validate-openspec-language.py`：通过。
- `python scripts/validate-directory-structure.py`：通过。
- `openspec validate enforce-css-content-ascii-escape`：通过。
- `python scripts/validate-sprint-scope.py sprint-004 --item enforce-css-content-ascii-escape`：通过。
- `python scripts/sync-workflow-status.py --event opsx.apply --change enforce-css-content-ascii-escape --sprint auto`：通过，无需派生文档更新。
- `scripts/archive-change.sh enforce-css-content-ascii-escape`：通过，已归档到 `openspec/archive/2026-09-03-enforce-css-content-ascii-escape/` 并合并 `design-system` 正式规格。
- `python scripts/sync-workflow-status.py --event opsx.archive --change enforce-css-content-ascii-escape --sprint auto`：通过，更新 `sprint-004` 派生文档。
- AI Usage hook：warning，当前会话无可持久化 command-run token 事件，Sprint 快照跳过。

## API/DB/Web/客户端/管理端/Orval/Docker Compose 影响

- API：N/A，未调整接口。
- DB：N/A，未调整数据模型或迁移。
- Web：仅新增 UI CSS 写法治理，不改运行时代码。
- 客户端生成：N/A，未调整 OpenAPI 或 Orval。
- 管理端：仅受设计系统校验规则约束，不改页面实现。
- Orval：N/A。
- Docker Compose：N/A。

## 后续建议

- 后续如引入 CSS-in-JS 或样式模板字符串，可评估把同类检查扩展到受控样式模板。
