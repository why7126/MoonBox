---
purpose: 对象存储策略
content: MoonBox 文档和图片资产存储策略
created_at: 2026-07-29 22:55:00
updated_at: 2026-08-07 22:52:00
owner: MoonBox 产品团队
---

# 对象存储策略

MoonBox 启用 MinIO 兼容对象存储，用于保存产品知识图谱相关文档、设计图片、附件和导入资产。

## Bucket 策略

MoonBox 采用“一个项目一个 Bucket”策略：

```text
moonbox
```

桶内使用二级目录/前缀区分资源类型。不得为图片、文档、导入导出、临时文件或租户新增独立 Bucket；业务归属、租户、权限、生命周期和知识图谱引用保存在数据库元数据中。

## 标准二级前缀

| 前缀 | 用途 |
|---|---|
| `images/original/` | 原始图片、Logo、设计资产、页面截图 |
| `images/avatars/` | 管理后台用户头像 |
| `images/thumbnails/` | 图片缩略图 |
| `images/processed/` | 处理后的图片 |
| `documents/source/` | 原始文档、需求、设计、决策、导入资料 |
| `documents/preview/` | 文档预览图或预览文件 |
| `documents/processed/` | 处理后的文档 |
| `imports/source/` | 导入源文件 |
| `imports/processed/` | 导入处理产物 |
| `exports/result/` | 导出结果文件 |
| `tmp/uploads/` | 上传临时文件和分片 |

## Object Key 规则

正式业务对象 Key 使用：

```text
{resource_type}/{subtype}/{uuid}.{ext}
```

示例：

```text
images/original/{uuid}.png
documents/source/{uuid}.pdf
tmp/uploads/{uuid}.part
```

对象默认私有访问，通过短期签名 URL 读取。对象元数据、业务归属和知识图谱引用保存在数据库中。

## 管理后台头像上传

`add-admin-user-management` 启用管理后台头像上传链路。Docker 本地 `self-storage-sqlite` 和生产对象存储接入均 MUST 使用 MinIO/S3 兼容对象存储，头像对象写入单 Bucket 前缀 `images/avatars/{uuid}.{ext}`，不得回退到后端本地 `data/media/avatars` 目录作为正式上传路径。

头像上传要求：

- 仅允许 JPG、PNG、WebP。
- 单文件大小不超过 2MB。
- 对象 Key 由服务端生成，格式为 `images/avatars/{uuid}.{ext}`，不使用用户原始文件名。
- 读取必须通过后台授权接口代理，前端不得直连 MinIO 私有对象。
- 上传成功后同一会话立即回显。
- Docker 本地验收必须解析实际 `HOST_PORT_WEB`，默认使用 `18102` Web 同源入口完成上传、读取和回显；不得硬编码 `:3000`。
- Docker 本地验收必须由脚本准备一次性测试用户、测试会话或可回收 fixture，不得依赖 `data/runtime/backend` 持久库中的管理员密码等于 `ADMIN_INITIAL_PASSWORD`。

## Chat 图片与文件上下文上传

REQ-0028 当前版本通过后端接收 Chat 工作台图片与文件上传，按 `capabilities.materials` 限制验证 MIME、单文件体积、总量、空间、仓库和用户权限后写入对象存储。对象 key 由服务端生成，格式为 `chat/materials/{space_id}/{repository_id}/{opaque-id}.{ext}`；前端只获得 opaque `ref_id`、名称、MIME、大小、类型和状态。不得把本机绝对路径、浏览器临时路径、完整对象 key、签名 URL、临时凭据、图片正文或文件正文写入轮次历史、请求日志、usage_events、task_traces 或错误信息。

上传成功后 Chat 轮次只绑定服务端 opaque `ref_id` 与脱敏摘要，读取历史时仍通过授权接口回显摘要或代理资源，前端不得直连私有 MinIO。清理策略需同步会话删除、备份删除重放和对象生命周期；对象删除失败必须保留待清理状态重试，不得仅因数据库轮次删除而假定对象已清理。

## Capture 私有材料（REQ-0029，实施中）

复用标准Bucket与 `images/original/` 前缀，文件名为服务端随机值。对外仅暴露材料ID和授权内容代理，不暴露对象key、访问凭证或公开签名地址。PUT前持久化uploading记录及配额，进程中断后仍有可清理对象身份。静态PNG/JPEG/WebP同时检查签名、格式、解码、动画帧、像素及字节限制。

自动清理每60秒检查主动删除材料和24小时未关联上传；候选来源及非终态整理使用中的材料跳过清理。从当前草稿移除的材料标记detached，重新关联可恢复ready。确认引用转retained长期保留，不受草稿清理影响。删除意图独立于业务库备份；对象删除失败保留待清理状态重试。正式来源存储独立于90天Task Trace和180天行为事件保留周期。
