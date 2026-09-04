---
change_id: enforce-openapi-client-generator-dependency-check
created_at: 2026-08-27 08:06:17
updated_at: 2026-08-27 08:06:17
---

# 设计说明

## 依赖检查策略

`scripts/generate-openapi-client.sh` 先导出 OpenAPI 契约，再进入客户端生成阶段。客户端生成阶段按以下顺序判断：

- 若 `pnpm` 可用，先运行 `pnpm --dir src/web --version` 触发项目包管理器版本校验；若当前 pnpm 与 `src/web/package.json` 的 `packageManager` 不一致，输出版本对齐提示后停止。
- 若缺少 `src/web/orval.config.ts`，脚本停止 Orval 生成并提示已保留 `src/web/openapi.json`，要求补齐配置。
- 若本地 `node_modules/.bin/orval` 可执行，优先使用本地 Orval，避免依赖全局环境。
- 若 pnpm 版本可用且匹配，提示执行 `pnpm --dir src/web install` 或安装 Orval；不隐式联网安装。
- 若 `pnpm` 不可用，提示先启用 pnpm 或 Corepack，再执行安装命令。
- 若 `package.json` 未声明 Orval，提示补充 devDependency，避免 `pnpm exec` 临时下载造成锁文件和版本不可控。
- OpenAPI JSON 导出保持缩进和中文可读，降低生成物无语义 churn。

## 治理校验策略

`scripts/validate-api-standard.py` 增加聚焦检查：

- 确认 `generate-openapi-client.sh` 存在。
- 确认脚本包含 `pnpm` 缺失提示和版本错配提示。
- 确认脚本包含 Orval 缺失提示。
- 确认脚本说明 OpenAPI 导出已完成但客户端生成被跳过或阻断的 fallback 状态。
- 保留既有 route 元数据检查，同时识别 `APIRouter(..., tags=[...])` 的 router 级 tags，避免误报遮蔽客户端生成脚本检查结果。

## 边界

本变更只让本地生成链路更可诊断，不改变 OpenAPI 语义内容、接口契约、前端调用方式或生产构建流程。
