---
title: 评审恢复记录生产与消费契约
created_at: '2026-10-19 14:55:00'
updated_at: '2026-10-19 14:55:00'
source: BUG-0047-review-recovery-operation-record-missing
status: verified
---

# 评审恢复记录生产与消费契约

部署旧动作名单跳过 req-review 操作初始化，收尾却要求 operation，导致合法评审遭到恢复阻断。工作区名单已扩展不能证明实际运行服务已修复。

准备成功应包含基线和操作记录完整性核验；worker 在模型启动前再次核对。两次原子文件写入之间可能中断，不能将单文件原子写入误称为多文件事务。缺失、损坏和身份冲突保留原记录并明确诊断，不补空文件绕过；重复准备保留已观察步骤和原终态。

继承 BUG-0044 的对象互斥、权限与成果核验。恢复不得伪改失败轮次；已应用结果回读、重复核查和并发变化分别验收。合成回归、真实评审、部署进程版本分别记录，最终证据见 fix-review-recovery-operation-record-missing 的 verification.md。

隔离验证中真实需求轮次中断后，既有成果核验链成功应用且保留 stopped；判断业务成功应回读唯一应用与源状态。测试副本应先核验初始索引、验收来源元数据及预期合法迁移，避免将夹具问题误判为修复失效。

## 本地业务部署与历史会话核验（2026-10-19）

用户授权同步本地运行容器后，复用已归档 BUG-0047 修复，执行 `test_review_operation_record.py`、`test_requirement_completion_recovery.py`、`test_chat_preparation_failure.py`，54 项通过。部署配置预检、backend/web/worker 镜像构建及 Compose 收敛检查通过；backend、worker、controller 健康，Web 运行。Worker 的三个相关模块指纹与已测试工作区一致，API 实际加载的错误映射包含原始恢复错误码，执行准入为 ready。更新前创建 SQLite 一致性备份，完整性检查通过；未修改环境文件、端口或安全配置。

目标 REQ-0046 评审的事实源仍在 plan、状态 pending_review、优先级 P2；没有 review.md，没有应用记录。私有候选与直接命令记录均仅保留 baseline.json，没有 result.json 或 operation.json。模型文字中的“评审通过”不能证明成果已应用，也没有足够文件证据直接恢复该次评审。

仅校正该历史候选的错误诊断：从 executor_unavailable 改为原轮次真实的 direct_command_recovery_blocked，沿既有 Task Trace 记录 diagnostic_corrected。保留候选 rejected、轮次 failed、原始轮次错误及业务文档；没有补造 operation、重跑模型或标记应用成功。产品候选查询回读为 rejected、文件数 0、无 application。

浏览器刷新另发现独立阻塞：`src/web/src/runtimeBuild.ts` 的旧面板清理扫描所有带 aria-label 的容器，并按包含的正文匹配“确认应用”等文字。最小 DOM 样本调用实际清理函数后移除两个节点，chat-main 不再存在；目标页面实际仅剩侧栏。该缺陷阻断本轮可视提示验收，未纳入已归档 BUG-0047 的代码修改。后续应单独修复清理选择器，并增加带 aria-label 的会话正文回归；本轮未自动创建 Issue/Change。

product_data_collection_observability: applicable；affected_layers: Task Trace、候选诊断、Web 回读。validation: 原始终态保留、单候选诊断校正及服务回读已验证。此次复用既有交付，无新增 API、数据库结构、客户端生成、对象存储或采集字段变化；原归档中隔离验收的结论不替代上述本地业务核验。
