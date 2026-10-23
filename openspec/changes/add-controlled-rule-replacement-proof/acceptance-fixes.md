---
title: REQ-0050 方案替换及验收返修台账
created_at: '2026-10-22 18:58:00'
updated_at: '2026-10-22 20:16:00'
status: in_progress
---

# REQ-0050 方案替换及验收返修台账

## 反馈与范围

用户要求补齐首次可信启用的部署接线、精确清单生成校验、运维制品审阅与独立授权入口、所有者转换详情/确认、执行结果和中断恢复，以及真实页面验收。属于原 AC-013/014/016/017/019 的交付缺口；继续原 Change，不增加权限角色或让在线后端持有运维私钥。Change applied 与首次 completed_at 保持，返修期间展示研发中。

根因 confirmed：PolicyInstallation 只有读取/确认/恢复；准备接口要求外部提交 manifest+ops_receipt，缺生成/导出/导入完整操作；标准 Compose 无信任/签名挂载。部署和运维准备不能由所有者点击替代。

## 附件截图逐项视觉对照表

| 参考 | 页面/状态 | 期望 | 实际与偏差 | 检查方式 | 处置与证据 |
|---|---|---|---|---|---|
| 用户 REQ-0050 卡片截图 | 需求中心验收中，浅色；原始视口未知 | 28/28 后明确首次启用条件及入口 | 通用兼容证明失败，没有可操作启用步骤 | 截图文字、archive_recovery准入路径 | 本次细化安全诊断；不改卡片布局 |
| evidence/product/bootstrap-prepared-1440.png | Chat抽屉，1440 | 运维清单来源/差异/证据可审阅 | 仅状态与摘要，不能生成或导入 | 已有真实截图与PolicyInstallation源码 | 在原抽屉内补步骤和详情，保持主题token |
| evidence/product/bootstrap-active-390-light.png | Chat抽屉，390浅色 | 完成事实与下一步明确 | 只有active提示 | 已有截图与DOM契约 | 补结果/归档边界及原操作恢复说明 |
| evidence/product/confirm-final-1440-light.png | 共用确认弹窗 | 独立确认、取消、焦点归还 | 原动作族可用，不应另建不一致弹窗 | ChatDialog与既有交互测试 | 复用确认族；重新采集受影响样式/截图 |

本轮实际产品39002首页可访问；正式数据不作为测试写入目标。细节仍用一次性隔离账号和项目真实验收。截图未知原视口不作为像素复刻要求；补充1440×900/390×844深浅主题矩阵。

## 方案与动作矩阵

- 部署检查/生成转换清单：只读API，服务端计算当前身份、各摘要与临时副本预演；不写归档或批准。精确候选来自机制Change，不允许任意旧新策略自由输入。
- 运维审阅：页面展示制品、变更、逐条差异、验收与独立门禁，导出无密钥清单包。独立运维CLI只读校验包和可信配置，用显式私钥文件签发bootstrap.ops；不生成默认信任或自动接受制品。
- 导入授权：粘贴/读取无私钥签名收据，确认后调用既有prepare；签名与当前输入不一致拒绝，保留输入和清单。
- 所有者确认：展示同一精确清单及差异，明确会归档机制Change，不关闭Sprint/批准其他对象。取消不提交；未知结果回读同一操作。
- 恢复：authorized/activating展示原operation、阶段、阻断处理指引和继续按钮，active显示唯一归档及验证事实。

| 动作 | 类型 | selector | 状态与验收 |
|---|---|---|---|
| 检查/生成 | 原抽屉内步骤 | installation-generate | loading/blocked/ready，生成无写入 |
| 导出运维包 | 下载 | installation-export | 精确摘要与公开绑定，不含私钥 |
| 导入运维收据 | 原抽屉表单+确认 | installation-import | malformed/invalid/stale/success，拒绝保留 |
| 所有者转换 | ChatDialog | replacement-bootstrap-dialog | 详情/取消/确认/未知，独立权限 |
| 原操作恢复 | 同确认族 | installation-resume | 阶段/安全错误/幂等，不能新建绕过 |

样式沿用现有720px抽屉/520px确认窗；窄屏单列、长摘要换行、步骤层级清晰、底部动作可达。采集字体、padding/gap、宽高、边框背景、overflow及焦点证据。布局方向承接用户既有确认，不重新问同一方向。

## 验证与一致性扫尾

逐项结果见下文；旧受影响视觉与指纹不作为本轮通过。

## 本轮完成事实与证据

