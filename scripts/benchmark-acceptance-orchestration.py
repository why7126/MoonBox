#!/usr/bin/env python3
"""Compare committed baseline and current runner on identical isolated synthetic scenarios."""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
import tempfile
import time
import types
from pathlib import Path

import opsx_acceptance as current


def run_case(module, scenario: str) -> dict:
    with tempfile.TemporaryDirectory(prefix='acceptance-comparison-') as tmp:
        root = Path(tmp).resolve()
        change = root / 'openspec/changes/comparison'
        change.mkdir(parents=True)
        (root / 'input.md').write_text('共享稳定条件')
        checks = [dict(id=f'AC-{i}', kind='command', inputs=['input.md'],
                       argv=[sys.executable, '-c', 'import time; time.sleep(0.02)'],
                       deduplicate=True) for i in range(1, 4)]
        if scenario == 'local-evidence-gap':
            checks[0]['artifacts'] = ['missing.md']
        (change / 'acceptance-plan.json').write_text(json.dumps({
            'schema_version': 1, 'orchestration_version': 1,
            'change_id': 'comparison', 'checks': checks}))
        executions = 0
        original = module.run_command
        def count(check, root):
            nonlocal executions
            executions += 1
            return original(check, root)
        module.run_command = count
        started = time.monotonic()
        try:
            result = module.run_acceptance(root, 'comparison', None)
        finally:
            module.run_command = original
        manifest = json.loads((root / result['path'] / 'manifest.json').read_text())
        return dict(status=result['status'], command_executions=executions,
                    passed=sum(c['status'] == 'passed' for c in manifest['checks']),
                    blocked=sum(c['status'] == 'blocked' for c in manifest['checks']),
                    elapsed_ms=round((time.monotonic() - started) * 1000))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--baseline-ref', default='HEAD', help='Git revision containing the old runner')
    parser.add_argument('--output', type=Path, help='Optional sanitized aggregate JSON evidence')
    args = parser.parse_args()
    revision = subprocess.run(['git', 'rev-parse', '--verify', args.baseline_ref], capture_output=True, text=True, check=True).stdout.strip()
    source = subprocess.run(['git', 'show', f'{revision}:scripts/opsx_acceptance.py'], capture_output=True, text=True, check=True).stdout
    baseline = types.ModuleType('acceptance_benchmark_baseline')
    baseline.__file__ = str(Path(current.__file__))
    exec(compile(source, '<committed-acceptance-baseline>', 'exec'), baseline.__dict__)
    scenarios = {name: {'baseline': run_case(baseline, name), 'current': run_case(current, name)}
                 for name in ('local-evidence-gap', 'duplicate-readonly-command')}
    gap = scenarios['local-evidence-gap']; repeat = scenarios['duplicate-readonly-command']
    passed = (gap['current']['passed'] == 2 and gap['current']['blocked'] == 1
              and repeat['current']['passed'] == 3 and repeat['current']['command_executions'] == 1
              and repeat['baseline']['passed'] == 3)
    report = {'schema_version': 1, 'evidence_type': 'synthetic-comparison', 'baseline_revision': revision,
              'baseline_sha256': hashlib.sha256(source.encode()).hexdigest(),
              'status': 'passed' if passed else 'failed', 'scenarios': scenarios,
              'limitation': '隔离脚本夹具；不代表真实产品 Agent 全链路耗时或浏览器行为。'}
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps(report, ensure_ascii=False))
    return 0 if passed else 1


if __name__ == '__main__':
    raise SystemExit(main())
