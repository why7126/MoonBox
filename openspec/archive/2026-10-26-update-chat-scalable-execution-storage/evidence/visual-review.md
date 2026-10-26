# 局部组件视觉与交互核对

2026-10-26，AI 依据用户确认的 UI Skeleton、原型 context 与 Change UI Contract 核对。30/30 组合：1440/1024/390 × light/dark × failed/stopped/unknown/completed/read_error；截图与对应 AX/样式文本在 visual/ 同名文件。逐组加载真实分页接口后截图，不以加载前空态代替结果。

范围为生产 ExecutionPanel / SavedResults 组件，置于指定宽度的 iframe 验收画布；API 使用生产路由和临时 SQLite，身份与内容是隔离合成样本。不是整站页面壳截图，不声称现有正式服务已部署新代码；Chat 页面壳未修改，现有轮次切换/停止目标锁定由组件回归覆盖。真实模型首次成功与恢复样本另见 live-rounds.json。

核对结论：阶段/摘要/原因/保存正文/恢复动作层级一致，长文换行，深浅主题可读，无页面横向溢出。宽视口 padding24、卡片最大960，390视口 padding16、卡片342；圆角6、正文14。深色背景 rgb(31,41,55)、文字 rgb(230,234,242)，浅色背景 rgb(255,255,255)、文字 rgb(32,38,54)。保存正文限定局部滚动，加载失败可再次读取，已加载内容不被错误清空。

额外交互：原因可展开；核验后只有满足未启动证明才出现“继续准备工作区”；执行环境未就绪返回明确拒绝，未启动模型；原有停止弹窗 Esc 关闭后焦点回到“停止当前运行”。证据为 visual/1440-light-recovery-check.png、recovery-rejected.png/.txt、stop-dialog.png/.txt。未点击确认停止，不影响测试运行。最终答复与执行输出分别读取由前端测试及真实轮次分流回读验证。

文件查看补充：最终隔离API提供190000字节文本修改样本，已通过界面比较内容块并读取190024字节执行后正文，末行修改可见。截图 visual/1440-light-file-blocks.png、file-content.png；正文局部滚动高度上限360px。