- 真实部署：构建 Dockerfile.replacement，完整基础/Chat/governance/replacement Compose 合并检查通过；隔离运行实际 replacement overlay 的 backend 和 signer，信任根/工具只读、事实目录可写、在线私钥仅签名器可读。governance-controller 只接公开信任，不接签名 socket；Agent 挂载构造未扩大。离线运维签名容器无网络，未挂载正式项目或密钥。证据 `evidence/modify-bootstrap/deployment.json`。
- 真实页面：已连接项目直接显示审阅入口，无需会话或模型。生成当前 Change 的精确 delta 副本清单，导出浏览器下载包，离线工具真实校验/签发，页面拒绝篡改收据并保留输入，再导入正确收据、由实际隔离所有者二次确认。并非 mock API 或伪造 active。
- 中断恢复：测试签名器仅允许 owner 用途，最终提交签名拒绝，实际操作停在 activating/synced；恢复正常签名用途并重启后端后，经页面继续同一 operation 到 active/completed。前后 spec_hash 相同，唯一机制归档，模型轮次为零。`interrupted.json`、`completed.json`、`exact-change-bootstrap.json` 保留对照。正式 REQ、BUG-0063、sprint-012 未启用或归档。
- 视觉：1440×1000 的生成、篡改错误、所有者确认和恢复；1440×900/390×844 深浅完成态；390 确认、恢复和长差异单列。目视确认无横向溢出、摘要完整换行、动作可达、深浅主题对比清晰。`styles-390.json`、`styles-1440.json`、`styles-dark-390.json`、`diff-styles-390.json` 记录 14px 字体、366px 确认窗、360px 单列、anywhere 摘要换行、pre-wrap 条文。关闭焦点回到审阅按钮；错误与恢复后草稿保留。截图均在 `evidence/modify-bootstrap/`，旧首次启用截图不作为本次覆盖；未修改的业务批准/拒绝族旧证据保留，并有现组件回归支持。
- 回归：后端原有替代测试与新增安装/部署/权限测试通过；前端 Composer、首次启用、替代审阅 29 项通过，TypeScript 与生产构建通过。Node 25 原生 Web Storage 与 jsdom 冲突通过测试环境关闭实验 Web Storage 消除；socket 用例在获准本机环境执行。仅保留既有 Starlette 弃用和构建块大小提示。最终逐 AC 结果另见当前 acceptance 证据包。

## REQ 子文档一致性扫尾检查

已同步 requirement.md、business-flow.md、user-stories.md、acceptance.md、prototype/web/context.md 和 prototype.html，覆盖常驻入口、独立运维、所有者、结果/恢复及 Mock/API 边界。trace.md 通过 Workflow Sync 更新；历史 capture.md、review.md 无需更新，原因是原始输入与评审授权范围未改变。Change design/spec delta/usage-notes、API 索引/生成客户端、部署说明/.env.example、Sprint 验收与发布说明同步。数据库无需新增迁移，原因是继续使用原 activations/events 表；对象存储无需变更，原因是审阅包由浏览器下载、签名收据为既有 JSON 请求。

product_data_collection_observability：适用；affected_layers 为 request_logs、usage_events、task_traces、authorization_audit、governance_archive；验证沿用 ReplacementRoute 与真实独立签名事件，敏感私钥不进页面、请求或证据。preview 只读请求不产生授权事件；授权事实仍来自签名收据与不可变事件账本，遥测不是批准证据。

执行中补充修正：常驻入口消除新会话无法进入准备流程；将请求失败文案调整为“转换尚未完成”，避免已授权且已归档中断被误称为“尚未确认”。原 applied 和首次 execution.completed_at 不变。

最终完整验收：28/28 passed，run `20261022201403331050-96f89e7c`，实际执行 7 组命令、去重 21 项，失败/阻断/待采集均为 0。正式归档准入仍为 archive_requirement_conflict，须正式首次可信启用，不用隔离授权替代。

## Chat 治理入口位置返修（2026-10-22）

反馈：审阅规则替代证明出现在消息输入框内，混淆消息发送与项目级治理操作。证据状态 confirmed：`src/web/src/components/chat/Composer.tsx` 原将 `ReplacementReview` 渲染在输入区与发送工具栏之间，`evidence/modify-bootstrap/result-light-1440.png` 可见旧布局；该截图只证明旧版展示，不证明本轮新布局。

