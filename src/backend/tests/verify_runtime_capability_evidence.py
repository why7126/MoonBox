"""Verify bounded, sanitized evidence for BUG-0045 without reopening resources."""
import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
EVIDENCE = ROOT / 'openspec/changes/fix-chat-acceptance-runtime-capability/evidence/acceptance'


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--preflight', action='store_true')
    args = parser.parse_args()
    styles = json.loads((EVIDENCE/'browser/computed-styles.json').read_text())['samples']
    assert len(styles) == 8
    for sample in styles:
        assert not sample['overflow'] and sample['padding'] == '20px'
        assert (EVIDENCE/f"browser/{sample['state']}-{sample['width']}.png").is_file()
    if args.preflight:
        print('Recorded browser capabilities and eight viewport/state samples available')
        return
    regression = json.loads((EVIDENCE/'manual/regression.json').read_text())
    assert regression['backend_passed'] == 176 and regression['frontend_passed'] == 11
    assert regression['typecheck'] == regression['web_build'] == 'passed'
    for relative, digest in regression['inputs'].items():
        assert hashlib.sha256((ROOT/relative).read_bytes()).hexdigest() == digest, relative
    python = json.loads((EVIDENCE/'manual/python-runtime.json').read_text())
    assert python['status'] == 'ready'
    mysql = json.loads((EVIDENCE/'manual/mysql.json').read_text())
    assert mysql['status'] == 'passed' and mysql['cleanup'] and mysql['exit_code'] == 0
    matrix = json.loads((EVIDENCE/'manual/product-matrix.json').read_text())
    assert matrix['status'] == 'passed' and matrix['cleanup_state'] == 'released'
    checks = {check['ac_id']: check['status'] for check in matrix['checks']}
    assert all(checks.get(ac) == 'passed' for ac in ('AC-LOCAL-MEMBER','AC-LOCAL-READER','AC-LOCAL-PYTEST','AC-LOCAL-NODE'))
    for relative, digest in matrix['source_hashes'].items():
        assert hashlib.sha256((ROOT/relative).read_bytes()).hexdigest() == digest, relative
    live = json.loads((EVIDENCE/'manual/chat-result.json').read_text())
    assert live['category'] == 'real_product_model_round' and not live['database_rows_injected']
    assert len(live['operations']) == 1
    operation = live['operations'][0]
    assert operation['status'] == 'passed' and operation['cleanup_state'] == 'released'
    assert operation['resume_count'] == 0 and not operation['cancel_requested']
    assert all(c['status'] == 'passed' for c in live['checks']) and len(live['checks']) == 4
    assert any(t['id'] == operation['source_turn_id'] and t['status'] == 'completed' for t in live['turns'])
    assert any(w['operation_id'] == operation['id'] and w['state'] == 'delivered' for w in live['tool_waits'])
    print('Current source fingerprints, Linux tests, MySQL isolation and real Chat result verified')


if __name__ == '__main__':
    main()
