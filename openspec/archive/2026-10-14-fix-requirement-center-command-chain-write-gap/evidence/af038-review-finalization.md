---
title: 后端评审收尾与隔离工具同步验证
created_at: 2026-10-07 15:35:00
updated_at: 2026-10-07 15:35:00
---

# 后端评审收尾与隔离工具同步验证

## 代码与数据回归

执行 `uv run --project src/backend --with pytest --with httpx python -m pytest -q src/backend/tests/test_governance_review.py src/backend/tests/test_governance_candidates.py src/backend/tests/test_requirement_completion_recovery.py src/backend/tests/test_governance_writer.py tests/unit/test_review_promotion_sync.py`：128 passed，1 项既有弃用 warning。

- 真实临时文件系统、SQLite candidate/application 和 controller：不是手工 DOM 或模型文字断言。
- REQ/BUG approved/rejected/deferred 投影遗漏补正及幂等，根因/结论/缺文档/越界/注册表冲突拒绝。
- source 模式真实文件收尾；模拟第二个文件写入失败，无成功应用记录，原轮次恢复后 applied/verified；再次恢复幂等。
- copy 模式原会话成果恢复，controller 回写后文档与工作区一致，checkpoint 后 Git 无未应用成果。
- 新评审工作区同步未提交的当前技能和迁移/同步/标题工具，env 不进入工作区。

## 证据限制

本轮未重建部署、未发送真实业务模型命令，不证明运行中容器已加载本次代码。产品部署复验使用标准 self-storage-sqlite 脚本；有活动任务时先等待其终止，再部署并以测试对象验证评审及卡片状态。无原始候选、迁移文件不完整或评审结论不合法时继续阻断，不自动推断批准。
