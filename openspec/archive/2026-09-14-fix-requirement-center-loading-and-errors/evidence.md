---
created_at: '2026-09-12 23:58:33'
updated_at: '2026-09-13 00:46:18'
bug_id: BUG-0016-capture
---

# 读取优化与异常交互验收证据

## 实现与边界

当前requirements注册表可正常解析，未再次修改其内容。无法确认历史错误由哪个写入者造成；既有候选校验拒绝非法YAML的回归通过，保留写入围栏和隔离副本。

稳定读取保留每次两遍真实内容扫描，已验证内容指纹仅跳过重复语法解析。稳定非法内容直接返回source_invalid，变化与无法安全读取分别为source_changing/source_unavailable；错误码仍为2603。分类和request_id均不包含路径或正文。

只读临时树按项目根/绑定版本/内容指纹分组，最多4份、128MiB。树构建、使用与淘汰通过进程内锁串行保护；写入器不使用该缓存。每个HTTP请求重新执行授权和数据库围栏。解析器只在显式immutable上下文启用请求内纯函数备忘，退出即清理；不缓存用户数据或权限结论。SafeLoader在libyaml可用时加速，否则回退原安全加载器。

## 回归

`PYTHONPATH=src/backend python -m pytest` 针对 test_governance_scope、read_cache、writer、candidates、capture、change_visibility、board 的合计124项通过；随后增加尺寸/总量/数量超限及暖缓存绑定变化4项，read_cache单文件10项通过。原测试中临时树调用计数切换到只读适配器；实际写入副本回归保持通过。TypeScript `tsc -b` 通过；OpenAPI从FastAPI导出，Orval生成governance/chat客户端成功。

## 性能对照

使用修复前保存的snapshot、reader、requirement_center模块；基线和优化版共享同一冻结文件树与隔离SQLite账号，走ASGI HTTP路由、授权和数据库围栏。身份依赖由测试夹具提供，不是用户浏览器登录或网络TTFB。

固定输入1065文件、4918971字节；内容指纹 `5ee84a73c1594a0bfc98faaf8358440d8199a062c3afad1bdebbf531b26d8cd5`。每操作首次请求后分别顺序30次暖读，所有HTTP200；p95使用排序后第29个样本。清空进程读取/验证缓存另测一次冷读，同输入指纹；不声明清空OS文件缓存。

| 路径 | 基线p50/ms | 优化p50/ms | 基线p95/ms | 优化p95/ms | p95改善 | 基线/优化缓存冷读ms |
|---|---:|---:|---:|---:|---:|---:|
| context | 1915.50 | 234.42 | 2173.23 | 289.79 | 86.67% | 1990.46 / 401.26 |
| BUG capture.md | 510.42 | 74.30 | 663.49 | 94.54 | 85.75% | 607.40 / 342.47 |

逐次样本：`logs/bug0016/benchmark.json`。可重复的显式测试入口：`src/backend/tests/test_governance_read_benchmark.py`，需设置BUG_READ_BENCHMARK=1、BUG_READ_BASELINE_DIR和BUG_READ_BENCHMARK_OUTPUT；BUG_BENCH_COLD=1测独立缓存冷读。基线模块为本轮编辑前的临时备份，不提交原始副本。首次适配器探测及未达到50%的试验仅用于调优，不充当最终验收。

## UI与交互验收

用户在本轮回复“确认”，首轮Skeleton门禁解除；骨架证据为 `logs/bug0016/bug0016-skeleton-page.png`、`bug0016-skeleton-dialog.png`。已接入真实页面和MD抽屉：紧凑页内错误、保留旧数据并标识更新时间与暂停写入、权限失败清空、主动详情弹窗、安全复制、重试去重及旧响应隔离。source_invalid停止自动轮询，手动重新加载仍可恢复。

前端全套20文件204项通过；随后补充自动轮询暂停和复制失败/遮罩回归，错误交互单文件9项通过（合计206项，分次执行）。`tsc -b`及backend/web Docker生产构建通过。测试选择器歧义和构建测试类型错误均在当前apply内修正并重验。

