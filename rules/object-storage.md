---
purpose: 对象存储使用规范
content: 桶、对象 Key、目录前缀、权限、生命周期与 AI 更新要求
update_method: 对象存储策略变化时由技术负责人确认后更新
created_at: 2026-06-13 00:00:00
updated_at: 2026-07-30 00:00:00
note: 一个项目一个 Bucket，桶内使用二级目录/前缀区分资源类型
---

# 对象存储规范

## 1. 总原则

对象存储栈由 `MinIO 兼容对象存储，面向文档与图片资产` 决定。MoonBox 使用固定策略：

```text
一个项目一个 Bucket
桶内使用二级目录/前缀区分资源类型
```

项目初始化后必须在 `.env.example` 中明确 Bucket、Endpoint、访问方式、Key 规则和安全边界。

默认 Bucket：

```text
moonbox
```

除非 OpenSpec 明确说明并经过评审，不得为图片、文档、导入导出、临时文件或租户单独新增 Bucket。

## 2. 标准对象前缀

```text
images/original/
images/thumbnails/
images/processed/
documents/source/
documents/preview/
documents/processed/
imports/source/
imports/processed/
exports/result/
tmp/uploads/
```

第一级目录 MUST 表示资源大类，例如 `images`、`documents`、`imports`、`exports`、`tmp`。
第二级目录 MUST 表示资源状态或用途，例如 `original`、`thumbnails`、`source`、`preview`、`processed`、`result`、`uploads`。
不得把租户、用户、业务对象 ID 或环境名作为顶层 Bucket 替代策略；业务归属写入数据库元数据。

## 3. Object Key 形态

推荐形态：

```text
{resource_type}/{subtype}/{uuid}.{ext}
```

示例：

```text
images/original/{uuid}.png
images/thumbnails/{uuid}.webp
documents/source/{uuid}.pdf
documents/preview/{uuid}.png
imports/source/{uuid}.xlsx
exports/result/{uuid}.csv
tmp/uploads/{uuid}.part
```

MUST NOT 使用用户原始文件名、真实身份信息或未经校验的路径片段。

## 4. AI 必须遵守

AI 在新增文件上传、视频上传、图片处理、导入导出能力时：

```text
□ 不新增多个业务 Bucket，除非 OpenSpec 明确要求
□ 复用 .env.example 中的对象存储变量
□ 使用二级标准前缀或在 OpenSpec 中说明例外
□ 更新媒体资源相关 OpenSpec 和文档
□ 补充对象 Key 生成逻辑和测试
```
