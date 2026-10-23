#!/usr/bin/env python3
"""Publish a separately reviewed compatibility certificate, never edit history."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src/backend'))
from app.governance import archive_recovery as recovery
from app.governance import compatible_successor as compatible


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--successor', required=True)
    parser.add_argument('--predecessor', required=True)
    parser.add_argument('--capability', required=True)
    parser.add_argument('--requirement', required=True)
    parser.add_argument('--review', required=True)
    parser.add_argument('--regression', required=True)
    parser.add_argument('--root', type=Path, default=ROOT)
    args = parser.parse_args()
    root = args.root.resolve()
    def folder(cid):
        if not recovery.IDENTITY.fullmatch(cid): raise ValueError('invalid identity')
        active = root/'openspec/changes'/cid
        paths = ([active] if active.is_dir() else []) + recovery.archive_paths(root, cid)
        if len(paths) != 1: raise ValueError('ambiguous identity')
        return paths[0]
    old, new = folder(args.predecessor), folder(args.successor)
    if old.parent.name != 'archive' or not recovery.completed_archive(old, args.predecessor):
        raise ValueError('predecessor must be a completed archive')
    key = (args.capability, args.requirement)
    before = recovery.delta_operations(old)[key][1]
    kind, after = recovery.delta_operations(new)[key]
    if kind != 'MODIFIED': raise ValueError('not an append modification')
    record = dict(schema_version=1, successor=args.successor, capability=key[0], requirement=key[1],
                  before_sha256=compatible.digest(before), after_sha256=compatible.digest(after),
                  added_scenarios=compatible.append_only(before, after), classification='compatible_append',
                  delta_sha256=recovery.tree_hash(new/'specs'), acceptance_sha256=compatible.acceptance_binding(root,new))
    for name in ('review','regression'):
        rel = getattr(args,name)
        path = root/rel
        item = {'path':rel,'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
        compatible.evidence_file(root,item)
        record[name]=item
    target=compatible.proof_path(root,args.successor,key)
    target.parent.mkdir(parents=True,exist_ok=True)
    # Publish atomically only after validating every bound input.
    raw=(json.dumps(record,ensure_ascii=False,sort_keys=True)+'\n').encode()
    if target.exists():
        if target.read_bytes()!=raw: raise ValueError('existing proof differs; preserve it and review a new successor')
        compatible.verify(root,args.successor,new,key,before,after)
        return
    # Validate statement payloads before creating the read-visible record.
    for name in ('review','regression'):
        evidence=json.loads(compatible.evidence_file(root,record[name]))
        for field in ('schema_version','successor','capability','requirement','before_sha256','after_sha256','added_scenarios','classification'):
            if evidence.get(field)!=record[field]: raise ValueError('evidence binding differs')
        if evidence.get('status')!='passed': raise ValueError('evidence not passed')
    review=json.loads(compatible.evidence_file(root,record['review']))
    regression=json.loads(compatible.evidence_file(root,record['regression']))
    if not review.get('reviewer') or not review.get('rationale') or review.get('contradictions') != []: raise ValueError('review incomplete')
    if not {'original_contract','added_scenarios','destructive_changes','broken_chain','concurrent_change'} <= set(regression.get('checks',[])): raise ValueError('regression incomplete')
    if record['acceptance_sha256']!=compatible.acceptance_binding(root,new) or record['delta_sha256']!=recovery.tree_hash(new/'specs'): raise ValueError('inputs changed')
    with tempfile.NamedTemporaryFile(dir=target.parent,delete=False) as file:
        file.write(raw);file.flush();os.fsync(file.fileno()); temporary=Path(file.name)
    try: os.link(temporary,target)
    finally: temporary.unlink()
    print('兼容追加证明已保存；历史记录保持不变。')

if __name__ == '__main__':
    main()
