---
title: 模型续接与长期证据转存验证
created_at: 2026-10-29 21:15:00
updated_at: 2026-10-30 11:25:00
---

# 模型续接与长期证据转存验证

## 本轮续接与长期转存实施（2026-10-29）

用户继续授权模型自动续接和长期证据转存，真实产品验收仍待接入。实现已接入固定 App Server 0.153.4 的 `item/tool/call`：新建受控实现线程注册 `moonbox_acceptance`，从当前授权范围捕获独立检查点；存活轮次由唯一执行器发送一次结果，收到对应完成通知才记录已消费。RPC 响应之前到达的工具请求保留到事件循环处理。发送后确认丢失时保留未知事实，不重发、不创建第二个消费者。

原轮次失败且执行器关闭、文件归集和环境释放均确认后，通过正常 Chat 准入事务创建最多一次关联轮次。事务重验权限、绑定、输入、原总期限、占用和额度，保留原轮次终态；有限 token 预算只允许使用原余额，未知用量或余额耗尽拒绝。关联轮次不能另建验收操作重置自动续接次数。主动停止及撤权在执行启动和事件循环重复核验；用户停止的原轮次与未知执行不自动续接。

长期转存保存白名单脱敏摘要到当前 Change 的 `evidence/runtime/`，以 attempt 身份和 SHA-256 保持不可变；使用项目写锁、原子替换、读回校验及持久 pending/published 记录恢复写后中断。查询每次重验当前权限和内容哈希。在线七日过期后仍可通过“长期摘要”读取已转存结果，不延长原截图或原始日志的访问期限。摘要包含逐 AC 结果、输入/部署/证据摘要，明确 `visual_artifacts_included=false`；真实产品视觉材料仍需按产品验收流程单独脱敏签认。

固定运行时的 thread/resume 协议不提供动态工具注册参数，因此既有未注册线程不被冒充具备该能力；新建受控线程可注册，既有线程保留现有 API 和已确认失败后的关联续接路径。未接入真实模型/产品轮次，不把合成 stdio、事务、截图或 MySQL 回归写成产品签认。

product_data_collection_observability: applicable；affected_layers: Chat API、请求/行为观测、持久编排、模型工具、Task Trace、Web。沿用现有分阶段追踪和请求封装，长期摘要读取仅记录既有脱敏请求元数据；不采集 prompt、命令原文、凭证或宿主路径。validation: 事务/协议/ACL/取消/预算/崩溃恢复回归、真实 MySQL 独立表、双视口组件取证；真实产品轮次待接入。

## 验证来源与边界

- 集中后端回归：148 passed、3 skipped。覆盖验收模块、Chat 本地执行与 App Server、会话/API；跳过项为显式 Docker 运行矩阵和本地真实登录/模型探针。Docker 合成矩阵已有独立运行证据，真实模型探针按用户范围待接入。
- 增量检查：新增真实 Git 存活检查点、写后关联恢复、原 token 预算及阻止关联轮次重置次数；最终结果记录在 `evidence/implementation/continuation-evidence.json`。
- 前端：6项交互测试通过，TypeScript通过；OpenAPI已导出、Orval8.29.0本地生成通过。脚本的pnpm版本探针受本机工具目录写权限限制，使用已安装的固定Orval可执行文件完成生成，未下载依赖或修改锁文件。
- 真实浏览器：生产组件+真实测试API+合成身份/状态，在线证据已过期而长期摘要可读；1440×900弹窗680px，390×844弹窗350px、左右20px，摘要换行无横向溢出，Esc关闭。入口 `evidence/implementation/ui/long-term-1440.png`、`long-term-390.png`、`long-term-style.json`。不是完整Chat/真实模型视觉验收。
- Docker磁盘边界：登记容器、只读根、8MiB tmpfs；实际填满返回ENOSPC，根写入返回EROFS。该小容量破坏性探针结合既有容器配置采样证明限制机制，不冒充完整20GiB压力测试。
- MySQL新增表约束与清理：见 `evidence/implementation/continuation-mysql.json`。

