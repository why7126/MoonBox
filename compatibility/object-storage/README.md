---
purpose: 对象存储兼容模块入口
content: 说明 object-storage 目录下各供应商适配文档的职责、启用条件、通用边界和初始化生成规则
update_method: 新增对象存储供应商、上传下载策略、生命周期或部署模式时更新
created_at: 2026-06-27 08:44:18
updated_at: 2026-06-27 08:44:18
owner: MoonBox
status: draft
note: 适用于 MoonBox 项目
---

# 对象存储兼容模块



本目录保存对象存储供应商级兼容说明。通用策略见 `rules/object-storage.md` 和 `docs/07-object-storage-strategy.md`。


| 供应商 | 文件 | 启用条件 |
|---|---|---|
| MinIO | `minio.md` | 本地开发、测试、私有化或 S3 兼容存储 |
| AWS S3 / S3 Compatible | `s3.md` | 云 S3 或通用 S3 兼容 |
| 腾讯 COS | `cos.md` | 腾讯云对象存储 |
| 阿里云 OSS | `oss.md` | 阿里云对象存储 |
| 华为 OBS | `obs.md` | 华为云对象存储 |
| RustFS | `rustfs.md` | 私有化 RustFS |


- 业务代码不得直接依赖供应商 SDK，必须通过 Storage Adapter 封装。
- Bucket、Key、签名 URL、权限、生命周期和测试结果必须按供应商记录。
- 未启用供应商不得保留强制配置和测试要求。
- 不得写入真实 Access Key、Secret Key、生产 Endpoint 或 Bucket。
