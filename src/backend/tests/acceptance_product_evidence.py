"""Export allowlisted facts from a disposable local acceptance controller."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import sqlite3


def export(root, output):
    root=root.resolve()
    if root.parent!=Path('/private/tmp') or not root.name.startswith(('moonbox-chat-e2e-','moonbox-product-acceptance-')):
        raise ValueError('isolated_root_required')
    output.parent.mkdir(parents=True,exist_ok=True)
    if root.name.startswith('moonbox-product-acceptance-'):
        report=json.loads((root/'report.json').read_text())
        report['screenshots']=[]
        for index,path in enumerate(sorted((root/'environments').rglob('*.png'))):
            name=output.stem+'-'+str(index)+'.png';shutil.copyfile(path,output.parent/name)
            report['screenshots'].append({'file':name,'sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
    else:
        queries={
            'turns':'SELECT id,conversation_id,status,error_code,created_at,updated_at FROM chat_turns',
            'operations':'SELECT id,source_turn_id,space_id,attempt_id,status,cleanup_state,resume_count,cancel_requested,reason_code,input_digest FROM verification_operations',
            'checks':'SELECT attempt_id,ac_id,status,reason_code,evidence_json FROM verification_ac_results',
            'tool_waits':'SELECT source_turn_id,operation_id,state,generation FROM verification_tool_waits',
            'deliveries':'SELECT operation_id,attempt_id,input_digest,state,target_turn_id FROM verification_result_deliveries',
            'archives':'SELECT operation_id,attempt_id,state,digest FROM verification_evidence_archives',
            'receipts':'SELECT turn_id,executor_closed,files_collected FROM moonbox_execution_receipts',
            'identities':'SELECT role,revocation_state FROM verification_identity_refs',
            'usage':'SELECT turn_id,status,tokens,actual_tokens FROM chat_usage_reservations'}
        with sqlite3.connect((root/'chat.db').as_uri()+'?mode=ro',uri=True) as db:
            db.row_factory=sqlite3.Row
            report={key:[dict(row) for row in db.execute(query)] for key,query in queries.items()}
        report.update(category='real_product_model_round',database_rows_injected=False)
    output.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('root',type=Path);parser.add_argument('output',type=Path)
    args=parser.parse_args();export(args.root,args.output)
