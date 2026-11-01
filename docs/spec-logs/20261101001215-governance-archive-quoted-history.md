---
title: 提案历史引用恢复
created_at: '2026-11-01 00:12:15'
updated_at: '2026-11-01 00:12:15'
---
# 提案历史引用恢复
## 目标和变更
共享收尾对提案背景的历史引用返回review。新增固定完整句式识别，继续绑定原证明、完整验收、全文和行号；只追加恢复记录，不改写原文。
## 文件与影响
共享archive_closure_restoration.py、tests/unit/test_archive_closure_restoration.py、脚本README、opsx-archive技能及fix-archive-quoted-history文档，纳入sprint-018。API、DB、Web、管理端、客户端、Orval、Docker Compose无变化。
## 验证
77项聚焦回归通过。真实fix-archive-historical-closure收尾finalized，7份文档无发现，delivery unchanged；BUG-0073既有记录unchanged。自动验收通过。旧输入、未知措辞或相邻真实冲突仍受门禁约束。
## 后续建议
新增措辞先提供对应反例再扩展，避免宽泛历史章节豁免。未创建后续Issue。未测量用量收益。
