---
title: 需求中心中文业务标题生成与校验治理记录
created_at: "2026-09-15 23:33:05"
updated_at: "2026-09-15 23:33:05"
---

# 需求中心中文业务标题生成与校验治理记录

## 授权与变更

来源BUG-0019，sprint-007，fix-requirement-center-stage-business-titles。用户批准阶段标题来源规则和全部生成文档中文标题要求。

规则入口为rules/language.md；12份capture/generate/complete/review/opsx生成技能补齐title/H1、注册表同步和失败门禁。新增validate-document-titles.py与共享titles.py；Workflow Sync在生成完成状态写入前校验，产品候选应用前验证，注册表用Issue业务title安全写回。

## 验证与边界

当前Change与BUG聚焦中文标题、OpenSpec严格解析、语言、上下文预算、目录和Sprint Scope校验；产品Capture、Agent候选及工作流回归详见Change verification.md。未批量更改历史归档或正式specs，不创建额外Issue/Change。API可选字段和Orval客户端已同步，无DB迁移。

## 复用建议

在其他治理项目落地时，先建立阶段来源矩阵，再把读取兼容与新产物校验分开。将中文title/H1与注册表同步纳入正式应用/状态写入前门禁，保留OpenSpec解析关键字，以不同合法标题、歧义关联、错误候选和真实页面证据验证。
