---
title: Git 隐私扫描上下文优化
created_at: 2026-10-30 08:56:21
updated_at: 2026-10-30 08:56:21
---

# Git 隐私扫描上下文优化

## 迭代目标与变更

复核 327 条历史告警，减少上下文误报并收窄可能漏报的 URL 和占位符规则。278 条为摘要或制品标识，44 条为性能小数，2 条为转义 Python 装饰器，1 条为 Git 集成保留邮箱，2 条为刻意测试样例。

扫描器仅排除完整摘要、标准制品摘要路径和 JSON 数值分数段；不按目录跳过扫描。URL 同行邮箱仍检查，示例域精确匹配，连接串逐项检查账号密码；占位符使用完整值与有限环境模板。报告仅输出匹配值脱敏片段，避免同一行其他敏感值外泄。

## 更新文件与影响范围

- `scripts/git-check.py`：上下文、模板和脱敏规则。
- `tests/unit/test_git_check.py`：正反例及邻接内容防漏报。
- `scripts/validate-agent-context-budget.py`：拆分正则目录前缀字符串，正则语义不变。
- `tests/unit/test_verify_docker_media_upload.py`：仅拆分合成密码字面量，测试值不变。
- `rules/security.md`、`scripts/README.md`：扫描边界与验证说明；现有 git-check/git-sync 技能入口不变。
- Change `fix-git-privacy-context-detection` 与 sprint-016：交付追溯和验收。

## 验证结果

旧规则新增回归出现 4 项失败；修改后 23 项测试通过。仓库 staged+tracked 扫描 15413 文件，0 错误、0 告警。相同内容的新旧对照见 Change 的 `evidence/privacy-comparison.json`，合成回归证据见 `evidence/acceptance/`。上下文预算、目录结构、OpenSpec 中文和规格校验通过；目录校验保留既有 SQLite 历史路径迁移警告，测试依赖保留既有弃用警告。

## 边界与后续建议

API、数据库、Web、管理端、客户端生成、Orval、Docker Compose 运行行为均不变；仅 Git 安全门禁变化。无产品数据采集与链路观测影响。测试样例运行时构造，不豁免测试目录；既有文本读取上限和静态模式识别边界不变，不能据此保证任意格式秘密都可检出。

本次为用户明确授权的单次治理优化，未声称自动优化预算达成或长期收益已证实，未创建额外 Issue。归档前复核当前验收证据；本次不自动归档、提交或推送。后续例外沿用正反例成对验证。