## 历史检查点（2026-10-29）

当前可执行实现、合成验证、文档和客户端同步已推进；仍不能将Change标为applied/ready。剩余6.3、6.4及7.3依赖真实产品部署批准模板、授权产品轮次与对应角色/视觉样本。用户已明确保留待接入，不重复请求“继续”，不制造产品turn ID、不自动归档。正式20项AC仍保留未签认。

首次MySQL复验遇到Docker默认地址池耗尽；只读核对占用后为本次测试设置独立私网子网，未删除其他任务网络。全登记reap预览曾被自动审批拒绝，理由为可能涉及其他登记资源；随后仅操作本run登记、精确清理和check。


## 本机真实产品验收（2026-10-30）

用户本轮明确授权本机隔离产品接入，禁止生产数据。此前“模板待接入”已解除。使用当前 MoonBox 源码的独立 Git 快照、全新 SQLite/MySQL 数据、随机短期测试账号和固定本机镜像；不复制项目 env、运行数据库或对象存储凭证。模型授权仅进入独立执行器私有认证介质，运行结束删除该副本。产品应用容器不持有模型凭据，执行网络内部隔离；所有容器与专属网络属于本次登记。

复现入口为 `src/backend/tests/ACCEPTANCE_PRODUCT.md`。模板由本机镜像真实摘要生成，不要求用户手写连接串。`product-final.json` 记录源文件摘要与模板摘要；它证明真实应用矩阵，不单独证明 Chat 轮次。真实模型轮次另见 `chat-final.json`、`chat-space2.json`、`chat-passed.json`、`chat-recovery-fixed.json`、`chat-stopped.json`。

### 产品适配与修复

- 使用 MoonBox 实际登录响应和浏览器会话存储；成员/只读身份分别通过实际授权检查，后台接口拒绝403。临时账号15分钟截止由隔离适配器冻结账号并撤销会话；另外以独立短期账号实测到期后重新登录401，不仅验证会话过期。
- 修复 MySQL 重复启动时索引已存在的兼容路径，仅接受相同列顺序与唯一性；时间统一按 UTC 存储和输出。无新增生产表结构。实际 MySQL 8.4.13、utf8mb4、utf8mb4_0900_ai_ci、UTC、JSON、排序/分页和事务回滚均在容器中断言；SQLite执行同组兼容探针。
- 执行器终止恢复时保留文件归集所需写锁到归集完成，避免提前释放导致 `files_collected=0`。新独立恢复样本确认执行器关闭、文件归集完成、原轮次 stopped 且不自动续接；旧失败样本保留用于根因，不作为通过证据。
- 异步打开长期摘要后 Esc 关闭恢复焦点到原按钮；单元测试与真实浏览器 `focus-return.json` 一致。
- 正式验收器增加只读原生工具证明，验证操作/轮次/attempt/输入身份、执行回执、工具确认及最多一次关联投递，不伪造 shell 命令或完成事件。缺数据库、缺归集或错代次均拒绝。

### 独立真实样本

| 样本 | 实际结果 | 证据 |
|---|---|---|
| 最终模板首次成功 | 真实模型调用 moonbox_acceptance，双数据库/双浏览器/双角色通过，工具结果一次消费，资源释放 | product-final.json、chat-final.json |
| 第二授权空间 | 独立控制器和空间绑定完成同一真实流程；不宣称同账本同时运行 | chat-space2.json |
| 应用容器中断 | 产品检查受阻，模型准确报告 blocked，资源释放 | chat-passed.json 的 0cb13150 操作 |
| 原执行器终止与重启回读 | 权威 App Server 记录 interrupted，原轮次 stopped、文件已归集、无关联续接 | chat-recovery-fixed.json |
| 失败源自动续接 | 仅破坏一次性私有命令日志，由真实完成守卫判 failed；原终态保留，同 attempt 创建并完成一个关联模型轮次，投递 consumed | failed-source.json、chat-passed.json 的 d9f36e81 操作 |
| 用户停止 | UI确认停止，操作 cancelled、原轮次 stopped、资源释放、resume_count=0 | chat-stopped.json |
| 清理失败与重试 | 本次登记的故障 peer 阻止专属网络删除；业务通过而 cleanup_failed，移除 peer 后产品重试清理，同 attempt 释放，不重跑 AC | chat-passed.json 的 f8ffdbcf 操作及 real-cleanup-failed/releasing/released 截图 |
| 证据权限 | 其他测试用户读操作、在线证据、长期摘要和停止均404，版本未变 | role-access.json |

