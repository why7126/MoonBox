---
req_id: REQ-0022-local-project-import-product-iteration
status: captured
created_at: 2026-08-19 15:24:24
updated_at: 2026-08-19 15:24:24
recorded_by: product
source: explore
priority_hint: P1
parent_requirement:
---

# 一句话

支持将本地存量项目导入 MoonBox，并在产品内完成从需求治理到 Codex 执行、验收和归档的迭代闭环。

# 原始描述

用户希望记录需求：“本地存量项目导入 MoonBox 并支持产品内迭代闭环”。

前置探索结论显示：当前 MoonBox 已具备空间管理、需求中心、REQ/BUG/Sprint/OpenSpec 治理事实源聚合和卡片动作命令映射，但尚未形成“导入本地项目后，由产品直接调度 Codex 执行并回写状态”的完整闭环。

# 待澄清

- [ ] MVP 是否先支持“本地路径导入 + 治理事实源读取”，还是直接支持 Git 仓库导入。
- [ ] 产品内迭代闭环是否必须包含真实 Codex 任务调度、执行日志、失败重试、人工审批和状态回写。
- [ ] 导入后的项目与空间、产品、仓库、工作区、分支和权限之间的数据模型边界。
- [ ] 本地路径、仓库内容、执行日志和 AI 会话数据的安全脱敏、访问控制和持久化策略。
- [ ] 首版是否允许 Codex 执行仍在本地客户端完成，产品只作为治理驾驶舱和命令引导入口。

# 探索结论

当前倾向将该需求作为一个产品化交付单元推进：先定义“存量项目导入 MoonBox”的项目/工作区模型，再逐步补齐产品内需求治理、Sprint、OpenSpec、Codex 执行桥接、日志回写、验收和归档闭环。MVP 可优先落在治理接入与产品看板，后续增强真实 Codex 调度与 Git 生命周期。
