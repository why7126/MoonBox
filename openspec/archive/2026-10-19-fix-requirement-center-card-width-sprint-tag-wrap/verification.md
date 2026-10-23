---
title: 需求中心卡片扩宽实施与验证记录
created_at: "2026-10-19 09:38:51"
updated_at: "2026-10-19 09:38:51"
---

# 需求中心卡片扩宽实施与验证记录

## 实施结果

共用九列从 320px 调整为 380px；Sprint 标签 nowrap、flex-shrink: 0；ID min-width: 0、overflow-wrap: anywhere。未修改数据、请求、阶段逻辑或弹层组件。

## 验证记录

- TypeScript：在 src/web 执行 node node_modules/typescript/bin/tsc -b，退出 0。
- 浏览器：node src/web/tests/requirement-center-card-width.cjs，九阶段×1440/768 双视口共 18 组通过；需求、BUG、Change、短 ID、长 ID、80 字符无空格 ID、无标签、空列、文档与进度抽屉打开/关闭均覆盖。
- 负向基准：LAYOUT_BASELINE=1 恢复旧样式，断言因期望 380、实际 320 正确失败（退出 1）；不修改产品源码。
- 视觉：已目视检查 done-1440.png 与 done-768.png，长 ID 在左侧换行，标签单行，末列可达；逐阶段证据和计算样式位于 evidence/acceptance/layout/。
- 自检修复：旧夹具拦截路径过宽和缺少当前迭代元数据导致空卡片；已限制 /api/v1/ 并补齐 planning 迭代元数据，后续补全动作前置文档后重验通过。

## 证据边界

浏览器使用真实组件与当前工作区 CSS，API 为隔离合成响应，不写业务数据。同会话原部署 /requirements 的 1440px 基准仍为 320px，刷新后未加载当前工作区变更，未宣称原部署已更新。本次不部署或重启服务。UI Skeleton 复用已确认设计与现有骨架，未改变区域或交互布局。

## 文档一致性与知识库

父需求历史原型为既有基线，本 BUG 经用户批准覆盖卡片列宽与文字折行两项；其他设计不变。父需求正文未固定本次列宽，追溯中补充修复覆盖关系。API、数据库、部署、安全、客户端生成均无需同步。product_data_collection_observability 为 N/A，原因和验证详见 design.md。

本次是标准 flex 文本空间分配修复，已有原型视觉验收最佳实践覆盖，暂无需独立新增 incidents 文档；保留本记录便于复用。

## 本地部署复核（2026-10-19 10:14）

按用户部署更新请求重建并启动 Web 容器，镜像摘要为 `sha256:3a9040e3e125016571e1b180664e7bab0df24fceb6b483600bf9b65dcc2195ba`。构建中的 TypeScript 与 Vite 检查通过。Chat 扩展 Compose 依赖启动脚本环境变量，直接组合解析失败后改用根 Compose 定义，仅更新 Web 服务，执行成功。

刷新实际部署的 `/requirements` 页面后，九阶段网格各列 computed width 均为 380px；两个 Sprint 标签均为 `white-space: nowrap`、`flex-shrink: 0`，高度 20.5px。长 Change ID 自动分行，Sprint 标签保持单行。实际部署截图：`evidence/acceptance/deployed-web.jpg`。本次实际观察补充此前隔离源码验收的部署边界；无需 API、数据库迁移或客户端生成。
