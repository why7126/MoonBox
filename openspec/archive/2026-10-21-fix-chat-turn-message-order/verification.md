---
title: Chat 消息顺序修复验证记录
created_at: 2026-10-21 14:30:43
updated_at: 2026-10-21 15:05:00
---

# Chat 消息顺序修复验证记录

## 交付与影响

统一服务端分页前的轮次四元组排序和前端正序展示，稳定投影/持久消息身份，保留首次保存时间并显式标记历史未知时间；增加受限游标、分批范围复核和会话响应隔离。适用于所有 Chat 会话，不按 REQ/BUG 身份特判。API、OpenAPI/生成客户端、数据库时间语义、Web 文档及经验文档已同步，无数据库迁移、权限放宽或生产变更。

## 稳定验证批次

- SQLite：23 项 + 3 个子测试通过；MySQL 8.2 独立容器：同样 23 项 + 3 个子测试通过。测试结束清理独立实例。
- 修改 MySQL 测试入口后，SQLite 聚焦 9 项 + 3 个子测试再次通过。
- Vitest：既有消息、输出和工作台 25 项通过。当前 Node 需禁用实验性 Web Storage 才能使用测试 localStorage 环境，未更改产品权限或依赖。
- React DOM：新增 7 项通过，覆盖迟到旧页、深页请求预算、单通道请求、刷新重挂载和切换会话。属于合成接口回归。
- TypeScript + Vite 生产构建通过；大 chunk 提示为已有非阻断 warning。
- 证据及源码哈希：[implementation-checks.json](evidence/implementation-checks.json)，脱敏日志位于 evidence/regression/。

## 部署后真实观察

后端、worker、治理控制器的 assistant_output.py/api.py 哈希与已测代码一致；Web index 哈希与本次构建一致。隔离服务使用相同后端源文件、构建及执行器，只含测试文件的独立仓库。

用户明确授权的 2 条简短提示均由产品输入框实际发送，未追加调用：正常轮 completed；停止轮在有真实输出后，经产品 interrupt HTTP 接口返回 200/stopping，随后 stopped。运行中刷新、停止后刷新均无重复助手消息；同轮投影和持久消息 ID/order_key 相同，停止输出仍为 partial。

API page_size=1 完整读取 28 条消息，28 个唯一身份，正向每轮 user→assistant；12 轮分页历史为合成，2 轮真实。Web 刷新后先显示 20 条，加载更多收敛到 28 条。历史未知回复有明确提示。深页/并发迟到等不可控时序另由确定性回归覆盖，未冒充真实模型观察。

- [真实链路核验](evidence/product/live-chain.json)
- [历史现场只读核验](evidence/product/historical-readonly.json)：原助手 08:32:34、用户 08:32:35 保存时间保持不变；当前展示 user→assistant，助手显示输出记录时间 08:33:02。
- [原现场截图](evidence/product/historical-original.png)
- [样式与视口](evidence/product/computed-style.json)，6 个阶段×视口截图位于 evidence/product/。

## 视觉签认

1440×900 与 390×844：消息先后正确，无横向溢出；时间来源明确；停止后部分输出提示可见。窄屏元数据按既有布局换行，本次未改变样式。刷新和加载更早保留已有消息；返回最新消息可定位停止轮。未新增 UI Skeleton 或 modal，行为参考与 selector/action 边界见 design.md。

## 原执行环境差异

此前产品执行镜像缺少 pytest、原生 Node 构建依赖、浏览器/MySQL 能力，9/12 检查点不能完成。此次在已配置宿主环境补齐这些验证，未降低门禁。隔离样本准备阶段曾缺少 workspace_mode 和 SQL 必填字段，均在模型调用前修正；Web 部署 shell 使用 Bash 后成功。保留之前执行记录，不继续将已解决环境问题标为当前阻塞。

## 验收收尾

逐 AC 证据包由 opsx-accept 生成，完成态和归档准入以最新机器报告为准；本次不自动正式归档。
