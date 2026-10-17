---
title: 修复 Chat 中纯治理 Change 归档授权与命令工具路径设计
created_at: 2026-10-09 10:54:00
updated_at: 2026-10-09 10:54:00
---

# 修复 Chat 中纯治理 Change 归档授权与命令工具路径设计

## 背景与现状

`write_policy` 先判断 `_archive_ready`，再回落 `_governance_writable`。现有 `_archive_ready` 要求主对象 ID 等于 Change trace 中的 REQ/BUG 来源；纯治理 Change 无该来源，故真实轮次选中 `moonbox-governance`。app-server 清空继承命令环境后，私有配置未设置 PATH；独立工具链预检通过仍不足以保证命令执行环境可解析工具。

## 根因与修复方案

1. 纯治理 Change 主对象只能在完整 `/opsx-archive` 命令、对象 ID 与 active Change ID 一致、trace 为 applied、无 REQ/BUG 来源且 Sprint 机器范围包含该 Change 时获得 `archive_write`。归档中断后若唯一 canonical archive 已存在，允许同一授权命令仅做收尾；歧义、失配、撤权和非归档命令均拒绝归档 profile。REQ/BUG 来源继续走既有逻辑。
   归档脚本的 Issue 验收门禁同样识别唯一 canonical archive 或 CLI 旧目录过渡阶段的 trace：活动目录缺失时读取唯一归档 trace，再照常校验关联 Issue 是否已签认；活动与归档并存或多个归档日期时保持阻断。续接不重新合并规格。
2. `write_profiles` 将固定镜像 PATH 注入 `shell_environment_policy.set`。PATH 只包含执行器镜像标准工具目录，不继承宿主环境或用户可写目录。工具链预检追加同一命令环境的验证，避免只在启动时验证外部环境。
3. 不修改普通 `moonbox-governance` 的写入范围，不挂载 Docker socket 或业务数据库到执行容器。

## 测试策略

- 策略测试覆盖纯治理成功、非归档/未 applied/未纳入 Sprint/来源字段存在/对象不匹配/撤权失败与归档续接。
- 沙箱测试在真实执行器镜像中验证 PATH、Node、OpenSpec、Python 与目录写入；预检与模型命令环境保持一致。
- 对新建隔离 Change 执行归档脚本；真实产品首次归档另记录轮次和事实源结果。

## 风险与回滚

错误授予归档 profile 的风险高于普通命令失败，因此纯治理分支必须 fail closed；Sprint 和来源字段异常时回落不可归档，不凭提示文案放权。若真实环境不满足边界，恢复旧镜像并暂用宿主归档，不修改既有备份或用户数据。

## 数据采集与链路观测

`product_data_collection_observability: applicable`；`affected_layers`: `chat_turns`、`request_logs`、`task_traces`、`task_trace_spans`。沿用既有脱敏权限决策与命令状态，不新增 API、DB 或行为事件字段；`usage_events` 新采集 N/A，因为 UI 动作和客户端请求协议不变。验证同轮次所选 profile、工具退出码与 Change 最终状态一致。