| 附件/截图编号 | 页面/状态 | 对照对象 | 期望 | 实际与偏差 | 检查方式 | 处置 | 证据入口 |
|---|---|---|---|---|---|---|---|
| 历史 1440 真实页 | Chat 新会话、浅色、抽屉开启 | 原型与旧交付 | 治理操作归属项目 | 旧入口位于 Composer 内 | 截图与源码 | 移至项目操作区 | `evidence/modify-bootstrap/result-light-1440.png` |
| 历史 390 真实页 | Chat 窄屏、浅色、抽屉开启 | 原型与旧交付 | 输入区只承担草稿发送 | 旧按钮占输入区一行 | 截图与源码 | 同一入口随项目栏折行 | `evidence/modify-bootstrap/result-light-390.png` |
| 归档阻断 | 兼容证明待核验 | ArchiveBlockers 与设计 | 可就地审阅同一提案 | 旧阻断项仅文本指引 | DOM/组件测试 | 增加上下文动作，共用抽屉 | `src/web/src/components/chat/ArchiveBlockers.test.tsx` |
| 本轮 1440×900 真实页 | Chat 新会话、浅色 | 项目关系栏与 Composer | 项目操作区可打开审阅，输入区无常驻按钮 | 新布局符合预期 | Chrome 响应式视口与抽屉操作 | 通过 | `evidence/modify-bootstrap/entry-relocated-1440.png`、`entry-relocated-drawer-desktop.png` |
| 本轮 390×844 真实页 | Chat 新会话、浅色 | 项目关系栏与抽屉 | 窄屏入口可见、抽屉可打开 | 新布局符合预期 | Chrome 响应式视口与抽屉操作 | 通过 | `evidence/modify-bootstrap/entry-relocated-390.png`、`entry-relocated-drawer-390.png` |

调整：项目关系栏显示常驻审阅入口；兼容证明阻断项另给快捷按钮，由页面状态统一打开同一 `ReplacementReview`，不新增授权端点或批准能力。新会话可从项目栏直接进入首次可信启用。Composer 移除常驻治理按钮；草稿、附件、Skill 和服务端鉴权不变。原型将入口移至项目操作示意，保留阻断项中的 Mock 快捷按钮。

验证：前端聚焦测试 26/26 通过，TypeScript 与 Vite 生产构建通过；正式可登录页及本轮隔离页均观察到项目入口、干净的 Composer、同一审阅抽屉与首次可信启用区域。深浅主题、1440×900/390×844 及 computed style 的返修轮次证据见下文，不以旧版截图充当证据。兼容阻断快捷入口由组件回归覆盖，正式项目当前没有可安全复用的该阻断现场。

增量验收：历史首次启用清单仍按原始哈希核对，返修后的当前规格另由 `evidence/modify-bootstrap/current-delta-hashes.json` 精确核验；证据脚本通过。16 项授权/签名/提交回归在允许临时 Unix socket 的本机环境通过。完整 AC 重跑得到 24 项通过、4 项视觉预检阻断、0 项失败（run `20261022220211759075-1a3bb200`）：旧隔离视觉服务 `127.0.0.1:39041` 已不在运行，不能把正式服务 `39002` 冒充隔离环境；本轮不宣称完整 acceptance ready。

隔离环境恢复与任务 7.3 收尾：使用 `/private/tmp` 的独立合成身份、项目、签名器和数据库重建 39045 后端，并将当前 Web 源码运行于 39041；视觉预检与隔离登录通过，正式服务 39002 未替代隔离样本。新增本轮 `entry-isolated-{light,dark}-{1440,390}.png`、相应 `-styles.json` 和 `entry-isolated-drawer-{light,dark}-{1440,390}.png`，逐项覆盖 1440×900/390×844、深浅主题、入口及抽屉。计算样式确认入口为 12px、主题 token 颜色，四种组合均无横向溢出；关闭抽屉后焦点返回 `replacement-review`。目视核对窄屏入口与抽屉内容可见；隔离 Chat 的执行服务提示不完整，故本轮仅作 UI 取证，不把它写作真实命令执行。当前计划覆盖已引用新截图与样式。完整验收 run `20261022221747288100-4ea3ff82` 为 28/28 passed，执行 2 组命令、去重 6 项、复用 20 项，失败、阻断、待采集均为 0；归档最终准入仍须后续共享门禁复核。

收尾：归档临时副本预演通过，`opsx.accept` 同步后 REQ 验收状态为 passed，AI Usage 为 actual 且无 warning。共享归档准入仍以 `archive_requirement_conflict` 阻断，原因是后继写入前兼容证明未通过；不以本轮 28/28 AC 通过覆盖该独立门禁。

