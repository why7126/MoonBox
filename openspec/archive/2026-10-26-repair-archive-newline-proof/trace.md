---
title: 归档规格空行补证追溯
change_id: repair-archive-newline-proof
status: applied
iteration: sprint-013
created_at: 2026-10-26 11:01:27
updated_at: 2026-10-26 11:09:15
execution:
  schema_version: 1
  started_at: 2026-10-26 11:01:40
  completed_at: 2026-10-26 11:09:15
  last_event: opsx.apply
---

# 归档规格空行补证追溯

## 授权与来源

用户明确要求修复规格基线证明与失效引用，验证通过后继续归档 sprint-013。补证不修改历史 journal、manifest 或条文。

## 根因与重放证据

Git 7c18373f 的规格树加本地既有 Finder 元数据哈希得到原 baseline `75c6f599e4c661d8d6dc2404db8cbb26cf0eea4d6020f4d0046772cbbc776737`。在临时目录用原已归档 delta 重放 OpenSpec，结果精确匹配原 expected `00c1d60bda0c6499ffb59fd7925e51d0d75e674f4f3b433b427085c818c05053`。Git b69d8328 的同一规格仅少一个末尾 LF；完整树精确匹配后继 baseline `3cd6fc96795509be73b82baf9debb27f351bde9788bc90981dc255889d26cf14`。

独立证据：`openspec/archive/.spec-normalizations/req-0050-eof-newline.json`，含全部文件哈希及唯一变化文件的前后公开正文，不包含 Finder 内容。原 journal、manifest 与正式规格保持原样。REQ-0050/0053 的四个路径只替换归档位置，不改变历史验收结论。现有七个 Change readiness 全部通过，陈旧扫描零阻断。

## 验证记录

独立补证正反例、历史归档链、共享入口和写入边界联合回归189项通过。旧条文冲突测试的三条断言与当前具体诊断不一致，已修正为 archive_requirement_conflict 并核对安全诊断身份；未改变条文冲突拒绝行为。最新完整验收清单位于 evidence/acceptance/，以收尾后的 readiness 为准。中文标题、聚焦中文、OpenSpec strict、上下文预算、Sprint范围、目录结构与 env ignore 校验通过；目录保留既有 legacy SQLite 警告。

本次无API路由、DB迁移、UI、客户端生成或部署配置变更。源码修复未部署到正在运行的容器，验证范围为本地共享门禁和隔离回归。原历史 journal/manifest 未修改。新增 Sprint 范围脚本沿用旧缩进导致 YAML 无效，仅修正其新增条目缩进后同步通过，未扩展脚本行为。
