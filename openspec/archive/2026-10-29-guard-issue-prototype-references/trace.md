---
title: Issue 原型引用保护追溯
created_at: 2026-10-29 06:49:32
updated_at: 2026-10-29 06:55:55
change_id: guard-issue-prototype-references
status: applied
iteration: sprint-014
execution:
  schema_version: 1
  started_at: 2026-10-29 06:49:33
  completed_at: 2026-10-29 06:55:55
  last_event: opsx.apply
---

# Issue 原型引用保护追溯

## 来源与范围
来源为用户明确 /spec-opt 授权，承接只读 explore 的脚本覆盖边界发现。无 REQ/BUG 来源。用户选择 sprint-014，估算 1 人天，纳入后 34/30，保留超容量风险，不新增业务 Issue。

product_data_collection_observability: N/A

affected_layers: 治理文件引用检查；不改变产品日志、Task Trace、API、DB 或数据采集。

validation: 原型引用与既有迁移回归43项通过；5项自动验收通过，见验证记录。

## 入口矩阵
| 入口 | 数据与环境 | 正向/拒绝 | 验证 |
|---|---|---|---|
| 直接迁移 CLI | 仓库本地静态文件；隔离夹具 | 正常、断链、dry-run、后检失败及重试 | AC-REF |
| 归档包装入口 | 同一底层迁移入口 | 引用门禁先于状态修复 | AC-REF |
| 产品 UI/部署 | N/A，无业务变更 | N/A | 不要求浏览器或 Docker |

## 验证记录
- 43项隔离与既有迁移回归通过（新增19项），覆盖预检、后检故障、重试、只读预览、关联引用、历史排除与局部阻断；pytest 报既有依赖弃用提示。
- 上下文预算、当前 Change 中文优先与全仓残留分离、目录结构、OpenSpec validate、中文标题及 diff 空白校验通过；Sprint scope 校验通过。
- 当前证据：[自动验收报告](evidence/acceptance/20261029065518858106-1477853a/summary.md)，5项全部 passed，受影响 AC-REF 重跑，4项按有效输入复用。
- 真实 REQ-0042 当前目录只读探针零阻断；未迁移正式 Issue。首次探针发现 prototype.html 被截断，修复匹配边界后新增独立回归并复核。
- 后检与重试复核旧阶段的外部引用，包装入口覆盖已迁移目标，不能用 already archived 跳过门禁。
- Docker reap 只读扫描因 daemon 不可用受阻，未创建或删除容器，不影响静态脚本验证。
- 本次为用户明确单次授权治理任务，未伪装为自动预算准入；真实迁移效果与净用量收益待观察。

