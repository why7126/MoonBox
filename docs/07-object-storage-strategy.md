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
- Docker 本地 `:3000` 边界必须可上传、读取和回显。
