---
title: 跨入口后继证明与执行保护收敛修复提案
created_at: '2026-10-21 16:11:48'
updated_at: '2026-10-21 16:11:48'
---

# 跨入口后继证明与执行保护收敛修复提案

## 背景

来源[BUG-0061](../../../issues/bugs/review/BUG-0061-cross-entry-continuation-guard-convergence/bug.md)，已批准并纳入sprint-012，估算8人天。产品原apply仅progress，CLI续接完成后因旧证明不等于当前清单而持续阻断；dry-run分号边界误识别使外层退出0被观察为同步成功。根因10项证据确认，19项累计差异的历史行级归因保持partial。

## 变更内容

- 独立后继交付证明与版本化安全恢复，保留原未完成执行事实。
- 明确正式同步事件、写入模式与实际结果，拒绝dry-run/check、内部失败外层0及仅start/progress冒充完成。
- 差异分类、当前阶段/旧结果/当前准入分离、产品与CLI共享准入。
- 并发、权限、缺证与真实冲突回归，以及产品实际发送归档、CLI对照和BUG-0055跨迭代现场恢复。

## 能力影响

### 新增能力

无新增独立能力域。

### 修改能力

- governance-command-durable-recovery：扩展动作级证明与当前签认；新增后继证明、同步观察可信性和实际归档验收契约。

## 影响范围

governance/direct_command_journal、direct_completion、execution_context、execution_guard、completion_handoff、reader与发送准入；共享CLI同步/归档协议、API错误原因、Web核验入口及生成客户端。实施阶段明确持久记录schema与双数据库兼容，不直接变更已生效规格。BUG-0052/0060作为已归档兼容基线；BUG-0055排序功能范围不迁入。

## 回滚方案

应用版本回退保持原历史与新增证明记录，不回写历史成功、不删guard。旧版本不支持的新证明版本拒绝自动放行；归档迁移若部分完成沿专用日志恢复，不倒退目录或重复合并。发布和正式对象操作以相应授权及当前门禁为准。
