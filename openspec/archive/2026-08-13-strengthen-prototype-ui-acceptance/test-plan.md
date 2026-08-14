# Test Plan

## Governance Validation

- Run `python scripts/validate-agent-context-budget.py`.
- Run `python scripts/validate-openspec-language.py`.
- Run `python scripts/validate-directory-structure.py`.
- Run `openspec validate strengthen-prototype-ui-acceptance`.
- Run `python scripts/validate-sprint-scope.py sprint-002 --item strengthen-prototype-ui-acceptance`.

## Manual Review

- Confirm no `src/` business runtime files are modified.
- Confirm `rules/ui-design.md` and `docs/standards/prototype-ui-acceptance.md` cover all requested gate items.
- Confirm changed skills reference the new standard without forcing non-UI Changes through prototype gates.

