# 需求元数据恢复历史

REQ-0048 在本次恢复前，两个 Change 投影分别为 proposed、archived；需求主文档与 trace 状态均为 in_sprint。旧主 Change 保持 add-isolated-candidate-validation，不修改身份或首次执行时间。

原 prototype_refs：

```yaml
prototype_refs:
  - path: issues/requirements/review/REQ-0048-chat-isolated-acceptance-orchestration/prototype/web/prototype.html
    role: html-structure
  - path: issues/requirements/review/REQ-0048-chat-isolated-acceptance-orchestration/prototype/web/context.md
    role: decomposition
prototype_gate:
  decomposition: done
  ui_skeleton: pending
  visual_acceptance_1440: pending
  req_final_consistency: pending
```

恢复依据：已归档 Change 原 trace 的 prototype_gate 为 done/done/passed/passed，完整验收清单 20 项通过，含双视口产品截图与样式证据。可变 Issue 引用改为需求目录内相对路径；原当前摘要完整留在 Issue trace 的归档恢复记录。受保护 Change 内容与原恢复日志逐文件哈希保存在 archive-before-sha256.json。
