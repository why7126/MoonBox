"""Validate sanitized real observations; never submits a product action."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
EVIDENCE = ROOT / 'openspec/changes/add-sprint-archive-chat-entry/evidence/acceptance'


def read(name):
    return json.loads((EVIDENCE / name).read_text())


def require(condition, reason):
    if not condition:
        raise SystemExit(reason)


def main():
    before = read('preparation-observation.json')
    rejected = read('signoff-rejection.json')
    for sample in (before, rejected):
        require(sample['counts'] == {'chat_conversations': 1, 'chat_turns': 0,
                'chat_messages': 0, 'governance_candidates': 0}, 'preparation-or-rejection-created-execution')
    require(rejected['active_sprint_exists'], 'rejection-archived-sprint')
    normal, recovered = read('live-observation.json'), read('recovery-observation.json')
    for sample, status, state in ((normal, 'completed', 'validated'), (recovered, 'stopped', 'recovered_valid')):
        require(sample['source'] == 'isolated-live-product', 'sample-not-isolated-product')
        require(sample['session_count'] == 1 and len(sample['turns']) == 1, 'duplicate-session-or-turn')
        turn = sample['turns'][0]
        require(turn['status'] == status, 'original-terminal-state-lost')
        writes = [s for s in turn['sync'] if not s['dry_run'] and s['exit_code'] == 0]
        require(len(writes) == 1, 'missing-or-repeated-sync')
        require(not sample['active_exists'] and sample['archive_exists'], 'archive-effect-missing')
        require(len(sample['guards']) == 1 and sample['guards'][0]['state'] == state
                and sample['guards'][0]['confirmed_stage'] == 'done'
                and sample['guards'][0]['operation_id'] == turn['id'], 'guard-does-not-match-original-operation')
    busy = read('busy-observation.json')
    require(busy['session_count'] == 1 and len(busy['turns']) == 1
            and busy['turns'][0]['id'] == recovered['turns'][0]['id']
            and busy['guards'][0]['state'] == 'running', 'busy-entry-created-new-operation')
    interrupt = read('recovery-interrupt.json')
    require(interrupt['turn_id'] == recovered['turns'][0]['id'] and interrupt['pre_interrupt_status'] == 'running'
            and interrupt['sync_sequences'] == [s['sequence'] for s in recovered['turns'][0]['sync'] if not s['dry_run']],
            'interrupt-not-after-real-sync')
    styles = read('ui/computed-styles.json')
    for viewport in ([1440,900], [768,900], [390,844]):
        require(any(s.get('stage') == 'draft-conflict' and s.get('viewport') == viewport
                    and s.get('scrollWidth') == viewport[0] for s in styles), 'visual-viewport-evidence-missing')
    print('Real Sprint evidence passed: normal completion, rejected send, one stopped/recovered operation, no duplicate sync; visual samples present.')


if __name__ == '__main__':
    main()
