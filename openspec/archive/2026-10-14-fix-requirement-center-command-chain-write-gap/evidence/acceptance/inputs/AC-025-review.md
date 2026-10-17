---
title: 新会话默认低推理程度复核
created_at: 2026-10-13 08:33:00
updated_at: 2026-10-13 08:33:00
---

# 新会话默认低推理程度复核

- 当前后端聚焦回归 `test_material_api_validation_and_skill_candidates` 1 passed，capabilities 默认 reasoning 为 low；前端 `chat-composer.test.tsx` 的 fallback Low 用例 1 passed。
- 当前真实 Firefox Chat 历史样本显示模型配置为 Low；原历史配置与前端运行态证据见 Change `verification.md` 的 AC-025 行。
- Node 25 运行前端测试使用临时本地 Storage 数据库以提供标准 `localStorage` 接口；该临时文件不纳入证据包。
