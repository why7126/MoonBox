# 实施验证记录

日期：2026-10-22。来源 REQ-0051-card-persistent-info-tags / sprint-013。

## 已实现范围

后端在授权项目快照的 ChangeIndex 中投影 Sprint 人天及 BUG 根因状态；前端复用现有标签行和 Markdown 抽屉。顺序为等级、负责人、根因、人天，0 与小数有效，缺失及冲突估算不猜测，根因冲突按待确认。所有阶段共用同一渲染，无完成阶段过滤。

API 新增四个兼容字段，OpenAPI/Orval 已生成；API 索引与产品手册已同步。无 DB 迁移、部署配置、安全权限或新采集字段变化。product_data_collection_observability: applicable；affected_layers: web、api、usage_events、request_logs；复用既有授权读取和点击事件，无根因正文日志。Task Trace、对象存储及保留周期不变。

## 命令证据

- 后端元数据单元/真实文件投影：28 passed。
- 真实授权 HTTP 集成：1 passed。覆盖0人天、同尺寸状态变化、确认变更、人天更新、文档删除、未登录读取与项目绑定移除。测试数据位于临时目录，不修改业务对象。该最小样本不具有完整交付证明，因此不冒充产品生命周期流转。
- 新标签组件3项测试通过；九阶段生产页面回归确认初始0个根因文档请求，点击已完成卡片后仅1个文档请求。聚焦相关页面回归15 passed，126项不在该次过滤范围。
- 扩展回归：Web 140 passed / 1 failed，失败为既有 Sprint 归档确认对话框断言；后端107 passed / 2 failed，失败为既有验收阻断文案断言。保留失败，不改动无关业务或放宽断言。本次标签缺省隐藏，后端失败路径直接调用旧 _build_issue 而非新增投影。
- TypeScript构建通过；当前Change OpenSpec strict及中文校验通过；全仓中文残留报告无残留；Mintlify校验通过。
- 100张卡片隔离基准：禁用新增投影中位121.25ms，启用105.32ms，详见projection-benchmark.json。非部署HTTP性能，不能外推生产延时。

## 浏览器与视觉证据

使用Codex侧边浏览器运行生产RequirementCenterPage及共享抽屉，测试入口位于src/web/tests/card-info-board.html。API为明确的合成响应；真实API由独立HTTP集成测试验证。没有将Mock注入生产入口。

ui/skeleton-1440.png 是首轮四组合Skeleton证据；ui/stage-{0..8}-{1440|390}-{dark|light}.png 覆盖九阶段（采集、规划、待评审、已评审、迭代规划、待开发、研发、验收、已完成）共36组合。手机保留原横向看板滚动，截图可只显示部分列，不宣称整卡自适应列宽。computed-styles.json证明每张标签行scrollWidth不大于实际宽度，根因及人天12px，gap6px；标签不溢出自己的卡片。

已目视检查深浅主题桌面与手机代表性默认、已完成抽屉、无权限、删除和加载态。drawer-{1|6|8}覆盖待确认、已确认和已完成；error-{denied|missing|loading}覆盖双视口双主题。字段缺省的合成样本抽屉副标题显示undefined为既有来源标签缺省，不属于本次根因正文或标签。

键盘Enter/Space打开、Esc/关闭按钮退出与焦点回归已验证，外部区域实际坐标点击关闭，内部文档操作不关闭。详见keyboard.json。抽屉样式记录在drawer-style文件，移动390px全宽，桌面保留既有可调宽度。

## 真实产品验证补齐

本地Web/API已按用户授权重建并重启，真实业务卡片、已完成根因抽屉及Network观察已验证。隔离真实HTTP服务完成同一BUG三阶段刷新、同尺寸更新、删除、切换及撤权。详细边界、截图与指标见[product/review.md](product/review.md)。Mock视觉、隔离真实服务与本地业务观察分列，不冒充Chat轮次或正式归档。

## 文档一致性与续接

已核对REQ requirement、business-flow、user-stories、acceptance、trace与prototype/context；人天是只读预估，根因点击打开原抽屉；560px原型差异按design决策保留产品能力。完成门禁后同步apply并进入18项自动验收；未经授权不正式归档。
