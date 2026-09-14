---
purpose: 文档入口
content: MoonBox 文档导航
created_at: 2026-07-29 22:55:00
updated_at: 2026-09-13 23:43:10
owner: MoonBox 产品团队
---

# Docs

| 文档 | 用途 |
|---|---|
| `00-product-overview.md` | 产品定位、用户、问题、能力 |
| `01-architecture.md` | 架构、模块和数据流 |
| `02-deployment.md` | docker-compose、本地端口、环境变量 |
| `03-api-index.md` | REST API 模块与契约治理 |
| `04-database-design.md` | SQLite 数据域和迁移 |
| `05-compatibility-matrix.md` | 当前启用与未启用平台 |
| `07-object-storage-strategy.md` | 文档与图片资产存储 |
| `08-command-execution-order.md` | REQ/BUG、Sprint、OpenSpec、发布、镜像与产品手册命令执行顺序、Apply 连续执行/完成/续接契约、停止前决策与[行为验收](standards/apply-behavior-acceptance.md)、下一步参数规范和执行复盘 Hook |
| `pending-decisions.md` | 集中未决策事项 |
| `standards/` | API、认证、测试、上传、安全、产品数据采集、链路观测、原型驱动 UI 验收等专项标准 |
| `standards/product-data-collection-observability.md` | 行为事件、请求日志、Task Trace、流程节点、脱敏、保留周期和治理门禁 |
| `standards/task-trace-coverage.md` | MoonBox 任务链路候选场景、接入优先级和流程节点策略 |
| `../data/ai-usage/README.md` | AI Usage 本地 session JSONL 输入、脱敏派生事实、自动发现与历史回填边界 |
| `standards/prototype-ui-acceptance.md` | 带 prototype 的 UI Change 的 UI Contract、Skeleton、截图、computed style、Mock/API 和一致性验收清单 |
| `../rules/root-cause-evidence.md` | 问题排查、BUG 完善、验收返修和效果不符场景的证据化根因分析规则 |
| `knowledge-base/` | Sprint 复盘、经验和事故沉淀 |
| `spec-logs/` | 规范工程日志：`/spec-study` 学习报告使用 `YYYYMMDDhhmmss-study-xxx.md`，`/spec-opt` 治理迭代日志使用 `YYYYMMDDhhmmss-governance-xxx.md` |

- [Issue 分级元数据与同步规则](../rules/document-governance.md#issue-分级元数据)：REQ 优先级、BUG 严重度的 Frontmatter 范围与事实源。

- [Change 身份唯一性](../rules/document-governance.md#change-身份唯一性)：创建前占用检查、归档门禁及历史身份纠正。

- [本地取证日志目录](../rules/directory-structure.md#本地取证日志目录)：logs/ 忽略边界与归档证据转存。
