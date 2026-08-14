---
req_id: REQ-0009-git-check-pre-push-security-gate
status: archived
created_at: 2026-08-09 07:12:28
updated_at: 2026-08-14 08:52:18
recorded_by: product
source: 用户输入
priority_hint: P1
parent_requirement:
---

# 一句话

新增 `git-check` 推送前安全检测命令，在代码推送到 Git 仓库前检查隐私数据、真实环境文件、运行时数据、数据库文件、大文件、密钥/Token/连接串、本机绝对路径和不应进入 Git 的本地数据，并复用现有 env ignore 校验。

# 原始描述

新增 git-check 推送前安全检测命令，用于检查 staged/tracked 文件中的隐私数据、真实环境文件、运行时数据、数据库文件、大文件、密钥/Token/连接串、本机绝对路径和不应进入 Git 的本地数据，并复用现有 env ignore 校验。

# 待澄清

- [ ] 命令定位：仅作为 Agent 命令 `/git-check` 使用，还是同时接入 Git `pre-push` hook。
- [ ] 扫描范围：默认只扫描 staged/tracked 文件，还是支持可选全仓扫描。
- [ ] 阻断策略：发现高危项时是否直接失败，低置信疑似项是否仅 warning。
- [ ] 大文件阈值、允许名单和误报豁免机制。

# 探索结论

（/req-explore 后人工确认写入）