REQ 子文档一致性扫尾检查：已同步 requirement.md、business-flow.md、user-stories.md、acceptance.md、prototype/web/context.md 与 prototype.html；trace.md 由 Workflow Sync 更新。capture.md/review.md 为历史输入和评审事实，无需重写。API/DB/部署/安全/客户端生成无需更新，原因是本轮仅调整现有 Web 入口与组件联动，未改变服务端契约、权限或持久化。

## 轻量方案替换（2026-10-23，进行中）

产品决定先停用旧版运维制品审阅、首次启用和常驻项目审阅入口，再实施对象阻断项中的“查看修改→空间所有者确认或拒绝→重新检查”。原版已归档记录、签署、证明和进行中的操作仍保持历史身份，不能被新确认直接替代。旧验收计划备份于 `evidence/legacy/acceptance-plan-original-20261022.json`，新版计划对应 AC-L01—L12，当前均待独立取证。

已完成：旧版页面及新写入入口停用；新增精确原新条文检查、确认记录和不可变事件；对象归档阻断项打开上下文抽屉；确认不发送 Chat 命令、不执行归档。当前 BUG-0063 样本的只读预检在无确认时阻断、精确确认后通过规则项、项目绑定改变后重新阻断；其他验收和归档门禁仍独立。初轮归档聚焦回归 105 项、Chat 回归 53 项通过，前端组件 4 项和 TypeScript 通过，OpenSpec 严格校验通过。该合成与源码验证不代替真实页面、完整归档或 MySQL 验收。

待完成：正式空间所有者与无权人员的独立登录操作、草稿与附件保留、MySQL 跨入口及中断恢复完整样本；验收通过前不将旧版 28/28 结果标为新版完成。

隔离组件视觉样本：`evidence/lightweight/rule-review-{1440,390}-{light,dark}.png` 与同名 JSON 使用真实新抽屉组件、合成 API 数据，在 1440/390 深浅主题下确认宽度、背景/文字计算样式及无横向溢出。它只证明组件布局，不证明当前正式页面的对象绑定、真实登录权限或归档调用；正式页面证据仍待采集。

隔离真实页面增量证据：`evidence/lightweight/isolated-real-chat-{1440,390}-{light,dark}.png` 与同名 JSON 使用隔离 Chat 服务及最新 Web 页面，验证对象操作区上下文入口、原新条文抽屉、1440/390 深浅主题计算样式、无横向溢出、草稿未被清空、未发送 Chat turn；`isolated-real-chat-confirm-dialog-1440.png`、`isolated-real-chat-confirmed-1440.png`、`isolated-real-chat-revoked-1440.png` 记录隔离样本的确认与撤销。隔离 API 分别验证无权账号 403、所有者确认 200、撤销 200，且确认后验收门禁仍独立。该样本是隔离验证，不代表正式项目已授权或已归档。

扩展回归：后端全量 1151 通过、11 失败、12 跳过；失败分别涉及已有需求中心文案预期、治理候选前置状态、进程守护在当前系统的进程查询限制，尚未纳入本 Change 通过结论。前端全量在关闭 Node 25 实验性全局 Web Storage 后 424 通过、10 失败；失败集中在 Capture 持久化与 Sprint 归档弹窗旧预期。REQ-0050 聚焦测试和类型检查通过，扩展回归失败需要与本次变更范围分别归因，不据此宣布全面验收通过。

### 2026-10-23 增量验收与当前服务核对

重新构建本地 Web、后端及 Chat worker 后，浏览器中重新加载 `localhost:39002/chat`，未关联对象的新会话不再显示旧版常驻“审阅规则替代证明”按钮；需求中心仍显示 REQ-0050 在验收中、当前有效验收 0/12。服务 OpenAPI 保留旧版只读及恢复路由供历史操作核对，旧版新增授权写入由服务端返回退出状态；新版 `/api/v1/chat/rule-changes` 及 `/decision` 已部署。该观察只证明当前服务版本与入口状态，不构成有权确认或归档成功。

自动检查器本轮诊断包为 `evidence/acceptance/20261023093043664746-0c1ead31/`：12 项均因缺少本版完整样本签认而 blocked，聚焦命令执行 2 次、相同命令复用 9 次、无功能检查失败。曾误将 AC-L07/L08 后端归档复核标为视觉检查，已改为命令与文件状态；AC-L06 的视觉前置条件也已补入计划，仍须以当前计划重新检查。最终只读归档准入返回 `ready: false`、`done: 0/12`，原因是验收证据未全部通过，不是规则确认已经足够。

按修正后的计划完成一轮完整检查：`evidence/acceptance/20261023093301482108-4f1cc6a4/`，`scope: complete`，12 项 blocked、0 项功能检查失败；两类聚焦命令实际执行 2 次、同轮去重 10 次。当前缺口为产品样本签认，命令成功未被冒充成 AC 通过。

