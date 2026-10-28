"""Validate sanitized BUG-0068 evidence against the current implementation."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
CHANGE = ROOT/'openspec/changes/fix-chat-database-lock-execution-interruption'


def fingerprint(paths):
    return {name:hashlib.sha256((ROOT/name).read_bytes()).hexdigest() for name in paths}


def main():
    report = json.loads((CHANGE/'evidence/verification.json').read_text())
    assert report['inputs'] == fingerprint(report['inputs']), 'implementation or evidence input changed'
    assert report['sqlite']['failed'] == report['mysql']['failed'] == 0
    assert report['sqlite']['passed'] >= 155 and report['mysql']['passed'] >= 82
    live = json.loads((CHANGE/'evidence/live.json').read_text())
    assert live['status'] == 'completed' and live['real_executor']
    assert live['concurrent_checks'] > 0 and not live['check_failures']
    assert live['temporary_auth_removed'] and live['reread_matches'] and live['has_final']
    browser = json.loads((CHANGE/'evidence/browser.json').read_text())
    assert browser['post_count'] == 0 and browser['answer_copies'] == 1
    assert browser['timeline'][-1]['state'] in ('validated','recovered_valid')
    concurrency = json.loads((CHANGE/'evidence/concurrency.json').read_text())
    assert concurrency['rounds'] == 20 and concurrency['failed'] == 0
    assert report['temporary_resources_clean']
    print('BUG-0068: current SQLite/MySQL, isolated real executor and browser evidence verified')


if __name__ == '__main__':
    main()
