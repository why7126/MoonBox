---
title: Git 隐私扫描优化追溯
created_at: 2026-10-30 08:49:30
updated_at: 2026-10-30 08:56:42
change_id: fix-git-privacy-context-detection
status: applied
sprint: sprint-016
iteration: sprint-016
product_data_collection_observability:
  status: not_applicable
  affected_layers: []
  reason: 仅本地静态Git扫描，不涉及产品采集与观测。
  validation: 扫描测试与真实仓库对照。
execution:
  schema_version: 1
  started_at: 2026-10-30 08:49:31
  completed_at: 2026-10-30 08:56:42
  last_event: opsx.apply
---

# Git 隐私扫描优化追溯

## 授权与基线

用户明确执行spec-opt；本次单次任务授权覆盖实施，不声明自动优化预算或收益已满足。当前基线327告警、0错误；真实扫描与合成对抗测试分别报告。

## 验证记录

- 同一 HEAD 内容旧版 327 条，325 条通过有限上下文排除，另 2 条刻意隐私样例保留检出；工作区测试改为运行时拼接后全仓 15413 文件扫描 0 错误、0 告警。
- 分类：278 摘要/制品标识、44 性能小数、2 转义装饰器、1 Git 集成保留邮箱、2 测试样例。详见 [对照统计](evidence/privacy-comparison.json)。
- 23 项回归通过，覆盖 URL 同行邮箱、伪示例域、占位子串、非安全默认值、相邻真实手机号、数据库凭据、Bearer/Cookie、报告脱敏；原规则新增用例 4 项失败证明回归有效。
- [自动验收报告](evidence/acceptance/20261030085539148440-40211107/summary.md) passed；仅命令级证据，本任务无需真实产品或视觉证据。
- 上下文预算、目录结构、OpenSpec 规格与中文、中文标题、Sprint 范围、diff 空白检查通过；保留既有 SQLite 历史路径及测试依赖弃用警告。
- 不修改业务 API、数据库、UI、部署或客户端生成。并发工作区中的业务和归档改动不属于本任务，保持不动。
- 原有 1 MiB 文本读取上限和启发式识别边界保留，不声明完整秘密检出保障。用户尚未授权本 Change 归档或本轮提交推送。
