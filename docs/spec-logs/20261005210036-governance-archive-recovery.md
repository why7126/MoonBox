---
title: 产品 Agent 归档跨挂载恢复与串行闭环
created_at: 2026-10-05 21:00:36
updated_at: 2026-10-05 22:00:00
---

# 产品 Agent 归档跨挂载恢复与串行闭环

来源：BUG-0026、Change `fix-chat-platform-opsx-archive-source-permission`、sprint-008 AF-008。

直接证据：BUG-0027 执行端 Path.rename 返回 EXDEV；补救后目录已移动但状态未同步。运行中权限仅读取 active trace 的代码路径会在移动后撤销 archive scope，回归证明该缺陷。历史 stopped 的唯一来源仍需执行端日志确认。

治理脚本改为 shutil.move；唯一 archive、active 缺失时续跑验证，不重复合并。`--finalize` 串行完成验证、Workflow Sync、Issue promote、AI Usage；任何必需步骤失败停止后续写入。技能和产品执行 prompt 同步该约束；人工 fallback 仍要求 delta 自检、安全移动与同一恢复闭环。重复身份保留证据并阻断。

产品补证修复：Issue promote 目录迁移间隙保持同身份读取；无 HOME 时本机会话用量发现明确 unavailable；流式通知保持有界队列并背压等待，避免密集文字使 terminal 和 usage 丢失。

验证：Chat、用量、长运行、App Server、AI Usage 与脚本回归 88 passed、1 skipped；OpenSpec strict、中文与根因证据校验通过。真实产品恢复轮次正常 completed、结果可见、标准脚本 exit_code=0、最终账单 settled；没有绕过产品直接搬移 Issue。恢复复验不替代全新对象首次跨设备归档观察。

长期 API、数据库结构、可写目录和部署拓扑不变，无客户端生成或迁移。用量恢复不伪造缺失收据，沿用工具输出脱敏。完整返修台账见 Change acceptance-fixes.md。