剩余实证边界：AC-L01/L02 需非 BUG-0063 正反样本；AC-L03/L04 需完整角色与逐类版本变化；AC-L05 需独立测试与验收签署；AC-L06/L09/L10 需阻断到抽屉、空态/错误/无权、附件与草稿的完整真实页面样本；AC-L07/L08 需跨入口、并发和中断恢复及前后哈希；AC-L11/L12 需新旧切换与双对象独立状态。当前隔离控制通道失联，按保护规则保留现场，不删除 socket 或按旧 PID 终止未知进程。不得将隔离已有截图、命令通过或当前正式服务只读观察扩大为上述未覆盖结论。

MySQL 增量样本：使用独立的 MySQL 8.2 内存容器完成新确认表及审计表迁移、写入、请求键唯一性和审计事件不可修改检查；结果见 `evidence/lightweight/mysql-rule-change-20261023.json`。首次尝试的测试夹具缺少管理员基础表而失败，补齐外部事实源空表后通过；临时容器已清理。它只覆盖数据库迁移和存储约束，未覆盖 MySQL 产品归档、并发与恢复，不能独自签认 AC-L03/L04/L07/L08。

重新启动独立 SQLite Chat 服务，在 BUG-0063 合成副本与两个独立测试账号下验证：空间所有者可读取并确认，查看者确认返回 403，过期内容版本被拒绝，确认后可撤销且状态回到阻断；结果见 `evidence/lightweight/isolated-api-roles-20261023.json`。没有向 Chat 发送命令，没有归档正式对象；临时服务及数据已受控清理。原 39021 样本仍占用端口且控制通道失联，本轮改用 39022，不强行终止未知进程。该证据补充 AC-L03/L04 的部分产品行为，其他版本变动、正式验收签署和跨入口提交前复核仍待验证。

最新完整检查包 `evidence/acceptance/20261023094233097430-0275c53b/` 已将上述两份脱敏记录绑定到 AC-L03/L04，标记为部分样本；12 项仍全部 blocked，0 项功能检查失败。随后共享归档准入再次返回 `ready: false`、`done: 0/12`，原因为新版验收未全部通过。未执行规格归档预演或正式归档。

### 2026-10-23 再次执行 /opsx-accept

新一轮完整检查包为 `evidence/acceptance/20261023094948478083-c1c756f3/`：后端轻量规则测试 7/7、前端审阅组件测试 5/5 通过；检查器执行 2 类命令并复用 10 次，功能检查失败 0 项。但 12 项均因产品样本、独立签署和跨入口证据未齐而保持 blocked；`--readiness` 与共享 `--archive-readiness` 均为 0/12、`ready: false`。隔离页 39022 将复制的 BUG-0063 治理样本显示为“状态或归档版本存在歧义”，未把该页面计为有效对象证据。该合成样本问题与正式项目事实分开，不据此推断正式对象异常。未执行归档预演或正式归档。

继续核对后，隔离文件的治理索引直接读取 BUG-0063 与关联 Change 均为“验收中”，说明副本文件身份本身可解析；39022 的产品页面路由当前返回 404，控制端失联。`evidence/lightweight/isolated-service-diagnostic-20261023.json` 只作为隔离环境故障诊断，先前的“歧义”页面不得充当有效产品样本。另用独立 REQ 合成副本检查同一精确规则修改：可识别原新文本与历史归属，额外弱化文本及缺少历史链均拒绝；见 `evidence/lightweight/non-bug-scope-matrix-20261023.json`。该副本仅补 AC-L01/L02 的部分矩阵，不等于真实非 BUG 对象页面验收。

本版任务 8.3—8.6 仍未勾选，需求中心展示研发 26/30、验收 0/12。后续不能在缺独立验收签署、跨入口恢复和真实页面证据时将任务或 AC 改为通过。

当前正式 Chat 未关联会话中未显示旧版 Composer 审阅按钮，画面与页面断言见 `evidence/lightweight/current-chat-no-composer-rule-button-20261023.png`、同名 JSON；它只覆盖无关联对象的新会话，不覆盖对象阻断项。将新增部分证据绑定计划后完整重跑，报告为 `evidence/acceptance/20261023100611084252-cafc44c9/`：命令执行 2 类、复用 10 次，功能失败 0，12 项仍因完整产品样本和独立签署缺失而 blocked，未扩大为已验收。

