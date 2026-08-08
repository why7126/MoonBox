---
purpose: OpenSpec Change Design
content: docs/spec-logs 变更历史文档设计
created_at: 2026-08-08 20:53:52
updated_at: 2026-08-08 20:53:52
owner: MoonBox 产品团队
---

# Design

## 设计决策

`docs/spec-logs/CHANGELOG.md` 作为目录级索引文档，只记录治理资产演进摘要、更新文件、验证结果和下一步建议，不承载单次变更的完整事实源。单次事实源仍保留在对应的 `YYYYMMDDhhmmss-governance-xxx.md` 或 `YYYYMMDDhhmmss-study-xxx.md` 文件中。

## 内容结构

- Frontmatter：记录文档目的、内容范围、创建和更新时间。
- 记录规则：说明新增条目的触发条件、推荐字段和隐私边界。
- 变更历史：按时间倒序记录每次治理更新。

## 安全边界

`CHANGELOG.md` 不得写入用户隐私数据、真实客户数据、密钥、访问令牌、未脱敏日志、订单原文、聊天原文、工单原文、截图中的个人信息、本机绝对路径、系统用户名或用户主目录。
