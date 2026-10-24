---
title: Git 路径误报修复与警告复核
created_at: 2026-10-24 21:09:27
updated_at: 2026-10-24 21:09:27
---

# Git 路径误报修复与警告复核

## 目标与变更

修复 git-sync 的路径误报。路径规则只排除用户名首位的正则分支分隔符，不豁免测试或业务文件；诊断测试夹具改用现有 example 占位符。清理 REQ-0050 验收文档和生效规格的末尾空行，此项仅格式调整，不改规格语义。

## 更新范围

scripts/git-check.py、tests/unit/test_git_check.py、src/backend/tests/test_archive_blocker_diagnostics.py、上述两份文档；治理 Change fix-git-scan-regex-false-positive 纳入 sprint-013，保留30人天容量。无 API、DB、Web、管理端、客户端生成、Docker Compose 或权限行为变化。

## 验证与警告复核

扫描器与诊断接口相关12项测试通过；已跟踪和暂存范围扫描0 error、229 warning。227条是验收清单及实现证据的哈希数字片段，2条是扫描器测试故意构造的邮箱与手机号；保留告警规则和样例，不批量忽略。OpenSpec、目录、Sprint和上下文校验结果以 Change trace 验证记录为准。

## 认证排查

远程采用 HTTPS，系统 credential helper 未返回 GitHub 凭据；环境未提供 GitHub Token，现有 SSH 身份认证被拒绝。用户选择自行登录后通知，未读取或保存凭据。

## 后续建议

仅记录当前修复质量，不宣称用量收益；登录恢复后重新 fetch 比较远端并推送。
