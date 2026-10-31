---
title: 聊天历史读取修复验证记录
created_at: '2026-10-31 08:54:00'
updated_at: '2026-10-31 08:54:00'
---

# 聊天历史读取修复验证记录

## 交付范围

新增授权轮次摘要接口，状态和页脚共享在途请求，终态无需重放事件；详情展开才读取，终态窗口复用前重新授权；恢复查询单在途、完成后调度。保留成果核验、写入保护和完整输出组件。截至 2026-10-31 08:57 的 apply 阶段，未更新现有产品镜像、未发起模型任务、未归档。

## 命令验证

- 后端 `test_chat.py` 与新增摘要测试初批：54通过、1既有跳过；追加缺失/非法用量与冻结权限后，新摘要测试6通过。覆盖404条末页用量、工具计数、非所有者404、冻结空间403、未知状态与数值白名单。
- Web Chat初批32通过；追加注销竞态、指定历史轮次和隐藏/403/瞬断等增量回归通过。最终自动验收调用完整8文件Chat回归，39项通过。
- TypeScript检查和Vite生产构建通过；保留现有大包提示，不将其解释为本次请求生命周期失败。
- OpenAPI按当前应用导出，Orval Chat重新生成；目标OpenSpec严格校验、中文校验及全仓残留分离报告、Sprint017范围校验、上下文预算校验通过。
- 初次 pytest 误用包装器不支持的 `-m` 后，改为支持的 `-c`/runpy入口；没有回退系统Python。

## 浏览器样本与计时边界

Codex侧边浏览器，1440×1000；恢复默认后当前视口亦为1440×1000。真实旧部署通过Chrome已有填充登录态访问，打开已有单轮历史并观察终态，未重新发送任务。该旧部署仅作参考，不作为修复版验收。

性能样本使用真实React组件与聊天API、隔离合成SQLite。修复前组件来自提交 `5353f79300d6a4bcbe33959a20dc6580c3f2fe20`，修复版使用当前工作区。对照均为相同API、数据与开发服务条件，单轮/十轮各404事件，最新用量在末页。每组首次挂载与重访各3次；每次清空ResourceTiming并重挂载，采样窗口约1.75秒（2秒结束前最后一次250ms采样）。不是整页冷启动，也不是稳定P95。

禁用缓存组由隔离页面对API fetch统一设置no-store；JS/CSS启动不在计时范围。默认与no-store四批共48个样本见 `evidence/acceptance/browser/*-default.json`、`*-no-store.json`。

|接口缓存|轮次|API请求数 前→后|传输字节 前→后|正文首见中位ms 前→后|状态稳定中位ms 前→后|
|---|---:|---:|---:|---:|---:|
|默认|1|19→2|98081→1904|19.5→16.5|56.5→24|
|默认|10|91→11|622683→15360|25.5→23|223→91|
|no-store|1|19→2|98081→1904|26→16|59→22|
|no-store|10|91→11|622683→15360|23.5→20.5|221.5→81.5|

修复前同键并发峰值3，修复后1；单轮事件首页原先读取3次，修复后收起时为0。正文首见差值较小，不能归因于本次摘要优化；状态等待在这组隔离样本中缩短，不外推到真实部署或历史2.04秒请求。

no-store组记录ResourceTiming的responseStart-requestStart（Waiting）和requestStart-fetchStart（排队/连接合计）；不能进一步分离DevTools Queueing与Stalled。未取得匹配request_id的服务端分段计时，服务器耗时占比仍未知。所述收益只限同环境对照，不把环境波动算作稳定收益。

## 逐项签认

|AC|结论与证据类型|证据入口|
|---|---|---|
|AC-001|通过：终态状态/页脚无需事件读取；组件回归与真实浏览器合成历史|historySummary生命周期测试；fixed-no-store.json；fixed-slow-1440.jpg|
|AC-002|通过：同键在途合并、独立取消和注销迟到结果隔离；浏览器峰值1|sharedChatRead测试；fixed-no-store.json|
|AC-003|通过：收起40.252秒无events/diff/context；消息列表14次必要刷新单独列示|closed-and-slow-window.json|
|AC-004|通过：199/200/401/1000/1001回归；浏览器200/404/1000+1窗口，404重开三页均不重发|ExecutionPanel生命周期测试；detail-reuse.json；detail-200/404/1000/tail截图|
|AC-005|通过：浏览器queued→running→unknown→stopping→completed，未知展示待确认；转终态后38秒摘要/事件次数不增加|active-states.json；terminal-stop.json；active-completed-1440.jpg|
|AC-006|通过：真实HTTP受控5秒响应仅1次，业务完成可见；乱序/通知合并由合成回归覆盖|RecoveryOperationPanel生命周期测试；closed-and-slow-window.json；fixed-slow-1440.jpg|
|AC-007|通过：浏览器切换四组会话、详情关闭/重开；隐藏暂停与旧响应隔离由生命周期回归覆盖|historySummary、ExecutionPanel及Recovery生命周期测试；各详情截图|
|AC-008|通过：权限失败清除展示、401/403/404停止无效重试，瞬断恢复；服务端非所有者与冻结空间拒绝；不更改核验写入边界|摘要API测试、historySummary测试、既有ObjectArchivePanel回归|
|AC-009|通过：同条件48个对照样本，计时和不足如上；无生产性能声明|四批JSON；observations.json|
|AC-010|通过：末页Token404、完整工具数403/1000和耗时2秒与详情一致；缺失用量不造0|摘要API测试；detail-tail-1440.jpg；fixed-slow-1440.jpg|

表中简写证据均在 `evidence/acceptance/browser/`。截图与DOM已目视核对：状态、末页用量和恢复完成可读，未引入布局改造；computed-style.json记录状态按钮flex、14px和visible。原型/参考稿复刻门禁不适用，本次没有原型或样式改造。合成HTTP恢复响应不冒称真实治理业务完成，已有产品会话只读参考不冒称修复部署。

## 边界同步与资源

API索引、OpenAPI、Orval Chat、组件README、Change设计/规格与BUG验收说明同步。无需数据库迁移、对象存储、部署配置或新增日志字段。原权限边界不变，新增响应private/no-store与白名单过滤。

product_data_collection_observability: applicable；affected_layers: Web、API、请求封装、request_logs。validation: 请求合并、权限与取消回归、脱敏数值/截图。usage_events与Task Trace字段N/A：不新增埋点或span；不保存消息原文、凭据或产品标识。

未创建Docker资源。已授权只读reap扫描成功，登记资源容器/网络计数均为0；不删除历史台账或共享资源。本机临时API/前端进程已在证据与自动验收收尾后停止，39045—39047无监听，临时SQLite随fixture清理。


## 自动验收结果

`20261031085829365826-c9eda38c` 完整证据包10/10通过，命令执行1次、去重9次。归档临时副本预演通过，最终共享准入ready；该验收时点尚未执行正式归档。Workflow Sync的apply/accept均零错误，BUG验收状态passed。
