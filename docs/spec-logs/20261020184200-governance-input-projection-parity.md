---
title: 验收输入跨环境一致性修复
created_at: 2026-10-20 18:42:00
updated_at: 2026-10-20 18:42:00
---

# 验收输入跨环境一致性修复

## 验收输入跨环境一致性返修

根因 confirmed：产品治理投影只从可信源码补读 src/scripts，新增 tests/unit 输入在产品侧变为 missing，而 CLI 完整工作区可读，阻断 AC-ARCHIVE-PREVIEW-REGRESSION。隔离只读诊断补读 tests 后两条链路均 ready。另有目录输入被当作 missing，遗漏规格内容及成员变化。

修复：仅扩展既有可信源码白名单到 tests；治理文档仍从当前投影读取，不回退其他工作区。目录采用 directory-v1 确定性成员名、类型与内容哈希，涵盖空目录、增删与重命名；拒绝内部/外部符号链接及特殊文件。原单文件指纹兼容不变，既有目录证据按新算法失效后重验。

入口矩阵：完整工作区 CLI → 分离投影共享读取器 → 部署后端 → 对象会话准备/发送预检 → 浏览器。必须核验实际产品准入，不能用 CLI ready 替代。新增 AC-INPUT-PROJECTION 覆盖正向/陈旧测试/治理文件缺失/越界/目录变更。部署后版本哈希与准入证据另存 evidence/input-projection-product.json。

附件对照：截图消息框报“验收证据缺失、过期或未全部通过”，期望有效当前验收允许发送；偏差来自后端输入读取，不是视觉布局。检查方式为部署后真实准备接口与页面状态；本轮不改前端，不触发模型消息或正式归档。

REQ 子文档一致性扫尾检查：requirement、business-flow、user-stories、acceptance、trace、prototype/web/context.md 与 prototype.html 产品行为和验收目标不变，无需重写；修复跨环境验证实现并在此回填证据。BUG 原根因保留，本次补充验收读取缺陷。

API/DB/Web/客户端/管理端/Orval 无契约变化；部署需更新后端、controller、worker 中共享读取器。product_data_collection_observability: N/A；affected_layers: []；不增加数据采集或事件字段，仅脱敏诊断。

更新文件：共享 acceptance_evidence.py、两份后端测试、两条 Change 文档与计划、验收标准和部署说明。最终验证证据归属两条 Change 的 evidence/acceptance 与 evidence/input-projection-product.json。
