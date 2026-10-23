#!/usr/bin/env python3
"""稳定验证契约正反例：python scripts/test-stable-validation-contract.py。"""
import importlib.util
from pathlib import Path
from tempfile import TemporaryDirectory

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('budget', ROOT / 'scripts/validate-agent-context-budget.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def main():
    source = 'docs/standards/opsx-acceptance.md'
    with TemporaryDirectory() as temporary:
        root = Path(temporary)
        for relative in (source, *module.STABLE_VALIDATION_PATHS):
            target = root / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text((ROOT / relative).read_text())
        assert not module.validate_stable_validation_contract(root)
        for term in module.STABLE_VALIDATION_TERMS:
            target = root / source
            original = target.read_text()
            target.write_text(original.replace(term, '已移除'))
            assert module.validate_stable_validation_contract(root), term
            target.write_text(original)
        for relative in module.STABLE_VALIDATION_PATHS:
            target = root / relative
            original = target.read_text()
            target.write_text(original.replace('opsx-acceptance.md#稳定批次与增量复验契约', '失效引用'))
            assert module.validate_stable_validation_contract(root), relative
            target.write_text(original)
        (root / source).unlink()
        assert module.validate_stable_validation_contract(root)
    print('通过：1 个正例、11 个条款删除反例、8 个入口引用反例、1 个事实源缺失反例。')


if __name__ == '__main__':
    main()
