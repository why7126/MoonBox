"""Validate the shape and invariants of already collected, sanitized live evidence.

This does not execute product actions or replace visual review.
"""
import json
from pathlib import Path


def main():
    base=Path('openspec/changes/add-object-archive-diagnostics/evidence')
    live=json.loads((base/'live-final-samples.json').read_text())
    recovery=json.loads((base/'live-recovery-and-denials.json').read_text())
    ui=json.loads((base/'ui/product-recovery.json').read_text())
    assert live['api_first_success']['data']['operations'][0]['replayed'] is False
    assert live['archive_hash_unchanged']
    assert live['block']['data']['reason']=='archive_finalization_blocked'
    assert recovery['original_identity_retained'] and recovery['completed_replay_unchanged']
    assert recovery['partial_requirement_unchanged']
    assert recovery['query_denied_status']==recovery['resume_denied_status']==403
    assert recovery['request_id'] and recovery['request_log_matches']==1
    assert ui['http_status']==200 and ui['response']['operation_id']==recovery['operation_id']==ui['operation_id']
    assert ui['response']['stage']=='completed' and ui['draft_preserved']
    assert not ui['narrow_page_overflow'] and 300<ui['styles']['width']<400
    print('Collected real API/CLI/browser invariants verified; visual semantics signed in acceptance.md.')


if __name__=='__main__':main()
