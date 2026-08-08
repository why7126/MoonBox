---
purpose: OpenSpec Change Trace
content: spec-study 本机路径脱敏追溯
created_at: 2026-08-07 11:55:25
updated_at: 2026-08-07 11:55:25
owner: MoonBox 产品团队
---

# Trace

status: applied
source: `/spec-opt 修正 spec-study 学习报告中的本机绝对路径隐私边界`
sprint: sprint-001
requirements: []
bugs: []

## 根因

现有规则把隐私边界描述为用户隐私数据、真实客户数据和可识别个人主体信息，但未显性列出本机绝对路径、系统用户名和用户主目录，导致学习报告在记录学习对象时保留了完整本地路径。

## 处理策略

- 学习对象持久化展示改为 `ProjectTilesFST（本地只读项目）`。
- 规范补充本机路径脱敏规则。
- 校验脚本增加 spec logs 与 active Change 隐私扫描。
