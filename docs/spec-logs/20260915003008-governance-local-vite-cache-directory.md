---
purpose: 本地 Vite 缓存目录结构治理日志
content: 记录根目录 .vite 本地缓存的 Git 忽略、目录结构校验和治理边界
created_at: 2026-09-15 00:30:08
updated_at: 2026-09-15 00:36:00
owner: MoonBox 产品团队
---

# 本地 Vite 缓存目录结构治理日志

## 迭代目标

修复根目录 `.vite/` 本地缓存导致 `scripts/validate-directory-structure.py` 报“未登记目录”的问题，同时保持正式顶层目录白名单严格。

## 变更摘要

- `.gitignore` 增加 `.vite/`。
- `scripts/validate-directory-structure.py` 将 `.vite` 纳入根目录本地忽略集合。
- `rules/directory-structure.md` 新增本地工具缓存目录边界。
- OpenSpec delta spec 记录 `.vite/` 不属于正式项目目录，不能作为长期事实源。

## 影响范围

- Git 忽略边界。
- 目录结构校验脚本。
- 目录结构规范。
- OpenSpec `harness-runtime` 目录边界规格。

## 更新文件

- `.gitignore`
- `scripts/validate-directory-structure.py`
- `rules/directory-structure.md`
- `openspec/archive/2026-09-15-ignore-local-vite-cache-directory/`
- `iterations/change/sprint-006/`
- `docs/spec-logs/CHANGELOG.md`

## 验证结果

- 通过：`python scripts/validate-directory-structure.py`
- 通过：`python -m py_compile scripts/validate-directory-structure.py`
- 通过：`python scripts/validate-agent-context-budget.py`
- 通过：`python scripts/validate-openspec-language.py --change ignore-local-vite-cache-directory --residual-report`
- 通过：`openspec validate ignore-local-vite-cache-directory --strict`
- 通过：`python scripts/validate-sprint-scope.py sprint-006 --item ignore-local-vite-cache-directory`
- 通过：`python scripts/sync-workflow-status.py --event opsx.apply --change ignore-local-vite-cache-directory --sprint auto`
- 通过：`bash scripts/archive-change.sh ignore-local-vite-cache-directory`
- 通过：`python scripts/validate-archive-evidence.py --change ignore-local-vite-cache-directory --archive-path openspec/archive/2026-09-15-ignore-local-vite-cache-directory`
- 通过：`python scripts/sync-workflow-status.py --event opsx.archive --change ignore-local-vite-cache-directory --sprint auto`
- 通过：`python scripts/promote-issues-for-archive.py --change ignore-local-vite-cache-directory --reason "/opsx-archive ignore-local-vite-cache-directory"`
- 通过：`openspec validate --all --strict`
- Warning：AI Usage hook 未发现可归因 command-run token 事件，`usage_mode: unavailable`。

## API/DB/Web/客户端/管理端/Orval/Docker Compose 影响

不适用。本次只调整本地目录治理、Git 忽略边界和校验脚本，不改变运行时业务实现、接口契约、数据库 schema、前端页面、管理端、客户端生成、Orval 或 Docker Compose。

## 后续建议

若后续出现新的根目录工具缓存，先确认是否可被 Git 忽略且不承载长期事实，再通过独立治理变更纳入忽略边界。
