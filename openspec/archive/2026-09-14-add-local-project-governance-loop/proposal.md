---
change_id: add-local-project-governance-loop
requirement_id: REQ-0022-local-project-import-product-iteration
created_at: 2026-09-11 09:05:00
updated_at: 2026-09-11 09:08:59
---

## 变更背景

Chat 已在独立副本执行，需求中心已读取治理文件，但两者尚未形成同项目的真实成果回流。以 MoonBox 一个本地项目贯通需求卡、关联 Chat、审阅应用和自动刷新，验证最小产品闭环。

## 变更内容

- 建立共用空间/仓库身份的项目治理查询，取消需求中心业务读取对全局目录的隐式依赖。
- 需求中心按项目自动刷新，保留草稿和最近完整快照；卡片进入本人关联 Chat，不自动发送。
- 引入受控治理基准、不可变成果、显式应用、内容冲突检查、串行写入和持久恢复。
- 首个可应用动作限定 req-generate，其他治理动作不在本期开放；需求对象与 registry、trace、索引联动。
- **BREAKING**：需求中心数据与文档请求需携带授权空间和仓库身份；保存需带版本。不再接受会隐式读取全局治理目录的无作用域请求。Web 与 API 同步部署。
- 保留单机、单项目验证范围；不新增通用代码合并、远程导入、自动 Git 提交/推送或生产升级。

## 能力范围

### 新增能力

- `local-project-governance-loop`：项目与会话关联、治理基准及成果受控应用、冲突恢复和真实闭环验收。

### 修改能力

- `web-catalog-requirement-center-real-data`：上下文与事实源按授权项目聚合，自动刷新和版本保护，部署使用分离的只读聚合与受控写入通道。

## 影响范围

后端需求中心聚合/文档接口、Chat 仓库绑定及执行准备、Web 需求中心和 Chat 增量 UI、SQLite/MySQL 应用记录、单机部署目录权限与日志观测。复用 REQ-0025 既有会话、隔离执行、鉴权、备份；不重建凭证体系。API 变更同步 OpenAPI/Orval 和 docs/03-api-index.md；数据库变化同步 docs/04-database-design.md 与迁移测试。

来源：REQ-0022，已纳入 sprint-005，估算8人天。需求文档 Partially Ready 的残余仅为实施阶段 Skeleton/视觉/真实运行证据；设计与交付承接 review RC-001至004。