真实故障均限定一次性环境；没有注入轮次终态、AC通过或投递成功数据库行。准备/就绪/执行截图采用真实状态迁移后的短暂观察屏障，心跳保持；不替换 API 返回或写假状态。取消、未知用量、响应确认丢失、旧 epoch、绑定变化、检查点损坏和竞争等边界由集中回归补充；该部分明确属于合成状态回归，不能称为所有故障均在真实模型上重放。

### 视觉与交互签认

真实 Chat 七阶段（preparing、ready、running、blocked、cleanup_failed、releasing、released）分别有1440×900与390×844深浅主题截图，共28张 `real-阶段-主题-宽度.png`。恢复/续接、停止确认、长期摘要另有独立交互图。真实API与真实模型产生状态，原型只作为区域与动作语义参考。

共享卡片与动作组件 computed style 风险点采样见 `space2-主题-宽度-style.json`、`real-running-light-390-style.json`、`real-released-light-390-style.json`。实测移动端文档宽390、卡片宽294、字号14/行高20.3、padding12；颜色/边框/间距/定位/z-index和宽度记录于样式文件。样式采样覆盖共享组件和深浅主题，未声称每张阶段截图都有独立完整样式采样。移动端沿用原 Chat 输入区，长卡片需滚动查看底部动作；阶段截图不等于所有按钮同时可见。独立弹窗和焦点证据证明关键动作可操作。

### 验收范围与证据分类

本机 Linux arm64 已实测；amd64未启用。实际浏览器/运行时版本由模板锁定。已有8MiB tmpfs填满及只读根探针证明硬限制机制，不宣称完成20GiB容量压测。长期转存仅白名单摘要，不延长原截图七日在线保留；七日到期和篡改拒绝使用受控时钟/合成记录回归，真实产品验证当前摘要可读取、ACL有效及哈希可核验。

product_data_collection_observability: applicable；affected_layers: Chat、API、数据库兼容、模型执行器、环境编排、Web、request_logs、task_traces、证据访问。validation: 真实产品矩阵/模型样本/ACL与脱敏导出，以及集中协议、事务、恢复和界面回归；不新增Prompt采集、不修改客户端API契约，无需本轮再次生成客户端。

当前逐AC结论、输入指纹和归档准入以随后生成的 evidence/acceptance/ 最新完整报告为准；下文完成记录只在实际门禁通过后填写。


### 撤权实测与最终修复

真实测试发现冻结账号的HTTP登录/请求已拒绝，但后台仅复核空间成员身份，仍可能继续运行。现已在 Chat 空间准入和治理授权中共同校验用户正常且未删除；后台每轮复核与关联续接继承相同限制。新增回归覆盖账户冻结后的 Chat/验收后台授权拒绝，测试数据库最小夹具同步真实状态字段。

独立修复后样本操作 `10cd530b-c2cc-4125-b64a-a5bd1997ee77` 在17.08秒内释放环境，执行器关闭、resume_count=0；当时来源轮次 unknown，如实保留。恢复测试账号授权后，通过有审计的运维恢复入口仅恢复权威回读，确认原轮次 stopped；没有新模型轮次。证据为 `revocation.json` 和 `chat-final.json`。修复前的独立失败样本仍保留，但不作为通过结论。

最终正常复验操作 `d9051808-6a42-4f17-a281-51b4c3a89f5f`、来源轮次 `622f38f0-3d49-4202-b04e-16d458e4572b` 完成真实模型工具链，验收passed、资源released。最新实际产品矩阵在权限修复后的源码上再次通过。
