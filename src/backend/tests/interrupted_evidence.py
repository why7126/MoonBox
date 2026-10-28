"""Read-only verification of sanitized evidence for BUG-0069."""
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
SAMPLES = ROOT/'openspec/changes/fix-chat-interrupted-successor-proof/evidence/acceptance/samples'


def main():
    item = sys.argv[1]
    if item == 'preflight':
        styles = json.loads((SAMPLES/'styles.json').read_text())
        assert {row['viewport'] for row in styles} == {390, 1440}
        assert all(row['scrollWidth'] <= row['viewport'] for row in styles)
        print('Retained browser viewport/style evidence is readable; no new browser observation claimed.')
        return
    n = int(item)
    report = json.loads((SAMPLES/f'ac-{n:03}.json').read_text())
    assert report['passed'] is True
    for name, expected in report['inputs'].items():
        assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest() == expected, f'stale input: {name}'
    if n <= 5:
        assert report['sqlite']['failed'] == report['mysql']['failed'] == 0
        assert report['sqlite']['independent_passed'] == 49
        assert report['mysql']['core_passed'] == 83 and report['mysql']['task_incremental_passed'] == 10
    if n == 6:
        assert report['real_api'] and report['old_status_preserved'] and report['card_observed']
        assert report['states'] == ['available','busy','failure','success']
    if n == 7:
        assert report['external_standard_cli'] and report['history_preserved']
        assert report['verification_http'] == report['send_http'] == 200
        assert report['real_executor'] and report['followup_status'] == 'completed'
        assert report['temporary_auth_removed']
        assert hashlib.sha256((ROOT/report['source_test']).read_bytes()).hexdigest() == report['test_sha256']
    if n == 8:
        assert report['authorized'] and report['history_preserved'] and report['admission_ready']
        assert report['verification_state'] == 'recovered_valid'
    print(f'AC-{n:03}: current evidence verified')


if __name__ == '__main__':
    main()
