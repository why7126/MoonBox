---
purpose: OpenSpec Change Design
content: spec-study 本机路径脱敏设计
created_at: 2026-08-07 11:55:25
updated_at: 2026-08-07 11:55:25
owner: MoonBox 产品团队
---

# Design

## 脱敏口径

学习对象在长期文档、study 报告和 active Change trace 中只记录可公开识别的项目级标识：

- 推荐：`ProjectTilesFST（本地只读项目）`
- 可选：`<local-project>/ProjectTilesFST`

禁止记录：

- `/Users/<name>/...`、`/home/<name>/...` 等本机绝对路径。
- 真实系统用户名、用户主目录和可反推出个人环境的目录结构。
- 学习对象源码、密钥、未脱敏日志或真实客户数据。

## 校验策略

在 `scripts/validate-agent-context-budget.py` 中增加治理隐私扫描，聚焦检查：

- `docs/spec-logs/**/*.md`
- `openspec/changes/**/trace.md`
- `openspec/changes/**/proposal.md`
- `openspec/changes/**/design.md`
- `openspec/changes/**/tasks.md`
- `openspec/changes/**/acceptance.md`

扫描命中未脱敏用户主目录或系统临时目录时失败。脚本自身和归档历史暂不纳入，避免误伤实现正则或历史归档快照。

## 影响范围

- API：无影响。
- 数据库：无影响。
- Web：无业务实现影响。
- 客户端：无影响。
- 管理端：无业务实现影响。
- Orval：不需要。
- Docker Compose：无影响。
- 测试：运行治理校验和 OpenSpec 校验。
