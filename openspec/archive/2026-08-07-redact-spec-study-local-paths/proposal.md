---
purpose: OpenSpec Change Proposal
content: 修正 spec-study 学习报告中的本机绝对路径隐私边界
created_at: 2026-08-07 11:55:25
updated_at: 2026-08-07 11:55:25
owner: MoonBox 产品团队
---

# Proposal

## 背景

MoonBox 的两份 ProjectTilesFST study 报告，以及相关 active Change trace，记录了学习对象的本机绝对路径。路径中包含系统用户名和本地目录结构，虽然不是密钥或客户数据，但作为仓库持久化文档不符合当前隐私边界。

根因是现有 `spec-study` 与 `docs/spec-logs` 规则仅泛化描述“用户隐私数据”和“可识别个人主体信息”，没有把本机绝对路径、系统用户名和用户主目录写成显性禁止项。

## 目标

- 将现有 study 报告和相关 active Change trace 中的学习对象路径改为脱敏项目标识。
- 在 `/spec-study`、`docs/spec-logs` 与上下文预算规则中明确禁止记录本机绝对路径、系统用户名和用户主目录。
- 增加治理校验，阻断 `docs/spec-logs/` 与 active Change 中再次写入本机绝对路径。

## 非目标

- 不修改学习对象 ProjectTilesFST。
- 不修改业务 `src/`。
- 不改变 `/spec-study` 的学习矩阵、应用范围或报告命名规则。
