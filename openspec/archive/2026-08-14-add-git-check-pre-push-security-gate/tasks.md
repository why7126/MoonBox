## 1. 命令与脚本入口

- [x] 1.1 新增 `/git-check` Agent 命令入口，说明用途、扫描范围、输出契约和禁止事项。
- [x] 1.2 新增 `scripts/git-check.py`，实现可从命令行直接运行的检测入口。
- [x] 1.3 支持默认 staged + tracked 扫描，并支持可选全仓扫描参数。

## 2. 检测策略

- [x] 2.1 复用 `scripts/validate-env-ignore-policy.py` 或等价逻辑作为 env ignore 前置检查。
- [x] 2.2 实现禁止提交路径检测，覆盖真实 env、数据库、运行时数据、上传数据、对象存储数据、临时目录、构建产物、压缩包和系统缓存。
- [x] 2.3 实现文本敏感内容检测，覆盖密钥、Token、Authorization header、Cookie、连接串、对象存储凭据、生产私有地址、本机绝对路径和隐私数据。
- [x] 2.4 实现占位符与公开示例识别，避免 `<access_token>`、`change-me-in-local-env`、`example`、`localhost` 等合法示例误报为 error。
- [x] 2.5 实现大文件和二进制产物检测，并给出项目默认阈值。

## 3. 报告与安全输出

- [x] 3.1 实现 error、warning、info 分级结果和非 0 返回码规则。
- [x] 3.2 实现脱敏输出，确保报告不完整打印密钥、Token、Cookie、Authorization header、数据库连接串、真实 `.env` 行或客户隐私数据。
- [x] 3.3 输出扫描摘要、error 列表、warning 列表、通过项摘要和修复建议。

## 4. 测试与文档同步

- [x] 4.1 增加脚本级测试或等价验证，覆盖真实 env、示例 env、数据库文件、运行时目录、真实连接串、占位符误报和脱敏输出。
- [x] 4.2 同步必要的 `rules/`、`docs/` 或 README 说明，记录 `/git-check` 的使用边界。
- [x] 4.3 运行 `python scripts/validate-env-ignore-policy.py`、`python scripts/git-check.py` 和相关测试。
- [x] 4.4 运行 OpenSpec 中文/结构校验，确认 Change 文档可归档。

## 验收返修记录

- [x] 2026-08-09 07:44:41 验收发现 `data/s3/**` 对象存储运行时数据已被 Git 跟踪，已通过 `git rm -r --cached data/s3` 迁出 Git 索引并保留本地文件；`python scripts/git-check.py` 复验返回 0。
- [x] 2026-08-09 08:04:52 验收要求本机绝对路径片段作为隐私阻断，已将 `local-absolute-path` 从 warning 提升为 error，并补充单元测试；历史归档文档中的本机路径已替换为占位符，校验脚本自检正则已避免字面本机路径命中。
- [x] 2026-08-09 08:18:35 验收要求补齐 `docs/spec-logs/CHANGELOG.md` 和治理日志，并强制 REQ/BUG 驱动但触达治理资产的 Change 纳入 spec-logs；已新增治理日志、更新索引、文档治理规则、spec-logs README 和 delta spec。
