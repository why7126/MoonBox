# Chat 读取生命周期

状态与页脚通过 `readTurnSummary` 共享同一认证身份、轮次的在途请求；不重放事件来重建终态，不跨已完成请求缓存授权。摘要沿用服务端轮次权限，工具数统计完整轮次，Token 等数值来自最后一个用量事件，缺失时不伪造0。身份变化后的迟到响应会被丢弃。

`sharedChatRead` 按资源类型、全局唯一对象ID和事件游标区分请求。每个消费者独立取消；最后一个订阅者离开才取消传输。事件游标读取、恢复读取也使用此入口；任何错误不保存为成功缓存。

`ExecutionPanel.visible` 为读取开关：隐藏时取消详情请求并停止列表/事件/diff/context读取。终态窗口最多保存1000条事件，重新展开先读摘要重新授权并检查更新时间与最新事件序号。只复用事件窗口，diff/context重新读取；变化、重试、权限错误或组件卸载使原窗口不可复用。活跃轮次继续更新，终态停止轮询。1000条以后的事件由用户显式读取后续窗口。

恢复面板等待响应结束后再安排下一次读取，核验通知在在途期间合并成一次后续刷新；保留页面隐藏暂停、完成停止、20次预算与版本拒旧。浏览器恢复可见时状态/页脚重新授权更新，不以历史缓存解除成果核验或写入保护。

回归入口：`sharedChatRead.test.ts`、`historySummary.lifecycle.test.tsx`、`ExecutionPanel.lifecycle.test.tsx`、`RecoveryOperationPanel.lifecycle.test.tsx`。隔离浏览器样本使用后端 `tests/history_read_browser_fixture.py` 与 Web `tests/history-read-live.html`；仅绑定本机，合成SQLite和合成身份，不连接产品数据或调用模型。生产构建不引用该测试入口。

## 执行中问答

QuestionPanel按原轮次读取问题，活跃状态等待响应后再轮询，隐藏页面暂停、终态停止，身份变化丢弃迟到响应。QuestionCard提供选项/补充、提交/错误/已答/过期反馈；失败保留草稿与同内容幂等键，不把接收成功当作任务完成。Composer显式声明question_capable，普通并发发送限制不变。接口类型来自生成的chat.ts；孤立浏览器夹具为tests/question-live.html，只有合成状态使用预置记录，真实模型结果单独记录。

`RuntimePreflight`显示会话授权的验收能力，只在首次显示/切换会话/用户重新检查时读取，不轮询；会话切换取消旧请求，失败清除旧就绪显示。`configured`与探针ready都不等于验收通过，实际结果继续由AcceptanceOperations呈现。布局沿用Chat主题与Button，支持窄屏及键盘。
