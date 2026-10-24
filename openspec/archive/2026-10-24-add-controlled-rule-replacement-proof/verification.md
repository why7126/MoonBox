---
title: 受控规则替代证明实施验证
created_at: '2026-10-22 17:46:00'
updated_at: '2026-10-22 17:46:00'
---

# 受控规则替代证明实施验证

## 交付范围

实现精确规则例外扩展、当前所有者授权、独立签名器、五表持久化、首次可信转换、统一归档围栏和恢复、在线 CLI 与 Chat 审阅。普通归档与已完整归档 Sprint 的关闭走同一围栏；未完成范围、独立签署、验收清单或可信配置缺失仍阻断。

API/OpenAPI/Orval、数据库、部署、安全、测试映射、知识库及用户说明已同步。公开 Mintlify latest 保持已发布版本，usage-notes.md 为待发布用户说明；没有扩大正式部署或归档授权。

## 证据类型与样本

| 类别 | 事实 | 证据 |
|---|---|---|
| 合成回归 | 逐类篡改、期限、角色变化、撤销领取竞争、围栏、混合链、断链和故障窗口 | acceptance-plan.json 中定向测试组 |
| 隔离真实 API/文件 | 独立信任根与不同用途密钥，策略转换、授权及首次归档完成 | evidence/product/runtime-v7-summary.json、archive-v5-result.json |
| 最新控制器执行 | 实际 service enqueue → worker claim → run_claim；Sprint 完成，轮次 completed，executor_turn_id 为空，用量 settled/0 | evidence/product/runtime-v8-summary.json |
| 最新故障恢复 | 停止签名器后原操作停于 synced；API 重启并恢复签名器，同一操作 completed；规格哈希不变；再次请求 replayed=true | evidence/product/recovery-v8-before.json、recovery-v8-after.json、recovery-v8-replay.json |
| 精确机制转换 | 本 Change 两份完整规格增量在独立合成基线中完成转换后 active；正式项目未写入 | evidence/product/exact-change-bootstrap.json |
| 真实浏览器附件 | 合成账号实际上传 69 字节文件到隔离 MinIO，ready 且未删除；归档门禁拒绝后草稿/Skill/附件保留，turn_count=0 | evidence/product/attachment-skill-rejection.json/.png |
| 真实浏览器审阅 | 实际 owner 审批动作、管理员审批403、取消/Esc/焦点归还、深浅主题与响应式 | evidence/visual-review.md、product/图片与样式 |
| 正式对象只读 | sprint-012 仍 BLOCKED：BUG-0063 验收证据需更新，以及5处历史子文档活动路径残留 | evidence/product/formal-sprint-012-readonly.txt |

控制器执行为实际服务集成，不冒充浏览器发起的模型轮次。旧 v7 unknown 轮次保留失败事实，修复治理目录快照后 v8 才取得成功；完成只允许当前可信控制器事件支撑零模型结算。过期和部分状态截图使用投影夹具；不冒充可信批准、自然经过24小时或实际归档。

## 逐项覆盖

AC-001/002/005/007：精确身份、受保护义务和可信分类 profile；同名任意替代、证据与交付变化拒绝。

AC-003/004/006：有效空间所有者与人类会话、可信签名用途/版本/项目绑定、24小时及撤销竞争；管理员 UI/API 拒绝，CLI在线核验。

AC-008/009/010/012：独立签署、验收、任务与范围门禁；共享锁/围栏、原操作恢复、完成事实唯一；真实签名器停机和服务重启验证。

AC-011/015：独立→追加→替代→追加跨Sprint混合链；缺边/重复/篡改阻断；普通到期、所有权变化和保留公钥的轮换不抹历史，信任撤销仍阻断。

AC-013/014：独立部署引导器、两类授权、精确机制转换后策略生效；缺根、自证、循环、错误制品和中断均闭锁或原操作恢复。

AC-016/017：差异/保留义务/独立签署分组、批准拒绝撤销及首次启用独立确认；批准不发送不归档，结果未知回读。

AC-018：通用非BUG-ID实现，正式BUG-0063及sprint-012只读，不能借本次交付跳过正式门禁。

AC-019/020：普通遥测写失败不取消已成功可信授权；授权事件写失败拒绝批准，审计不可变，五表迁移可重放。SQLite与MySQL实际兼容测试分开记账。

AC-XCUT-001—004：既有 Composer 19项测试涵盖上传状态/重试/草稿；真实附件成功后的拒绝保留与隔离身份观察补足。

AC-PROTOTYPE-001—004：用户骨架确认已取得；五阶段×四视口主题明确映射，最终确认窗补齐业务说明；REQ/流程/故事/原型/trace一致性检查完成。签认只涉及产品实施，不代签正式Sprint。

## 验证记录

定向后端稳定批次先前216通过，受 PATH 影响的真实 OpenSpec 用例单独补跑通过；新增完整混合链30通过、工作流20通过、API8通过、可信Chat5通过；MySQL兼容批次27通过。上述批次存在交集，不累加成总测试数。最终逐项证据包将保留本轮精确执行与复用计数。

前端最终29通过，TypeScript通过；生产构建及治理校验结果见 trace.md。所有恢复证据通过 evidence/verify-evidence.py 只读一致性验证。该脚本不替代视觉签认。

## 正式归档边界

当前 Change 触及受保护机制规则，正式归档仍须可信部署制品确认与项目所有者精确转换授权。隔离成功不构成正式启用授权。未执行正式 BUG-0063 替代、未关闭 sprint-012、未改写 openspec/specs。

## 首次可信启用返修验证

完整逐 AC 28/28 通过，证据包 evidence/acceptance/20261022201403331050-96f89e7c；真实部署、独立离线签发、页面导入/确认、中断重启恢复及 1440/390 深浅主题证据见 evidence/modify-bootstrap。独立规格副本实际转换成功，正式项目未启用。前端 29 项、TypeScript、构建及治理校验通过，完整台账见 acceptance-fixes.md。
