---
created_at: 2026-09-12 21:28:51
updated_at: 2026-09-12 21:28:51
---

# 生命周期修复验收

## 实施与验证记录

- CLI 的 opsx.start、opsx.progress、opsx.apply 分别记录启动、进度和完成；Change trace.execution.schema_version=1。started_at 与任务计数分离；0/N 已启动为研发中，全勾选但未完成仍为研发中。旧条目保留兼容推导，不补造历史时间。
- 共享纯函数位于 src/backend/app/governance/lifecycle.py，CLI 通过 scripts/workflow_sync/shared.py 导入；后端镜像已有 app 目录，不依赖部署 scripts。CLI 简单 YAML 解析器不能解析嵌套映射，因此为 execution 使用受限、版本化块解析器，后端沿用现有 YAML 读取。
- 全流程项目锁、逐文件原子替换及内容冲突检查；Change 事实先写，投影失败保留事实、重跑恢复。协作锁不替代其他编辑器的锁，也不是跨文件数据库事务。
- tests/unit/test_workflow_execution.py：启动0/N、dry-run、缺Sprint拒绝、未启动拒绝进度、未全勾选拒绝完成、全勾选进度不完成、重复启动、旧六状态、聚合、符号链接拒绝、冲突/替换中断恢复与投影失败重跑。
- src/backend/tests/test_governance_lifecycle.py：REQ/BUG 真实 context 接口阶段和快照变化；test_governance_board.py 覆盖既有项目绑定、范围读取及缺文件兼容。工作流与后端目标回归85项通过。
- src/web/src/governance.test.tsx：9项通过，含REQ/BUG服务端阶段刷新及现有项目范围、并发刷新回归；npm run build通过，未改业务UI布局。
- 真实Chromium：1440×1000，/requirements；隔离账号和合成项目内REQ-9091/BUG-9091，真实登录、CLI和HTTP，无网络mock。10次CLI事件成功，11个不同snapshot_revision。验证轮询、手动刷新、页面重载、focus事件处理器、0/2启动以及2/2完成前后状态。focus由浏览器脚本派发，不等同人工切换操作系统窗口；没有修改BUG-0014作为通过证据。
- 浏览器证据：evidence/browser-lifecycle.json 与 before-start-1440.png、requirement-started-1440.png、bug-started-1440.png、completed-1440.png。已检查截图：卡片阶段与动作一致；computed style为display:flex、font-size:13px、width:300px。截图中的合成BUG分级标签沿用现有展示，本次不调整分级映射。
- 自检修复：隔离API夹具缺工作区表改为测试边界隔离；CLI夹具YAML列表缩进修正；故障恢复测试重新从文件读取完整frontmatter，避免旧record错误报告额外变更。失败均在当前apply内修复并重验。
- 证据边界：浏览器是真实本地服务与合成数据，未执行生产发布；中断/冲突为故障注入测试，未制造线上进程故障。API响应结构、DB、OpenAPI/Orval、对象存储、部署配置、安全权限及埋点协议均无变化，无需迁移或客户端重生成；API索引补充状态语义。CLI不伪造usage_events。

AC映射：001/002/007→共享状态+接口+浏览器；003→dry-run/缺Sprint/未启动拒绝；004→状态计数+接口；005/006→重复/旧终态/原子中断/投影重跑；008→两份apply与sprint-apply契约；009→CLI投影+context；010→真实浏览器；011→既有项目范围回归+脱敏证据。技能文本契约校验不宣称启动了其他Agent会话。

## 完成门禁结果

13/13任务完成；最终后端/工作流85项回归通过。OpenSpec严格、中文、目录、上下文预算、观测、目标Sprint Scope与真实行为轨迹校验通过。opsx.apply同步更新5项、错误0，关联Change为applied，Issue仍in_sprint、人工验收pending。隔离服务已停止，无生产发布。

AI Usage钩子已执行：warning，usage_mode=unavailable，command_run_count=0；缺少可归属token_count记录，Sprint用量快照跳过，未估算或伪造用量。
