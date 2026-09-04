---
purpose: OpenAPI 客户端生成依赖提示治理
content: 记录 generate-openapi-client.sh 对 pnpm 缺失、pnpm 版本错配、Orval 和配置缺失时的提示、fallback 与校验脚本门禁
created_at: 2026-08-27 08:06:17
updated_at: 2026-08-27 08:12:00
owner: MoonBox 产品团队
---

# OpenAPI 客户端生成依赖提示治理

## 迭代目标

- 让 `scripts/generate-openapi-client.sh` 在 pnpm 缺失、pnpm 版本错配、Orval、本地二进制或 Orval 配置缺失时输出明确修复提示。
- 让脚本在 OpenAPI JSON 已导出但客户端生成无法继续时说明 fallback 状态，避免只暴露低层 shell 错误。
- 将该提示与 fallback 要求纳入 API 标准校验。

## 变更摘要

- `generate-openapi-client.sh` 增加 `WEB_DIR`、`OPENAPI_JSON`、`ORVAL_CONFIG`、`LOCAL_ORVAL` 和 `PACKAGE_JSON` 变量，统一输出依赖诊断。
- 脚本先导出 `src/web/openapi.json`，再检查 `orval.config.ts`、本地 Orval、pnpm 可用性、pnpm 版本匹配和 `package.json` 中的 Orval 声明。
- OpenAPI JSON 导出保留缩进和中文可读，避免运行脚本时产生整文件格式 churn。
- 依赖不满足时输出已导出契约路径、缺失原因、修复步骤和不隐式联网安装声明。
- `validate-api-standard.py` 增加对客户端生成脚本 pnpm / Orval 提示和 fallback 文案的静态检查。
- `validate-api-standard.py` 同步识别 `APIRouter(..., tags=[...])` 的 router 级 tags，避免既有误报遮蔽本次新增检查项。
- `docs/standards/openapi-rules.md` 补充客户端生成脚本依赖提示与 API 标准校验要求。

## 影响范围

- 影响治理脚本：`scripts/generate-openapi-client.sh`、`scripts/validate-api-standard.py`。
- 影响长期治理文档：`docs/standards/openapi-rules.md`。
- 影响 OpenSpec：`openspec/changes/enforce-openapi-client-generator-dependency-check/`。
- 影响 Sprint scope：`iterations/change/sprint-003/sprint.yaml`。
- 不影响后端 API 行为、DB、Web、管理端、客户端运行时代码或 Docker Compose。

## 更新文件

- `scripts/generate-openapi-client.sh`
- `scripts/validate-api-standard.py`
- `docs/standards/openapi-rules.md`
- `openspec/changes/enforce-openapi-client-generator-dependency-check/`
- `iterations/change/sprint-003/sprint.yaml`
- `docs/spec-logs/20260827080617-governance-openapi-client-generator-dependency-check.md`
- `docs/spec-logs/CHANGELOG.md`

## 验证结果

- `bash -n scripts/generate-openapi-client.sh`：通过。
- `scripts/generate-openapi-client.sh`：预期失败；OpenAPI JSON 已导出，客户端生成因缺少 `src/web/orval.config.ts` 被明确阻断，并输出 pnpm/Corepack、安装依赖、补 Orval 和补配置提示。
- `python scripts/validate-api-standard.py`：通过。
- `python scripts/validate-agent-context-budget.py`：通过。
- `python scripts/validate-openspec-language.py`：通过。
- `python scripts/validate-directory-structure.py`：通过。
- `openspec validate enforce-openapi-client-generator-dependency-check`：通过。
- `python scripts/sync-workflow-status.py --event opsx.apply --change enforce-openapi-client-generator-dependency-check --sprint auto`：通过。
- `python scripts/extract-ai-usage.py --post-command-hook --workflow-event opsx.apply --change enforce-openapi-client-generator-dependency-check --sprint sprint-003 --json`：已执行，返回 warning；`usage_mode: unavailable`，原因是当前会话没有可持久化 token_count 事件。

## API/DB/Web/客户端/管理端/Orval/Docker Compose 影响

- API：不适用；未改变接口路径、请求头、响应字段、错误码或安全声明。
- DB：不适用；未改变 schema、迁移、索引、保留周期或数据采集表。
- Web：不适用；未改变 Web 运行时页面、请求封装或交互。
- 客户端：不适用；未生成或提交客户端运行时代码，只补强生成脚本提示。
- 管理端：不适用。
- Orval：适用；补强 pnpm 版本错配、Orval 依赖缺失、配置缺失和本地二进制缺失时的诊断与 fallback 提示。
- Docker Compose：不适用。

## 后续建议

后续若正式启用 Orval 客户端生成，应补齐 `src/web/orval.config.ts` 和 `orval` devDependency，并重新运行 `./scripts/generate-openapi-client.sh`。
