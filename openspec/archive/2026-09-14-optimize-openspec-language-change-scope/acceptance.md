---
created_at: 2026-09-14 15:20:11
updated_at: 2026-09-14 15:47:29
acceptance_status: passed
---

# 验收标准

## 功能验收

- `python scripts/validate-openspec-language.py --change optimize-openspec-language-change-scope` 只校验目标 Change，并在目标文档中文优先时通过。
- `python scripts/validate-openspec-language.py --change __missing__` 对不存在 Change 返回失败，且输出包含目标不存在的说明。
- `python scripts/validate-openspec-language.py --change optimize-openspec-language-change-scope --residual-report` 在当前 Change 通过时返回成功，并把其他 Change 的中文残留作为分离报告输出。
- `python scripts/validate-openspec-language.py` 未传 `--change` 时保持全量 active Change 校验行为。
- `python scripts/validate-openspec-language.py --include-archive --change <已归档 Change ID>` 可校验归档 Change。
- `bash scripts/validate-openspec.sh --change optimize-openspec-language-change-scope --residual-report` 可聚焦运行当前 Change 中文优先校验与 `openspec validate`。
- `bash scripts/validate-openspec.sh --include-archive --change optimize-openspec-language-change-scope --residual-report` 可聚焦校验归档 Change 中文优先文档，并校验已合并的正式规格结构。
- `bash scripts/validate-openspec.sh --change __missing__` 对不存在 Change 返回失败，且不会静默跳过结构校验。

## 治理验收

- 目标 Change 已纳入 `sprint-006`。
- `openspec validate optimize-openspec-language-change-scope` 通过。
- `python scripts/validate-sprint-scope.py sprint-006 --item optimize-openspec-language-change-scope` 通过。
- 治理日志和 `docs/spec-logs/CHANGELOG.md` 已同步。

## 不适用说明

- API、数据库、Web、管理端、客户端生成、Docker Compose、安全和对象存储验收不适用；本次不触达相关实现或契约。
