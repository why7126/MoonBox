---
requirement_id: REQ-0009-git-check-pre-push-security-gate
created_at: 2026-08-09 07:21:45
updated_at: 2026-08-09 07:21:45
---

# 业务流程

## 主流程

```text
开发者 / Agent
  |
  | 运行 /git-check
  v
git-check 命令入口
  |
  |-- 复用 env ignore 校验
  |     |
  |     |-- 失败 -> 输出 error，返回非 0
  |
  |-- 收集默认扫描对象
  |     |
  |     |-- staged files
  |     |-- tracked files
  |
  |-- 路径策略扫描
  |     |
  |     |-- 真实 env / runtime data / db / uploads / build / archive / large files
  |
  |-- 文本敏感内容扫描
  |     |
  |     |-- secret / token / cookie / auth header / connection string / local absolute path / privacy data
  |
  |-- 结果分级与脱敏
        |
        |-- 有 error -> 返回非 0，提示修复
        |-- 仅 warning -> 返回 0 或按策略返回非 0，提示人工复核
        |-- 无风险 -> 返回 0，输出通过摘要
```

## 可选全仓扫描流程

```text
/git-check --all
  |
  |-- 使用全仓扫描对象替代默认 staged + tracked 范围
  |-- 继续执行 env ignore、路径策略、文本敏感内容、大文件和报告流程
  |-- 输出中必须标明 scan_scope: all
```

## 与现有能力关系

- 复用 `scripts/validate-env-ignore-policy.py`，不复制另一套 env ignore 判断。
- 补齐 `.gitignore` 无法覆盖的 staged/tracked 风险检查。
- 不替代 OpenSpec、发布、Mintlify、镜像和目录结构校验；它是推送前安全入口。

## 状态与异常

| 场景 | 期望处理 |
|---|---|
| 本地 `.env` 存在但被 ignore 且未 staged/tracked | 不阻断 |
| `.env.example` 被误 ignore | error |
| 真实 `.env` 已 staged 或 tracked | error |
| `*.db` 或 `data/runtime/**` 已 staged/tracked | error |
| 文档中出现 `<access_token>` | 不因占位符本身 error |
| 文档中出现真实 Authorization header | error，输出脱敏片段 |
| 命中低置信个人信息模式 | warning，提示人工复核 |
| 文件超过大文件阈值 | 按路径和类型输出 error 或 warning |
