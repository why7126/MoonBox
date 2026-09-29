## 验证范围

- 目录结构校验脚本能在当前 legacy 目录存在时通过，并输出可见 warning。
- OpenSpec Change 文档、delta spec 和中文优先规则通过校验。
- `sprint-007` 能识别本纯治理 Change。
- 治理日志和长期文档不包含真实运行数据、密钥或本机绝对路径。

## 验证命令

```bash
python -m py_compile scripts/validate-directory-structure.py
python scripts/validate-directory-structure.py
python scripts/validate-agent-context-budget.py
python scripts/validate-openspec-language.py --change standardize-data-runtime-storage-layout --residual-report
openspec validate standardize-data-runtime-storage-layout --strict
python scripts/validate-sprint-scope.py sprint-007 --item standardize-data-runtime-storage-layout
python scripts/sync-workflow-status.py --event opsx.apply --change standardize-data-runtime-storage-layout --sprint auto
```

## 不适用验证

- API、数据库 schema、Web、管理端、客户端和 Orval 生成验证不适用；本 Change 不触达业务实现。
- Docker Compose 运行时切换验证不适用；本 Change 只沉淀治理目标和迁移注意事项，不直接切换挂载路径。
