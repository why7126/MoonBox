---
purpose: 验收项与测试映射
content: REQ/BUG acceptance 与自动化测试的追踪索引
created_at: 2026-07-29 23:10:00
updated_at: 2026-07-29 23:10:00
owner: MoonBox 产品团队
---

# 测试映射

```yaml
REQ-0000-build-design-system:
  acceptance: [DS-AC-001]
  tests:
    - scripts/validate-design-system.py
    - src/web/src/design-system.test.tsx
REQ-0000-build-api-standard:
  acceptance: [API-AC-001]
  tests:
    - scripts/validate-api-standard.py
    - src/backend/tests/test_health.py
    - tests/integration/api/test_health_contract.py
REQ-0000-build-test-standard:
  acceptance: [TEST-AC-001]
  tests:
    - scripts/validate-test-framework.py
    - tests/unit/test_baseline.py
```
