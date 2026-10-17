---
bug_id: BUG-0034-chat-standalone-archive-scope-tool-path
title: 产品内纯治理 Change 归档权限与工具路径失败根因分析
status: confirmed
created_at: 2026-10-09 10:52:00
updated_at: 2026-10-13 18:38:00
owner: 产品团队
---

# 产品内纯治理 Change 归档权限与工具路径失败根因分析

## 根因状态

status: confirmed

## 现象

本地 Chat 对象会话发送纯治理 Change 的 `/opsx-archive` 后，轮次 completed，但规格与归档目录不可写，普通命令和 OpenSpec CLI 无法解析，未完成归档。

## 证据链

| id | type | source | 摘要 | 支持的判断 |
|---|---|---|---|---|
| E1 | screenshot | 用户本次截图，2026-10-09 10:43 | 归档受阻，未修改文件；回复称归档目录不可写、Node/OpenSpec 不可用 | 直接证明用户可见失败与目标命令 |
| E2 | runtime_log | 同一轮次 `chat_events.execution.state.permission_decision`，只读脱敏查询 | selected 与 acknowledged 均为 `governance_write / moonbox-governance`，reason=`governance_object_writable` | 确认实际授予普通治理权限，不是模型猜测 |
| E3 | runtime_log | 同一轮次 `execution.tool` 完成事件 | 首个命令 exit 127：`cat: command not found`；后续命令 exit 127：`env: node: No such file or directory` | 确认模型命令环境查找失败 |
| E4 | code_path | `src/backend/app/chat/policy.py` `_archive_ready` | 仅当主对象与 trace 的 requirement/bug 字段匹配时返回 archive；纯治理 Change 的字段均为空 | 解释 E2 的策略回退 |
| E5 | code_path | `src/backend/app/chat/container_server.py` `write_profiles` 与 `app_server.py` 启动参数 | app-server `shell_environment_policy.inherit="none"`，私有配置未显式设置 PATH | 解释 E3 的命令路径缺失 |
| E6 | reproduction | 执行器镜像只读工具链探针 | 报告 `ready=true`、`unavailable=[]` | 排除镜像缺少 Node/OpenSpec 的假设；预检环境与模型命令环境不同 |
| E7 | reproduction | 宿主标准归档脚本与工作流同步结果 | 同一 Change 归档成功、规格合并成功、Workflow Sync 0 errors | 排除 Change 内容本身未满足归档门禁的假设 |

## 已排除假设

| 假设 | 排除证据 |
|---|---|
| 执行器镜像未安装 Node/OpenSpec | E6 显示工具存在且版本探针通过；E3 是命令 PATH 查找失败 |
| Change 任务或规格尚未完成 | E7 的标准脚本完成归档且证据校验通过 |
| 用户成员没有治理写权限 | E2 已授予并确认普通治理写权限；缺的是归档专用范围 |

## 已确认根因

纯治理 Change 使用主对象自身 ID 发起归档，而现有 `_archive_ready` 仅识别 REQ/BUG 来源关系，因此落回普通治理 profile。另一个独立缺口是 app-server 清空继承命令环境后没有显式注入固定 PATH，导致沙箱命令无法找到镜像内工具。两者共同阻断产品内归档。

## 修复方向

在成员、主对象、完整命令、Change applied 状态和 Sprint 关联均校验通过时，允许纯治理 Change 使用最小 `archive_write`；其他命令仍不扩权。给命令环境注入固定的镜像内 PATH，并在真实沙箱而非镜像外部验证常用命令与归档目录写入。

## 验证闭环

隔离构造纯治理 Change、REQ/BUG 来源、未 applied Change、非归档命令和撤权场景；验证权限决策、实际沙箱 PATH、Node/OpenSpec 命令、归档脚本及无越权。真实产品首次归档与隔离合成回归分开记录。

## 验收续接补充

2026-10-13 隔离源仓库产品 Chat 首次归档轮次 `8436f1d1-4381-423a-89f2-2f29f789edc0` 完成且归档脚本退出码 0；源仓库仅保留唯一 canonical archive。随后 `--finalize` 轮次 `2a0f8ff2-5be0-43d6-9485-bad1e6c69cf6` 返回 `ACCEPTANCE_GATE_BLOCKED change_trace_missing`。代码定位显示 `scripts/validate-issue-acceptance-ready.py` 只读取活动目录 trace；首次归档移动目录后，续接即被误判为缺失。这是已确认的归档续接根因，未推翻上文的原始权限与 PATH 根因。修复后轮次 `f908138b-7395-438b-add3-ece95e413b6b` 完成，门禁通过、脚本退出码 0、Workflow Sync 0 errors。
