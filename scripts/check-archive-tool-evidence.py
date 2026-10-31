#!/usr/bin/env python3
"""Check recorded real-container evidence against the current package sources."""
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
files={}
for relative in ('scripts','src/backend/app','rules'):
    allowed={'.py','.sh'} if relative=='scripts' else {'.py'} if relative=='src/backend/app' else {'.md','.json','.yaml','.yml'}
    for path in sorted((ROOT/relative).rglob('*')):
        if '__pycache__' in path.parts or path.suffix not in allowed or not path.is_file():continue
        assert not path.is_symlink()
        files[path.relative_to(ROOT).as_posix()]=hashlib.sha256(path.read_bytes()).hexdigest()
raw=(json.dumps({'schema_version':1,'files':files},sort_keys=True,separators=(',',':'))+'\n').encode()
report=json.loads((ROOT/'openspec/changes/add-archive-tool-version-routing/evidence/container-routing.json').read_text())
assert report['positive']['digest']==hashlib.sha256(raw).hexdigest(), 'container evidence stale'
assert all(report['positive'][k] for k in ('cli','service_driver','actual_child_startup','readonly','business_root_preserved'))
assert report['digest_mismatch_rejected'] and report['missing_package_rejected'] and report['history_unknown_occupancy_unchanged']
print('Current package matches real container evidence; CLI/service/child and rejection checks passed.')
