---
change_id: apply-tilesfst-data-collection-governance
status: proposed
created_at: 2026-08-27 00:27:55
updated_at: 2026-08-27 00:27:55
---

# Acceptance

- [x] AC-001：MoonBox 存在产品数据采集与链路观测标准，覆盖行为事件、请求日志、Task Trace、流程节点、脱敏、保留周期和固定声明。
- [x] AC-002：MoonBox 存在 Task Trace 覆盖清单，候选场景按当前启用范围重写，不包含小程序/App 或学习对象业务专属内容。
- [x] AC-003：产品数据采集门禁脚本可校验标准文档、规则入口、技能入口和目标 Change/Sprint 声明。
- [x] AC-004：`AGENTS.md`、`rules/`、`.agents/skills/` 和 `docs/README.md` 已接入轻量门禁摘要。
- [x] AC-005：本次学习报告落入 `docs/spec-logs/`，不包含学习对象本机绝对路径、系统用户名、源码全文、密钥或真实客户数据。
- [x] AC-006：验证通过，且 `git diff --name-only -- src` 输出为空。

product_data_collection_observability:
  status: applicable
  affected_layers:
    - governance_rules
    - docs_standards
    - workflow_skills
    - validation_scripts
  reason: "验收对象就是数据采集治理门禁本身；本次不承诺运行时采集表、API 或前端请求封装已经实现。"
  validation: "以标准文档校验、门禁脚本、OpenSpec validate、Sprint scope 校验和 Workflow Sync 作为验收证据。"
