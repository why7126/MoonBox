---
purpose: 规范工程日志目录
content: spec-study 学习报告与 spec-opt 治理迭代日志的存放规则、命名约束和公开安全边界
created_at: 2026-08-07 00:00:00
updated_at: 2026-08-08 20:53:52
owner: MoonBox 产品团队
---

# Spec Logs

`docs/spec-logs/` 用于存放规范工程日志，包括 `/spec-study` 跨项目 Harness 学习报告，以及 `/spec-opt` 对本项目规范、技能、脚本、目录边界和校验规则的治理迭代日志。

`CHANGELOG.md` 是本目录的变更历史入口，用于按时间倒序汇总每一次规范、脚本、命令、目录边界和校验规则更新；单次变更的完整事实源仍以对应 `study` / `governance` 日志、OpenSpec Change、Sprint 四件套和正式规格为准。

## 命名规则

文件名 MUST 使用：

```text
YYYYMMDDhhmmss-study-xxx.md
YYYYMMDDhhmmss-governance-xxx.md
```

- `YYYYMMDDhhmmss`：报告生成时刻的 `Asia/Shanghai` 日期时间，精确到秒。
- `study`：`/spec-study` 跨项目学习报告。
- `governance`：`/spec-opt` 本项目规范、技能、脚本、目录边界或校验规则迭代日志。
- `xxx`：小写 kebab-case 主题，例如 `projecttilesfst`、`deployment-governance`、`usage-docs`、`spec-logs`。

历史日期级文件名（如 `YYYYMMDD-xxx.md`）也 SHOULD 迁移为时间戳级命名；新报告 MUST 使用时间戳级命名，避免同一天多次学习或治理迭代互相覆盖。

本目录不替代 `docs/standards/`、`docs/knowledge-base/`、`openspec/changes/`、`iterations/`、`releases/`、`deploy/` 或正式业务文档。

## 变更历史

- `CHANGELOG.md`：目录级变更历史索引，记录每次规范、脚本、命令、目录边界和校验规则更新摘要。
- `YYYYMMDDhhmmss-governance-xxx.md`：单次 `/spec-opt` 治理迭代日志。
- `YYYYMMDDhhmmss-study-xxx.md`：单次 `/spec-study` 学习报告。

## 去重规则

- 同一次 `/spec-study` 学习应用流程只生成一份正式 `study` 报告。
- 学习阶段候选内容不得另行落盘为第二份正式 `study` 报告；可保留在最终回复、active Change 文档或同一报告的阶段章节中。
- `/spec-study` 触发的治理资产应用结果必须汇总到同一份 `study` 报告，不得再额外生成内容重复的 `governance` 日志。
- 若同一学习对象、学习主题和用户确认批次已存在本流程报告，后续应用结果、验证结果或修正 MUST 更新同一文件。
- `/spec-opt` 每次独立治理变更 MAY 生成一份 `governance` 日志；同一治理变更的补充修正 SHOULD 更新同一日志。

## 边界

- 本目录只存放 `/spec-study` 学习报告和 `/spec-opt` 治理迭代日志。
- 不存放需求、BUG、Sprint 四件套、OpenSpec Change 事实源、正式规格、release 快照或部署 env。
- 不存放学习对象源码、密钥、真实客户数据、用户隐私数据、运行时数据库、依赖目录、构建产物、缓存、日志或临时文件。
- 不得记录可识别个人或客户主体的信息，包括但不限于姓名、手机号、邮箱、地址、证件号、账号 ID、访问令牌、订单原文、聊天原文、工单原文、截图中的个人信息和未脱敏日志。
- 不得记录本机绝对路径、系统用户名、用户主目录或可反推出个人环境的目录结构；本地学习对象 MUST 使用项目名或脱敏占位符，例如 `ProjectTilesFST（本地只读项目）`、`<local-project>/ProjectTilesFST`。
- 如确需说明隐私相关风险，MUST 使用脱敏占位符或聚合描述，例如 `<user-email>`、`<customer-id>`、`某类用户标识`，不得写入原始值。