新建 39023 隔离环境后，先登录合成空间所有者，再打开已准备的 Change 对象会话，需求中心正确展示 BUG-0063 为验收中，消除了上一轮旧服务页面的歧义。真实 Chat 项目操作区显示“查看规则修改”，可展开原规则和修改后全文；取消确认、Esc 关闭并返回触发按钮、确认、撤销均已在页面观察。确认后仍显示验收缺失且不自动归档；撤销后规则项重新阻断。全过程草稿保留、Chat 轮次为零、合成 Change 保持活动态。证据为 `evidence/lightweight/isolated-round3-rule-review-owner.png`、`isolated-round3-rule-review-confirmed.png`、`isolated-round3-rule-review-confirmed.json`、`isolated-round3-ui-actions.json` 和 `isolated-round3-no-archive.json`。无权合成账号可查看差异但不能确认或拒绝，见 `isolated-round3-rule-review-nonowner.png/json`。39023 隔离实例及合成数据已通过控制端清理。

附件上传仍受 Chrome 扩展文件网址访问限制：自动选择无敏感数据的隔离测试附件被扩展明确拒绝。该项不计为附件保留验收通过；正式签署、跨入口归档提交前复核、长文/错误/空态完整视觉矩阵也继续保留缺口。

新增视觉样本第一次纳入计划时，AC-L09 的逐视口截图尚未列入顶层证据清单，产生一次 `scope: diagnostic` 预检阻断；已补全映射并重新执行完整入口。当前完整报告为 `evidence/acceptance/20261023102436765453-4ce4d84f/`：12 项 blocked、0 项功能检查失败、命令实际执行 2 类、同轮去重 10 次。此前诊断包 `evidence/acceptance/20261023102332136464-d49c61c0/` 不作为整体验收结论。

本轮补证（2026-10-23）：隔离技术回归合计 133/133 通过，覆盖确认后七类保护资料变化、历史证明重复发布及篡改、REQ/BUG 跨入口准入和归档合并并发阻断。摘要见 `evidence/lightweight/confirmation-invalidation-matrix-20261023.json`、`rule-proof-idempotence-20261023.json`、`archive-cross-entry-regression-20261023.json`。旧版准备和审批写入端点在当前代码中返回 409，旧版新归档端点只允许已领取操作恢复；此项仍缺真实产品状态切换验证。以上是隔离技术证据，不替代真实产品轮次、附件、独立签署或正式归档准入。

本轮真实产品补证（2026-10-23）：恢复独立 Chat 测试服务，并接入仅本机、无持久卷的测试对象存储。先在缺对象存储配置的隔离环境验证：文件选择器可选中测试文件，但页面明确报“文件保存失败”，故不算附件验收。补齐隔离存储后，用系统文件选择器上传 52 字节无客户数据文本；页面出现可移除附件，数据库记录 `ready`，对象存储记录 52 字节。尝试发送 `/opsx-archive BUG-0063-compatible-requirement-successor-blocked` 后，发送前因验收证据不齐被拒绝；附件与草稿仍在，Chat 轮次为 0，未执行归档。证据 `evidence/lightweight/isolated-upload-blocked-retained-20261023.{png,json}`。该阻断先于规则确认，不冒充完整规则门禁验收。

旧流程切换隔离样本：建立一条仅供测试的旧版 prepared 记录，经真实 API 调用旧审批和旧新归档入口，均返回 409；未新增旧授权事件或归档操作，历史记录保留。证据 `evidence/lightweight/isolated-legacy-write-guard-20261023.json`。未找到具备原始可信材料的已领取旧操作，故旧进行中恢复仍待取证；不会伪造旧操作或将新版确认当成旧授权。

独立验收签署：当前 REQ 验收记录仍为 pending，accepted_by 为空；产品确认者与验收签署需独立，本轮自动取证不能代签。由有权验收人员审阅本轮正反例、页面与归档阻断证据后签署，签署前 AC-L05 与归档准入继续阻断。

用户澄清：BUG-0063 的历史操作发生在 Codex 当前会话，并无产品内旧进行中操作，不能据此要求或伪造产品旧操作 ID。改用旧版隔离安装的真实中断/恢复记录核对同一 operation、清单和规格哈希、单一归档数量，再用本版隔离真实 API 和合成 claimed 路由回归验证旧新写入阻断、原操作身份稳定、新确认未自动生成。旧版测试中 1 项仍要求停用的候选入口放行，另 4 项夹具缺新版确认事件表；已校正测试预期与夹具，相关 40/40 通过。证据 `evidence/lightweight/legacy-recovery-cross-version-20261023.json`。此组合不冒充 BUG-0063 产品内旧操作的真实恢复；AC-L11 仍保持部分证据。

