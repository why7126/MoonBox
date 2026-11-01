---
title: 归档历史声明恢复
created_at: '2026-11-01 00:06:57'
updated_at: '2026-11-01 00:06:57'
---
# 归档历史声明恢复
## 目标和变更
修复BUG-0073已迁移归档后，验收前历史声明触发当前态阻塞。恢复记录绑定全文和行号，只处理trace验收结论的完整精确句，不修改历史证据。独立Change为fix-archive-historical-closure，纳入sprint-018。
## 更新文件与影响范围
archive_closure_restoration.py、archive_finalization.py、tests/unit/test_archive_closure_restoration.py、scripts/README.md、opsx-archive技能及Change证据。API、DB、Web样式、客户端、管理端、Orval、Docker Compose均无变化。
## 验证
70项聚焦测试通过；BUG-0073真实恢复wrapper返回finalized，15份文档无发现、原交付不变。未知措辞、同段失败、非目标章节、证明失配继续阻断。测试中修正既有历史章节review断言，未降低门禁。
## 后续建议
验收记录应显式标记阶段，减少状态歧义；本次未扩展未知措辞。用量收益未测量，不宣称收益确认。
