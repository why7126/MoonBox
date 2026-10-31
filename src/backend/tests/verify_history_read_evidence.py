"""Verify BUG-0058 sanitized browser evidence and run its focused regressions."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parents[3]
CHANGE = 'fix-chat-history-read-lifecycle'


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--preflight', action='store_true')
    args = parser.parse_args()
    if args.preflight:
        for port, path in [(39046, '/tests/history-read-live.html'), (39047, '/api/fixture/history-scenes')]:
            with urlopen(f'http://127.0.0.1:{port}{path}', timeout=5) as response:
                assert response.status == 200
        print('Loopback synthetic browser/API environment available')
        return
    change = ROOT / 'openspec/changes' / CHANGE
    if not change.exists():
        matches = list((ROOT/'openspec/archive').glob('*-'+CHANGE))
        assert len(matches) == 1
        change = matches[0]
    evidence = change/'evidence/acceptance/browser'
    for mode in ['default', 'no-store']:
        for version in ['baseline', 'fixed']:
            rows = json.loads((evidence/f'{version}-{mode}.json').read_text())
            assert len(rows) == 12
            for rounds in [1, 10]:
                for visit in ['first', 'revisit']:
                    selected = [r for r in rows if r['sample'].startswith(f'{rounds}轮 ') and r['visit'] == visit]
                    assert len(selected) == 3 and all(r['status_ms'] is not None for r in selected)
                    if version == 'fixed':
                        for row in selected:
                            assert not any('/events' in k or k.endswith(('/diff','/context')) for k in row['requests'])
                            assert row['requests']['/api/v1/chat/turns/ROUND/summary']['count'] == rounds
                            if mode == 'no-store':
                                assert all(v['same_key_peak'] <= 1 for v in row['requests'].values())
    closed = json.loads((evidence/'closed-and-slow-window.json').read_text())
    assert closed['elapsed_ms'] >= 15000
    assert not any('/events' in k or k.endswith(('/diff','/context')) for k in closed['requests'])
    slow = closed['requests']['/api/v1/chat/governance-operations/synthetic-slow']
    assert slow['count'] == slow['same_key_peak'] == 1 and slow['duration'][0] >= 5000
    reuse = json.loads((evidence/'detail-reuse.json').read_text())
    pages = lambda row: {k:v['count'] for k,v in row['requests'].items() if '/events' in k}
    assert pages(reuse['first']) == pages(reuse['reopen']) and len(pages(reuse['first'])) == 3
    active = json.loads((evidence/'active-states.json').read_text())
    assert [x['state'] for x in active] == ['queued','running','unknown','stopping','completed']
    assert '已完成' not in active[2]['display'] and '已完成' in active[-1]['display']
    stopped = json.loads((evidence/'terminal-stop.json').read_text())
    assert stopped['after']['elapsed_ms'] - stopped['before']['elapsed_ms'] >= 15000
    counts = lambda row: {k:v['count'] for k,v in row['requests'].items() if '/turns/' in k}
    assert counts(stopped['before']) == counts(stopped['after'])
    observations = json.loads((evidence/'observations.json').read_text())
    assert observations['visual_review'] == 'passed'
    assert observations['states'] == ['queued','running','unknown','stopping','completed']
    for relative, expected in observations['source_sha256'].items():
        assert hashlib.sha256((ROOT/relative).read_bytes()).hexdigest() == expected, relative+' changed since collection'
    commands = [
        ([sys.executable,'-m','pytest','src/backend/tests/test_chat_history_summary.py','-q'],ROOT),
        (['node','node_modules/vitest/vitest.mjs','run','src/components/chat'],ROOT/'src/web'),
        (['node','node_modules/typescript/bin/tsc','-b','--pretty','false'],ROOT/'src/web'),
    ]
    for argv,cwd in commands:
        subprocess.run(argv,cwd=cwd,check=True,env=os.environ.copy())
    sys.path.insert(0, str(ROOT/'src/backend'))
    from app.main import app
    assert app.openapi() == json.loads((ROOT/'src/web/openapi.json').read_text())
    print('BUG-0058 browser evidence, API, component regressions and typecheck passed')

if __name__ == '__main__':
    main()