### 2026-10-23 最小闭环收敛

验收反馈：产品目标仍是解决一次可解释规则修改的归档阻断，但 AC-L08/L11 曾要求 BUG-0063 的产品旧进行中操作，实际仅有 Codex 会话。此样本不存在，不能由人工补造。已将 REQ 正文、业务流程、故事、验收、Change 提案/设计/规格、Sprint 验收报告统一为五类必要结论；保留 AC-L01—L12 编号、安全负例、独立签署及最终写入门禁。同一有效样本可多项复用；页面仅对受影响入口做真实视觉取证，现有组件状态用既有回归证明。没有降低断链、篡改、并发、越权或未签署的拒绝条件。

REQ 子文档一致性扫尾：`requirement.md`、`business-flow.md`、`user-stories.md`、`acceptance.md` 已同步。`prototype/web/context.md` 与 `prototype.html` 已是阻断项内查看修改的轻量交互，不包含旧操作恢复入口，本轮无需改动。`trace.md` 的生命周期字段由 Workflow Sync 维护；本次只在 Change trace 追加返修摘要。未修改 API、数据库、部署、安全或生成客户端契约，现有确认及归档代码路径不变。

状态边界：本轮仅收敛验收要求，不将部分样本标记为通过。独立验收人员尚未签署；BUG-0063 的当前输入变化需单独重跑 18 项验收。REQ-0050 自身归档与 BUG-0063 具体规则确认仍分开，sprint-012 未获关闭资格。

BUG-0063 当前版本增量复验首次诊断为 14 项通过、2 项前端测试失败、2 项产品轮次因隔离数据库已停止而阻断。前端失败是本机 Node 对 `localStorage` 暴露了不完整接口，非页面实际拒绝逻辑；在 `src/web/src/archive-blockers.test.tsx` 给该用例显式隔离存储后，相关 4/4 测试通过。隔离数据库缺失仍须重建相关样本后复验，不用旧截图伪造当前轮次。

本轮最终复验：REQ-0050 完整入口 `20261023113130227673-0e0aad06` 为 12 项因样本未齐 blocked、0 项功能失败；BUG-0063 入口 `20261023113149453103-14e59f30` 为 16 项通过、2 项因历史隔离产品数据库离线 blocked、0 项失败。两条 `opsx.accept` Workflow Sync 均成功，Issue 验收状态仍为 pending；sprint-012 准入仍因 BUG-0063 的当前验收未就绪而 blocked。未签署、未改写历史、未正式归档。

继续补齐可独立执行的 UI 回归：`ReplacementReview.test.tsx` 增加加载中、读取失败和无权确认三个状态断言，6/6 通过；它们补充 AC-L09 的组件行为证据，不充当真实页面视觉签认。

2026-10-23 继续完成新版实现核对：旧版提案审批及首次启用写入口已停用，集成测试改为断言“历史提案可读、旧入口拒绝新写入且不产生审批/归档记录”；新版接口增加真实登录、空间所有者、无权成员、精确版本、幂等与版本变化测试。SQLite 及独立临时 MySQL 8.2 均通过新版确认表和唯一性约束检查，临时容器及凭据已清理。后端聚焦回归 68 passed、1 skipped（MySQL 只在独立环境显式启用）；单独 MySQL 兼容用例 1 passed；Chat 抽屉与阻断项前端用例 7 passed。归档共用复核及旧操作恢复由上述后端回归覆盖，因此任务 8.3、8.4 作为实现任务完成；这不代表 AC-L01—L12 的真实产品验收或独立人员签署通过，任务 8.5、8.6 和归档门禁继续保留。

本轮隔离产品正向归档未通过：业务预检及缺签署拦截正常；补入明确标注的隔离测试签署值后，归档器因隔离夹具脚本不在只读可信部署目录而拒绝写入。模型实际用量 0 Token，未更改正式 Sprint。BUG-0063 的 AC-014/015 仍缺当前同轮产品正向证据，详见 `openspec/changes/fix-compatible-requirement-successor/evidence/reapply/isolated-trusted-archive-boundary-20261023.md`。此失败不能折算为新版规则确认通过。全仓 API 标准校验另报 `capture_drafts.py` 的 image 路由缺少 response_model，属于本 Change 外既存问题，不据此改写本轮 API 结果。

