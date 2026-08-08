---
purpose: 兼容性矩阵
content: MoonBox 当前启用端、数据库、对象存储和未启用能力边界
created_at: 2026-07-29 22:55:00
updated_at: 2026-07-30 09:15:29
owner: MoonBox 产品团队
---

# 兼容性矩阵

| 类型 | 当前状态 |
|---|---|
| Web | 启用，覆盖品牌入口、工作台和管理后台 |
| REST API | 启用，FastAPI |
| SQLite | 启用，作为本地开发和快速测试数据库 |
| MySQL | 启用，作为生产数据库和发布前兼容验证目标 |
| MinIO | 启用，作为 S3 兼容对象存储 |
| 微信小程序 | 未启用 |
| iOS / Android / H5 | 未启用 |
| 桌面端 | 未启用 |
| 本地模型 | 未启用 |

兼容性扩展必须通过 OpenSpec Change 明确目标平台、测试矩阵和发布门禁。
