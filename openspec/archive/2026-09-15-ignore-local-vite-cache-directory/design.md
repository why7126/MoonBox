## 背景与现状

`.vite/` 是前端工具链的本地缓存目录，和 `tmp/`、`.pytest_cache/` 一样不应成为正式项目结构的一部分。目录结构校验的职责是阻断未治理的正式根目录，而不是因为已忽略的工具缓存阻断工作流。

## 目标

- 保留根目录正式目录白名单的严格性。
- 允许被 `.gitignore` 覆盖的根目录 `.vite/` 本地缓存存在。
- 不删除本地缓存，不移动缓存内容，不引入业务代码改动。

## 非目标

- 不放宽任意未知根目录。
- 不允许 `.vite/` 被提交、归档或写入长期文档作为事实源。
- 不修改前端构建配置或 Vite 行为。

## 设计方案

`.gitignore` 增加 `.vite/`，表达该目录是本地缓存。`scripts/validate-directory-structure.py` 的 `IGNORED_ROOT_NAMES` 增加 `.vite`，保持和现有 `.pytest_cache`、`.venv`、`tmp`、`logs` 一致的忽略策略。

`rules/directory-structure.md` 新增本地工具缓存目录说明，明确 `.vite/` 不属于正式项目目录，不能承载长期证据、密钥、真实客户数据或运行时数据库。

## 风险

| 风险 | 缓解 |
|---|---|
| 误把 `.vite/` 当作正式缓存资产 | 规则明确 `.vite/` 不属于正式项目目录，不得归档或提交。 |
| 后续出现其它工具缓存继续阻断 | 本次只处理已出现且可识别的 `.vite/`；新增缓存目录仍需单独治理。 |

## product_data_collection_observability

```yaml
status: not_applicable
affected_layers: []
reason: 仅修改目录结构规则、校验脚本、Git 忽略边界和 OpenSpec 文档，不触达 API、DB、请求日志、行为事件、Task Trace、Web/管理端请求封装或对象存储。
validation: 通过目录结构校验、上下文预算校验、OpenSpec 中文校验、目标 Change 校验、Sprint scope 校验和 Workflow Sync 校验确认。
```