本轮继续在隔离真实 Chat 补齐新版受影响入口视觉与附件证据：1440×900、390×844 的深浅主题均打开规则修改抽屉并采集截图与计算样式；未见横向溢出。抽屉关闭后焦点回到入口，命令草稿保留。实际上传 68 字节无客户数据图片，产品记录与隔离对象存储均显示已保存；随后在同一会话尝试发送归档命令，服务于发送前返回 409「验收证据缺失、过期或未全部通过」，附件与命令草稿仍在，Chat 轮次 0。证据见 `evidence/lightweight/live-rule-review-visual-20261023.json`、`live-rule-review-{light,dark}-{1440,390}.png`、`live-rule-review-attachment-retained-20261023.json`、`live-rule-review-attachment-after-gate-reject-1440.png`。结合此前确认/拒绝动作证据与组件回归，任务 8.5 已完成。该拒绝发生在验收准入，不证明规则确认后的成功归档；任务 8.6 与独立签署仍待完成。

新版完整验收入口 `20261023130514316369-a93d13f9` 重新核对 12 项：0 项失败、12 项因计划所需样本仍标为部分而 blocked；当前视觉和附件证据已经列入 AC-L09/L10，但不会自动代替独立验收签认。`opsx.accept` 状态同步成功，REQ-0050 保持待验收。sprint-013 仍因本 Change 的 8.6 和验收准入未就绪被阻断；sprint-012 因 BUG-0063 的验收未就绪被阻断。两个 Sprint 的历史链扫描均通过，未写入正式归档。隔离 Chat、对象存储及临时凭据已清理。

## 2026-10-23 v4 去除额外规则确认

用户选择直接修订 REQ-0050 并重新评审。需求、流程、故事、原型与 AC-L01—L12 已同步为“查看修改→独立验收→重新检查→原归档命令”；移除确认、拒绝及撤销按钮和新版证明的确认依赖，旧完成证明沿原版本只读核验。旧 `/decision` 写入口返回 409，不产生新确认。BUG-0063 当前草案写“不再要求独立兼容证明”，与本版首个安全允许场景不同，精确差异检查继续阻断。历史样本保留供追溯，但 acceptance-plan 的当前必需样本均回到 partial，不能把旧确认视觉或 API 证据算作 v4 通过。聚焦后端 8 项和前端 8 项通过；完整真实页面、独立验收及跨入口复验尚待补齐。

当前 v4 完整验收入口 `20261023211447519762-7f16a24d`：12 项受阻、0 项测试失败，归档准入 0/12；命令执行 2 组、去重 10 项。后端归档聚焦回归 128 项通过，前端组件及关联栏 8 项通过，OpenSpec 严格校验和中文标题校验通过。v4 视觉门禁重新标为 pending，正式服务仍为旧版本，尚未用当前前后端完成真实页面和独立签署验收。

## 2026-10-23 v5 BUG-0063 归档后事实校正

偏差证据 confirmed：`issues/bugs/_registry.yaml` 将 BUG-0063 指向 archive，`openspec/archive/2026-10-23-fix-compatible-requirement-successor/` 存在且活动 Change 不存在；`openspec/specs/governance-command-durable-recovery/spec.md` 已明确同条文后继按正常验收，不再要求独立兼容证明。v4 仍把 BUG-0063 当候选且要求额外证明，造成需求、样本与生效规则矛盾。

本次将 BUG-0063 改为历史读取样本；当前归档正反例使用未归档隔离对象。差异页只回显现行验收和归档结论，不创造第二套许可或证明。旧确认入口仍拒绝写入，旧版完成证明保留只读。REQ 子文档、原型、Change 规格和 sprint-013 验收/发布说明按此收敛；旧历史段落保留但不作为当前验收。独立签署和真实页面/归档复验仍待完成。

### v5 逐项诊断（2026-10-23）

当前完整入口 `20261023225114357767-f44e70ec` 为 diagnostic：AC-L12 命令与当前历史文件检查通过；其余 11 项保持未就绪，其中 AC-L06/L09 缺本版真实页面的四视口/主题截图与计算样式，另外 9 项仍缺当前未归档产品样本、跨入口或独立验收证据。命令执行 2 组、去重 8 项，0 功能测试失败。由于整体证据不齐，共享归档准入仍为 0/12、blocked；单项诊断通过不能折算为整体完成。

聚焦回归：后端归档与恢复 140 项通过、前端 9 项通过，TypeScript、OpenSpec 严格和中文校验通过。浏览器只读观察当前本地需求中心 `localhost:39002/requirements` 显示 REQ-0050 在验收中、0/12；该服务页面未证明 v5 当前源码已部署，不能作为本版视觉证据。已归档 BUG-0063 的正常验收基线仅用于历史核对，未重写。
