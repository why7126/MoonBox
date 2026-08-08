---
purpose: OpenSpec Change Design
content: spec-logs 跨项目落地提示词列设计
created_at: 2026-08-08 21:01:51
updated_at: 2026-08-08 21:01:51
owner: MoonBox 产品团队
---

# Design

## 设计决策

`CHANGELOG.md` 的“跨项目落地提示词”列用于承载短句 Prompt，帮助其他项目复用 MoonBox 的治理经验。该列应避免写入本机路径、个人信息或项目私有细节，并鼓励其他项目按自己的规则、目录和 OpenSpec/Sprint 流程落地。

## 字段约束

- Prompt SHOULD 使用可复制的一句话或短段落。
- Prompt SHOULD 明确目标文件或治理能力，但不得要求照搬本项目私有路径。
- Prompt MUST 提醒遵守目标项目自身的规范、OpenSpec 和验证流程。
- Prompt MUST NOT 包含用户隐私数据、真实客户数据、密钥、访问令牌、未脱敏日志、本机绝对路径、系统用户名或用户主目录。
