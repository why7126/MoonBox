# 真实产品验收记录

2026-10-22。用户已明确授权重建并重启本地 Web/API。Compose 仅重建启动 backend/web；后端 healthy，Web页面与 API 200 可访问。浏览器确认新版 bundle index-DQTLgaxW.js。

## 本地业务观察

REQ-0051 研发中卡片显示开发3人天；BUG-0062已完成卡片按根因已确认、开发5人天排序。点击根因标签显示原Markdown安全预览及真实根因正文。证据 local-observation.json、local-done-document.png。

Network一次刷新观察含自动轮询：聚合context返回200，样本耗时22.86秒、传输1960kB；可见表格中3条context、0条根因文档请求。此数为可见行，非完整请求总数；初始逐卡文档请求为0、点击后1次由页面回归精确计数。无可比旧镜像HTTP基线，不宣称生产加速。隔离100卡片同样本前后读取中位121.25/105.32ms见projection-benchmark.json；两种证据不可互换。

## 隔离真实服务观察

使用当前FastAPI、真实HTTP认证、临时SQLite和治理目录、构建后的Web，未拦截或Mock网络。浏览器端口39036；账号、权限与样本均为专用临时数据。未修改实际业务对象或其权限。

| 检查 | 观察 | 证据 |
| --- | --- | --- |
| 同一BUG研发→验收→已完成 | 三阶段刷新均保留根因已确认及0.5人天 | isolated-development.png、isolated-acceptance.png、isolated-done.png |
| 已完成根因入口 | 点击后读取真实API根因正文 | isolated-done-document.png |
| 同尺寸源修改 | confirmed改为probable并保持字节长度，0.5改3.5；刷新显示待确认及3.5人天 | same-size-updated.png |
| 删除根因源 | 刷新后根因隐藏，人天保留 | source-deleted.png |
| 项目切换 | 切到空项目无旧标签，切回恢复 | project-switch-empty.png |
| 撤销对象读取权限 | 已打开正文、卡片和根因入口均清除 | revoked.png、revoked.json |

阶段源由隔离脚本构造完整治理事实并移动专用样本至归档目录，不是产品Chat命令轮次，也不是正式业务归档。该需求验证展示与读取，不要求Chat执行轮次；九阶段/视口/主题视觉组合仍以明确标注Mock的ui证据补齐。

## 边界与结论

上述真实运行观察补齐AC-008/009及AC-XCUT-001/002/003样本。实际部署读取仍约23秒，不能据此认定由本次标签引起；保留现有性能问题边界。扩展回归107后端通过、2项既有验收文案断言失败，Web140通过、1项既有Sprint归档确认断言失败；标签专项验证单独计数，不宣称全仓测试全绿。未自动创建Issue或正式归档。
