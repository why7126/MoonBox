---
change_id: enforce-openapi-client-generator-dependency-check
type: update
status: applied
created_at: 2026-08-27 08:06:17
updated_at: 2026-08-27 08:12:00
---

# 补强 OpenAPI 客户端生成依赖提示

## 背景

`scripts/generate-openapi-client.sh` 负责导出 FastAPI OpenAPI 契约并触发 Orval 客户端生成。旧脚本直接调用 `src/web/node_modules/.bin/orval`，当 `pnpm install` 未执行、`pnpm` 不存在、pnpm 当前版本与 `packageManager` 不一致、Orval 未声明或生成配置缺失时，只会暴露低层 shell 错误，不便开发者判断该对齐包管理器版本、安装依赖、补配置还是只复用已导出的 `openapi.json`。

## 目标

- 在 OpenAPI 客户端生成脚本中补充 `pnpm` 可用性、pnpm 版本匹配、本地 Orval、包声明和 Orval 配置的显式检查。
- 当 Orval 客户端生成条件不足时，保留已完成的 `src/web/openapi.json` 导出，并输出可执行修复提示。
- 在 API 治理校验中加入脚本依赖提示与 fallback 的检查项，防止脚本退回低层报错。
- 同步 OpenAPI 长期治理文档和治理日志。

## 非目标

- 不修改后端 API 行为、响应字段、数据库结构、Web 或管理端运行时代码。
- 不自动安装 pnpm、Orval 或改写前端依赖锁文件。
- 不生成或提交新的客户端生成产物。

## 影响范围

```yaml
impact:
  backend: false
  web: false
  miniapp: false
  admin: false
  database: false
  storage: false
  api: false
  governance: true
  orval: true
```

## 产品数据采集与链路观测声明

```yaml
product_data_collection_observability:
  status: not_applicable
  affected_layers: []
  reason: "本次只补强本地 OpenAPI 客户端生成脚本的依赖提示、fallback 与治理校验，不改变 API 请求头、响应字段、错误码、请求封装、行为事件、request_logs、usage_events、Task Trace 或数据库采集路径。"
  validation: "通过脚本自检、API 标准校验和 OpenSpec 校验确认变更范围限定在治理脚本与文档。"
```