真实Chromium使用真实React页面、合成HTTP故障/恢复，运行 `cd src/web && node tests/requirement-center-errors.cjs`，深浅主题×1440×1000和390×844共4组通过。首次失败、详情、旧数据提示、抽屉失败均有截图，路径为 `logs/bug0016/{error,details,stale,drawer}-{dark,light}-{1440,390}.png`。截图检查与computed style见 `logs/bug0016/ui-validation.json`：标题15px、说明13px；弹窗宽度受480px及viewport约束；按钮、间距、边框、颜色、overflow与层级均采样。无pageerror，最大并行context为1；复制、焦点恢复、Tab双向圈定、只关闭最上层Esc、失败重试恢复通过。单测补充权限撤销、同版本隐藏对象清空、迟到响应、草稿保护、缺失request_id不伪造、复制失败内联反馈。

Mock/API边界：错误注入仅用于隔离浏览器及单测；未向用户项目写入畸形文件。用户附件用于现状问题分析，非逐像素复刻目标。真实部署正常读取另列，不将Mock当成线上观察。

## 实际部署观察

2026-09-13，本地Docker Compose重建backend/web并仅替换这两个服务，backend健康检查Healthy；web为running且HTTP入口200（未配置容器Health字段）；使用用户在可见登录页自行登录的日常项目账号。未修改权限、数据库、env或其他服务。实际看板、BUG的bug.md、REQ的requirement.md、关联Change的design.md均返回200，抽屉呈现正文并结束loading，手动刷新成功。卡片未提供capture.md入口，该文档由ASGI真实路由基准覆盖，不冒称浏览器打开过。

通过临时同源观察入口采集真实fetch和Resource Timing，只保留操作、状态、request_id、TTFB、总耗时和Server-Timing；不提取会话或响应正文。`logs/bug0016/live-browser-observation.json`保存代表样本，`live-request-log.json`保存同编号的后端request_logs安全字段。BUG/REQ/Change文档TTFB为250/217/370ms，context观察约263–2584ms；较慢样本后端2474.88ms，其中扫描/围栏1349.10ms、解析1122.55ms，说明差异主要在服务端读取处理，不能全归因于网络。容器挂载实时项目、宿主机负载和输入条件不同于冻结ASGI基准，未建立部署前30次同条件基线，不对外承诺SLA。

CUA曾因点击时按钮disabled而超时；100ms DOM持续采样记录可用2302次、禁用314次，随后实际手动点击成功及context返回200，排除持续卡住。未将单次工具超时认定为应用根因。临时观察HTML验收后删除，浏览器回到正常需求中心；真实登录保留。

API兼容：2603不变，新增可选安全kind/request_id与503模型，OpenAPI和Orval客户端已同步；Server-Timing仅输出固定白名单分段数字，不暴露路径或正文。新增响应头关联断言通过，scope/read_cache最近18项通过。

## 回滚与恢复

部署前保存本地旧镜像标签 `moonbox-backend:bug0016-before`、`moonbox-web:bug0016-before`；如需回退，恢复对应两个服务镜像并仅重建backend/web，再验证健康与需求中心读取。已验证标签可用、当前服务健康；本轮未实际执行回滚，不冒称回滚演练通过。只回退本Change代码时保留其他活动Change，禁止全仓库reset。API重启释放进程缓存；缓存是可重建临时文件，无DB迁移，不需要DB恢复。写入器保持独立materialize。

## 完成与行为记录

BUG AC-001至019的工程验证已逐项回填，整体业务验收状态由opsx.apply同步为pending，归档另行执行。根因、Sprint、目标中文优先、OpenSpec严格校验及observed行为轨迹在完成前执行。真实行为记录 `logs/bug0016/apply-behavior.json` 仅覆盖已观察的自检修复、登录依赖期间继续独立工作和压缩续接，不宣称未发生场景通过。
