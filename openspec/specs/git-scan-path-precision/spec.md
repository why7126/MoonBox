# git-scan-path-precision Specification

## Purpose
TBD - created by archiving change fix-git-scan-regex-false-positive. Update Purpose after archive.
## Requirements
### Requirement: 路径检测区分正则前缀与具体用户路径

安全扫描 MUST 保留真实本机用户路径的阻断，单纯表示用户目录前缀的过滤正则不应被识别为具体用户目录。

#### Scenario: 过滤正则只含目录前缀

- **WHEN** 目录前缀之后是正则分支分隔符
- **THEN** 不产生本机路径错误

#### Scenario: 具体用户路径仍被拦截

- **WHEN** 文档、源码或测试包含具体用户目录路径且未使用显式占位符
- **THEN** 继续报告 error 并脱敏输出

