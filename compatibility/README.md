---
purpose: 兼容性目录入口
content: 说明 compatibility 目录下数据库、设备端、对象存储等独立兼容模块的职责、生成规则和同步要求
update_method: 新增端形态、数据库、对象存储、运行环境或兼容目标时更新
created_at: 2026-06-27 08:44:18
updated_at: 2026-06-27 08:44:18
owner: MoonBox
status: draft
note: 适用于 MoonBox 项目
---

# 兼容性模块索引


`compatibility/` 用于沉淀项目级兼容性事实源，覆盖端设备、数据库、对象存储、运行环境和部署差异。

兼容性规则总入口见 `rules/compatibility.md`；本目录保存可独立维护、可独立测试的专项适配说明。


| 参数 | 说明 | 示例 |
|---|---|---|
| `MoonBox` | 产品名称 | 见 docs/pending-decisions.md |
| `Web 端、管理后台、REST API` | 产品形态 | Web、微信小程序、H5、桌面端 |
| `SQLite` | 数据库栈 | SQLite / PostgreSQL / MySQL |
| `MoonBox` | 信创数据库 | 达梦 / 海量 / 无 |
| `MinIO 兼容对象存储，面向文档与图片资产` | 对象存储 | MinIO / S3 / COS / OSS / OBS |
| `MoonBox` | 兼容性负责人 | 见 docs/pending-decisions.md |


| 模块 | 文件 | 启用条件 |
|---|---|---|
| 数据库迁移规则 | `database/migration-rules.md` | 使用数据库时 |
| 数据库测试矩阵 | `database/test-matrix.md` | 使用数据库时 |
| SQLite | `database/sqlite.md` | 主库或测试库使用 SQLite |
| PostgreSQL | `database/postgresql.md` | 声明支持 PostgreSQL |
| MySQL | `database/mysql.md` | 声明支持 MySQL |
| 达梦 DM | `database/dm.md` | 信创数据库包含达梦 |
| 海量 HighGo | `database/highgo.md` | 信创数据库包含海量 |
| Web | `devices/web.md` | 产品形态包含 Web 或管理后台 |
| 微信小程序 | `devices/wechat-miniapp.md` | 产品形态包含微信小程序 |
| H5 | `devices/h5.md` | 产品形态包含移动端 H5 |
| 桌面端 | `devices/desktop.md` | 产品形态包含桌面端 |
| Android | `devices/android.md` | 产品形态包含 Android |
| iOS | `devices/ios.md` | 产品形态包含 iOS |
| MinIO | `object-storage/minio.md` | 对象存储包含 MinIO |
| S3 | `object-storage/s3.md` | 对象存储包含 S3 或 S3 Compatible |
| COS | `object-storage/cos.md` | 对象存储包含腾讯 COS |
| OSS | `object-storage/oss.md` | 对象存储包含阿里云 OSS |
| OBS | `object-storage/obs.md` | 对象存储包含华为 OBS |
| RustFS | `object-storage/rustfs.md` | 对象存储包含 RustFS |


- 未启用的端、数据库、对象存储文档不得作为强制兼容要求保留。
- 启用但信息未知的模块必须写 `见 docs/pending-decisions.md`，不得编造版本、厂商、测试结果或客户环境。
- 兼容范围必须可验证，不能只写“主流浏览器”“常见数据库”。
- 兼容性变更必须同步 `docs/05-compatibility-matrix.md`、`rules/compatibility.md`、测试和发布说明。


AI Agent 修改端能力、数据库、对象存储、部署方式或兼容范围时，必须先读取本目录对应模块，并同步更新测试矩阵。不得伪造兼容测试通过结果。
