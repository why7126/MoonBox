# 续执行及停止前置验证

2026-09-09，用户要求继续测试。真实浏览器在原会话发送一次续改任务；container沿用同一执行线程，counter.txt从1变为2，本轮Diff为1→2，累计Diff为0→2。模型确认完成，正文、引用及差异均保留。

## 未通过项与证据链

停止测试的发送被拒绝，未创建新轮次，不能记为停止功能通过。第二轮用量为usage_unavailable，Token预留60000保持reserved；实际业务轮次均completed，但空间及用户基础账本active_runs均为1，限制为1。月度used_tokens为62254，远未达到400000上限，空间/用户存储也未超限，定位本次拦截为并发槽未释放。

直接证据为本批verification.json和admission-blocked.png；代码路径是app/chat/execution.py仅usage非空时调用reconcile_usage，app/chat/admission.py仅settle内递减active_runs，而enqueue以active_runs判断并发。并发释放与Token结算耦合导致已完成轮次继续占槽，根因confirmed。执行端未提供可接受用量的原因尚未验证，与并发占用缺陷区分。

本批不清空账本、不伪造零Token、不提升额度、不新建测试身份绕过限制。后续应在既有REQ-0025 Change范围内实现可信终态释放并发与用量预留独立记账，覆盖幂等、并发竞争和迟到用量结算，再恢复实际停止验收。当前服务、会话和文件结果保留。

本批未修改业务源码、API、数据库schema或部署配置，仅记录验证证据；不更新任务完成状态或归档，也未自动创建新的Issue/Change。
