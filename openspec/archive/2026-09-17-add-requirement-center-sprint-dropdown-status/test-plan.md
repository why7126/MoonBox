---
change_id: add-requirement-center-sprint-dropdown-status
requirement_id: REQ-0032-requirement-center-sprint-dropdown-status
sprint_id: sprint-006
created_at: 2026-09-14 15:36:27
updated_at: 2026-09-14 18:11:58
---

# 测试计划

## 范围

验证需求中心 Sprint 筛选下拉新增状态展示后，后端上下文字段、前端筛选交互、加入迭代弹窗状态口径、OpenAPI/Orval 生成物、视觉布局和安全降级均符合 REQ-0032。

## 用例矩阵

| 编号 | 覆盖项 | 验证方式 | 结果 |
|---|---|---|---|
| TP-001 | 后端返回 `sprint_option_details`，覆盖规划中、进行中、已归档和状态待核实 | `uv run pytest tests/integration/api/test_requirement_center.py -q` | 通过 |
| TP-002 | 前端 Sprint 下拉展示状态徽标，并保持多选筛选与未知状态降级 | `./node_modules/.bin/vitest run src/requirement-center.test.tsx` | 通过 |
| TP-003 | TypeScript 类型与生成客户端兼容 | `./node_modules/.bin/tsc --noEmit` | 通过 |
| TP-004 | OpenAPI JSON 与 Orval 客户端同步 | `./scripts/generate-openapi-client.sh` 导出 OpenAPI；`./node_modules/.bin/orval --config orval.config.ts` 生成客户端 | 通过；pnpm/Corepack 缺失导致脚本内客户端步骤跳过，已用本地 Orval 二进制补跑 |
| TP-005 | 1440px 深色主题、390px 浅色窄屏、下拉打开态、unknown 状态和 computed style | `node tests/requirement-center-sprint-status.cjs` | 通过 |
| TP-006 | OpenSpec 变更合法性 | `openspec validate add-requirement-center-sprint-dropdown-status` | 通过 |
| TP-007 | 设计系统扫描 | `python scripts/validate-design-system.py` | 仓库既有 115 项违规；本次新增样式文件未出现在违规清单 |
| TP-008 | OpenSpec 中文优先扫描 | `python scripts/validate-openspec-language.py` | 仓库其他活动 Change 存在英文标题/任务项；本 Change 未出现在失败清单 |
| TP-009 | 验收返修：删除“已完成 / 归档”重复筛选项，子下拉贴近触发器 | `./node_modules/.bin/vitest run src/requirement-center.test.tsx -t "keeps per-Change progress\|shows traceable Sprint statuses"`；`node tests/requirement-center-sprint-status.cjs` | 通过；Playwright 采样 `popoverGapPx=6` |
| TP-010 | 需求中心测试文件全量回归观察 | `./node_modules/.bin/vitest run src/requirement-center.test.tsx --reporter=dot` | warning；76 passed、14 failed，失败集中在既有默认当前迭代筛选/旧文档按钮查询断言，非本次浮层与重复控件返修路径 |

## 观测与安全

本次实现扩展需求中心读聚合响应，不新增 DB 表、对象存储、后台任务或新的日志落库路径。`sprint_option_details.warning` 仅返回 `sprint_status_unknown`、`sprint_lifecycle_conflict` 等脱敏原因，不返回内部路径、原始 YAML、Markdown 正文、token、密钥或堆栈。

验收返修只调整前端筛选面板布局和重复控件，不新增 API、DB、日志字段、对象存储、权限或部署边界。
